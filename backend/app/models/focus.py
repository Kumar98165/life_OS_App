from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class FocusGoal(BaseModel):
    """User daily/weekly target focus hours and configurations."""
    __tablename__ = "focus_goals"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    daily_target_minutes: Mapped[int] = mapped_column(
        Integer,
        default=120,
        nullable=False
    )
    weekly_target_minutes: Mapped[int] = mapped_column(
        Integer,
        default=600,
        nullable=False
    )
    preferred_technique: Mapped[str] = mapped_column(
        String(30),
        default="25/5",
        nullable=False
    )  # 25/5, 50/10, custom
    custom_work_minutes: Mapped[int] = mapped_column(
        Integer,
        default=25,
        nullable=False
    )
    custom_break_minutes: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False
    )
    custom_long_break_minutes: Mapped[int] = mapped_column(
        Integer,
        default=15,
        nullable=False
    )
    long_break_interval: Mapped[int] = mapped_column(
        Integer,
        default=4,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", backref="focus_goal")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "daily_target_minutes": self.daily_target_minutes,
            "weekly_target_minutes": self.weekly_target_minutes,
            "preferred_technique": self.preferred_technique,
            "custom_work_minutes": self.custom_work_minutes,
            "custom_break_minutes": self.custom_break_minutes,
            "custom_long_break_minutes": self.custom_long_break_minutes,
            "long_break_interval": self.long_break_interval,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FocusSession(BaseModel):
    """Individual deep work / Pomodoro focus session records."""
    __tablename__ = "focus_sessions"

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
    planner_block_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("planner_blocks.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Focus Session"
    )
    session_type: Mapped[str] = mapped_column(
        String(30),
        default="work",
        nullable=False
    )  # work, short_break, long_break
    target_duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=25,
        nullable=False
    )
    actual_duration_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False
    )  # active, paused, completed, cancelled
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    paused_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", backref="focus_sessions")
    task: Mapped["Task | None"] = relationship("Task", backref="focus_sessions")
    planner_block: Mapped["PlannerBlock | None"] = relationship("PlannerBlock", backref="focus_sessions")
    distractions: Mapped[List["FocusDistraction"]] = relationship(
        "FocusDistraction",
        back_populates="focus_session",
        cascade="all, delete-orphan",
        order_by="FocusDistraction.logged_at.desc()"
    )

    __table_args__ = (
        Index("ix_focus_user_start", "user_id", "start_time"),
        Index("ix_focus_user_status", "user_id", "status"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "task_id": self.task_id,
            "task": self.task.to_dict() if self.task else None,
            "planner_block_id": self.planner_block_id,
            "title": self.title,
            "session_type": self.session_type,
            "target_duration_minutes": self.target_duration_minutes,
            "actual_duration_seconds": self.actual_duration_seconds,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "paused_at": self.paused_at.isoformat() if self.paused_at else None,
            "notes": self.notes,
            "distraction_count": len(self.distractions) if self.distractions else 0,
            "distractions": [d.to_dict() for d in self.distractions] if self.distractions else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FocusDistraction(BaseModel):
    """Distraction logs tagged during active focus sessions."""
    __tablename__ = "focus_distractions"

    focus_session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("focus_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    distraction_type: Mapped[str] = mapped_column(
        String(50),
        default="internal",
        nullable=False
    )  # internal (thought, urge), external (phone, colleague, noise)
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    # Relationships
    focus_session: Mapped["FocusSession"] = relationship("FocusSession", back_populates="distractions")

    def to_dict(self):
        return {
            "id": self.id,
            "focus_session_id": self.focus_session_id,
            "user_id": self.user_id,
            "distraction_type": self.distraction_type,
            "description": self.description,
            "logged_at": self.logged_at.isoformat() if self.logged_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
