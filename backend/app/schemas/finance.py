"""LifeOS - Personal Finance Validation Schemas.

Pydantic v2 schemas for accounts, transactions, categories, budgets,
savings goals, and financial ledger contributions.
"""
from typing import Optional, Literal
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class CreateAccountRequest(BaseModel):
    """Payload for creating a financial account."""
    name: str = Field(..., min_length=1, max_length=100)
    account_type: Literal["checking", "savings", "credit", "cash", "wallet", "other"] = "checking"
    balance: Decimal = Field(default=Decimal("0.00"), description="Opening balance")
    currency: str = Field(default="USD", min_length=3, max_length=10)
    color_hex: Optional[str] = Field("#6C63FF", max_length=10)
    icon: Optional[str] = Field("wallet", max_length=50)
    is_default: Optional[bool] = False

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Account name cannot be blank")
        return trimmed

    @field_validator("currency")
    @classmethod
    def sanitize_currency(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("balance")
    @classmethod
    def validate_balance_precision(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.01"))

    model_config = {"extra": "forbid"}


class UpdateAccountRequest(BaseModel):
    """Payload for editing a financial account."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    account_type: Optional[Literal["checking", "savings", "credit", "cash", "wallet", "other"]] = None
    color_hex: Optional[str] = Field(None, max_length=10)
    icon: Optional[str] = Field(None, max_length=50)
    is_default: Optional[bool] = None
    is_archived: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Account name cannot be blank")
        return trimmed

    model_config = {"extra": "forbid"}


class CreateCategoryRequest(BaseModel):
    """Payload for creating a financial category."""
    name: str = Field(..., min_length=1, max_length=100)
    category_type: Literal["income", "expense"] = "expense"
    icon: Optional[str] = Field("pricetag", max_length=50)
    color_hex: Optional[str] = Field("#6C63FF", max_length=10)
    monthly_budget: Optional[Decimal] = None

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Category name cannot be blank")
        return trimmed

    @field_validator("monthly_budget")
    @classmethod
    def validate_budget_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None:
            if v < 0:
                raise ValueError("Monthly budget cannot be negative")
            return v.quantize(Decimal("0.01"))
        return None

    model_config = {"extra": "forbid"}


class UpdateCategoryRequest(BaseModel):
    """Payload for editing a financial category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    color_hex: Optional[str] = Field(None, max_length=10)
    monthly_budget: Optional[Decimal] = None

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Category name cannot be blank")
        return trimmed

    @field_validator("monthly_budget")
    @classmethod
    def validate_budget_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None:
            if v < 0:
                raise ValueError("Monthly budget cannot be negative")
            return v.quantize(Decimal("0.01"))
        return None

    model_config = {"extra": "forbid"}


class CreateTransactionRequest(BaseModel):
    """Payload for logging an income, expense, or transfer transaction."""
    account_id: str = Field(..., min_length=36, max_length=36)
    category_id: Optional[str] = Field(None, min_length=36, max_length=36)
    amount: Decimal = Field(..., gt=Decimal("0.00"), description="Transaction amount (must be positive)")
    transaction_type: Literal["income", "expense", "transfer"] = "expense"
    description: str = Field(..., min_length=1, max_length=255)
    transaction_date: Optional[datetime] = None
    is_recurring: Optional[bool] = False

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Description cannot be blank")
        return trimmed

    @field_validator("amount")
    @classmethod
    def validate_amount_precision(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Transaction amount must be strictly greater than zero")
        return v.quantize(Decimal("0.01"))

    model_config = {"extra": "forbid"}


class UpdateTransactionRequest(BaseModel):
    """Payload for modifying an existing transaction."""
    account_id: Optional[str] = Field(None, min_length=36, max_length=36)
    category_id: Optional[str] = Field(None, min_length=36, max_length=36)
    amount: Optional[Decimal] = Field(None, gt=Decimal("0.00"))
    transaction_type: Optional[Literal["income", "expense", "transfer"]] = None
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    transaction_date: Optional[datetime] = None
    is_recurring: Optional[bool] = None

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Description cannot be blank")
        return trimmed

    @field_validator("amount")
    @classmethod
    def validate_amount_precision(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None:
            if v <= 0:
                raise ValueError("Transaction amount must be strictly greater than zero")
            return v.quantize(Decimal("0.01"))
        return None

    model_config = {"extra": "forbid"}


class CreateBudgetRequest(BaseModel):
    """Payload for creating a monthly category or overall budget."""
    category_id: Optional[str] = Field(None, min_length=36, max_length=36)
    month: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="Target month YYYY-MM")
    amount: Decimal = Field(..., gt=Decimal("0.00"), description="Budget limit")
    currency: Optional[str] = Field("USD", min_length=3, max_length=10)

    @field_validator("amount")
    @classmethod
    def validate_amount_precision(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Budget amount must be strictly greater than zero")
        return v.quantize(Decimal("0.01"))

    model_config = {"extra": "forbid"}


class UpdateBudgetRequest(BaseModel):
    """Payload for modifying an existing budget."""
    amount: Decimal = Field(..., gt=Decimal("0.00"), description="Updated budget limit")

    @field_validator("amount")
    @classmethod
    def validate_amount_precision(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Budget amount must be strictly greater than zero")
        return v.quantize(Decimal("0.01"))

    model_config = {"extra": "forbid"}


class CreateSavingsGoalRequest(BaseModel):
    """Payload for setting up a savings goal."""
    title: str = Field(..., min_length=1, max_length=150)
    target_amount: Decimal = Field(..., gt=Decimal("0.00"))
    initial_deposit: Optional[Decimal] = Field(Decimal("0.00"), ge=Decimal("0.00"))
    target_date: Optional[datetime] = None
    currency: Optional[str] = Field("USD", min_length=3, max_length=10)
    color_hex: Optional[str] = Field("#6C63FF", max_length=10)
    icon: Optional[str] = Field("flag", max_length=50)
    notes: Optional[str] = None

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Title cannot be blank")
        return trimmed

    @field_validator("target_amount")
    @classmethod
    def validate_target_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Target amount must be strictly greater than zero")
        return v.quantize(Decimal("0.01"))

    @field_validator("initial_deposit")
    @classmethod
    def validate_initial_deposit(cls, v: Optional[Decimal]) -> Decimal:
        if v is None:
            return Decimal("0.00")
        if v < 0:
            raise ValueError("Initial deposit cannot be negative")
        return v.quantize(Decimal("0.01"))

    model_config = {"extra": "forbid"}


class UpdateSavingsGoalRequest(BaseModel):
    """Payload for editing a savings goal."""
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    target_amount: Optional[Decimal] = Field(None, gt=Decimal("0.00"))
    target_date: Optional[datetime] = None
    status: Optional[Literal["in_progress", "completed", "archived"]] = None
    color_hex: Optional[str] = Field(None, max_length=10)
    icon: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Title cannot be blank")
        return trimmed

    @field_validator("target_amount")
    @classmethod
    def validate_target_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None:
            if v <= 0:
                raise ValueError("Target amount must be strictly greater than zero")
            return v.quantize(Decimal("0.01"))
        return None

    model_config = {"extra": "forbid"}


class AddSavingsContributionRequest(BaseModel):
    """Payload for contributing funds toward a savings goal."""
    amount: Decimal = Field(..., gt=Decimal("0.00"))
    account_id: Optional[str] = Field(None, min_length=36, max_length=36)
    note: Optional[str] = Field(None, max_length=255)
    deduct_from_account: Optional[bool] = False

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Contribution amount must be strictly greater than zero")
        return v.quantize(Decimal("0.01"))

    model_config = {"extra": "forbid"}

