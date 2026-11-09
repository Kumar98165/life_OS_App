"""LifeOS - Productivity Extensions Data Models.

Implements data models for:
- Notes & Documents (folders, attachments, tags)
- Contacts & Relationships (interactions, important dates)
- Subscriptions (recurring charges, renewals)
- Learning & Skills (courses, study sessions)
- Travel Planner (trips, itineraries, packing items, bookings)
- Fitness & Workouts (exercises, logs)
- Personal Assets (gadgets, warranties, maintenance)
- Bills & Recurring Payments (utilities, due dates, payments)
"""
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, Text, Boolean, Integer, Numeric, Date, DateTime,
    ForeignKey, Index, UniqueConstraint, Table, Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel
from app.extensions import db


# ============================================================================
# 12. NOTES & DOCUMENTS EXTENSIONS
# ============================================================================

class NoteFolder(BaseModel):
    """Hierarchical organization folder for notes."""
    __tablename__ = "note_folders"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color_hex: Mapped[str] = mapped_column(String(10), default="#6C63FF", nullable=False)
    icon: Mapped[str] = mapped_column(String(50), default="folder-outline", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="note_folders")
    notes: Mapped[List["Note"]] = relationship("Note", back_populates="folder")

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_note_folder_user_name"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "color_hex": self.color_hex,
            "icon": self.icon,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class NoteAttachment(BaseModel):
    """File or document metadata attached to a note."""
    __tablename__ = "note_attachments"

    note_id: Mapped[str] = mapped_column(String(36), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)

    note: Mapped["Note"] = relationship("Note", back_populates="attachments")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "note_id": self.note_id,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size_bytes": self.file_size_bytes,
            "file_url": self.file_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# 13. CONTACTS & RELATIONSHIP MANAGER
# ============================================================================

class Contact(BaseModel):
    """Personal or professional contact."""
    __tablename__ = "contacts"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(50), default="friend", nullable=False)  # family, friend, colleague, mentor, other
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    birthday: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    anniversary: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="contacts")
    interactions: Mapped[List["ContactInteraction"]] = relationship("ContactInteraction", back_populates="contact", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "relationship_type": self.relationship_type,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "company": self.company,
            "job_title": self.job_title,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "anniversary": self.anniversary.isoformat() if self.anniversary else None,
            "notes": self.notes,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ContactInteraction(BaseModel):
    """Interaction log / follow-up record with a contact."""
    __tablename__ = "contact_interactions"

    contact_id: Mapped[str] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type: Mapped[str] = mapped_column(String(50), default="call", nullable=False)  # call, meeting, message, email, social
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    follow_up_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    contact: Mapped["Contact"] = relationship("Contact", back_populates="interactions")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "contact_id": self.contact_id,
            "interaction_type": self.interaction_type,
            "summary": self.summary,
            "details": self.details,
            "interaction_date": self.interaction_date.isoformat() if self.interaction_date else None,
            "follow_up_date": self.follow_up_date.isoformat() if self.follow_up_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# 14. SUBSCRIPTION MANAGER
# ============================================================================

class Subscription(BaseModel):
    """Recurring service or software subscription."""
    __tablename__ = "subscriptions"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="entertainment", nullable=False)  # entertainment, productivity, utility, education, other
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    billing_cycle: Mapped[str] = mapped_column(String(20), default="monthly", nullable=False)  # monthly, yearly, quarterly, weekly
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, cancelled, paused, expired
    renewal_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="subscriptions")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "category": self.category,
            "amount": float(self.amount),
            "currency": self.currency,
            "billing_cycle": self.billing_cycle,
            "status": self.status,
            "renewal_date": self.renewal_date.isoformat() if self.renewal_date else None,
            "payment_method": self.payment_method,
            "notes": self.notes,
            "auto_renew": self.auto_renew,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# ============================================================================
# 15. LEARNING & SKILL TRACKER
# ============================================================================

class LearningGoal(BaseModel):
    """Skill or subject learning curriculum/goal."""
    __tablename__ = "learning_goals"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="technology", nullable=False)  # technology, language, music, business, other
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_hours: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    current_hours: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="in_progress", nullable=False)  # in_progress, completed, paused
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    target_completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="learning_goals")
    sessions: Mapped[List["StudySession"]] = relationship("StudySession", back_populates="goal", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "target_hours": self.target_hours,
            "current_hours": float(self.current_hours),
            "status": self.status,
            "progress_percent": round(min(100.0, (float(self.current_hours) / self.target_hours * 100)) if self.target_hours > 0 else 0.0, 1),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "target_completion_date": self.target_completion_date.isoformat() if self.target_completion_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class StudySession(BaseModel):
    """Individual study session log for a learning goal."""
    __tablename__ = "study_sessions"

    goal_id: Mapped[str] = mapped_column(String(36), ForeignKey("learning_goals.id", ondelete="CASCADE"), nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    topics_covered: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False)

    goal: Mapped["LearningGoal"] = relationship("LearningGoal", back_populates="sessions")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal_id": self.goal_id,
            "duration_minutes": self.duration_minutes,
            "topics_covered": self.topics_covered,
            "notes": self.notes,
            "session_date": self.session_date.isoformat() if self.session_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# 16. TRAVEL PLANNER
# ============================================================================

class Trip(BaseModel):
    """Travel itinerary and trip organizer."""
    __tablename__ = "trips"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    destination: Mapped[str] = mapped_column(String(150), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="planned", nullable=False)  # planned, ongoing, completed, cancelled
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="trips")
    itinerary_items: Mapped[List["TripItineraryItem"]] = relationship("TripItineraryItem", back_populates="trip", cascade="all, delete-orphan")
    packing_items: Mapped[List["TripPackingItem"]] = relationship("TripPackingItem", back_populates="trip", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "destination": self.destination,
            "title": self.title,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "budget": float(self.budget),
            "currency": self.currency,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TripItineraryItem(BaseModel):
    """Single itinerary activity or scheduled event within a trip."""
    __tablename__ = "trip_itinerary_items"

    trip_id: Mapped[str] = mapped_column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_date: Mapped[date] = mapped_column(Date, nullable=False)
    activity_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # HH:MM
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    booking_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    estimated_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    trip: Mapped["Trip"] = relationship("Trip", back_populates="itinerary_items")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "trip_id": self.trip_id,
            "activity_date": self.activity_date.isoformat() if self.activity_date else None,
            "activity_time": self.activity_time,
            "title": self.title,
            "location": self.location,
            "booking_reference": self.booking_reference,
            "estimated_cost": float(self.estimated_cost),
            "is_completed": self.is_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TripPackingItem(BaseModel):
    """Packing checklist item for a trip."""
    __tablename__ = "trip_packing_items"

    trip_id: Mapped[str] = mapped_column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="essentials", nullable=False)  # clothing, electronics, documents, toiletries, essentials
    is_packed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    trip: Mapped["Trip"] = relationship("Trip", back_populates="packing_items")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "trip_id": self.trip_id,
            "item_name": self.item_name,
            "category": self.category,
            "is_packed": self.is_packed,
            "quantity": self.quantity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# 17. FITNESS & ACTIVITY TRACKER
# ============================================================================

class Workout(BaseModel):
    """Workout or physical exercise session."""
    __tablename__ = "workouts"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workout_type: Mapped[str] = mapped_column(String(50), default="strength", nullable=False)  # running, cycling, strength, hiit, swimming, yoga, walking
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    calories_burned: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distance_km: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    intensity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # low, medium, high
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    workout_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False, index=True)

    user: Mapped["User"] = relationship("User", back_populates="workouts")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "workout_type": self.workout_type,
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "calories_burned": self.calories_burned,
            "distance_km": float(self.distance_km) if self.distance_km is not None else None,
            "intensity": self.intensity,
            "notes": self.notes,
            "workout_date": self.workout_date.isoformat() if self.workout_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# 18. PERSONAL ASSET MANAGER
# ============================================================================

class PersonalAsset(BaseModel):
    """Personal property, electronics, or equipment with warranty and maintenance tracking."""
    __tablename__ = "personal_assets"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="electronics", nullable=False)  # electronics, vehicle, appliance, furniture, gadget, other
    purchase_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    purchase_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    warranty_expiry: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, sold, disposed, in_repair
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="personal_assets")
    maintenance_records: Mapped[List["AssetMaintenanceRecord"]] = relationship("AssetMaintenanceRecord", back_populates="asset", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "category": self.category,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "purchase_price": float(self.purchase_price) if self.purchase_price is not None else None,
            "currency": self.currency,
            "serial_number": self.serial_number,
            "warranty_expiry": self.warranty_expiry.isoformat() if self.warranty_expiry else None,
            "location": self.location,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AssetMaintenanceRecord(BaseModel):
    """Service or maintenance log for an asset."""
    __tablename__ = "asset_maintenance_records"

    asset_id: Mapped[str] = mapped_column(String(36), ForeignKey("personal_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    service_provider: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    asset: Mapped["PersonalAsset"] = relationship("PersonalAsset", back_populates="maintenance_records")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "service_date": self.service_date.isoformat() if self.service_date else None,
            "description": self.description,
            "cost": float(self.cost),
            "service_provider": self.service_provider,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# 19. BILLS & PAYMENTS MANAGER
# ============================================================================

class Bill(BaseModel):
    """Recurring or one-off utility/service bill."""
    __tablename__ = "bills"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="utility", nullable=False)  # electricity, water, internet, rent, insurance, phone, other
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    frequency: Mapped[str] = mapped_column(String(20), default="monthly", nullable=False)  # monthly, quarterly, yearly, once
    status: Mapped[str] = mapped_column(String(20), default="unpaid", nullable=False)  # unpaid, paid, overdue
    auto_pay: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="bills")
    payments: Mapped[List["BillPayment"]] = relationship("BillPayment", back_populates="bill", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "category": self.category,
            "amount": float(self.amount),
            "currency": self.currency,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "is_recurring": self.is_recurring,
            "frequency": self.frequency,
            "status": self.status,
            "auto_pay": self.auto_pay,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class BillPayment(BaseModel):
    """Payment record for a bill."""
    __tablename__ = "bill_payments"

    bill_id: Mapped[str] = mapped_column(String(36), ForeignKey("bills.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), default="bank_transfer", nullable=False)
    reference_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    bill: Mapped["Bill"] = relationship("Bill", back_populates="payments")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "bill_id": self.bill_id,
            "amount_paid": float(self.amount_paid),
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "payment_method": self.payment_method,
            "reference_number": self.reference_number,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

