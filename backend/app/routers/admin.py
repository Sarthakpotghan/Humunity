from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole, NgoProfile
from app.schemas import NgoProfileResponse, UserResponse
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ngos/pending", response_model=List[NgoProfileResponse])
def list_pending_ngos(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    ngos = db.query(NgoProfile).join(User).filter(
        User.verified == False,
        User.role == UserRole.NGO
    ).all()
    return ngos


@router.patch("/ngos/{ngo_id}/verify", response_model=NgoProfileResponse)
def verify_ngo(
    ngo_id: int,
    approve: bool = True,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    ngo = db.query(NgoProfile).filter(NgoProfile.id == ngo_id).first()
    if not ngo:
        raise HTTPException(status_code=404, detail="NGO not found")
    
    user = ngo.user
    user.verified = approve
    db.commit()
    db.refresh(ngo)
    return ngo


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