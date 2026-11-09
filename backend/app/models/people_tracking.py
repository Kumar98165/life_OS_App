"""LifeOS - People & Personal Tracking Models.

Implements:
- Module 20: Task Assignment & Follow-Up Manager (AssignedTask, TaskFollowUp)
- Module 21: Personal Lending & Borrowing Manager (MoneyTransaction, MoneyRepayment)
- Module 22: Personal Item Lending Manager (PersonalItem, ItemLendingRecord)
- Module 23: People Ledger & Unified Person Activity (PersonActivity)
"""
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, Text, Boolean, Integer, Numeric, Date, DateTime,
    ForeignKey, Index, Table, Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


# ============================================================================
# MODULE 20: TASK ASSIGNMENT & FOLLOW-UP MANAGER
# ============================================================================

class AssignedTask(BaseModel):
    """Task assigned to another person."""
    __tablename__ = "assigned_tasks"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)
    person_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    person_contact: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Phone / Email
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assignment_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False)
    expected_completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    actual_completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # low, medium, high, urgent
    status: Mapped[str] = mapped_column(String(20), default="assigned", nullable=False, index=True)  # assigned, accepted, in_progress, on_hold, completed, cancelled
    attachment_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    user: Mapped["User"] = relationship("User")
    contact: Mapped[Optional["Contact"]] = relationship("Contact")
    follow_ups: Mapped[List["TaskFollowUp"]] = relationship("TaskFollowUp", back_populates="task", cascade="all, delete-orphan", order_by="desc(TaskFollowUp.follow_up_date)")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "contact_id": self.contact_id,
            "person_name": self.person_name,
            "person_contact": self.person_contact,
            "title": self.title,
            "description": self.description,
            "assignment_date": self.assignment_date.isoformat() if self.assignment_date else None,
            "expected_completion_date": self.expected_completion_date.isoformat() if self.expected_completion_date else None,
            "actual_completion_date": self.actual_completion_date.isoformat() if self.actual_completion_date else None,
            "priority": self.priority,
            "status": self.status,
            "attachment_url": self.attachment_url,
            "follow_ups": [f.to_dict() for f in self.follow_ups] if self.follow_ups else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TaskFollowUp(BaseModel):
    """Follow-up notes and reminders for an assigned task."""
    __tablename__ = "task_follow_ups"

    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("assigned_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    follow_up_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False)
    reminder_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    task: Mapped["AssignedTask"] = relationship("AssignedTask", back_populates="follow_ups")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "note": self.note,
            "follow_up_date": self.follow_up_date.isoformat() if self.follow_up_date else None,
            "reminder_date": self.reminder_date.isoformat() if self.reminder_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# MODULE 21: PERSONAL LENDING & BORROWING MANAGER
# ============================================================================

class MoneyTransaction(BaseModel):
    """Money lent to or borrowed from another person."""
    __tablename__ = "money_transactions"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)
    person_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    person_contact: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # "lent" (I gave) or "borrowed" (I received)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    amount_repaid: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.0"), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False)
    expected_return_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    payment_method: Mapped[str] = mapped_column(String(50), default="UPI", nullable=False)  # Cash, UPI, Bank Transfer, Other
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    proof_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)  # pending, partially_paid, fully_paid, overdue

    user: Mapped["User"] = relationship("User")
    contact: Mapped[Optional["Contact"]] = relationship("Contact")
    repayments: Mapped[List["MoneyRepayment"]] = relationship("MoneyRepayment", back_populates="transaction", cascade="all, delete-orphan", order_by="desc(MoneyRepayment.payment_date)")

    @property
    def remaining_amount(self) -> Decimal:
        return max(Decimal("0.0"), self.amount - self.amount_repaid)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "contact_id": self.contact_id,
            "person_name": self.person_name,
            "person_contact": self.person_contact,
            "transaction_type": self.transaction_type,
            "amount": float(self.amount),
            "amount_repaid": float(self.amount_repaid),
            "remaining_amount": float(self.remaining_amount),
            "currency": self.currency,
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
            "expected_return_date": self.expected_return_date.isoformat() if self.expected_return_date else None,
            "payment_method": self.payment_method,
            "description": self.description,
            "proof_url": self.proof_url,
            "status": self.status,
            "repayments": [r.to_dict() for r in self.repayments] if self.repayments else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class MoneyRepayment(BaseModel):
    """Repayment installment record for money lent or borrowed."""
    __tablename__ = "money_repayments"

    transaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("money_transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), default="UPI", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    proof_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    transaction: Mapped["MoneyTransaction"] = relationship("MoneyTransaction", back_populates="repayments")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "amount": float(self.amount),
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "payment_method": self.payment_method,
            "notes": self.notes,
            "proof_url": self.proof_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# MODULE 22: PERSONAL ITEM LENDING MANAGER
# ============================================================================

class PersonalItem(BaseModel):
    """Personal belonging or gadget that can be lent out."""
    __tablename__ = "personal_items"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), default="other", nullable=False)  # electronics, books, accessories, tools, other
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    initial_condition: Mapped[str] = mapped_column(String(50), default="good", nullable=False)  # new, excellent, good, fair, worn
    photo_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="available", nullable=False, index=True)  # available, lent, overdue, lost

    user: Mapped["User"] = relationship("User")
    lending_records: Mapped[List["ItemLendingRecord"]] = relationship("ItemLendingRecord", back_populates="item", cascade="all, delete-orphan", order_by="desc(ItemLendingRecord.given_date)")

    def to_dict(self) -> Dict[str, Any]:
        active_record = next((r for r in self.lending_records if r.actual_return_date is None), None)
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "initial_condition": self.initial_condition,
            "photo_url": self.photo_url,
            "status": self.status,
            "currently_with": active_record.person_name if active_record else None,
            "expected_return_date": active_record.expected_return_date.isoformat() if active_record and active_record.expected_return_date else None,
            "active_lending_record": active_record.to_dict() if active_record else None,
            "lending_records": [r.to_dict() for r in self.lending_records] if self.lending_records else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ItemLendingRecord(BaseModel):
    """Historical lending log of an item to a specific person."""
    __tablename__ = "item_lending_records"

    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("personal_items.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)
    person_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    person_contact: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    given_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False)
    expected_return_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    actual_return_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    condition_on_return: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    item: Mapped["PersonalItem"] = relationship("PersonalItem", back_populates="lending_records")
    contact: Mapped[Optional["Contact"]] = relationship("Contact")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "item_id": self.item_id,
            "contact_id": self.contact_id,
            "person_name": self.person_name,
            "person_contact": self.person_contact,
            "given_date": self.given_date.isoformat() if self.given_date else None,
            "expected_return_date": self.expected_return_date.isoformat() if self.expected_return_date else None,
            "actual_return_date": self.actual_return_date.isoformat() if self.actual_return_date else None,
            "condition_on_return": self.condition_on_return,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# MODULE 23: PEOPLE LEDGER — UNIFIED PERSON ACTIVITY
# ============================================================================

class PersonActivity(BaseModel):
    """Unified chronological ledger activity across tasks, money, items, and follow-ups."""
    __tablename__ = "person_activities"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=True, index=True)
    person_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: task_assigned, task_completed, money_lent, money_borrowed, repayment_made, repayment_received, item_lent, item_returned, follow_up_added
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    reference_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    activity_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    user: Mapped["User"] = relationship("User")
    contact: Mapped[Optional["Contact"]] = relationship("Contact")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "contact_id": self.contact_id,
            "person_name": self.person_name,
            "activity_type": self.activity_type,
            "summary": self.summary,
            "details": self.details,
            "amount": float(self.amount) if self.amount is not None else None,
            "reference_id": self.reference_id,
            "activity_date": self.activity_date.isoformat() if self.activity_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
