from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Notification(BaseModel):
    """System, reminder, and contextual notifications dispatched to the user."""
    __tablename__ = "notifications"

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
    body: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    notification_type: Mapped[str] = mapped_column(
        String(30),
        default="general",
        nullable=False,
        index=True
    )  # task, planner, habit, goal, finance, reminder, system
    entity_type: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )  # task, habit, planner_block, goal, finance_account, budget, savings_goal, reminder
    entity_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    scheduled_for: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    data_payload: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )  # JSON-encoded payload for client deep-linking (e.g. {"route": "TasksTab", "id": "..."})
    dedup_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True
    )  # SHA-256 hash or deterministic key for duplicate suppression
    is_delivered: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    deliveries: Mapped[List["NotificationDelivery"]] = relationship(
        "NotificationDelivery",
        back_populates="notification",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_notifications_user_unread", "user_id", "is_read"),
        Index("ix_notifications_user_scheduled", "user_id", "scheduled_for"),
        Index("ix_notifications_user_created", "user_id", "created_at"),
        Index("ix_notifications_user_dedup", "user_id", "dedup_hash"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "body": self.body,
            "notification_type": self.notification_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "scheduled_for": self.scheduled_for.isoformat() if self.scheduled_for else None,
            "data_payload": self.data_payload,
            "dedup_hash": self.dedup_hash,
            "is_delivered": self.is_delivered,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class NotificationPreference(BaseModel):
    """User-specific granular notification channel and category preferences."""
    __tablename__ = "notification_preferences"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    # Category Toggles
    tasks_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    planner_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    habits_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    goals_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    finance_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Channel Toggles
    push_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    in_app_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Quiet Hours (Do Not Disturb)
    quiet_hours_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    quiet_hours_start: Mapped[str] = mapped_column(
        String(5),
        default="22:00",
        nullable=False
    )  # "HH:MM" 24h format
    quiet_hours_end: Mapped[str] = mapped_column(
        String(5),
        default="08:00",
        nullable=False
    )  # "HH:MM" 24h format

    # User timezone for quiet hours evaluation
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="UTC",
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notification_preference")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tasks_enabled": self.tasks_enabled,
            "planner_enabled": self.planner_enabled,
            "habits_enabled": self.habits_enabled,
            "goals_enabled": self.goals_enabled,
            "finance_enabled": self.finance_enabled,
            "push_enabled": self.push_enabled,
            "in_app_enabled": self.in_app_enabled,
            "quiet_hours_enabled": self.quiet_hours_enabled,
            "quiet_hours_start": self.quiet_hours_start,
            "quiet_hours_end": self.quiet_hours_end,
            "timezone": self.timezone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Reminder(BaseModel):
    """User-scheduled or contextual reminder triggering at a specific point in time."""
    __tablename__ = "reminders"

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
    reminder_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    entity_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )  # task, habit, planner_block, goal, finance, custom
    entity_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True
    )
    is_recurring: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    recurrence_rule: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )  # daily, weekdays, weekly, monthly
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True
    )  # pending, triggered, cancelled, snoozed, expired
    triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    notification_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("notifications.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reminders")
    notification: Mapped[Optional["Notification"]] = relationship("Notification")

    __table_args__ = (
        Index("ix_reminders_user_status_time", "user_id", "status", "reminder_time"),
        Index("ix_reminders_status_time", "status", "reminder_time"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "reminder_time": self.reminder_time.isoformat() if self.reminder_time else None,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "is_recurring": self.is_recurring,
            "recurrence_rule": self.recurrence_rule,
            "status": self.status,
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "notification_id": self.notification_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PushDeviceToken(BaseModel):
    """Registered user device push token for Expo notification delivery."""
    __tablename__ = "push_device_tokens"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    token: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    device_type: Mapped[str] = mapped_column(
        String(20),
        default="mobile",
        nullable=False
    )  # ios, android, web, mobile
    device_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="push_device_tokens")
    deliveries: Mapped[List["NotificationDelivery"]] = relationship(
        "NotificationDelivery",
        back_populates="device_token"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "token", name="uq_push_device_user_token"),
        Index("ix_push_tokens_user_active", "user_id", "is_active"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token": self.token,
            "device_type": self.device_type,
            "device_name": self.device_name,
            "is_active": self.is_active,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class NotificationDelivery(BaseModel):
    """Delivery log and audit trail of notification attempts across channels."""
    __tablename__ = "notification_deliveries"

    notification_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    channel: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # in_app, expo_push
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )  # delivered, failed, skipped_quiet_hours, skipped_preference
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    device_token_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("push_device_tokens.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    notification: Mapped["Notification"] = relationship("Notification", back_populates="deliveries")
    device_token: Mapped[Optional["PushDeviceToken"]] = relationship("PushDeviceToken", back_populates="deliveries")

    __table_args__ = (
        Index("ix_notif_deliveries_notif_status", "notification_id", "status"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "notification_id": self.notification_id,
            "channel": self.channel,
            "status": self.status,
            "attempted_at": self.attempted_at.isoformat() if self.attempted_at else None,
            "error_message": self.error_message,
            "device_token_id": self.device_token_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
