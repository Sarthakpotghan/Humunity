from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Match, MatchStatus, Donation, DonationStatus, User, UserRole, Delivery, DeliveryStatus, DeliveryMode, DeliveryEvent
from app.schemas import MatchResponse, MatchAction
from app.utils.security import get_current_user, require_role
from app.services.matching import run_matching_for_donation
from app.services.notifier import notify_match_created_sync, notify_match_accepted_sync, notify_match_rejected_sync
from app.services.maps import calculate_distance_km, suggest_delivery_mode

router = APIRouter(prefix="/donations", tags=["matches"])


@router.post("/{donation_id}/match", response_model=List[MatchResponse])
def match_donation(
    donation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if donation.donor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    if donation.status != DonationStatus.LISTED:
        raise HTTPException(status_code=400, detail="Donation not in listed status")
    
    matches = run_matching_for_donation(donation_id, db)
    donation.status = DonationStatus.MATCHED
    db.commit()
    for match in matches:
        try:
            notify_match_created_sync(db, match)
        except Exception:
            pass
    
    # Enrich with NGO name
    result = []
    for match in matches:
        match_dict = {
            "id": match.id,
            "donation_id": match.donation_id,
            "request_id": match.request_id,
            "score": match.score,
            "score_breakdown": match.score_breakdown,
            "status": match.status,
            "created_at": match.created_at,
            "ngo_name": match.request.ngo.name if match.request and match.request.ngo else None
        }
        result.append(match_dict)
    
    return result


@router.get("/{donation_id}/matches", response_model=List[MatchResponse])
def get_matches(
    donation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if donation.donor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    matches = db.query(Match).filter(Match.donation_id == donation_id).all()
    
    # Enrich with NGO name
    result = []
    for match in matches:
        match_dict = {
            "id": match.id,
            "donation_id": match.donation_id,
            "request_id": match.request_id,
            "score": match.score,
            "score_breakdown": match.score_breakdown,
            "status": match.status,
            "created_at": match.created_at,
            "ngo_name": match.request.ngo.name if match.request and match.request.ngo else None
        }
        result.append(match_dict)
    
    return result


@router.patch("/matches/{match_id}/accept", response_model=MatchResponse)
def accept_match(
    match_id: int,
    current_user: User = Depends(require_role(UserRole.NGO)),
    db: Session = Depends(get_db)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match.request.ngo_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if match.status != MatchStatus.PENDING:
        raise HTTPException(status_code=400, detail="Match not in pending status")
    
    # Calculate distance and determine delivery mode
    donation = match.donation
    ngo = match.request.ngo
    mode = DeliveryMode.DROPOFF
    location_unknown = False
    
    if donation.lat is not None and donation.lng is not None and ngo.lat is not None and ngo.lng is not None:
        from app.services.maps import calculate_distance_km, suggest_delivery_mode
        distance_km = calculate_distance_km(donation.lat, donation.lng, ngo.lat, ngo.lng)
        mode_str, long_distance_flag = suggest_delivery_mode(distance_km)
        
        if distance_km <= 5.0:
            mode = DeliveryMode.DROPOFF
        elif distance_km <= 25.0:
            mode = DeliveryMode.PICKUP
        else:
            mode = DeliveryMode.DROPOFF
    else:
        mode = DeliveryMode.DROPOFF
        location_unknown = True
    
    # Check if delivery already exists
    existing_delivery = db.query(Delivery).filter(Delivery.match_id == match.id).first()
    if not existing_delivery:
        delivery = Delivery(
            match_id=match.id,
            mode=mode,
            status=DeliveryStatus.SCHEDULED,
            location_unknown=location_unknown
        )
        db.add(delivery)
        db.flush()
        
        event = DeliveryEvent(delivery_id=delivery.id, status=DeliveryStatus.SCHEDULED)
        db.add(event)
        
        match.donation.status = DonationStatus.PICKUP_SCHEDULED
    else:
        # Delivery already exists, just update match status
        pass
    
    match.status = MatchStatus.ACCEPTED
    match.donation.status = DonationStatus.ACCEPTED
    db.commit()
    db.refresh(match)
    try:
        notify_match_accepted_sync(db, match)
    except Exception:
        pass
    return match


@router.patch("/matches/{match_id}/reject", response_model=MatchResponse)
def reject_match(
    match_id: int,
    current_user: User = Depends(require_role(UserRole.NGO)),
    db: Session = Depends(get_db)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match.request.ngo_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if match.status != MatchStatus.PENDING:
        raise HTTPException(status_code=400, detail="Match not in pending status")
    
    match.status = MatchStatus.REJECTED
    db.commit()
    db.refresh(match)
    try:
        notify_match_rejected_sync(db, match)
    except Exception:
        pass
    return match