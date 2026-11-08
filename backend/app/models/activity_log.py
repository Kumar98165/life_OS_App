from sqlalchemy import String, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class ActivityLog(BaseModel):
    """Immutable audit trail for user operations, state changes, and security events."""
    __tablename__ = "activity_logs"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # create, update, delete, complete, login, chat
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # task, habit, goal, note, finance, session
    entity_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True
    )
    details: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="activity_logs")

    __table_args__ = (
        Index("ix_activity_logs_user_created", "user_id", "created_at"),
        Index("ix_activity_logs_user_entity", "user_id", "entity_type"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

