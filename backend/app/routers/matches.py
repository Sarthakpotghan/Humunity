from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Match, MatchStatus, Donation, DonationStatus, User, UserRole
from app.schemas import MatchResponse, MatchAction
from app.utils.security import get_current_user, require_role
from app.services.matching import run_matching_for_donation

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
    return matches


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
    
    return db.query(Match).filter(Match.donation_id == donation_id).all()


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
    
    match.status = MatchStatus.ACCEPTED
    match.donation.status = DonationStatus.ACCEPTED
    db.commit()
    db.refresh(match)
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
    return match