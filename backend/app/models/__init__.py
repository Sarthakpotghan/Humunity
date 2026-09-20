import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Enum, 
    Float, Boolean, JSON, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    DONOR = "donor"
    NGO = "ngo"
    VOLUNTEER = "volunteer"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.DONOR)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    donations = relationship("Donation", back_populates="donor", foreign_keys="Donation.donor_id")
    ngo_profile = relationship("NgoProfile", back_populates="user", uselist=False)
    deliveries_as_volunteer = relationship("Delivery", back_populates="volunteer", foreign_keys="Delivery.volunteer_id")
    notifications = relationship("Notification", back_populates="user")
    feedback_given = relationship("Feedback", back_populates="giver", foreign_keys="Feedback.giver_id")

    __table_args__ = (
        Index("ix_users_lat_lng", "lat", "lng"),
    )


class DonationStatus(str, enum.Enum):
    LISTED = "listed"
    MATCHED = "matched"
    ACCEPTED = "accepted"
    PICKUP_SCHEDULED = "pickup_scheduled"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ItemCondition(str, enum.Enum):
    NEW = "new"
    GOOD = "good"
    FAIR = "fair"


class ItemCategory(str, enum.Enum):
    CLOTHES = "clothes"
    STATIONERY = "stationery"


class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(Enum(ItemCategory), nullable=False)
    item_type = Column(String(100), nullable=False)
    size = Column(String(50), nullable=True)
    age_group = Column(String(50), nullable=True)
    gender = Column(String(20), nullable=True)
    season = Column(String(50), nullable=True)
    condition = Column(Enum(ItemCondition), nullable=False)
    quantity = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    available_from = Column(DateTime, nullable=True)
    available_to = Column(DateTime, nullable=True)
    status = Column(Enum(DonationStatus), default=DonationStatus.LISTED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    donor = relationship("User", back_populates="donations", foreign_keys=[donor_id])
    photos = relationship("DonationPhoto", back_populates="donation", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="donation")

    __table_args__ = (
        Index("ix_donations_category_status", "category", "status"),
    )


class DonationPhoto(Base):
    __tablename__ = "donation_photos"

    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("donations.id"), nullable=False)
    url = Column(String(500), nullable=False)

    donation = relationship("Donation", back_populates="photos")


class RequestStatus(str, enum.Enum):
    ACTIVE = "active"
    FULFILLED = "fulfilled"
    CLOSED = "closed"
    EXPIRED = "expired"


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    ngo_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(Enum(ItemCategory), nullable=False)
    item_type = Column(String(100), nullable=False)
    size = Column(String(50), nullable=True)
    age_group = Column(String(50), nullable=True)
    gender = Column(String(20), nullable=True)
    season = Column(String(50), nullable=True)
    quantity_needed = Column(Integer, nullable=False)
    urgency = Column(Integer, nullable=False, default=1)
    beneficiary_group = Column(String(100), nullable=True)
    deadline = Column(DateTime, nullable=True)
    status = Column(Enum(RequestStatus), default=RequestStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    ngo = relationship("User", foreign_keys=[ngo_id])
    matches = relationship("Match", back_populates="request")

    __table_args__ = (
        Index("ix_requests_category_status_deadline", "category", "status", "deadline"),
    )


class NgoProfile(Base):
    __tablename__ = "ngo_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    reg_number = Column(String(100), nullable=False)
    reg_doc_url = Column(String(500), nullable=True)
    focus_areas = Column(JSON, nullable=True)
    reliability_score = Column(Float, default=1.0)

    user = relationship("User", back_populates="ngo_profile")


class MatchStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("donations.id"), nullable=False)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    score = Column(Float, nullable=False)
    score_breakdown = Column(JSON, nullable=True)
    status = Column(Enum(MatchStatus), default=MatchStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    donation = relationship("Donation", back_populates="matches")
    request = relationship("Request", back_populates="matches")
    delivery = relationship("Delivery", back_populates="match", uselist=False)
    feedback = relationship("Feedback", back_populates="match", uselist=False)


class DeliveryStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class DeliveryMode(str, enum.Enum):
    DROPOFF = "dropoff"
    PICKUP = "pickup"


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), unique=True, nullable=False)
    mode = Column(Enum(DeliveryMode), nullable=False)
    volunteer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.SCHEDULED, nullable=False)

    match = relationship("Match", back_populates="delivery")
    volunteer = relationship("User", back_populates="deliveries_as_volunteer", foreign_keys=[volunteer_id])
    events = relationship("DeliveryEvent", back_populates="delivery", cascade="all, delete-orphan")


class DeliveryEvent(Base):
    __tablename__ = "delivery_events"

    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id"), nullable=False)
    status = Column(Enum(DeliveryStatus), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    delivery = relationship("Delivery", back_populates="events")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), unique=True, nullable=False)
    giver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="feedback")
    giver = relationship("User", back_populates="feedback_given", foreign_keys=[giver_id])