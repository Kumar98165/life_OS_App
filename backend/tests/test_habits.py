"""LifeOS - Habit Management and Streak Engine Test Suite."""
import pytest
from datetime import date, timedelta


def test_create_habit_success(client, auth_headers):
    """Test creating a valid habit with daily frequency."""
    payload = {
        "title": "Morning Meditation",
        "description": "15 minutes mindfulness breathing",
        "frequency": "daily",
        "target_days_per_week": 7,
        "color_hex": "#10B981",
        "icon": "leaf"
    }

    resp = client.post("/api/v1/habits", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert "habit" in data
    habit = data["habit"]
    assert habit["title"] == "Morning Meditation"
    assert habit["frequency"] == "daily"
    assert habit["color_hex"] == "#10B981"
    assert habit["current_streak"] == 0
    assert habit["longest_streak"] == 0
    assert habit["is_archived"] is False


def test_create_habit_validation_errors(client, auth_headers):
    """Test validation errors for blank title or invalid frequency."""
    # Blank title
    resp1 = client.post("/api/v1/habits", json={"title": "   "}, headers=auth_headers)
    assert resp1.status_code == 422

    # Invalid frequency
    resp2 = client.post(
        "/api/v1/habits",
        json={"title": "Workout", "frequency": "biweekly_invalid"},
        headers=auth_headers
    )
    assert resp2.status_code == 422


def test_list_and_filter_habits(client, auth_headers):
    """Test listing user habits with frequency filter."""
    client.post("/api/v1/habits", json={"title": "Daily Water", "frequency": "daily"}, headers=auth_headers)
    client.post("/api/v1/habits", json={"title": "Weekday Coding", "frequency": "weekdays"}, headers=auth_headers)

    resp = client.get("/api/v1/habits", headers=auth_headers)
    assert resp.status_code == 200
    habits = resp.get_json()["data"]["habits"]
    assert len(habits) >= 2
    assert "completed_today" in habits[0]

    # Filter by weekdays
    resp_filter = client.get("/api/v1/habits?frequency=weekdays", headers=auth_headers)
    assert resp_filter.status_code == 200
    w_habits = resp_filter.get_json()["data"]["habits"]
    assert all(h["frequency"] == "weekdays" for h in w_habits)


def test_update_and_archive_habit(client, auth_headers):
    """Test updating habit title, color, and archiving."""
    create_resp = client.post(
        "/api/v1/habits",
        json={"title": "Evening Reading", "frequency": "daily"},
        headers=auth_headers
    )
    habit_id = create_resp.get_json()["data"]["habit"]["id"]

    update_resp = client.patch(
        f"/api/v1/habits/{habit_id}",
        json={"title": "30 Min Evening Reading", "color_hex": "#3B82F6", "is_archived": True},
        headers=auth_headers
    )
    assert update_resp.status_code == 200
    updated = update_resp.get_json()["data"]["habit"]
    assert updated["title"] == "30 Min Evening Reading"
    assert updated["color_hex"] == "#3B82F6"
    assert updated["is_archived"] is True

    # Check unarchived list excludes it
    list_resp = client.get("/api/v1/habits", headers=auth_headers)
    assert not any(h["id"] == habit_id for h in list_resp.get_json()["data"]["habits"])


def test_delete_habit(client, auth_headers):
    """Test deleting a habit."""
    create_resp = client.post(
        "/api/v1/habits",
        json={"title": "Temporary Habit", "frequency": "daily"},
        headers=auth_headers
    )
    habit_id = create_resp.get_json()["data"]["habit"]["id"]

    del_resp = client.delete(f"/api/v1/habits/{habit_id}", headers=auth_headers)
    assert del_resp.status_code == 200

    get_resp = client.get(f"/api/v1/habits/{habit_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_daily_check_in_and_streaks(client, auth_headers):
    """Test checking in today and yesterday to advance current streak to 2."""
    create_resp = client.post(
        "/api/v1/habits",
        json={"title": "Pushups", "frequency": "daily"},
        headers=auth_headers
    )
    habit_id = create_resp.get_json()["data"]["habit"]["id"]

    today = date.today()
    yesterday = today - timedelta(days=1)

    # 1. Log yesterday
    resp_yest = client.post(
        f"/api/v1/habits/{habit_id}/logs",
        json={"log_date": yesterday.isoformat(), "completed": True},
        headers=auth_headers
    )
    assert resp_yest.status_code == 201
    assert resp_yest.get_json()["data"]["habit"]["current_streak"] == 1

    # 2. Log today
    resp_today = client.post(
        f"/api/v1/habits/{habit_id}/logs",
        json={"log_date": today.isoformat(), "completed": True, "notes": "Felt great!"},
        headers=auth_headers
    )
    assert resp_today.status_code == 201
    assert resp_today.get_json()["data"]["habit"]["current_streak"] == 2
    assert resp_today.get_json()["data"]["habit"]["longest_streak"] >= 2

    # 3. Duplicate check-in updates existing log idempotently
    resp_dup = client.post(
        f"/api/v1/habits/{habit_id}/logs",
        json={"log_date": today.isoformat(), "completed": True, "notes": "Updated note"},
        headers=auth_headers
    )
    assert resp_dup.status_code == 201
    assert resp_dup.get_json()["data"]["habit"]["current_streak"] == 2


def test_future_check_in_forbidden(client, auth_headers):
    """Test that check-ins in the future are rejected with 400."""
    create_resp = client.post(
        "/api/v1/habits",
        json={"title": "Walking", "frequency": "daily"},
        headers=auth_headers
    )
    habit_id = create_resp.get_json()["data"]["habit"]["id"]

    tomorrow = date.today() + timedelta(days=1)
    resp = client.post(
        f"/api/v1/habits/{habit_id}/logs",
        json={"log_date": tomorrow.isoformat(), "completed": True},
        headers=auth_headers
    )
    assert resp.status_code == 400


def test_weekday_habit_weekend_check_in_forbidden(client, auth_headers):
    """Test that weekday-only habits reject check-ins on Saturday or Sunday."""
    create_resp = client.post(
        "/api/v1/habits",
        json={"title": "Weekday Standup", "frequency": "weekdays"},
        headers=auth_headers
    )
    habit_id = create_resp.get_json()["data"]["habit"]["id"]

    # Find next or previous Saturday
    today = date.today()
    saturday = today + timedelta(days=(5 - today.weekday()))
    if saturday > today:
        saturday -= timedelta(days=7)

    resp = client.post(
        f"/api/v1/habits/{habit_id}/logs",
        json={"log_date": saturday.isoformat(), "completed": True},
        headers=auth_headers
    )
    assert resp.status_code == 400


def test_undo_check_in(client, auth_headers):
    """Test undoing a check-in recalculates the streak downward."""
    create_resp = client.post(
        "/api/v1/habits",
        json={"title": "Guitar Practice", "frequency": "daily"},
        headers=auth_headers
    )
    habit_id = create_resp.get_json()["data"]["habit"]["id"]

    today = date.today()
    log_resp = client.post(
        f"/api/v1/habits/{habit_id}/logs",
        json={"log_date": today.isoformat(), "completed": True},
        headers=auth_headers
    )
    log_id = log_resp.get_json()["data"]["log"]["id"]
    assert log_resp.get_json()["data"]["habit"]["current_streak"] == 1

    # Delete log (undo)
    del_resp = client.delete(f"/api/v1/habits/{habit_id}/logs/{log_id}", headers=auth_headers)
    assert del_resp.status_code == 200
    assert del_resp.get_json()["data"]["habit"]["current_streak"] == 0


def test_habit_stats_endpoint(client, auth_headers):
    """Test fetching statistical overview for a habit."""
    create_resp = client.post(
        "/api/v1/habits",
        json={"title": "Hydration", "frequency": "daily"},
        headers=auth_headers
    )
    habit_id = create_resp.get_json()["data"]["habit"]["id"]

    today = date.today()
    client.post(
        f"/api/v1/habits/{habit_id}/logs",
        json={"log_date": today.isoformat(), "completed": True},
        headers=auth_headers
    )

    stats_resp = client.get(f"/api/v1/habits/{habit_id}/stats", headers=auth_headers)
    assert stats_resp.status_code == 200
    data = stats_resp.get_json()["data"]
    assert "stats" in data
    stats = data["stats"]
    assert stats["current_streak"] == 1
    assert stats["total_completed_days"] == 1
    assert "completion_rate" in stats
    assert "weekly_consistency" in stats
    assert "recent_logs" in data


def test_daily_and_weekly_summaries(client, auth_headers):
    """Test retrieving daily and weekly summary statistics."""
    # Create habit and check in
    create_resp = client.post(
        "/api/v1/habits",
        json={"title": "Summary Test Habit", "frequency": "daily"},
        headers=auth_headers
    )
    habit_id = create_resp.get_json()["data"]["habit"]["id"]
    today = date.today()
    client.post(
        f"/api/v1/habits/{habit_id}/logs",
        json={"log_date": today.isoformat(), "completed": True},
        headers=auth_headers
    )

    # Daily summary
    daily_resp = client.get(f"/api/v1/habits/summary/daily?date={today.isoformat()}", headers=auth_headers)
    assert daily_resp.status_code == 200
    daily_data = daily_resp.get_json()["data"]
    assert daily_data["completed_count"] >= 1
    assert daily_data["scheduled_count"] >= 1
    assert "completion_percentage" in daily_data

    # Weekly summary
    mon = today - timedelta(days=today.weekday())
    weekly_resp = client.get(f"/api/v1/habits/summary/weekly?week_start={mon.isoformat()}", headers=auth_headers)
    assert weekly_resp.status_code == 200
    weekly_data = weekly_resp.get_json()["data"]
    assert len(weekly_data["days"]) == 7


def test_cross_user_isolation(client, auth_headers):
    """Test that User A cannot access, check in, or delete User B's habit."""
    # Create habit under User A
    create_resp = client.post(
        "/api/v1/habits",
        json={"title": "User A Secret Habit", "frequency": "daily"},
        headers=auth_headers
    )
    habit_id = create_resp.get_json()["data"]["habit"]["id"]

    # Register and authenticate User B
    client.post("/api/v1/auth/register", json={
        "email": "userb_habits@example.com",
        "password": "Password123!",
        "full_name": "User B"
    })
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "userb_habits@example.com",
        "password": "Password123!"
    })
    token_b = login_resp.get_json()["data"]["tokens"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B attempts to access habit A -> 404/403
    resp_get = client.get(f"/api/v1/habits/{habit_id}", headers=headers_b)
    assert resp_get.status_code in [403, 404]

    # User B attempts check in -> 404/403
    resp_log = client.post(
        f"/api/v1/habits/{habit_id}/logs",
        json={"log_date": date.today().isoformat(), "completed": True},
        headers=headers_b
    )
    assert resp_log.status_code in [403, 404]

