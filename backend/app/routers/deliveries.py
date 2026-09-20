from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import Delivery, DeliveryStatus, DeliveryMode, DeliveryEvent, Match, MatchStatus, User, UserRole, DonationStatus
from app.schemas import DeliveryCreate, DeliveryUpdate, DeliveryResponse, DeliveryEventResponse
from app.utils.security import get_current_user, require_role
from app.services.maps import get_route

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.post("", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(
    delivery_in: DeliveryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    match = db.query(Match).filter(Match.id == delivery_in.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match.status != MatchStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="Match not accepted")
    if match.donation.donor_id != current_user.id and match.request.ngo_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    existing = db.query(Delivery).filter(Delivery.match_id == delivery_in.match_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Delivery already exists for this match")
    
    delivery = Delivery(
        match_id=delivery_in.match_id,
        mode=delivery_in.mode,
        volunteer_id=delivery_in.volunteer_id,
        scheduled_at=delivery_in.scheduled_at,
        status=DeliveryStatus.SCHEDULED
    )
    db.add(delivery)
    
    event = DeliveryEvent(delivery=delivery, status=DeliveryStatus.SCHEDULED)
    db.add(event)
    
    match.donation.status = DonationStatus.PICKUP_SCHEDULED
    db.commit()
    db.refresh(delivery)
    return delivery


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(
    delivery_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    match = delivery.match
    if match.donation.donor_id != current_user.id and match.request.ngo_id != current_user.id and delivery.volunteer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    return delivery


@router.patch("/{delivery_id}/status", response_model=DeliveryResponse)
def update_delivery_status(
    delivery_id: int,
    status_update: DeliveryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    match = delivery.match
    if match.donation.donor_id != current_user.id and match.request.ngo_id != current_user.id and delivery.volunteer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = status_update.model_dump(exclude_unset=True)
    if "status" in update_data:
        new_status = update_data["status"]
        delivery.status = new_status
        event = DeliveryEvent(delivery_id=delivery.id, status=new_status)
        db.add(event)
        
        if new_status == DeliveryStatus.IN_TRANSIT:
            match.donation.status = DonationStatus.IN_TRANSIT
        elif new_status == DeliveryStatus.DELIVERED:
            match.donation.status = DonationStatus.DELIVERED
            delivery.delivered_at = datetime.utcnow()
        elif new_status == DeliveryStatus.CONFIRMED:
            match.donation.status = DonationStatus.CONFIRMED
    
    for field, value in update_data.items():
        if field != "status":
            setattr(delivery, field, value)
    
    db.commit()
    db.refresh(delivery)
    return delivery


@router.get("/{delivery_id}/route")
async def get_delivery_route(
    delivery_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    match = delivery.match
    if match.donation.donor_id != current_user.id and match.request.ngo_id != current_user.id and delivery.volunteer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    donor_lat, donor_lng = match.donation.lat, match.donation.lng
    ngo_lat, ngo_lng = match.request.ngo.lat, match.request.ngo.lng
    
    if not all([donor_lat, donor_lng, ngo_lat, ngo_lng]):
        raise HTTPException(status_code=400, detail="Missing location data")
    
    waypoints = [(donor_lat, donor_lng), (ngo_lat, ngo_lng)]
    route = await get_route(waypoints)
    return route


@router.get("/{delivery_id}/events", response_model=List[DeliveryEventResponse])
def get_delivery_events(
    delivery_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    match = delivery.match
    if match.donation.donor_id != current_user.id and match.request.ngo_id != current_user.id and delivery.volunteer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    return delivery.events