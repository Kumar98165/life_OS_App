import bcrypt
from typing import Dict, Any, List, Optional
from sqlalchemy import String, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class User(BaseModel):
    """User account model for authentication, profile management, and root of ownership."""
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        nullable=False
    )

    # Relationships across LifeOS domains
    preferences: Mapped["UserPreference"] = relationship(
        "UserPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    task_categories: Mapped[List["TaskCategory"]] = relationship(
        "TaskCategory",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    goals: Mapped[List["Goal"]] = relationship(
        "Goal",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    habits: Mapped[List["Habit"]] = relationship(
        "Habit",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    planner_blocks: Mapped[List["PlannerBlock"]] = relationship(
        "PlannerBlock",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notes: Mapped[List["Note"]] = relationship(
        "Note",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    note_tags: Mapped[List["NoteTag"]] = relationship(
        "NoteTag",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    ai_conversations: Mapped[List["AIConversation"]] = relationship(
        "AIConversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    ai_memories: Mapped[List["AIMemory"]] = relationship(
        "AIMemory",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    ai_feedback: Mapped[List["AIFeedback"]] = relationship(
        "AIFeedback",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    ai_training_samples: Mapped[List["AITrainingSample"]] = relationship(
        "AITrainingSample",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    financial_accounts: Mapped[List["FinancialAccount"]] = relationship(
        "FinancialAccount",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    financial_categories: Mapped[List["FinancialCategory"]] = relationship(
        "FinancialCategory",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    financial_transactions: Mapped[List["FinancialTransaction"]] = relationship(
        "FinancialTransaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    budgets: Mapped[List["Budget"]] = relationship(
        "Budget",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    savings_goals: Mapped[List["SavingsGoal"]] = relationship(
        "SavingsGoal",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    savings_goal_contributions: Mapped[List["SavingsGoalContribution"]] = relationship(
        "SavingsGoalContribution",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notification_preference: Mapped[Optional["NotificationPreference"]] = relationship(
        "NotificationPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    reminders: Mapped[List["Reminder"]] = relationship(
        "Reminder",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    push_device_tokens: Mapped[List["PushDeviceToken"]] = relationship(
        "PushDeviceToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    activity_logs: Mapped[List["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_users_email_lower", "email"),
    )

    def set_password(self, plain_password: str) -> None:
        """Hash password using bcrypt with salt."""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        self.password_hash = hashed.decode("utf-8")

    def check_password(self, plain_password: str) -> bool:
        """Verify plain text password against stored bcrypt hash."""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            self.password_hash.encode("utf-8")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize user object without sensitive credentials."""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
