from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import Delivery, DeliveryStatus, DeliveryMode, DeliveryEvent, Match, MatchStatus, User, UserRole, DonationStatus, Request, Donation
from app.schemas import DeliveryCreate, DeliveryUpdate, DeliveryResponse, DeliveryEventResponse, DeliveryDetailsResponse
from app.utils.security import get_current_user, require_role
from app.services.maps import get_route
from app.services.notifier import create_notification, notify_pickup_scheduled_sync, notify_in_transit_sync, notify_delivered_sync, notify_confirmed_sync

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


def _detail(delivery: Delivery) -> dict:
    match = delivery.match
    return {
        "id": delivery.id,
        "match_id": delivery.match_id,
        "mode": delivery.mode,
        "volunteer_id": delivery.volunteer_id,
        "scheduled_at": delivery.scheduled_at,
        "delivered_at": delivery.delivered_at,
        "status": delivery.status,
        "donation_item": match.donation.item_type,
        "donation_quantity": match.donation.quantity,
        "donation_id": match.donation_id,
        "request_id": match.request_id,
        "donor_name": match.donation.donor.name if match.donation.donor else None,
        "donor_lat": match.donation.lat,
        "donor_lng": match.donation.lng,
        "ngo_name": match.request.ngo.name if match.request.ngo else None,
        "ngo_lat": match.request.ngo.lat,
        "ngo_lng": match.request.ngo.lng,
        "match_status": match.status.value if match.status else None,
    }


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
    try:
        notify_pickup_scheduled_sync(db, delivery)
    except Exception:
        pass
    return delivery


@router.get("", response_model=List[DeliveryDetailsResponse])
def list_deliveries(
    status_filter: Optional[DeliveryStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Delivery).join(Match, Delivery.match_id == Match.id)
    if current_user.role == UserRole.VOLUNTEER:
        query = query.filter(Delivery.volunteer_id == current_user.id)
    elif current_user.role == UserRole.NGO:
        query = query.filter(Match.request_id.in_(
            db.query(Request.id).filter(Request.ngo_id == current_user.id)
        ))
    elif current_user.role == UserRole.DONOR:
        query = query.filter(Match.donation_id.in_(
            db.query(Donation.id).filter(Donation.donor_id == current_user.id)
        ))
    if status_filter:
        query = query.filter(Delivery.status == status_filter)
    deliveries = query.order_by(Delivery.scheduled_at.desc().nullslast()).all()
    return [_detail(d) for d in deliveries]


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


@router.patch("/{delivery_id}/assign", response_model=DeliveryResponse)
def assign_volunteer(
    delivery_id: int,
    assignment: DeliveryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    if not assignment.volunteer_id:
        raise HTTPException(status_code=400, detail="volunteer_id is required")

    volunteer = db.query(User).filter(
        User.id == assignment.volunteer_id,
        User.role == UserRole.VOLUNTEER,
        User.verified == True
    ).first()
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found or not verified")

    match = delivery.match
    is_owner = (match.donation.donor_id == current_user.id
                or match.request.ngo_id == current_user.id)
    if not is_owner and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    delivery.volunteer_id = volunteer.id
    if not delivery.scheduled_at:
        delivery.scheduled_at = datetime.utcnow()
    db.add(DeliveryEvent(delivery_id=delivery.id, status=DeliveryStatus.SCHEDULED))
    db.commit()
    db.refresh(delivery)

    create_notification(
        db, volunteer.id,
        f"You are assigned to deliver '{delivery.match.donation.item_type}' "
        f"for {delivery.match.request.ngo.name}."
    )
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
            try:
                notify_in_transit_sync(db, delivery)
            except Exception:
                pass
        elif new_status == DeliveryStatus.DELIVERED:
            match.donation.status = DonationStatus.DELIVERED
            delivery.delivered_at = datetime.utcnow()
            try:
                notify_delivered_sync(db, delivery)
            except Exception:
                pass
        elif new_status == DeliveryStatus.CONFIRMED:
            match.donation.status = DonationStatus.CONFIRMED
            try:
                notify_confirmed_sync(db, delivery)
            except Exception:
                pass
    
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