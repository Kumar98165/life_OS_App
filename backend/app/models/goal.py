from datetime import datetime
from sqlalchemy import String, Text, Boolean, Float, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Goal(BaseModel):
    """High-level OKRs and personal goals with measurable milestones."""
    __tablename__ = "goals"

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
    target_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="in_progress",
        nullable=False
    )  # not_started, in_progress, completed, paused, cancelled (also active, achieved, abandoned)
    priority: Mapped[str] = mapped_column(
        String(20),
        default="medium",
        nullable=False
    )  # low, medium, high
    progress_percent: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False
    )
    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="goals")
    milestones: Mapped[list["GoalMilestone"]] = relationship(
        "GoalMilestone",
        back_populates="goal",
        cascade="all, delete-orphan",
        order_by="GoalMilestone.sort_order"
    )

    __table_args__ = (
        Index("ix_goals_user_status", "user_id", "status"),
        Index("ix_goals_user_priority", "user_id", "priority"),
    )

    def calculate_progress(self) -> float:
        """Calculate progress percentage based on completed milestones."""
        if not self.milestones:
            return 0.0
        total = len(self.milestones)
        completed = sum(1 for m in self.milestones if m.is_completed)
        return round((completed / total) * 100.0, 1)

    def to_dict(self, include_milestones: bool = True):
        completed_count = sum(1 for m in self.milestones if m.is_completed) if self.milestones else 0
        total_count = len(self.milestones) if self.milestones else 0

        res = {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "status": self.status,
            "priority": self.priority,
            "progress_percent": round(self.progress_percent, 1),
            "category": self.category,
            "total_milestones": total_count,
            "completed_milestones": completed_count,
            "milestones_count": total_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_milestones:
            res["milestones"] = [m.to_dict() for m in self.milestones] if self.milestones else []
        return res
class GoalMilestone(BaseModel):
    """Specific measurable checkpoints belonging to a goal."""
    __tablename__ = "goal_milestones"

    goal_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("goals.id", ondelete="CASCADE"),
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
    target_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    # Relationship
    goal: Mapped[Goal] = relationship("Goal", back_populates="milestones")

    def to_dict(self):
        return {
            "id": self.id,
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "is_completed": self.is_completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
