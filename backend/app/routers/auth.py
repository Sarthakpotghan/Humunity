from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole, NgoProfile
from app.schemas import UserCreate, UserLogin, UserResponse, Token, NgoProfileCreate, NgoProfileResponse
from app.utils.security import verify_password, get_password_hash, create_access_token, get_current_user, require_role

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        name=user_in.name,
        role=user_in.role,
        phone=user_in.phone,
        address=user_in.address,
        password_hash=hashed_password,
        verified=user_in.role != UserRole.NGO
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    if user_in.role == UserRole.NGO:
        # NGO profile will be created via separate endpoint
        pass
    
    return user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Block unverified NGOs from logging in
    if user.role == UserRole.NGO and not user.verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your NGO account is pending admin approval. Please wait for verification before logging in."
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/ngo/profile", response_model=NgoProfileResponse, status_code=status.HTTP_201_CREATED)
def create_ngo_profile(
    profile_in: NgoProfileCreate,
    current_user: User = Depends(require_role(UserRole.NGO)),
    db: Session = Depends(get_db)
):
    existing = db.query(NgoProfile).filter(NgoProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="NGO profile already exists")
    
    profile = NgoProfile(
        user_id=current_user.id,
        reg_number=profile_in.reg_number,
        reg_doc_url=profile_in.reg_doc_url,
        focus_areas=profile_in.focus_areas
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/ngo/profile", response_model=NgoProfileResponse)
def get_ngo_profile(
    current_user: User = Depends(require_role(UserRole.NGO)),
    db: Session = Depends(get_db)
):
    profile = db.query(NgoProfile).filter(NgoProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="NGO profile not found")
    return profile