from datetime import datetime
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class TaskCategory(BaseModel):
    """Category grouping for tasks (e.g. Work, Health, Personal, Deep Work)."""
    __tablename__ = "task_categories"

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
    color_hex: Mapped[str] = mapped_column(
        String(10),
        default="#6C63FF",
        nullable=False
    )
    icon: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="task_categories")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="category", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_task_category_user_name"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "color_hex": self.color_hex,
            "icon": self.icon,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Task(BaseModel):
    """Actionable tasks with priority matrix, due dates, and completion status."""
    __tablename__ = "tasks"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    category_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("task_categories.id", ondelete="SET NULL"),
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
    status: Mapped[str] = mapped_column(
        String(20),
        default="todo",
        nullable=False
    )  # todo, in_progress, completed, archived
    priority: Mapped[str] = mapped_column(
        String(20),
        default="medium",
        nullable=False
    )  # low, medium, high, urgent
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    estimated_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tasks")
    category: Mapped[TaskCategory | None] = relationship("TaskCategory", back_populates="tasks")
    planner_blocks: Mapped[list["PlannerBlock"]] = relationship("PlannerBlock", back_populates="task")

    __table_args__ = (
        Index("ix_tasks_user_status", "user_id", "status"),
        Index("ix_tasks_user_due_date", "user_id", "due_date"),
        Index("ix_tasks_user_priority", "user_id", "priority"),
        Index("ix_tasks_user_archived", "user_id", "is_archived"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category": self.category.to_dict() if self.category else None,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_archived": self.is_archived,
            "estimated_minutes": self.estimated_minutes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

