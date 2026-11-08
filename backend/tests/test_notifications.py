from datetime import datetime, timezone, timedelta
import pytest
from app import db
from app.models.notification import Notification, NotificationPreference, Reminder, PushDeviceToken
from app.models.task import Task
from app.models.habit import Habit
from app.models.finance import Budget
from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository


@pytest.fixture
def other_auth_headers(client):
    """Register and log in a secondary user for IDOR testing."""
    payload = {
        "email": "user.secondary@lifeos.internal",
        "password": "Password123!",
        "full_name": "Secondary User"
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    if resp.status_code == 201:
        token = resp.get_json()["data"]["tokens"]["access_token"]
    else:
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "user.secondary@lifeos.internal",
            "password": "Password123!"
        })
        token = login_resp.get_json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_notification_creation_and_listing(client, auth_headers):
    """Verify notification listing, unread filtering, and unread counter."""
    service = NotificationService()

    # Get user id from /api/v1/auth/me or preferences
    pref_resp = client.get("/api/v1/notifications/preferences", headers=auth_headers)
    assert pref_resp.status_code == 200
    user_id = pref_resp.get_json()["data"]["preferences"]["user_id"]

    # Dispatch two test notifications
    n1 = service.create_and_dispatch(
        user_id=user_id,
        title="Welcome to LifeOS Notifications",
        body="Stay on track with intelligent reminders.",
        notification_type="system",
        dedup_key="test_welcome_1"
    )
    n2 = service.create_and_dispatch(
        user_id=user_id,
        title="Your Daily Focus",
        body="Review your morning planner blocks.",
        notification_type="planner",
        dedup_key="test_planner_1"
    )
    assert n1 is not None
    assert n2 is not None

    # Check unread count
    count_resp = client.get("/api/v1/notifications/unread-count", headers=auth_headers)
    assert count_resp.status_code == 200
    assert count_resp.get_json()["data"]["unread_count"] >= 2

    # List all notifications
    list_resp = client.get("/api/v1/notifications", headers=auth_headers)
    assert list_resp.status_code == 200
    data = list_resp.get_json()["data"]
    assert data["total"] >= 2
    titles = [item["title"] for item in data["notifications"]]
    assert "Welcome to LifeOS Notifications" in titles
    assert "Your Daily Focus" in titles


def test_mark_as_read_and_mark_all_read(client, auth_headers):
    """Verify single and bulk read operations."""
    service = NotificationService()
    pref_resp = client.get("/api/v1/notifications/preferences", headers=auth_headers)
    user_id = pref_resp.get_json()["data"]["preferences"]["user_id"]

    n = service.create_and_dispatch(
        user_id=user_id,
        title="Mark Read Test",
        body="Testing status change.",
        dedup_key="test_read_1"
    )
    assert n.is_read is False

    # Mark single as read
    patch_resp = client.patch(f"/api/v1/notifications/{n.id}/read", headers=auth_headers)
    assert patch_resp.status_code == 200
    assert patch_resp.get_json()["data"]["notification"]["is_read"] is True

    # Create another unread notification
    n2 = service.create_and_dispatch(
        user_id=user_id,
        title="Bulk Read Test",
        body="Another notification.",
        dedup_key="test_read_2"
    )
    # Bulk mark all read
    bulk_resp = client.patch("/api/v1/notifications/read-all", headers=auth_headers)
    assert bulk_resp.status_code == 200
    assert bulk_resp.get_json()["data"]["marked_count"] >= 1

    # Verify unread count is now 0
    count_resp = client.get("/api/v1/notifications/unread-count", headers=auth_headers)
    assert count_resp.get_json()["data"]["unread_count"] == 0


def test_delete_notification_and_idor_protection(client, auth_headers, other_auth_headers):
    """Verify IDOR security: other user cannot access or delete notifications."""
    service = NotificationService()
    pref_resp = client.get("/api/v1/notifications/preferences", headers=auth_headers)
    user_id = pref_resp.get_json()["data"]["preferences"]["user_id"]

    n = service.create_and_dispatch(
        user_id=user_id,
        title="Private Security Alert",
        body="Confidential user data.",
        dedup_key="test_idor_1"
    )

    # Other user attempts to get notification
    other_get = client.get(f"/api/v1/notifications/{n.id}", headers=other_auth_headers)
    assert other_get.status_code == 404

    # Other user attempts to mark as read
    other_read = client.patch(f"/api/v1/notifications/{n.id}/read", headers=other_auth_headers)
    assert other_read.status_code == 404

    # Other user attempts to delete
    other_del = client.delete(f"/api/v1/notifications/{n.id}", headers=other_auth_headers)
    assert other_del.status_code == 404

    # Owner deletes notification
    owner_del = client.delete(f"/api/v1/notifications/{n.id}", headers=auth_headers)
    assert owner_del.status_code == 200


def test_deduplication_suppression(client, auth_headers):
    """Ensure duplicate notifications with the same dedup key within 24h are suppressed."""
    service = NotificationService()
    pref_resp = client.get("/api/v1/notifications/preferences", headers=auth_headers)
    user_id = pref_resp.get_json()["data"]["preferences"]["user_id"]

    key = "daily_habit_streak_check_123"
    n1 = service.create_and_dispatch(
        user_id=user_id,
        title="Habit Reminder",
        body="Streak check.",
        dedup_key=key
    )
    n2 = service.create_and_dispatch(
        user_id=user_id,
        title="Habit Reminder",
        body="Streak check.",
        dedup_key=key
    )

    assert n1.id == n2.id  # Same notification record returned, duplicate suppressed


def test_notification_preferences_and_quiet_hours(client, auth_headers):
    """Verify notification preference toggles and quiet hours logic."""
    service = NotificationService()

    # Update preferences to disable task notifications and set quiet hours
    update_payload = {
        "tasks_enabled": False,
        "quiet_hours_enabled": True,
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "08:00",
        "timezone": "UTC"
    }
    patch_resp = client.patch("/api/v1/notifications/preferences", json=update_payload, headers=auth_headers)
    assert patch_resp.status_code == 200
    pref_data = patch_resp.get_json()["data"]["preferences"]
    assert pref_data["tasks_enabled"] is False
    assert pref_data["quiet_hours_enabled"] is True

    user_id = pref_data["user_id"]
    pref = NotificationRepository().get_or_create_preferences(user_id)

    # 1. Category suppression: Task notification should be skipped
    n_task = service.create_and_dispatch(
        user_id=user_id,
        title="Task Due",
        body="Should be suppressed by preference.",
        notification_type="task"
    )
    assert n_task is None

    # 2. Quiet hours evaluation
    # Test during quiet hours (e.g. 23:30 UTC)
    late_night = datetime(2026, 11, 8, 23, 30, 0, tzinfo=timezone.utc)
    assert service.is_in_quiet_hours(pref, now_utc=late_night) is True

    # Test during daytime (e.g. 14:00 UTC)
    daytime = datetime(2026, 11, 8, 14, 0, 0, tzinfo=timezone.utc)
    assert service.is_in_quiet_hours(pref, now_utc=daytime) is False

    # Restore preferences
    client.patch("/api/v1/notifications/preferences", json={"tasks_enabled": True}, headers=auth_headers)


def test_reminder_lifecycle(client, auth_headers, other_auth_headers):
    """Verify creating, listing, updating, and cancelling reminders with IDOR rejection."""
    reminder_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    payload = {
        "title": "Dentist Appointment",
        "description": "Annual dental checkup.",
        "reminder_time": reminder_time,
        "entity_type": "custom",
        "is_recurring": False,
    }

    # Create reminder
    create_resp = client.post("/api/v1/notifications/reminders", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    reminder_id = create_resp.get_json()["data"]["reminder"]["id"]

    # List reminders
    list_resp = client.get("/api/v1/notifications/reminders", headers=auth_headers)
    assert list_resp.status_code == 200
    reminders = list_resp.get_json()["data"]["reminders"]
    assert any(r["id"] == reminder_id for r in reminders)

    # IDOR Check: other user cannot update
    other_patch = client.patch(
        f"/api/v1/notifications/reminders/{reminder_id}",
        json={"title": "Hacked Title"},
        headers=other_auth_headers
    )
    assert other_patch.status_code == 404

    # Update reminder
    patch_resp = client.patch(
        f"/api/v1/notifications/reminders/{reminder_id}",
        json={"title": "Doctor Appointment"},
        headers=auth_headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.get_json()["data"]["reminder"]["title"] == "Doctor Appointment"

    # Delete reminder
    del_resp = client.delete(f"/api/v1/notifications/reminders/{reminder_id}", headers=auth_headers)
    assert del_resp.status_code == 200


def test_reminder_scheduler_processing(client, auth_headers):
    """Verify due reminder processing, status transition to triggered, and recurrence generation."""
    repo = NotificationRepository()
    service = NotificationService(repo=repo)

    pref_resp = client.get("/api/v1/notifications/preferences", headers=auth_headers)
    user_id = pref_resp.get_json()["data"]["preferences"]["user_id"]

    # Create a due recurring reminder (scheduled for 5 minutes ago)
    past_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    r = repo.create_reminder(
        user_id=user_id,
        title="Daily Standup Meeting",
        reminder_time=past_time,
        is_recurring=True,
        recurrence_rule="daily"
    )
    assert r.status == "pending"

    # Process due reminders
    processed = service.process_due_reminders(current_time=datetime.now(timezone.utc))
    assert processed >= 1

    # Verify original reminder is triggered
    db.session.refresh(r)
    assert r.status == "triggered"
    assert r.triggered_at is not None
    assert r.notification_id is not None

    # Verify next occurrence was created
    reminders, _ = repo.list_reminders(user_id=user_id, status="pending")
    next_standup = next((rem for rem in reminders if rem.title == "Daily Standup Meeting"), None)
    assert next_standup is not None
    r_time = next_standup.reminder_time
    if r_time.tzinfo is None:
        r_time = r_time.replace(tzinfo=timezone.utc)
    assert r_time > datetime.now(timezone.utc)


def test_device_token_registration_and_deletion(client, auth_headers):
    """Verify Expo device push token registration, idempotency, and deletion."""
    token = "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]"
    payload = {
        "token": token,
        "device_type": "ios",
        "device_name": "iPhone 15 Pro"
    }

    # Register token
    reg_resp = client.post("/api/v1/notifications/devices", json=payload, headers=auth_headers)
    assert reg_resp.status_code == 201
    device_id = reg_resp.get_json()["data"]["device"]["id"]

    # Re-register same token (should update idempotently without error)
    reg_dup = client.post("/api/v1/notifications/devices", json=payload, headers=auth_headers)
    assert reg_dup.status_code == 201

    # Delete token
    del_resp = client.delete(f"/api/v1/notifications/devices/{device_id}", headers=auth_headers)
    assert del_resp.status_code == 200

