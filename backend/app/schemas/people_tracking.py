"""LifeOS - People & Personal Tracking Validation Schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# MODULE 20: ASSIGNED TASKS
# ============================================================================

class AssignedTaskCreateSchema(BaseModel):
    person_name: str = Field(..., min_length=1, max_length=120)
    person_contact: Optional[str] = Field(None, max_length=100)
    contact_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assignment_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    priority: Optional[str] = Field("medium", max_length=20)  # low, medium, high, urgent
    status: Optional[str] = Field("assigned", max_length=20)
    attachment_url: Optional[str] = Field(None, max_length=1000)


class AssignedTaskUpdateSchema(BaseModel):
    person_name: Optional[str] = Field(None, min_length=1, max_length=120)
    person_contact: Optional[str] = None
    contact_id: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    assignment_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    attachment_url: Optional[str] = None


class TaskFollowUpCreateSchema(BaseModel):
    note: str = Field(..., min_length=1)
    follow_up_date: Optional[date] = None
    reminder_date: Optional[date] = None


# ============================================================================
# MODULE 21: MONEY TRANSACTIONS
# ============================================================================

class MoneyTransactionCreateSchema(BaseModel):
    person_name: str = Field(..., min_length=1, max_length=120)
    person_contact: Optional[str] = Field(None, max_length=100)
    contact_id: Optional[str] = None
    transaction_type: str = Field(..., pattern="^(lent|borrowed)$")
    amount: Decimal = Field(..., gt=0)
    currency: Optional[str] = Field("INR", max_length=10)
    transaction_date: Optional[date] = None
    expected_return_date: Optional[date] = None
    payment_method: Optional[str] = Field("UPI", max_length=50)
    description: Optional[str] = None
    proof_url: Optional[str] = Field(None, max_length=1000)


class MoneyRepaymentCreateSchema(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_date: Optional[date] = None
    payment_method: Optional[str] = Field("UPI", max_length=50)
    notes: Optional[str] = None
    proof_url: Optional[str] = Field(None, max_length=1000)


# ============================================================================
# MODULE 22: PERSONAL ITEM LENDING
# ============================================================================

class PersonalItemCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    category: Optional[str] = Field("other", max_length=50)
    description: Optional[str] = None
    initial_condition: Optional[str] = Field("good", max_length=50)
    photo_url: Optional[str] = Field(None, max_length=1000)


class ItemLendActionSchema(BaseModel):
    person_name: str = Field(..., min_length=1, max_length=120)
    person_contact: Optional[str] = Field(None, max_length=100)
    contact_id: Optional[str] = None
    given_date: Optional[date] = None
    expected_return_date: Optional[date] = None
    notes: Optional[str] = None


class ItemReturnActionSchema(BaseModel):
    actual_return_date: Optional[date] = None
    condition_on_return: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
