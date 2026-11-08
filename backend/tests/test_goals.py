import pytest
from datetime import datetime, timezone, timedelta


def test_create_goal_success(client, auth_headers):
    """Test creating a valid goal with priority, target date, and category."""
    target_date = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
    payload = {
        "title": "Become a Principal Cloud Architect",
        "description": "Master distributed systems, AWS/GCP architecture, and team leadership",
        "priority": "high",
        "status": "in_progress",
        "category": "Career",
        "target_date": target_date
    }

    resp = client.post("/api/v1/goals", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert "goal" in data
    goal = data["goal"]
    assert goal["title"] == "Become a Principal Cloud Architect"
    assert goal["priority"] == "high"
    assert goal["status"] == "in_progress"
    assert goal["category"] == "Career"
    assert goal["progress_percent"] == 0.0
    assert goal["total_milestones"] == 0


def test_create_goal_validation_errors(client, auth_headers):
    """Test validation errors for blank title or invalid priority."""
    # Blank title
    resp1 = client.post("/api/v1/goals", json={"title": "   "}, headers=auth_headers)
    assert resp1.status_code == 422

    # Invalid priority
    resp2 = client.post(
        "/api/v1/goals",
        json={"title": "Valid Title", "priority": "super_urgent_invalid"},
        headers=auth_headers
    )
    assert resp2.status_code == 422


def test_list_goals_and_filters(client, auth_headers):
    """Test listing goals with status filter, search, and pagination."""
    # Create multiple goals
    client.post("/api/v1/goals", json={"title": "Goal Alpha", "priority": "high", "status": "in_progress"}, headers=auth_headers)
    client.post("/api/v1/goals", json={"title": "Goal Beta", "priority": "low", "status": "completed"}, headers=auth_headers)
    client.post("/api/v1/goals", json={"title": "Fitness Target Gamma", "priority": "medium", "status": "in_progress"}, headers=auth_headers)

    # Filter by status
    resp = client.get("/api/v1/goals?status=in_progress", headers=auth_headers)
    assert resp.status_code == 200
    goals = resp.get_json()["data"]["goals"]
    assert all(g["status"] in ["in_progress", "active"] for g in goals)

    # Filter by priority
    resp_prio = client.get("/api/v1/goals?priority=high", headers=auth_headers)
    assert resp_prio.status_code == 200
    assert any(g["title"] == "Goal Alpha" for g in resp_prio.get_json()["data"]["goals"])

    # Search filter
    resp_search = client.get("/api/v1/goals?search=Fitness", headers=auth_headers)
    assert resp_search.status_code == 200
    search_goals = resp_search.get_json()["data"]["goals"]
    assert len(search_goals) == 1
    assert "Fitness Target Gamma" in search_goals[0]["title"]


def test_get_and_update_goal(client, auth_headers):
    """Test retrieving and updating goal fields."""
    create_resp = client.post("/api/v1/goals", json={"title": "Original Goal Title"}, headers=auth_headers)
    goal_id = create_resp.get_json()["data"]["goal"]["id"]

    # Get goal
    get_resp = client.get(f"/api/v1/goals/{goal_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.get_json()["data"]["goal"]["title"] == "Original Goal Title"

    # Update goal
    patch_resp = client.patch(
        f"/api/v1/goals/{goal_id}",
        json={"title": "Updated Goal Title", "priority": "urgent", "status": "paused"},
        headers=auth_headers
    )
    # Note: 'urgent' is invalid priority (must be low/medium/high) -> returns 422
    assert patch_resp.status_code == 422

    # Valid update
    valid_patch = client.patch(
        f"/api/v1/goals/{goal_id}",
        json={"title": "Updated Goal Title", "priority": "high", "status": "paused"},
        headers=auth_headers
    )
    assert valid_patch.status_code == 200
    updated = valid_patch.get_json()["data"]["goal"]
    assert updated["title"] == "Updated Goal Title"
    assert updated["priority"] == "high"
    assert updated["status"] == "paused"


def test_delete_goal_cascades_milestones(client, auth_headers):
    """Test deleting a goal removes the goal and cascades to its milestones."""
    goal_resp = client.post("/api/v1/goals", json={"title": "Goal To Delete"}, headers=auth_headers)
    goal_id = goal_resp.get_json()["data"]["goal"]["id"]

    # Add milestone
    m_resp = client.post(
        f"/api/v1/goals/{goal_id}/milestones",
        json={"title": "Sub Milestone"},
        headers=auth_headers
    )
    assert m_resp.status_code == 201

    # Delete goal
    del_resp = client.delete(f"/api/v1/goals/{goal_id}", headers=auth_headers)
    assert del_resp.status_code == 200

    # Verify goal is gone
    get_resp = client.get(f"/api/v1/goals/{goal_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_milestone_creation_and_progress_calculation(client, auth_headers):
    """Test creating milestones and verifying automatic progress percentage calculation."""
    goal_resp = client.post("/api/v1/goals", json={"title": "Master Spring Boot"}, headers=auth_headers)
    goal_id = goal_resp.get_json()["data"]["goal"]["id"]

    # Goal starts with 0% progress
    assert goal_resp.get_json()["data"]["goal"]["progress_percent"] == 0.0

    # Add milestone 1
    m1_resp = client.post(
        f"/api/v1/goals/{goal_id}/milestones",
        json={"title": "Complete Core Java", "sort_order": 1},
        headers=auth_headers
    )
    assert m1_resp.status_code == 201
    m1_id = m1_resp.get_json()["data"]["milestone"]["id"]

    # Add milestone 2
    m2_resp = client.post(
        f"/api/v1/goals/{goal_id}/milestones",
        json={"title": "Build Spring Security API", "sort_order": 2},
        headers=auth_headers
    )
    assert m2_resp.status_code == 201
    m2_id = m2_resp.get_json()["data"]["milestone"]["id"]

    # With 2 incomplete milestones, progress is 0.0%
    goal_check = client.get(f"/api/v1/goals/{goal_id}", headers=auth_headers).get_json()["data"]["goal"]
    assert goal_check["progress_percent"] == 0.0
    assert goal_check["total_milestones"] == 2
    assert goal_check["completed_milestones"] == 0

    # Complete milestone 1: (1/2) * 100 = 50.0%
    complete_resp = client.patch(
        f"/api/v1/goals/{goal_id}/milestones/{m1_id}/complete",
        json={"is_completed": True},
        headers=auth_headers
    )
    assert complete_resp.status_code == 200
    updated_goal = complete_resp.get_json()["data"]["goal"]
    assert updated_goal["progress_percent"] == 50.0
    assert updated_goal["completed_milestones"] == 1

    # Complete milestone 2: (2/2) * 100 = 100.0%
    complete2_resp = client.patch(
        f"/api/v1/goals/{goal_id}/milestones/{m2_id}/complete",
        json={"is_completed": True},
        headers=auth_headers
    )
    assert complete2_resp.status_code == 200
    assert complete2_resp.get_json()["data"]["goal"]["progress_percent"] == 100.0

    # Reopen milestone 1: (1/2) * 100 = 50.0%
    reopen_resp = client.patch(
        f"/api/v1/goals/{goal_id}/milestones/{m1_id}/complete",
        json={"is_completed": False},
        headers=auth_headers
    )
    assert reopen_resp.status_code == 200
    assert reopen_resp.get_json()["data"]["goal"]["progress_percent"] == 50.0

    # Delete milestone 2: now 1 milestone total, 0 completed = 0.0%
    del_m_resp = client.delete(
        f"/api/v1/goals/{goal_id}/milestones/{m2_id}",
        headers=auth_headers
    )
    assert del_m_resp.status_code == 200
    assert del_m_resp.get_json()["data"]["goal"]["progress_percent"] == 0.0
    assert del_m_resp.get_json()["data"]["goal"]["total_milestones"] == 1


def test_cross_user_goal_protection(client, auth_headers):
    """Test that User B cannot read, update, or delete User A's goal (IDOR protection)."""
    resp = client.post("/api/v1/goals", json={"title": "User A Private Goal"}, headers=auth_headers)
    goal_id = resp.get_json()["data"]["goal"]["id"]

    # Register User B
    reg = client.post("/api/v1/auth/register", json={
        "email": "userb_goals@lifeos.internal",
        "password": "Password123!",
        "full_name": "User B Goals"
    })
    user_b_token = reg.get_json()["data"]["tokens"]["access_token"]
    user_b_headers = {"Authorization": f"Bearer {user_b_token}"}

    # User B read
    assert client.get(f"/api/v1/goals/{goal_id}", headers=user_b_headers).status_code == 403
    # User B update
    assert client.patch(f"/api/v1/goals/{goal_id}", json={"title": "Hacked"}, headers=user_b_headers).status_code == 403
    # User B delete
    assert client.delete(f"/api/v1/goals/{goal_id}", headers=user_b_headers).status_code == 403


def test_cross_user_milestone_protection(client, auth_headers):
    """Test that User B cannot access, create, or modify milestones on User A's goal."""
    resp = client.post("/api/v1/goals", json={"title": "User A Goal for Milestone Test"}, headers=auth_headers)
    goal_id = resp.get_json()["data"]["goal"]["id"]

    m_resp = client.post(
        f"/api/v1/goals/{goal_id}/milestones",
        json={"title": "Milestone A"},
        headers=auth_headers
    )
    milestone_id = m_resp.get_json()["data"]["milestone"]["id"]

    # Register User B
    reg = client.post("/api/v1/auth/register", json={
        "email": "userb_milestones@lifeos.internal",
        "password": "Password123!",
        "full_name": "User B Milestones"
    })
    user_b_token = reg.get_json()["data"]["tokens"]["access_token"]
    user_b_headers = {"Authorization": f"Bearer {user_b_token}"}

    # User B cannot create milestone on User A's goal
    assert client.post(
        f"/api/v1/goals/{goal_id}/milestones",
        json={"title": "Intruder Milestone"},
        headers=user_b_headers
    ).status_code == 403

    # User B cannot complete milestone on User A's goal
    assert client.patch(
        f"/api/v1/goals/{goal_id}/milestones/{milestone_id}/complete",
        json={"is_completed": True},
        headers=user_b_headers
    ).status_code == 403

    # User B cannot delete milestone on User A's goal
    assert client.delete(
        f"/api/v1/goals/{goal_id}/milestones/{milestone_id}",
        headers=user_b_headers
    ).status_code == 403

