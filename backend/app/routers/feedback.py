from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Feedback, Match, MatchStatus, User, UserRole, Delivery, DeliveryStatus, NgoProfile, Request
from app.schemas import FeedbackCreate, FeedbackResponse
from app.utils.security import get_current_user
from app.services.notifier import create_notification

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_in: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    match = db.query(Match).filter(Match.id == feedback_in.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match.status != MatchStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="Can only give feedback on accepted matches")

    is_donor = match.donation.donor_id == current_user.id
    is_ngo = match.request.ngo_id == current_user.id
    if not is_donor and not is_ngo:
        raise HTTPException(status_code=403, detail="Not authorized")

    existing = db.query(Feedback).filter(
        Feedback.match_id == feedback_in.match_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Feedback already exists for this match")

    delivery = db.query(Delivery).filter(Delivery.match_id == match.id).first()
    if not delivery or delivery.status not in [DeliveryStatus.DELIVERED, DeliveryStatus.CONFIRMED]:
        raise HTTPException(status_code=400, detail="Delivery must be completed before feedback")

    feedback = Feedback(
        match_id=feedback_in.match_id,
        giver_id=current_user.id,
        rating=feedback_in.rating,
        comments=feedback_in.comments,
    )
    db.add(feedback)

    target_id = match.request.ngo_id if is_donor else match.donation.donor_id
    giver_label = "A donor" if is_donor else match.request.ngo.name
    create_notification(db, target_id, f"{giver_label} left a {feedback_in.rating}-star rating for match #{match.id}.")

    if is_donor:
        ngo_profile = db.query(NgoProfile).filter(NgoProfile.user_id == match.request.ngo_id).first()
        if ngo_profile:
            avg_rating = db.query(func.avg(Feedback.rating)).join(
                Match, Feedback.match_id == Match.id
            ).join(
                Request, Match.request_id == Request.id
            ).filter(Request.ngo_id == match.request.ngo_id).scalar()
            if avg_rating:
                ngo_profile.reliability_score = round(float(avg_rating) / 5.0 * 0.9 + 0.1, 2)

    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/match/{match_id}", response_model=List[FeedbackResponse])
def get_match_feedback(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match.donation.donor_id != current_user.id and match.request.ngo_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(Feedback).filter(Feedback.match_id == match_id).all()


@router.get("/ngo/{ngo_id}", response_model=List[FeedbackResponse])
def get_ngo_feedback(
    ngo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Feedback).join(
        Match, Feedback.match_id == Match.id
    ).join(
        Request, Match.request_id == Request.id
    ).filter(Request.ngo_id == ngo_id).all()