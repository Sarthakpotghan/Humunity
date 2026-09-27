from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole, NgoProfile
from app.schemas import NgoProfileResponse, UserResponse, PendingNGOResponse
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ngos/pending", response_model=List[PendingNGOResponse])
def list_pending_ngos(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    results = []
    
    # Get NGOs with profiles that are pending verification
    ngos_with_profiles = db.query(NgoProfile).join(User).filter(
        User.verified == False,
        User.role == UserRole.NGO
    ).all()
    
    for ngo in ngos_with_profiles:
        user = ngo.user
        results.append(PendingNGOResponse(
            id=ngo.id,
            user_id=ngo.user_id,
            reg_number=ngo.reg_number,
            reg_doc_url=ngo.reg_doc_url,
            focus_areas=ngo.focus_areas,
            reliability_score=ngo.reliability_score,
            ngo_name=user.name if user else None,
            email=user.email if user else None,
            phone=user.phone if user else None,
            address=user.address if user else None,
            lat=user.lat if user else None,
            lng=user.lng if user else None,
            verified=user.verified if user else False,
            created_at=user.created_at if user else None,
            has_profile=True
        ))
    
    # Also get NGO users who don't have a profile yet (verified=False, role=NGO, no NgoProfile)
    ngo_users_without_profile = db.query(User).filter(
        User.role == UserRole.NGO,
        User.verified == False,
        ~User.id.in_(
            db.query(NgoProfile.user_id).filter(NgoProfile.user_id == User.id)
        )
    ).all()
    
    for user in ngo_users_without_profile:
        results.append(PendingNGOResponse(
            id=user.id,  # Use user.id as identifier
            user_id=user.id,
            reg_number=None,
            reg_doc_url=None,
            focus_areas=None,
            reliability_score=1.0,
            ngo_name=user.name,
            email=user.email,
            phone=user.phone,
            address=user.address,
            lat=user.lat,
            lng=user.lng,
            verified=user.verified,
            created_at=user.created_at,
            has_profile=False
        ))
    
    return results


@router.patch("/ngos/{identifier}/verify", response_model=PendingNGOResponse)
def verify_ngo(
    identifier: int,
    approve: bool = True,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Verify an NGO. The identifier can be either:
    - NgoProfile.id (for NGOs with profiles)
    - User.id (for NGOs without profiles yet)
    """
    # First try to find by NgoProfile.id
    ngo = db.query(NgoProfile).filter(NgoProfile.id == identifier).first()
    
    if ngo:
        # Found by NgoProfile.id
        user = ngo.user
        if approve:
            user.verified = True
            db.commit()
            db.refresh(ngo)
            user = ngo.user
            return PendingNGOResponse(
                id=ngo.id,
                user_id=ngo.user_id,
                reg_number=ngo.reg_number,
                reg_doc_url=ngo.reg_doc_url,
                focus_areas=ngo.focus_areas,
                reliability_score=ngo.reliability_score,
                ngo_name=user.name if user else None,
                email=user.email if user else None,
                phone=user.phone if user else None,
                address=user.address if user else None,
                lat=user.lat if user else None,
                lng=user.lng if user else None,
                verified=user.verified if user else False,
                created_at=user.created_at if user else None,
                has_profile=True
            )
        else:
            # Reject: delete the NGO profile and user
            ngo_name = ngo.user.name if ngo.user else None
            db.delete(ngo)
            db.delete(user)
            db.commit()
            return PendingNGOResponse(
                id=identifier,
                user_id=identifier,
                reg_number=None,
                reg_doc_url=None,
                focus_areas=None,
                reliability_score=1.0,
                ngo_name=ngo_name,
                has_profile=True
            )
    
    # Try to find by User.id (for NGOs without profiles)
    user = db.query(User).filter(
        User.id == identifier,
        User.role == UserRole.NGO,
        User.verified == False
    ).first()
    
    if user:
        if approve:
            user.verified = True
            db.commit()
            db.refresh(user)
            return PendingNGOResponse(
                id=user.id,
                user_id=user.id,
                reg_number=None,
                reg_doc_url=None,
                focus_areas=None,
                reliability_score=1.0,
                ngo_name=user.name,
                email=user.email,
                phone=user.phone,
                address=user.address,
                lat=user.lat,
                lng=user.lng,
                verified=user.verified,
                created_at=user.created_at,
                has_profile=False
            )
        else:
            # Reject: delete the user
            ngo_name = user.name
            db.delete(user)
            db.commit()
            return PendingNGOResponse(
                id=identifier,
                user_id=identifier,
                reg_number=None,
                reg_doc_url=None,
                focus_areas=None,
                reliability_score=1.0,
                ngo_name=ngo_name,
                has_profile=False
            )
    
    raise HTTPException(status_code=404, detail="NGO not found")


@router.get("/users", response_model=List[UserResponse])
def list_users(
    role: UserRole = None,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.all()


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = new_role
    if new_role != UserRole.NGO:
        user.verified = True
    db.commit()
    return {"message": "Role updated"}