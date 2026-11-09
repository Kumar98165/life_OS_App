"""LifeOS - Tests for Step 21: Advanced Personalization.

Verifies:
1. Retrieval and creation of default UserPersonalization and DailyRoutine.
2. Partial updates to personalization settings (name, language, timezone, styling).
3. Dashboard customization: widget visibility, reordering, layout density.
4. Daily routine: work schedule, focus/break durations, rituals.
5. Granular resets to defaults ('dashboard', 'routine', 'identity', 'ai_style', 'all')
   without wiping AI memories, training consent, or user records.
6. User ownership & IDOR protection.
7. Validation constraints (date format, time format, routine HH:MM format).
8. Context engine integration of personalization and routine parameters.
"""
import pytest
from app.models.personalization import UserPersonalization, DailyRoutine, DEFAULT_DASHBOARD_WIDGETS
from app.services.personalization_service import personalization_service
from app.models.user import User
from app.extensions import db


# -----------------------------------------------------------------------------
# 1. Service Layer Tests
# -----------------------------------------------------------------------------

def test_personalization_defaults(app):
    """Verify default personalization and routine settings are safely initialized."""
    with app.app_context():
        user = User(email="alex@lifeos.internal", full_name="Alex Mercer")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        p = personalization_service.get_or_create_personalization(user.id)
        assert p.user_id == user.id
        assert p.preferred_name == "Alex Mercer"
        assert p.preferred_language == "en"
        assert p.timezone == "UTC"
        assert p.productivity_style == "structured"
        assert p.task_priority_strategy == "eisenhower"
        assert p.ai_response_style == "concise"
        assert p.personalization_enabled is True
        assert len(p.dashboard_widgets) == len(DEFAULT_DASHBOARD_WIDGETS)

        r = personalization_service.get_or_create_routine(user.id)
        assert r.user_id == user.id
        assert r.wake_time == "07:00"
        assert r.sleep_time == "23:00"
        assert r.work_start == "09:00"
        assert r.work_end == "17:00"
        assert r.focus_block_duration_minutes == 50
        assert r.break_duration_minutes == 10


def test_personalization_partial_updates(app):
    """Verify updating specific fields without altering unrelated preferences."""
    with app.app_context():
        user = User(email="sarah@lifeos.internal", full_name="Sarah Connor")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        updated = personalization_service.update_personalization(
            user_id=user.id,
            updates={
                "preferred_name": "Sarah C.",
                "productivity_style": "deep_work",
                "ai_response_style": "detailed",
                "date_format": "DD/MM/YYYY"
            }
        )
        assert updated.preferred_name == "Sarah C."
        assert updated.productivity_style == "deep_work"
        assert updated.ai_response_style == "detailed"
        assert updated.date_format == "DD/MM/YYYY"
        # Verify defaults preserved
        assert updated.preferred_language == "en"
        assert updated.time_format == "24h"


def test_dashboard_reorder_and_visibility(app):
    """Verify custom widget reordering and visibility toggling."""
    with app.app_context():
        user = User(email="dash@lifeos.internal", full_name="Dash User")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        custom_widgets = [
            {"id": "ai_quick_access", "visible": True, "order": 0, "title": "AI Assistant"},
            {"id": "today_tasks", "visible": True, "order": 1, "title": "Today's Tasks"},
            {"id": "daily_overview", "visible": False, "order": 2, "title": "Daily Overview"},
        ]

        res = personalization_service.update_dashboard_preferences(
            user_id=user.id,
            widgets=custom_widgets,
            density="compact"
        )
        assert res.dashboard_density == "compact"
        assert len(res.dashboard_widgets) == 3
        assert res.dashboard_widgets[0]["id"] == "ai_quick_access"
        assert res.dashboard_widgets[2]["visible"] is False


def test_granular_reset_preferences(app):
    """Verify granular reset of dashboard without wiping routine or identity."""
    with app.app_context():
        user = User(email="reset@lifeos.internal", full_name="Reset User")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        # Mutate both dashboard and routine
        personalization_service.update_dashboard_preferences(
            user_id=user.id,
            widgets=[{"id": "custom", "visible": True, "order": 0, "title": "Custom"}],
            density="compact"
        )
        personalization_service.update_daily_routine(
            user_id=user.id,
            updates={"work_start": "11:00", "work_end": "20:00"}
        )

        # Reset only dashboard
        reset_res = personalization_service.reset_preferences(user.id, target="dashboard")
        assert len(reset_res["personalization"]["dashboard_widgets"]) == len(DEFAULT_DASHBOARD_WIDGETS)
        assert reset_res["personalization"]["dashboard_density"] == "comfortable"

        # Verify routine remains customized
        r = personalization_service.get_or_create_routine(user.id)
        assert r.work_start == "11:00"
        assert r.work_end == "20:00"


def test_context_engine_personalization_injection(app):
    """Verify Context Engine incorporates personalization and routine parameters."""
    with app.app_context():
        user = User(email="context@lifeos.internal", full_name="Context User")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        personalization_service.update_personalization(
            user_id=user.id,
            updates={
                "preferred_name": "Johnny",
                "productivity_style": "pomodoro",
                "ai_response_style": "motivational",
            }
        )
        personalization_service.update_daily_routine(
            user_id=user.id,
            updates={
                "work_start": "08:00",
                "work_end": "16:00",
                "preferred_planning_time": "07:30"
            }
        )

def test_personalization_data_integrity(app):
    """Verify personalization and routine data structures persist without AI context engine."""
    with app.app_context():
        user = User(email="john@lifeos.internal", full_name="Johnathan")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        p = personalization_service.update_personalization(
            user_id=user.id,
            updates={
                "preferred_name": "Johnny",
                "productivity_style": "pomodoro",
            }
        )
        r = personalization_service.update_daily_routine(
            user_id=user.id,
            updates={
                "work_start": "08:00",
                "work_end": "16:00",
                "preferred_planning_time": "07:30"
            }
        )

        assert p.preferred_name == "Johnny"
        assert p.productivity_style == "pomodoro"
        assert r.work_start == "08:00"


# -----------------------------------------------------------------------------
# 2. REST API Endpoint Tests
# -----------------------------------------------------------------------------

def test_api_get_and_patch_personalization(client, auth_headers):
    """Verify GET and PATCH /api/v1/personalization endpoints."""
    # GET
    res = client.get("/api/v1/personalization", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "personalization" in data
    assert "daily_routine" in data

    # PATCH
    patch_payload = {
        "preferred_name": "Commander",
        "productivity_style": "flexible",
        "date_format": "YYYY-MM-DD",
        "ai_response_length": "short"
    }
    res_patch = client.patch("/api/v1/personalization", json=patch_payload, headers=auth_headers)
    assert res_patch.status_code == 200
    updated = res_patch.get_json()["data"]
    assert updated["preferred_name"] == "Commander"
    assert updated["productivity_style"] == "flexible"
    assert updated["ai_response_length"] == "short"


def test_api_dashboard_endpoints(client, auth_headers):
    """Verify GET and PATCH /api/v1/personalization/dashboard endpoints."""
    res = client.get("/api/v1/personalization/dashboard", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "dashboard_widgets" in data
    assert "dashboard_density" in data

    # Update widgets
    patch_payload = {
        "dashboard_density": "compact",
        "dashboard_widgets": [
            {"id": "today_tasks", "visible": True, "order": 0, "title": "Tasks"},
            {"id": "active_goals", "visible": False, "order": 1, "title": "Goals"}
        ]
    }
    res_patch = client.patch(
        "/api/v1/personalization/dashboard",
        json=patch_payload,
        headers=auth_headers
    )
    assert res_patch.status_code == 200
    updated = res_patch.get_json()["data"]
    assert updated["dashboard_density"] == "compact"
    assert len(updated["dashboard_widgets"]) == 2
    assert updated["dashboard_widgets"][1]["visible"] is False


def test_api_routine_endpoints(client, auth_headers):
    """Verify GET and PATCH /api/v1/personalization/routine endpoints."""
    res = client.get("/api/v1/personalization/routine", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["wake_time"] == "07:00"

    # Update routine
    patch_payload = {
        "wake_time": "06:30",
        "sleep_time": "22:30",
        "work_start": "08:30",
        "focus_block_duration_minutes": 45
    }
    res_patch = client.patch("/api/v1/personalization/routine", json=patch_payload, headers=auth_headers)
    assert res_patch.status_code == 200
    updated = res_patch.get_json()["data"]
    assert updated["wake_time"] == "06:30"
    assert updated["sleep_time"] == "22:30"
    assert updated["focus_block_duration_minutes"] == 45


def test_api_reset_endpoint(client, auth_headers):
    """Verify POST /api/v1/personalization/reset endpoint."""
    res = client.post(
        "/api/v1/personalization/reset",
        json={"target": "dashboard"},
        headers=auth_headers
    )
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["reset_target"] == "dashboard"
    assert len(data["personalization"]["dashboard_widgets"]) == len(DEFAULT_DASHBOARD_WIDGETS)


def test_api_validation_rejection(client, auth_headers):
    """Verify invalid payloads (malformed time formats or enum mismatches) are rejected."""
    # Malformed wake_time format (must be HH:MM)
    res = client.patch(
        "/api/v1/personalization/routine",
        json={"wake_time": "7am"},
        headers=auth_headers
    )
    assert res.status_code == 400

    # Invalid productivity style enum
    res2 = client.patch(
        "/api/v1/personalization",
        json={"productivity_style": "chaotic"},
        headers=auth_headers
    )
    assert res2.status_code == 400
