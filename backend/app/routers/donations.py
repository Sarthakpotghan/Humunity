from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Donation, DonationPhoto, DonationStatus, User, UserRole
from app.schemas import DonationCreate, DonationUpdate, DonationResponse, DonationPhotoResponse
from app.utils.security import get_current_user, require_role
from app.services.nlp import extract_donation_fields
from app.services.maps import geocode_user_address
import asyncio
import os
import shutil
from uuid import uuid4

router = APIRouter(prefix="/donations", tags=["donations"])

UPLOAD_DIR = "uploads/donations"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("", response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
def create_donation(
    donation_in: DonationCreate,
    current_user: User = Depends(require_role(UserRole.DONOR)),
    db: Session = Depends(get_db)
):
    # Extract structured fields from description if provided
    extracted = {}
    if donation_in.description:
        extracted = extract_donation_fields(donation_in.description)
    
    # Use provided lat/lng, fall back to user's stored lat/lng
    lat = donation_in.lat or current_user.lat
    lng = donation_in.lng or current_user.lng
    
    # If no coordinates but user has address, geocode it
    if (lat is None or lng is None) and current_user.address:
        try:
            coords = asyncio.run(geocode_user_address(current_user.address))
            if coords:
                lat, lng = coords
                # Cache on user for future use
                current_user.lat = lat
                current_user.lng = lng
        except Exception:
            pass  # Gracefully ignore geocoding failure
    
    donation = Donation(
        donor_id=current_user.id,
        category=donation_in.category,
        item_type=donation_in.item_type,
        size=donation_in.size or extracted.get("size"),
        age_group=donation_in.age_group or extracted.get("age_group"),
        gender=donation_in.gender or extracted.get("gender"),
        season=donation_in.season or extracted.get("season"),
        condition=donation_in.condition,
        quantity=donation_in.quantity,
        description=donation_in.description,
        lat=lat,
        lng=lng,
        available_from=donation_in.available_from,
        available_to=donation_in.available_to,
        status=DonationStatus.LISTED
    )
    db.add(donation)
    db.commit()
    db.refresh(donation)
    return donation


@router.get("", response_model=List[DonationResponse])
def list_donations(
    status_filter: Optional[DonationStatus] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Donation).filter(Donation.donor_id == current_user.id)
    if status_filter:
        query = query.filter(Donation.status == status_filter)
    if category:
        query = query.filter(Donation.category == category)
    return query.order_by(Donation.created_at.desc()).all()


@router.get("/{donation_id}", response_model=DonationResponse)
def get_donation(
    donation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if donation.donor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    return donation


@router.patch("/{donation_id}", response_model=DonationResponse)
def update_donation(
    donation_id: int,
    donation_in: DonationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if donation.donor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if donation.status != DonationStatus.LISTED:
        raise HTTPException(status_code=400, detail="Cannot update donation in current status")
    
    update_data = donation_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(donation, field, value)
    
    db.commit()
    db.refresh(donation)
    return donation


@router.delete("/{donation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_donation(
    donation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if donation.donor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if donation.status != DonationStatus.LISTED:
        raise HTTPException(status_code=400, detail="Cannot delete donation in current status")
    
    db.delete(donation)
    db.commit()


@router.post("/{donation_id}/photos", response_model=DonationPhotoResponse)
def upload_photo(
    donation_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if donation.donor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    photo = DonationPhoto(donation_id=donation_id, url=f"/{filepath}")
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo