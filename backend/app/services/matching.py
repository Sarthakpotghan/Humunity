from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import math
from sentence_transformers import SentenceTransformer
from app.models import Donation, Request, Match, MatchStatus, RequestStatus, DonationStatus, User, NgoProfile
from app.config import get_settings

settings = get_settings()

model = None


def get_embedding_model():
    global model
    if model is None:
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def compute_urgency_score(request: Request) -> float:
    base = request.urgency / 5.0
    if request.deadline:
        days_left = (request.deadline - datetime.utcnow()).days
        if days_left <= 0:
            return 1.0
        elif days_left <= 3:
            return min(1.0, base + 0.3)
        elif days_left <= 7:
            return min(1.0, base + 0.15)
    return base


def compute_similarity_score(donation: Donation, request: Request) -> float:
    donation_text = f"{donation.item_type} {donation.description or ''} {donation.category.value} {donation.season or ''}"
    request_text = f"{request.item_type} {request.category.value} {request.season or ''} {request.beneficiary_group or ''}"
    
    embedder = get_embedding_model()
    emb1 = embedder.encode([donation_text])
    emb2 = embedder.encode([request_text])
    
    from sklearn.metrics.pairwise import cosine_similarity
    sim = cosine_similarity(emb1, emb2)[0][0]
    return max(0.0, float(sim))


def compute_seasonal_score(donation: Donation) -> float:
    if not donation.season:
        return 0.5
    current_month = datetime.utcnow().month
    season_months = {
        "spring": [3, 4, 5],
        "summer": [6, 7, 8],
        "autumn": [9, 10, 11],
        "winter": [12, 1, 2],
    }
    if current_month in season_months.get(donation.season, []):
        return 1.0
    return 0.3


def compute_proximity_score(donation: Donation, request: Request) -> float:
    if not all([donation.lat, donation.lng, request.ngo.lat, request.ngo.lng]):
        return 0.5
    distance = haversine(donation.lat, donation.lng, request.ngo.lat, request.ngo.lng)
    max_dist = settings.MAX_MATCH_DISTANCE_KM
    return max(0.0, 1.0 - (distance / max_dist))


def compute_quantity_fit(donation: Donation, request: Request) -> float:
    if request.quantity_needed <= 0:
        return 0.0
    return min(1.0, donation.quantity / request.quantity_needed)


def compute_condition_score(donation: Donation) -> float:
    condition_scores = {"new": 1.0, "good": 0.7, "fair": 0.4}
    return condition_scores.get(donation.condition.value, 0.5)


def compute_reliability_score(request: Request) -> float:
    if request.ngo.ngo_profile:
        return request.ngo.ngo_profile.reliability_score
    return 1.0


def calculate_match_score(donation: Donation, request: Request) -> Tuple[float, Dict]:
    urgency = compute_urgency_score(request)
    similarity = compute_similarity_score(donation, request)
    seasonal = compute_seasonal_score(donation)
    proximity = compute_proximity_score(donation, request)
    quantity = compute_quantity_fit(donation, request)
    condition = compute_condition_score(donation)
    reliability = compute_reliability_score(request)

    # Default weights. `proximity`/`similarity` were re-tuned via offline grid
    # search (see notebooks/03_weight_tuning.ipynb) which raised NDCG@5 by ~0.11
    # and cut mean match distance by ~700 km on the synthetic benchmark.
    weights = {
        "urgency": 0.056,
        "similarity": 0.111,
        "seasonal": 0.056,
        "proximity": 0.333,
        "quantity_fit": 0.111,
        "condition": 0.222,
        "reliability": 0.111,
    }

    score = (
        weights["urgency"] * urgency +
        weights["similarity"] * similarity +
        weights["seasonal"] * seasonal +
        weights["proximity"] * proximity +
        weights["quantity_fit"] * quantity +
        weights["condition"] * condition +
        weights["reliability"] * reliability
    )
    
    breakdown = {
        "urgency": {"value": urgency, "weight": weights["urgency"], "contribution": weights["urgency"] * urgency},
        "similarity": {"value": similarity, "weight": weights["similarity"], "contribution": weights["similarity"] * similarity},
        "seasonal": {"value": seasonal, "weight": weights["seasonal"], "contribution": weights["seasonal"] * seasonal},
        "proximity": {"value": proximity, "weight": weights["proximity"], "contribution": weights["proximity"] * proximity},
        "quantity_fit": {"value": quantity, "weight": weights["quantity_fit"], "contribution": weights["quantity_fit"] * quantity},
        "condition": {"value": condition, "weight": weights["condition"], "contribution": weights["condition"] * condition},
        "reliability": {"value": reliability, "weight": weights["reliability"], "contribution": weights["reliability"] * reliability},
        "total_score": score,
    }
    
    return score, breakdown


def run_matching_for_donation(donation_id: int, db: Session, top_n: int = 5) -> List[Match]:
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        return []
    
    requests = db.query(Request).join(User, Request.ngo_id == User.id).filter(
        Request.category == donation.category,
        Request.status == RequestStatus.ACTIVE,
        User.lat.isnot(None),
        User.lng.isnot(None),
        User.verified == True
    ).all()
    
    if not donation.lat or not donation.lng:
        return []
    
    scored_requests = []
    for req in requests:
        if not req.ngo.lat or not req.ngo.lng:
            continue
        distance = haversine(donation.lat, donation.lng, req.ngo.lat, req.ngo.lng)
        if distance > settings.MAX_MATCH_DISTANCE_KM:
            continue
        score, breakdown = calculate_match_score(donation, req)
        scored_requests.append((req, score, breakdown))
    
    scored_requests.sort(key=lambda x: x[1], reverse=True)
    top_requests = scored_requests[:top_n]
    
    matches = []
    for req, score, breakdown in top_requests:
        match = Match(
            donation_id=donation.id,
            request_id=req.id,
            score=score,
            score_breakdown=breakdown,
            status=MatchStatus.PENDING
        )
        db.add(match)
        matches.append(match)
    
    db.commit()
    for m in matches:
        db.refresh(m)
    return matches