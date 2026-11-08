from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Numeric, Boolean, DateTime, ForeignKey, Index, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class FinancialAccount(BaseModel):
    """Bank account, cash wallet, credit card, or savings vault."""
    __tablename__ = "financial_accounts"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    account_type: Mapped[str] = mapped_column(
        String(30),
        default="checking",
        nullable=False
    )  # checking, savings, credit, cash, wallet, other
    balance: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False
    )
    currency: Mapped[str] = mapped_column(
        String(10),
        default="USD",
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    color_hex: Mapped[str] = mapped_column(
        String(10),
        default="#6C63FF",
        nullable=False
    )
    icon: Mapped[str] = mapped_column(
        String(50),
        default="wallet",
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="financial_accounts")
    transactions: Mapped[List["FinancialTransaction"]] = relationship(
        "FinancialTransaction",
        back_populates="account",
        cascade="all, delete-orphan"
    )
    savings_contributions: Mapped[List["SavingsGoalContribution"]] = relationship(
        "SavingsGoalContribution",
        back_populates="account"
    )

    __table_args__ = (
        Index("ix_financial_accounts_user_active", "user_id", "is_active"),
        Index("ix_financial_accounts_user_archived", "user_id", "is_archived"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "account_type": self.account_type,
            "balance": str(self.balance),
            "currency": self.currency,
            "is_active": self.is_active,
            "is_archived": self.is_archived,
            "is_default": self.is_default,
            "color_hex": self.color_hex,
            "icon": self.icon,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FinancialCategory(BaseModel):
    """Income or expense classification with optional monthly budget."""
    __tablename__ = "financial_categories"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    category_type: Mapped[str] = mapped_column(
        String(20),
        default="expense",
        nullable=False
    )  # income, expense
    icon: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    color_hex: Mapped[str] = mapped_column(
        String(10),
        default="#6C63FF",
        nullable=False
    )
    monthly_budget: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="financial_categories")
    transactions: Mapped[List["FinancialTransaction"]] = relationship(
        "FinancialTransaction",
        back_populates="category"
    )
    budgets: Mapped[List["Budget"]] = relationship(
        "Budget",
        back_populates="category",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "name", "category_type", name="uq_finance_category_user_name_type"),
        Index("ix_financial_categories_user_type", "user_id", "category_type"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "category_type": self.category_type,
            "icon": self.icon,
            "color_hex": self.color_hex,
            "monthly_budget": str(self.monthly_budget) if self.monthly_budget is not None else None,
            "is_system": self.is_system,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FinancialTransaction(BaseModel):
    """Monetary transaction record associated with an account and category."""
    __tablename__ = "financial_transactions"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    account_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("financial_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    category_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("financial_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )
    transaction_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # income, expense, transfer
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    is_recurring: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="financial_transactions")
    account: Mapped[FinancialAccount] = relationship("FinancialAccount", back_populates="transactions")
    category: Mapped[FinancialCategory | None] = relationship("FinancialCategory", back_populates="transactions")

    __table_args__ = (
        Index("ix_fin_trans_user_date", "user_id", "transaction_date"),
        Index("ix_fin_trans_account_date", "account_id", "transaction_date"),
        Index("ix_fin_trans_user_type", "user_id", "transaction_type"),
        Index("ix_fin_trans_user_deleted", "user_id", "is_deleted"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "account_id": self.account_id,
            "account_name": self.account.name if self.account else None,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "category_color": self.category.color_hex if self.category else "#6C63FF",
            "category_icon": self.category.icon if self.category else "pricetag",
            "amount": str(self.amount),
            "transaction_type": self.transaction_type,
            "description": self.description,
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
            "is_recurring": self.is_recurring,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Budget(BaseModel):
    """Monthly budget threshold for a specific category or overall monthly spending."""
    __tablename__ = "budgets"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    category_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("financial_categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    month: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        index=True
    )  # Format: YYYY-MM (e.g. 2026-11)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )
    currency: Mapped[str] = mapped_column(
        String(10),
        default="USD",
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="budgets")
    category: Mapped[Optional[FinancialCategory]] = relationship("FinancialCategory", back_populates="budgets")

    __table_args__ = (
        UniqueConstraint("user_id", "category_id", "month", name="uq_budget_user_category_month"),
        Index("ix_budgets_user_month", "user_id", "month"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else "Overall Budget",
            "category_color": self.category.color_hex if self.category else "#6C63FF",
            "month": self.month,
            "amount": str(self.amount),
            "currency": self.currency,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SavingsGoal(BaseModel):
    """Target savings vault for specific personal milestones or rainy-day funds."""
    __tablename__ = "savings_goals"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )
    target_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )
    current_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        nullable=False
    )
    target_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="in_progress",
        nullable=False
    )  # in_progress, completed, archived
    currency: Mapped[str] = mapped_column(
        String(10),
        default="USD",
        nullable=False
    )
    color_hex: Mapped[str] = mapped_column(
        String(10),
        default="#6C63FF",
        nullable=False
    )
    icon: Mapped[str] = mapped_column(
        String(50),
        default="flag",
        nullable=False
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="savings_goals")
    contributions: Mapped[List["SavingsGoalContribution"]] = relationship(
        "SavingsGoalContribution",
        back_populates="savings_goal",
        cascade="all, delete-orphan",
        order_by="desc(SavingsGoalContribution.contribution_date)"
    )

    __table_args__ = (
        Index("ix_savings_goals_user_status", "user_id", "status"),
    )

    def to_dict(self):
        progress_pct = (
            min(100.0, float(round((self.current_amount / self.target_amount) * 100, 1)))
            if self.target_amount > 0 else 0.0
        )
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "target_amount": str(self.target_amount),
            "current_amount": str(self.current_amount),
            "progress_percentage": progress_pct,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "status": self.status,
            "currency": self.currency,
            "color_hex": self.color_hex,
            "icon": self.icon,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SavingsGoalContribution(BaseModel):
    """Historical ledger record of money added to a savings goal."""
    __tablename__ = "savings_goal_contributions"

    savings_goal_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("savings_goals.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    account_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("financial_accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )
    contribution_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    note: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="savings_goal_contributions")
    savings_goal: Mapped[SavingsGoal] = relationship("SavingsGoal", back_populates="contributions")
    account: Mapped[Optional[FinancialAccount]] = relationship("FinancialAccount", back_populates="savings_contributions")

    __table_args__ = (
        Index("ix_savings_contrib_goal_date", "savings_goal_id", "contribution_date"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "savings_goal_id": self.savings_goal_id,
            "user_id": self.user_id,
            "account_id": self.account_id,
            "account_name": self.account.name if self.account else None,
            "amount": str(self.amount),
            "contribution_date": self.contribution_date.isoformat() if self.contribution_date else None,
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
