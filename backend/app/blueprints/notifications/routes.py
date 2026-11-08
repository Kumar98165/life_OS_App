"""LifeOS - Centralized Notifications & Reminders Blueprint Routes.

REST endpoints for notification center, unread counters, preferences,
scheduled reminders, and push device token management.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import (
    NotificationResponse,
    NotificationPreferencesResponse,
    UpdateNotificationPreferencesRequest,
    CreateReminderRequest,
    UpdateReminderRequest,
    ReminderResponse,
    RegisterDeviceTokenRequest,
)
from app.core.response import api_response, error_response

notifications_bp = Blueprint("notifications", __name__)
notification_repo = NotificationRepository()
notification_service = NotificationService(repo=notification_repo)


# -----------------------------------------------------------------------------
# Notification Center Endpoints
# -----------------------------------------------------------------------------

@notifications_bp.route("", methods=["GET"])
@jwt_required()
def list_notifications():
    """Retrieve paginated notifications for authenticated user."""
    user_id = get_jwt_identity()
    unread_only = request.args.get("unread_only", "false").lower() == "true"
    notification_type = request.args.get("notification_type")
    page = int(request.args.get("page", 1))
    limit = min(int(request.args.get("limit", 50)), 100)

    items, total = notification_repo.list_notifications(
        user_id=user_id,
        unread_only=unread_only,
        notification_type=notification_type,
        page=page,
        limit=limit,
    )

    return api_response(
        data={
            "notifications": [n.to_dict() for n in items],
            "total": total,
            "page": page,
            "limit": limit,
        },
        message="Notifications retrieved successfully.",
        status_code=200,
    )


@notifications_bp.route("/unread-count", methods=["GET"])
@jwt_required()
def get_unread_count():
    """Get total count of unread notifications for badge indicators."""
    user_id = get_jwt_identity()
    count = notification_repo.get_unread_count(user_id=user_id)
    return api_response(
        data={"unread_count": count},
        message="Unread notification count retrieved.",
        status_code=200,
    )


@notifications_bp.route("/<notification_id>", methods=["GET"])
@jwt_required()
def get_notification(notification_id: str):
    """Retrieve single notification details."""
    user_id = get_jwt_identity()
    notif = notification_repo.get_notification_by_id(notification_id=notification_id, user_id=user_id)
    if not notif:
        return error_response(
            message="Notification not found.",
            status_code=404,
        )

    return api_response(
        data={"notification": notif.to_dict()},
        message="Notification retrieved.",
        status_code=200,
    )


@notifications_bp.route("/<notification_id>/read", methods=["PATCH"])
@jwt_required()
def mark_notification_read(notification_id: str):
    """Mark single notification as read."""
    user_id = get_jwt_identity()
    notif = notification_repo.mark_as_read(notification_id=notification_id, user_id=user_id)
    if not notif:
        return error_response(
            message="Notification not found.",
            status_code=404,
        )

    return api_response(
        data={"notification": notif.to_dict()},
        message="Notification marked as read.",
        status_code=200,
    )


@notifications_bp.route("/read-all", methods=["PATCH"])
@jwt_required()
def mark_all_notifications_read():
    """Mark all unread notifications for authenticated user as read."""
    user_id = get_jwt_identity()
    count = notification_repo.mark_all_as_read(user_id=user_id)
    return api_response(
        data={"marked_count": count},
        message=f"Marked {count} notifications as read.",
        status_code=200,
    )


@notifications_bp.route("/<notification_id>", methods=["DELETE"])
@jwt_required()
def delete_notification(notification_id: str):
    """Delete a notification with IDOR protection."""
    user_id = get_jwt_identity()
    deleted = notification_repo.delete_notification(notification_id=notification_id, user_id=user_id)
    if not deleted:
        return error_response(
            message="Notification not found or access denied.",
            status_code=404,
        )

    return api_response(
        message="Notification deleted successfully.",
        status_code=200,
    )


# -----------------------------------------------------------------------------
# Preferences Endpoints
# -----------------------------------------------------------------------------

@notifications_bp.route("/preferences", methods=["GET"])
@jwt_required()
def get_preferences():
    """Retrieve user notification preferences and quiet hours settings."""
    user_id = get_jwt_identity()
    pref = notification_repo.get_or_create_preferences(user_id=user_id)
    return api_response(
        data={"preferences": pref.to_dict()},
        message="Notification preferences retrieved.",
        status_code=200,
    )


@notifications_bp.route("/preferences", methods=["PATCH"])
@jwt_required()
def update_preferences():
    """Update user notification categories, channels, or quiet hours."""
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = UpdateNotificationPreferencesRequest(**body)

    pref = notification_repo.update_preferences(
        user_id=user_id,
        **validated.model_dump(exclude_unset=True)
    )

    return api_response(
        data={"preferences": pref.to_dict()},
        message="Notification preferences updated successfully.",
        status_code=200,
    )


# -----------------------------------------------------------------------------
# Reminders Endpoints
# -----------------------------------------------------------------------------

@notifications_bp.route("/reminders", methods=["GET"])
@jwt_required()
def list_reminders():
    """List scheduled reminders for authenticated user."""
    user_id = get_jwt_identity()
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    limit = min(int(request.args.get("limit", 50)), 100)

    items, total = notification_repo.list_reminders(
        user_id=user_id,
        status=status,
        page=page,
        limit=limit,
    )

    return api_response(
        data={
            "reminders": [r.to_dict() for r in items],
            "total": total,
            "page": page,
            "limit": limit,
        },
        message="Reminders retrieved successfully.",
        status_code=200,
    )


@notifications_bp.route("/reminders", methods=["POST"])
@jwt_required()
def create_reminder():
    """Create a new scheduled reminder."""
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = CreateReminderRequest(**body)

    reminder = notification_repo.create_reminder(
        user_id=user_id,
        title=validated.title,
        reminder_time=validated.reminder_time,
        description=validated.description,
        entity_type=validated.entity_type,
        entity_id=validated.entity_id,
        is_recurring=validated.is_recurring,
        recurrence_rule=validated.recurrence_rule,
    )

    return api_response(
        data={"reminder": reminder.to_dict()},
        message="Reminder scheduled successfully.",
        status_code=201,
    )


@notifications_bp.route("/reminders/<reminder_id>", methods=["PATCH"])
@jwt_required()
def update_reminder(reminder_id: str):
    """Update or reschedule an existing reminder."""
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = UpdateReminderRequest(**body)

    updated = notification_repo.update_reminder(
        reminder_id=reminder_id,
        user_id=user_id,
        **validated.model_dump(exclude_unset=True)
    )

    if not updated:
        return error_response(
            message="Reminder not found or access denied.",
            status_code=404,
        )

    return api_response(
        data={"reminder": updated.to_dict()},
        message="Reminder updated successfully.",
        status_code=200,
    )


@notifications_bp.route("/reminders/<reminder_id>", methods=["DELETE"])
@jwt_required()
def delete_reminder(reminder_id: str):
    """Cancel and delete a scheduled reminder."""
    user_id = get_jwt_identity()
    deleted = notification_repo.delete_reminder(reminder_id=reminder_id, user_id=user_id)
    if not deleted:
        return error_response(
            message="Reminder not found or access denied.",
            status_code=404,
        )

    return api_response(
        message="Reminder cancelled successfully.",
        status_code=200,
    )


# -----------------------------------------------------------------------------
# Device Tokens Endpoints
# -----------------------------------------------------------------------------

@notifications_bp.route("/devices", methods=["POST"])
@jwt_required()
def register_device():
    """Register an Expo device push token for authenticated user."""
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = RegisterDeviceTokenRequest(**body)

    dev = notification_repo.register_device_token(
        user_id=user_id,
        token=validated.token,
        device_type=validated.device_type,
        device_name=validated.device_name,
    )

    return api_response(
        data={"device": dev.to_dict()},
        message="Device push token registered successfully.",
        status_code=201,
    )


@notifications_bp.route("/devices/<device_id>", methods=["DELETE"])
@jwt_required()
def delete_device(device_id: str):
    """Unregister or deactivate a push device token."""
    user_id = get_jwt_identity()
    deleted = notification_repo.delete_device_token(device_id=device_id, user_id=user_id)
    if not deleted:
        return error_response(
            message="Device token not found or access denied.",
            status_code=404,
        )

    return api_response(
        message="Device token unregistered.",
        status_code=200,
    )


# -----------------------------------------------------------------------------
# Trigger & Scan Operations
# -----------------------------------------------------------------------------

@notifications_bp.route("/process-due", methods=["POST"])
def process_due_reminders_trigger():
    """System / Cron hook to process due scheduled reminders."""
    processed = notification_service.process_due_reminders()
    return api_response(
        data={"processed_count": processed},
        message=f"Processed {processed} due reminders.",
        status_code=200,
    )


@notifications_bp.route("/scan", methods=["POST"])
@jwt_required()
def scan_user_context():
    """Scan and generate contextual reminders for active user (tasks, habits, budgets)."""
    user_id = get_jwt_identity()
    tasks_notifs = notification_service.check_task_reminders(user_id)
    habits_notifs = notification_service.check_habit_reminders(user_id)
    finance_notifs = notification_service.check_finance_alerts(user_id)

    total_generated = len(tasks_notifs) + len(habits_notifs) + len(finance_notifs)
    return api_response(
        data={
            "task_notifications": len(tasks_notifs),
            "habit_notifications": len(habits_notifs),
            "finance_notifications": len(finance_notifs),
            "total_generated": total_generated,
        },
        message=f"Scanned context. Generated {total_generated} notifications.",
        status_code=200,
    )
