from datetime import datetime
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class PlannerBlock(BaseModel):
    """Time-blocked calendar units for day planning and deep work."""
    __tablename__ = "planner_blocks"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    task_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
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
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    block_type: Mapped[str] = mapped_column(
        String(30),
        default="task",
        nullable=False
    )  # task, personal, work, break, learning, meeting, other, focus, routine
    status: Mapped[str] = mapped_column(
        String(20),
        default="scheduled",
        nullable=False
    )  # scheduled, completed, cancelled, skipped
    color_hex: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    recurrence_rule: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )  # daily, weekly, monthly, weekdays
    reminder_minutes_before: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    timezone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        default="UTC"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="planner_blocks")
    task: Mapped["Task | None"] = relationship("Task", back_populates="planner_blocks")

    __table_args__ = (
        Index("ix_planner_user_start", "user_id", "start_time"),
        Index("ix_planner_user_status", "user_id", "status"),
        Index("ix_planner_user_completed", "user_id", "is_completed"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "task_id": self.task_id,
            "task": self.task.to_dict() if self.task else None,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "block_type": self.block_type,
            "status": self.status,
            "color_hex": self.color_hex,
            "is_completed": self.is_completed,
            "recurrence_rule": self.recurrence_rule,
            "reminder_minutes_before": self.reminder_minutes_before,
            "timezone": self.timezone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
