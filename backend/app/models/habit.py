from datetime import date
from sqlalchemy import String, Text, Boolean, Integer, Date, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Habit(BaseModel):
    """Daily or weekly recurring habits tracked with streaks."""
    __tablename__ = "habits"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    frequency: Mapped[str] = mapped_column(
        String(20),
        default="daily",
        nullable=False
    )  # daily, weekly
    target_days_per_week: Mapped[int] = mapped_column(
        Integer,
        default=7,
        nullable=False
    )
    current_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    longest_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    color_hex: Mapped[str] = mapped_column(
        String(10),
        default="#6C63FF",
        nullable=False
    )
    icon: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="habits")
    logs: Mapped[list["HabitLog"]] = relationship(
        "HabitLog",
        back_populates="habit",
        cascade="all, delete-orphan",
        order_by="desc(HabitLog.log_date)"
    )

    __table_args__ = (
        Index("ix_habits_user_archived", "user_id", "is_archived"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "frequency": self.frequency,
            "target_days_per_week": self.target_days_per_week,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "color_hex": self.color_hex,
            "icon": self.icon,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class HabitLog(BaseModel):
    """Daily check-in logs for habits."""
    __tablename__ = "habit_logs"

    habit_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("habits.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    log_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )
    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Relationship
    habit: Mapped[Habit] = relationship("Habit", back_populates="logs")

    __table_args__ = (
        UniqueConstraint("habit_id", "log_date", name="uq_habit_log_date"),
        Index("ix_habit_logs_habit_date", "habit_id", "log_date"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "log_date": self.log_date.isoformat() if self.log_date else None,
            "completed": self.completed,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

