from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Request, RequestStatus, User, UserRole, Match, MatchStatus, Donation
from app.schemas import RequestCreate, RequestUpdate, RequestResponse, NGOPlatformMatchResponse, DonationResponse
from app.utils.security import get_current_user, require_role, require_verified_user

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(
    request_in: RequestCreate,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db)
):
    request = Request(
        ngo_id=current_user.id,
        category=request_in.category,
        item_type=request_in.item_type,
        size=request_in.size,
        age_group=request_in.age_group,
        gender=request_in.gender,
        season=request_in.season,
        quantity_needed=request_in.quantity_needed,
        urgency=request_in.urgency,
        beneficiary_group=request_in.beneficiary_group,
        deadline=request_in.deadline,
        status=RequestStatus.ACTIVE
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("", response_model=List[RequestResponse])
def list_requests(
    status_filter: Optional[RequestStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Request)
    if current_user.role == UserRole.NGO:
        query = query.filter(Request.ngo_id == current_user.id)
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if status_filter:
        query = query.filter(Request.status == status_filter)
    return query.order_by(Request.created_at.desc()).all()


@router.get("/{request_id}", response_model=RequestResponse)
def get_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    if request.ngo_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    return request


@router.patch("/{request_id}", response_model=RequestResponse)
def update_request(
    request_id: int,
    request_in: RequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    if request.ngo_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = request_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(request, field, value)
    
    db.commit()
    db.refresh(request)
    return request


@router.get("/{request_id}/matches", response_model=List[NGOPlatformMatchResponse])
def get_request_matches(
    request_id: int,
    current_user: User = Depends(require_role(UserRole.NGO)),
    db: Session = Depends(get_db)
):
    """Get all matches for a specific request belonging to the NGO"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    if request.ngo_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    matches = db.query(Match).filter(Match.request_id == request_id).all()
    
    result = []
    for match in matches:
        donation = match.donation
        donor = donation.donor if donation else None
        # Calculate general area from donor lat/lng (simple approach)
        donor_area = None
        if donor and donor.lat is not None and donor.lng is not None:
            # Simple area representation - could be enhanced with reverse geocoding
            donor_area = f"Lat: {donor.lat:.4f}, Lng: {donor.lng:.4f}"
        
        # Convert SQLAlchemy Donation to DonationResponse schema
        donation_schema = DonationResponse.model_validate(donation) if donation else None
        
        result.append(NGOPlatformMatchResponse(
            id=match.id,
            donation_id=match.donation_id,
            request_id=match.request_id,
            score=match.score,
            score_breakdown=match.score_breakdown,
            status=match.status,
            created_at=match.created_at,
            donation=donation_schema,
            donor_area=donor_area
        ))
    
    return result


@router.get("/matches/all", response_model=List[NGOPlatformMatchResponse])
def get_all_matches_for_ngo(
    current_user: User = Depends(require_role(UserRole.NGO)),
    db: Session = Depends(get_db)
):
    """Get all matches for all requests belonging to the NGO"""
    # Get all request IDs for this NGO
    request_ids = db.query(Request.id).filter(Request.ngo_id == current_user.id).all()
    request_ids = [r[0] for r in request_ids]
    
    if not request_ids:
        return []
    
    matches = db.query(Match).filter(Match.request_id.in_(request_ids)).all()
    
    result = []
    for match in matches:
        donation = match.donation
        donor = donation.donor if donation else None
        donor_area = None
        if donor and donor.lat is not None and donor.lng is not None:
            donor_area = f"Lat: {donor.lat:.4f}, Lng: {donor.lng:.4f}"
        
        result.append(NGOPlatformMatchResponse(
            id=match.id,
            donation_id=match.donation_id,
            request_id=match.request_id,
            score=match.score,
            score_breakdown=match.score_breakdown,
            status=match.status,
            created_at=match.created_at,
            donation=match.donation,
            donor_area=donor_area
        ))
    
    return result