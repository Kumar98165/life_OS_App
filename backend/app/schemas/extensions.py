"""LifeOS - Productivity Extensions Validation Schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, constr


# 12. Notes & Folders
class NoteFolderCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color_hex: Optional[str] = Field("#6C63FF", max_length=10)
    icon: Optional[str] = Field("folder-outline", max_length=50)


class NoteCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = Field("", max_length=50000)
    is_pinned: Optional[bool] = False
    is_archived: Optional[bool] = False
    folder_id: Optional[str] = None
    tag_names: Optional[List[str]] = []


class NoteUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None
    folder_id: Optional[str] = None
    tag_names: Optional[List[str]] = None


class NoteAttachmentCreateSchema(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., min_length=1, max_length=50)
    file_size_bytes: int = Field(0, ge=0)
    file_url: str = Field(..., min_length=1, max_length=1000)


# 13. Contacts
class ContactCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    relationship_type: Optional[str] = Field("friend", max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    company: Optional[str] = Field(None, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)
    birthday: Optional[date] = None
    anniversary: Optional[date] = None
    notes: Optional[str] = None
    is_favorite: Optional[bool] = False


class ContactUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    relationship_type: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    birthday: Optional[date] = None
    anniversary: Optional[date] = None
    notes: Optional[str] = None
    is_favorite: Optional[bool] = None


class ContactInteractionCreateSchema(BaseModel):
    interaction_type: Optional[str] = Field("call", max_length=50)
    summary: str = Field(..., min_length=1, max_length=255)
    details: Optional[str] = None
    interaction_date: Optional[datetime] = None
    follow_up_date: Optional[date] = None


# 14. Subscriptions
class SubscriptionCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    category: Optional[str] = Field("entertainment", max_length=50)
    amount: Decimal = Field(..., gt=0)
    currency: Optional[str] = Field("USD", max_length=10)
    billing_cycle: Optional[str] = Field("monthly", max_length=20)
    status: Optional[str] = Field("active", max_length=20)
    renewal_date: date
    payment_method: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    auto_renew: Optional[bool] = True


class SubscriptionUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    category: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = None
    billing_cycle: Optional[str] = None
    status: Optional[str] = None
    renewal_date: Optional[date] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    auto_renew: Optional[bool] = None


# 15. Learning Goals
class LearningGoalCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    category: Optional[str] = Field("technology", max_length=50)
    description: Optional[str] = None
    target_hours: Optional[int] = Field(50, gt=0)
    start_date: Optional[date] = None
    target_completion_date: Optional[date] = None


class LearningGoalUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    category: Optional[str] = None
    description: Optional[str] = None
    target_hours: Optional[int] = Field(None, gt=0)
    status: Optional[str] = None
    start_date: Optional[date] = None
    target_completion_date: Optional[date] = None


class StudySessionCreateSchema(BaseModel):
    duration_minutes: int = Field(..., gt=0, le=1440)
    topics_covered: str = Field(..., min_length=1, max_length=255)
    notes: Optional[str] = None
    session_date: Optional[date] = None


# 16. Travel Planner
class TripCreateSchema(BaseModel):
    destination: str = Field(..., min_length=1, max_length=150)
    title: str = Field(..., min_length=1, max_length=150)
    start_date: date
    end_date: date
    budget: Optional[Decimal] = Field(Decimal("0.0"), ge=0)
    currency: Optional[str] = Field("USD", max_length=10)
    status: Optional[str] = Field("planned", max_length=20)
    notes: Optional[str] = None


class TripUpdateSchema(BaseModel):
    destination: Optional[str] = Field(None, min_length=1, max_length=150)
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class TripItineraryItemCreateSchema(BaseModel):
    activity_date: date
    activity_time: Optional[str] = Field(None, max_length=10)
    title: str = Field(..., min_length=1, max_length=150)
    location: Optional[str] = Field(None, max_length=200)
    booking_reference: Optional[str] = Field(None, max_length=100)
    estimated_cost: Optional[Decimal] = Field(Decimal("0.0"), ge=0)


class TripPackingItemCreateSchema(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field("essentials", max_length=50)
    quantity: Optional[int] = Field(1, ge=1)
    is_packed: Optional[bool] = False


# 17. Fitness
class WorkoutCreateSchema(BaseModel):
    workout_type: Optional[str] = Field("strength", max_length=50)
    title: str = Field(..., min_length=1, max_length=120)
    duration_minutes: int = Field(..., gt=0, le=1440)
    calories_burned: Optional[int] = Field(None, ge=0)
    distance_km: Optional[Decimal] = Field(None, ge=0)
    intensity: Optional[str] = Field("medium", max_length=20)
    notes: Optional[str] = None
    workout_date: Optional[date] = None


class WorkoutUpdateSchema(BaseModel):
    workout_type: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=120)
    duration_minutes: Optional[int] = Field(None, gt=0, le=1440)
    calories_burned: Optional[int] = Field(None, ge=0)
    distance_km: Optional[Decimal] = Field(None, ge=0)
    intensity: Optional[str] = None
    notes: Optional[str] = None
    workout_date: Optional[date] = None


# 18. Assets
class PersonalAssetCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    category: Optional[str] = Field("electronics", max_length=50)
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field("USD", max_length=10)
    serial_number: Optional[str] = Field(None, max_length=100)
    warranty_expiry: Optional[date] = None
    location: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field("active", max_length=20)
    notes: Optional[str] = None


class PersonalAssetUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    category: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = None
    serial_number: Optional[str] = None
    warranty_expiry: Optional[date] = None
    location: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AssetMaintenanceCreateSchema(BaseModel):
    service_date: date
    description: str = Field(..., min_length=1, max_length=255)
    cost: Optional[Decimal] = Field(Decimal("0.0"), ge=0)
    service_provider: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


# 19. Bills
class BillCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    category: Optional[str] = Field("utility", max_length=50)
    amount: Decimal = Field(..., gt=0)
    currency: Optional[str] = Field("USD", max_length=10)
    due_date: date
    is_recurring: Optional[bool] = True
    frequency: Optional[str] = Field("monthly", max_length=20)
    status: Optional[str] = Field("unpaid", max_length=20)
    auto_pay: Optional[bool] = False
    notes: Optional[str] = None


class BillUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=120)
    category: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = None
    due_date: Optional[date] = None
    is_recurring: Optional[bool] = None
    frequency: Optional[str] = None
    status: Optional[str] = None
    auto_pay: Optional[bool] = None
    notes: Optional[str] = None


class BillPaymentCreateSchema(BaseModel):
    amount_paid: Decimal = Field(..., gt=0)
    payment_date: Optional[date] = None
    payment_method: Optional[str] = Field("bank_transfer", max_length=50)
    reference_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
