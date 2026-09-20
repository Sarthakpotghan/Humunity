from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from app.models import UserRole, DonationStatus, ItemCondition, ItemCategory, RequestStatus, MatchStatus, DeliveryStatus, DeliveryMode


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.DONOR
    phone: Optional[str] = None
    address: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class UserResponse(UserBase):
    id: int
    verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class NgoProfileCreate(BaseModel):
    reg_number: str
    reg_doc_url: Optional[str] = None
    focus_areas: Optional[List[str]] = None


class NgoProfileUpdate(BaseModel):
    reg_doc_url: Optional[str] = None
    focus_areas: Optional[List[str]] = None


class NgoProfileResponse(NgoProfileCreate):
    id: int
    user_id: int
    reliability_score: float

    class Config:
        from_attributes = True


class DonationPhotoBase(BaseModel):
    url: str


class DonationPhotoResponse(DonationPhotoBase):
    id: int

    class Config:
        from_attributes = True


class DonationBase(BaseModel):
    category: ItemCategory
    item_type: str = Field(..., max_length=100)
    size: Optional[str] = None
    age_group: Optional[str] = None
    gender: Optional[str] = None
    season: Optional[str] = None
    condition: ItemCondition
    quantity: int = Field(..., gt=0)
    description: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    available_from: Optional[datetime] = None
    available_to: Optional[datetime] = None


class DonationCreate(DonationBase):
    pass


class DonationUpdate(BaseModel):
    category: Optional[ItemCategory] = None
    item_type: Optional[str] = None
    size: Optional[str] = None
    age_group: Optional[str] = None
    gender: Optional[str] = None
    season: Optional[str] = None
    condition: Optional[ItemCondition] = None
    quantity: Optional[int] = None
    description: Optional[str] = None
    available_from: Optional[datetime] = None
    available_to: Optional[datetime] = None


class DonationResponse(DonationBase):
    id: int
    donor_id: int
    status: DonationStatus
    created_at: datetime
    photos: List[DonationPhotoResponse] = []

    class Config:
        from_attributes = True


class RequestBase(BaseModel):
    category: ItemCategory
    item_type: str = Field(..., max_length=100)
    size: Optional[str] = None
    age_group: Optional[str] = None
    gender: Optional[str] = None
    season: Optional[str] = None
    quantity_needed: int = Field(..., gt=0)
    urgency: int = Field(..., ge=1, le=5)
    beneficiary_group: Optional[str] = None
    deadline: Optional[datetime] = None


class RequestCreate(RequestBase):
    pass


class RequestUpdate(BaseModel):
    category: Optional[ItemCategory] = None
    item_type: Optional[str] = None
    size: Optional[str] = None
    age_group: Optional[str] = None
    gender: Optional[str] = None
    season: Optional[str] = None
    quantity_needed: Optional[int] = None
    urgency: Optional[int] = None
    beneficiary_group: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[RequestStatus] = None


class RequestResponse(RequestBase):
    id: int
    ngo_id: int
    status: RequestStatus
    created_at: datetime

    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    id: int
    donation_id: int
    request_id: int
    score: float
    score_breakdown: Optional[dict] = None
    status: MatchStatus
    created_at: datetime

    class Config:
        from_attributes = True


class MatchAction(BaseModel):
    action: str


class DeliveryCreate(BaseModel):
    match_id: int
    mode: DeliveryMode
    volunteer_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None


class DeliveryUpdate(BaseModel):
    status: Optional[DeliveryStatus] = None
    volunteer_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class DeliveryResponse(BaseModel):
    id: int
    match_id: int
    mode: DeliveryMode
    volunteer_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    status: DeliveryStatus

    class Config:
        from_attributes = True


class DeliveryEventResponse(BaseModel):
    id: int
    delivery_id: int
    status: DeliveryStatus
    timestamp: datetime

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationRead(BaseModel):
    is_read: bool = True


class FeedbackCreate(BaseModel):
    match_id: int
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    match_id: int
    giver_id: int
    rating: int
    comments: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    total_items_redistributed: int
    by_category: dict
    avg_time_match_to_delivery_hours: Optional[float] = None
    unmet_requests: int
    top_ngos: List[dict]
    monthly_trend: List[dict]


class HeatmapPoint(BaseModel):
    lat: float
    lng: float
    donations: int
    requests: int