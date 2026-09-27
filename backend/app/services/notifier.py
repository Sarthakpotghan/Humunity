from typing import Optional
from sqlalchemy.orm import Session
from app.models import Notification, User
from app.config import get_settings
import aiosmtplib
from email.message import EmailMessage
import asyncio

settings = get_settings()


def _run_async(coro):
    """Run an async coroutine in sync context, handling both with and without running event loop."""
    try:
        loop = asyncio.get_running_loop()
        # If there's a running loop, schedule as task (fire-and-forget)
        loop.create_task(coro)
    except RuntimeError:
        # No running loop, run in new loop
        asyncio.run(coro)


async def send_email(to_email: str, subject: str, body: str) -> bool:
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return False
    
    message = EmailMessage()
    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)
    
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            start_tls=True,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
        )
        return True
    except Exception:
        return False


def create_notification(db: Session, user_id: int, message: str) -> Notification:
    notification = Notification(user_id=user_id, message=message)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


async def notify_match_created(db: Session, match):
    donation = match.donation
    request = match.request
    
    create_notification(
        db, donation.donor_id,
        f"Your donation '{donation.item_type}' has been matched with {request.ngo.name}'s request."
    )
    
    create_notification(
        db, request.ngo_id,
        f"New match for your request '{request.item_type}': {donation.quantity} items from {donation.donor.name}."
    )
    
    await send_email(
        donation.donor.email,
        "New Match Found",
        f"Your donation has been matched with {request.ngo.name}."
    )
    
    await send_email(
        request.ngo.email,
        "New Match for Your Request",
        f"A donor has matched your request for {request.item_type}."
    )


async def notify_match_accepted(db: Session, match):
    donation = match.donation
    request = match.request
    
    create_notification(
        db, donation.donor_id,
        f"{request.ngo.name} accepted your donation match for {donation.item_type}."
    )
    
    await send_email(
        donation.donor.email,
        "Donation Accepted",
        f"{request.ngo.name} accepted your donation. Please schedule pickup/drop-off."
    )


async def notify_match_rejected(db: Session, match):
    donation = match.donation
    request = match.request
    
    create_notification(
        db, donation.donor_id,
        f"{request.ngo.name} declined the match for {donation.item_type}."
    )


async def notify_pickup_scheduled(db: Session, delivery):
    match = delivery.match
    donation = match.donation
    request = match.request
    
    for user_id in [donation.donor_id, request.ngo_id]:
        create_notification(
            db, user_id,
            f"Pickup scheduled for {delivery.scheduled_at.strftime('%Y-%m-%d %H:%M')} for {donation.item_type}."
        )


async def notify_in_transit(db: Session, delivery):
    match = delivery.match
    donation = match.donation
    request = match.request
    
    for user_id in [donation.donor_id, request.ngo_id]:
        create_notification(
            db, user_id,
            f"Delivery in transit for {donation.item_type}. ETA: {delivery.scheduled_at}."
        )


async def notify_delivered(db: Session, delivery):
    match = delivery.match
    donation = match.donation
    request = match.request
    
    for user_id in [donation.donor_id, request.ngo_id]:
        create_notification(
            db, user_id,
            f"Delivery completed for {donation.item_type}. Please confirm receipt."
        )


async def notify_confirmed(db: Session, delivery):
    match = delivery.match
    donation = match.donation
    request = match.request
    
    create_notification(
        db, donation.donor_id,
        f"{request.ngo.name} confirmed receipt of {donation.item_type}. Thank you for donating!"
    )
    
    create_notification(
        db, request.ngo_id,
        f"You confirmed receipt of {donation.item_type} from {donation.donor.name}."
    )


# Sync-compatible wrappers for use in synchronous routers
def notify_match_created_sync(db: Session, match):
    _run_async(notify_match_created(db, match))


def notify_match_accepted_sync(db: Session, match):
    _run_async(notify_match_accepted(db, match))


def notify_match_rejected_sync(db: Session, match):
    _run_async(notify_match_rejected(db, match))


def notify_pickup_scheduled_sync(db: Session, delivery):
    _run_async(notify_pickup_scheduled(db, delivery))


def notify_in_transit_sync(db: Session, delivery):
    _run_async(notify_in_transit(db, delivery))


def notify_delivered_sync(db: Session, delivery):
    _run_async(notify_delivered(db, delivery))


def notify_confirmed_sync(db: Session, delivery):
    _run_async(notify_confirmed(db, delivery))