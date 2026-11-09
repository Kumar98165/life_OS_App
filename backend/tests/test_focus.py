import pytest
from datetime import datetime, timezone, timedelta
from app.models.focus import FocusGoal, FocusSession, FocusDistraction
from app.models.task import Task
from app.extensions import db


def test_focus_goal_get_and_update(client, auth_headers):
    # Get default goal
    res = client.get("/api/v1/focus/goal", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]["goal"]
    assert data["daily_target_minutes"] == 120
    assert data["preferred_technique"] == "25/5"

    # Update goal
    update_res = client.patch("/api/v1/focus/goal", json={
        "daily_target_minutes": 150,
        "preferred_technique": "50/10",
        "custom_work_minutes": 50,
        "custom_break_minutes": 10
    }, headers=auth_headers)
    assert update_res.status_code == 200
    updated = update_res.get_json()["data"]["goal"]
    assert updated["daily_target_minutes"] == 150
    assert updated["preferred_technique"] == "50/10"
    assert updated["custom_work_minutes"] == 50


def test_focus_session_lifecycle(client, auth_headers):
    # 1. Create a task to link
    task_res = client.post("/api/v1/tasks", json={
        "title": "Study Deep Architecture",
        "priority": "high"
    }, headers=auth_headers)
    assert task_res.status_code == 201
    task_id = task_res.get_json()["data"]["task"]["id"]

    # 2. Start session
    start_res = client.post("/api/v1/focus/sessions", json={
        "title": "Deep Architecture Sprint",
        "session_type": "work",
        "target_duration_minutes": 25,
        "task_id": task_id,
        "notes": "Focused deep dive"
    }, headers=auth_headers)
    assert start_res.status_code == 201
    session_id = start_res.get_json()["data"]["session"]["id"]
    assert start_res.get_json()["data"]["session"]["status"] == "active"

    # 3. Check active session
    active_res = client.get("/api/v1/focus/sessions/active", headers=auth_headers)
    assert active_res.status_code == 200
    assert active_res.get_json()["data"]["session"]["id"] == session_id

    # 4. Log distraction
    dist_res = client.post(f"/api/v1/focus/sessions/{session_id}/distractions", json={
        "distraction_type": "internal",
        "description": "Urge to check emails"
    }, headers=auth_headers)
    assert dist_res.status_code == 201
    assert dist_res.get_json()["data"]["distraction"]["description"] == "Urge to check emails"

    # 5. Pause session
    pause_res = client.post(f"/api/v1/focus/sessions/{session_id}/pause", headers=auth_headers)
    assert pause_res.status_code == 200
    assert pause_res.get_json()["data"]["session"]["status"] == "paused"

    # 6. Resume session
    resume_res = client.post(f"/api/v1/focus/sessions/{session_id}/resume", headers=auth_headers)
    assert resume_res.status_code == 200
    assert resume_res.get_json()["data"]["session"]["status"] == "active"

    # 7. Stop/complete session
    stop_res = client.post(f"/api/v1/focus/sessions/{session_id}/stop", json={
        "actual_duration_seconds": 1500,
        "notes": "Completed 25 full minutes of focus"
    }, headers=auth_headers)
    assert stop_res.status_code == 200
    completed = stop_res.get_json()["data"]["session"]
    assert completed["status"] == "completed"
    assert completed["actual_duration_seconds"] == 1500

    # 8. Stats check
    stats_res = client.get("/api/v1/focus/stats", headers=auth_headers)
    assert stats_res.status_code == 200
    stats = stats_res.get_json()["data"]["stats"]
    assert stats["today_minutes"] == 25.0
    assert stats["completed_sessions_today"] >= 1
    assert stats["distractions_logged_today"] >= 1


def test_advanced_calendar_free_time_and_ical(client, auth_headers):
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_utc = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)
    end_utc = now_utc + timedelta(hours=2)

    # Create a scheduled block
    block_res = client.post("/api/v1/planner/blocks", json={
        "title": "Calendar Meeting Test",
        "start_time": now_utc.isoformat(),
        "end_time": end_utc.isoformat(),
        "block_type": "work",
        "status": "scheduled",
        "recurrence_rule": "weekly",
        "reminder_minutes_before": 15,
        "timezone": "UTC"
    }, headers=auth_headers)
    assert block_res.status_code == 201

    # Query free time
    free_res = client.get(f"/api/v1/planner/free-time?date={today_str}&start_hour=8&end_hour=18", headers=auth_headers)
    assert free_res.status_code == 200
    slots = free_res.get_json()["data"]["free_slots"]
    assert isinstance(slots, list)
    assert len(slots) >= 1

    # Query iCal export
    ics_res = client.get("/api/v1/planner/export.ics", headers=auth_headers)
    assert ics_res.status_code == 200
    assert "BEGIN:VCALENDAR" in ics_res.text
    assert "SUMMARY:Calendar Meeting Test" in ics_res.text
    assert "RRULE:FREQ=WEEKLY" in ics_res.text
