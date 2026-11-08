from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class UserPreference(BaseModel):
    """User account settings, design preferences, and notification defaults."""
    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    theme: Mapped[str] = mapped_column(
        String(20),
        default="light",
        nullable=False
    )
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="UTC",
        nullable=False
    )
    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    ai_daily_summary: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    ai_tone: Mapped[str] = mapped_column(
        String(30),
        default="balanced",
        nullable=False
    )
    ai_memory_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    ai_training_consent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    currency: Mapped[str] = mapped_column(
        String(10),
        default="USD",
        nullable=False
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="preferences")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "theme": self.theme,
            "timezone": self.timezone,
            "notifications_enabled": self.notifications_enabled,
            "ai_daily_summary": self.ai_daily_summary,
            "ai_tone": self.ai_tone,
            "ai_memory_enabled": self.ai_memory_enabled,
            "ai_training_consent": self.ai_training_consent,
            "currency": self.currency,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

