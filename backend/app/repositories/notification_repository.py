from datetime import datetime, timezone, timedelta
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import select, update, delete, func, and_, or_
from app import db
from app.models.notification import (
    Notification,
    NotificationPreference,
    Reminder,
    PushDeviceToken,
    NotificationDelivery,
)


class NotificationRepository:
    """Data access repository for notifications, reminders, preferences, and device push tokens."""

    # -------------------------------------------------------------------------
    # Notification Queries & Mutations
    # -------------------------------------------------------------------------

    def list_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        notification_type: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> Tuple[List[Notification], int]:
        """List notifications for user with optional unread and type filters."""
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.is_read.is_(False))

        if notification_type:
            query = query.where(Notification.notification_type == notification_type)

        count_stmt = select(func.count()).select_from(query.subquery())
        total = db.session.execute(count_stmt).scalar() or 0

        query = query.order_by(Notification.created_at.desc())
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        items = list(db.session.execute(query).scalars().all())
        return items, total

    def get_unread_count(self, user_id: str) -> int:
        """Count unread notifications for user."""
        stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False)
        )
        return db.session.execute(stmt).scalar() or 0

    def get_notification_by_id(
        self,
        notification_id: str,
        user_id: Optional[str] = None
    ) -> Optional[Notification]:
        """Retrieve single notification with optional user IDOR validation."""
        query = select(Notification).where(Notification.id == notification_id)
        if user_id:
            query = query.where(Notification.user_id == user_id)
        return db.session.execute(query).scalar_one_or_none()

    def create_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        notification_type: str = "general",
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        scheduled_for: Optional[datetime] = None,
        data_payload: Optional[str] = None,
        dedup_hash: Optional[str] = None,
        is_delivered: bool = False,
    ) -> Optional[Notification]:
        """Create notification with deduplication suppression."""
        if dedup_hash:
            # Check if matching dedup_hash exists for this user in the last 24 hours
            since = datetime.now(timezone.utc) - timedelta(hours=24)
            existing_stmt = select(Notification).where(
                Notification.user_id == user_id,
                Notification.dedup_hash == dedup_hash,
                Notification.created_at >= since
            )
            existing = db.session.execute(existing_stmt).scalar_one_or_none()
            if existing:
                return existing

        notif = Notification(
            user_id=user_id,
            title=title,
            body=body,
            notification_type=notification_type,
            entity_type=entity_type,
            entity_id=entity_id,
            scheduled_for=scheduled_for,
            data_payload=data_payload,
            dedup_hash=dedup_hash,
            is_delivered=is_delivered,
            delivered_at=datetime.now(timezone.utc) if is_delivered else None,
        )
        db.session.add(notif)
        db.session.commit()
        return notif

    def mark_as_read(self, notification_id: str, user_id: str) -> Optional[Notification]:
        """Mark single notification as read."""
        notif = self.get_notification_by_id(notification_id, user_id=user_id)
        if not notif:
            return None

        if not notif.is_read:
            notif.is_read = True
            notif.read_at = datetime.now(timezone.utc)
            db.session.commit()

        return notif

    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all unread notifications for user as read."""
        now = datetime.now(timezone.utc)
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .values(is_read=True, read_at=now)
        )
        result = db.session.execute(stmt)
        db.session.commit()
        return result.rowcount or 0

    def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete notification with user ownership validation."""
        notif = self.get_notification_by_id(notification_id, user_id=user_id)
        if not notif:
            return False

        db.session.delete(notif)
        db.session.commit()
        return True

    # -------------------------------------------------------------------------
    # Notification Preferences
    # -------------------------------------------------------------------------

    def get_or_create_preferences(self, user_id: str) -> NotificationPreference:
        """Fetch user notification preferences or initialize defaults."""
        stmt = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        pref = db.session.execute(stmt).scalar_one_or_none()

        if not pref:
            pref = NotificationPreference(
                user_id=user_id,
                tasks_enabled=True,
                planner_enabled=True,
                habits_enabled=True,
                goals_enabled=True,
                finance_enabled=True,
                push_enabled=True,
                in_app_enabled=True,
                quiet_hours_enabled=False,
                quiet_hours_start="22:00",
                quiet_hours_end="08:00",
                timezone="UTC"
            )
            db.session.add(pref)
            db.session.commit()

        return pref

    def update_preferences(self, user_id: str, **kwargs) -> NotificationPreference:
        """Update notification preferences for user."""
        pref = self.get_or_create_preferences(user_id)
        for key, val in kwargs.items():
            if val is not None and hasattr(pref, key):
                setattr(pref, key, val)
        db.session.commit()
        return pref

    # -------------------------------------------------------------------------
    # Reminders
    # -------------------------------------------------------------------------

    def list_reminders(
        self,
        user_id: str,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> Tuple[List[Reminder], int]:
        """List reminders for user ordered by reminder_time ascending."""
        query = select(Reminder).where(Reminder.user_id == user_id)
        if status:
            query = query.where(Reminder.status == status)

        count_stmt = select(func.count()).select_from(query.subquery())
        total = db.session.execute(count_stmt).scalar() or 0

        query = query.order_by(Reminder.reminder_time.asc())
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        items = list(db.session.execute(query).scalars().all())
        return items, total

    def get_reminder_by_id(
        self,
        reminder_id: str,
        user_id: Optional[str] = None
    ) -> Optional[Reminder]:
        """Retrieve single reminder with optional user ownership validation."""
        query = select(Reminder).where(Reminder.id == reminder_id)
        if user_id:
            query = query.where(Reminder.user_id == user_id)
        return db.session.execute(query).scalar_one_or_none()

    def create_reminder(
        self,
        user_id: str,
        title: str,
        reminder_time: datetime,
        description: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        is_recurring: bool = False,
        recurrence_rule: Optional[str] = None,
    ) -> Reminder:
        """Create new scheduled reminder."""
        reminder = Reminder(
            user_id=user_id,
            title=title,
            description=description,
            reminder_time=reminder_time,
            entity_type=entity_type,
            entity_id=entity_id,
            is_recurring=is_recurring,
            recurrence_rule=recurrence_rule,
            status="pending",
        )
        db.session.add(reminder)
        db.session.commit()
        return reminder

    def update_reminder(
        self,
        reminder_id: str,
        user_id: str,
        **kwargs
    ) -> Optional[Reminder]:
        """Update existing reminder fields."""
        reminder = self.get_reminder_by_id(reminder_id, user_id=user_id)
        if not reminder:
            return None

        for key, val in kwargs.items():
            if val is not None and hasattr(reminder, key):
                setattr(reminder, key, val)

        db.session.commit()
        return reminder

    def delete_reminder(self, reminder_id: str, user_id: str) -> bool:
        """Delete reminder."""
        reminder = self.get_reminder_by_id(reminder_id, user_id=user_id)
        if not reminder:
            return False

        db.session.delete(reminder)
        db.session.commit()
        return True

    def get_due_reminders(
        self,
        current_time: datetime,
        limit: int = 100
    ) -> List[Reminder]:
        """Fetch pending reminders whose reminder_time has arrived, using row lock to avoid race conditions."""
        stmt = (
            select(Reminder)
            .where(
                Reminder.status == "pending",
                Reminder.reminder_time <= current_time
            )
            .order_by(Reminder.reminder_time.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return list(db.session.execute(stmt).scalars().all())

    # -------------------------------------------------------------------------
    # Push Device Tokens & Deliveries
    # -------------------------------------------------------------------------

    def register_device_token(
        self,
        user_id: str,
        token: str,
        device_type: str = "mobile",
        device_name: Optional[str] = None,
    ) -> PushDeviceToken:
        """Upsert device push token for user."""
        stmt = select(PushDeviceToken).where(
            PushDeviceToken.user_id == user_id,
            PushDeviceToken.token == token
        )
        dev = db.session.execute(stmt).scalar_one_or_none()
        now = datetime.now(timezone.utc)

        if dev:
            dev.is_active = True
            dev.device_type = device_type
            if device_name:
                dev.device_name = device_name
            dev.last_used_at = now
        else:
            dev = PushDeviceToken(
                user_id=user_id,
                token=token,
                device_type=device_type,
                device_name=device_name,
                is_active=True,
                last_used_at=now
            )
            db.session.add(dev)

        db.session.commit()
        return dev

    def delete_device_token(self, device_id: str, user_id: str) -> bool:
        """Deactivate or remove device push token."""
        stmt = select(PushDeviceToken).where(
            PushDeviceToken.id == device_id,
            PushDeviceToken.user_id == user_id
        )
        dev = db.session.execute(stmt).scalar_one_or_none()
        if not dev:
            return False

        db.session.delete(dev)
        db.session.commit()
        return True

    def list_active_device_tokens(self, user_id: str) -> List[PushDeviceToken]:
        """List active push device tokens for user."""
        stmt = select(PushDeviceToken).where(
            PushDeviceToken.user_id == user_id,
            PushDeviceToken.is_active.is_(True)
        )
        return list(db.session.execute(stmt).scalars().all())

    def log_delivery(
        self,
        notification_id: str,
        channel: str,
        status: str,
        error_message: Optional[str] = None,
        device_token_id: Optional[str] = None,
    ) -> NotificationDelivery:
        """Record delivery attempt audit entry."""
        delivery = NotificationDelivery(
            notification_id=notification_id,
            channel=channel,
            status=status,
            error_message=error_message,
            device_token_id=device_token_id,
            attempted_at=datetime.now(timezone.utc)
        )
        db.session.add(delivery)
        db.session.commit()
        return delivery

