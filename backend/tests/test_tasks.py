import pytest
from datetime import datetime, timezone, timedelta


def test_create_task_success(client, auth_headers):
    """Test creating a valid task with priority and due date."""
    payload = {
        "title": "Complete System Architecture",
        "description": "Design modular layered architecture for tasks",
        "priority": "high",
        "status": "pending",
        "estimated_minutes": 60
    }
    response = client.post("/api/v1/tasks", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert "task" in data
    task = data["task"]
    assert task["title"] == "Complete System Architecture"
    assert task["priority"] == "high"
    assert task["status"] == "pending"
    assert task["estimated_minutes"] == 60


def test_create_task_validation_errors(client, auth_headers):
    """Test validation errors for blank title and invalid priority."""
    # Blank title
    resp1 = client.post("/api/v1/tasks", json={"title": "   "}, headers=auth_headers)
    assert resp1.status_code == 422

    # Invalid priority
    resp2 = client.post(
        "/api/v1/tasks",
        json={"title": "Valid Title", "priority": "critical_invalid"},
        headers=auth_headers
    )
    assert resp2.status_code == 422


def test_list_tasks_and_pagination(client, auth_headers):
    """Test listing tasks with pagination meta."""
    for i in range(5):
        client.post(
            "/api/v1/tasks",
            json={"title": f"Batch Task {i}", "priority": "medium"},
            headers=auth_headers
        )

    response = client.post("/api/v1/tasks", json={"title": "Extra Task"}, headers=auth_headers)
    assert response.status_code == 201

    list_resp = client.get("/api/v1/tasks?page=1&per_page=3", headers=auth_headers)
    assert list_resp.status_code == 200
    json_data = list_resp.get_json()
    assert len(json_data["data"]["tasks"]) == 3
    assert json_data["meta"]["page"] == 1
    assert json_data["meta"]["per_page"] == 3
    assert json_data["meta"]["total"] >= 6
    assert json_data["meta"]["has_next"] is True


def test_task_filtering_and_search(client, auth_headers):
    """Test filtering by status, priority, and text search."""
    client.post(
        "/api/v1/tasks",
        json={"title": "Urgent Security Audit", "priority": "urgent", "status": "pending"},
        headers=auth_headers
    )
    client.post(
        "/api/v1/tasks",
        json={"title": "Routine Maintenance", "priority": "low", "status": "completed"},
        headers=auth_headers
    )

    # Search filter
    search_resp = client.get("/api/v1/tasks?search=Security", headers=auth_headers)
    assert search_resp.status_code == 200
    tasks = search_resp.get_json()["data"]["tasks"]
    assert any("Security" in t["title"] for t in tasks)

    # Priority filter
    prio_resp = client.get("/api/v1/tasks?priority=urgent", headers=auth_headers)
    assert prio_resp.status_code == 200
    tasks = prio_resp.get_json()["data"]["tasks"]
    assert all(t["priority"] == "urgent" for t in tasks)


def test_task_details_and_update(client, auth_headers):
    """Test getting single task and updating attributes."""
    create_resp = client.post(
        "/api/v1/tasks",
        json={"title": "Original Title", "priority": "low"},
        headers=auth_headers
    )
    task_id = create_resp.get_json()["data"]["task"]["id"]

    # Get details
    get_resp = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.get_json()["data"]["task"]["title"] == "Original Title"

    # Update
    patch_resp = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated Title", "priority": "high"},
        headers=auth_headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.get_json()["data"]["task"]["title"] == "Updated Title"
    assert patch_resp.get_json()["data"]["task"]["priority"] == "high"


def test_task_toggle_complete(client, auth_headers):
    """Test toggling task completion state and setting completed_at."""
    create_resp = client.post(
        "/api/v1/tasks",
        json={"title": "Task to complete", "status": "pending"},
        headers=auth_headers
    )
    task_id = create_resp.get_json()["data"]["task"]["id"]

    # Toggle to complete
    comp_resp = client.patch(f"/api/v1/tasks/{task_id}/complete", headers=auth_headers)
    assert comp_resp.status_code == 200
    task_data = comp_resp.get_json()["data"]["task"]
    assert task_data["status"] == "completed"
    assert task_data["completed_at"] is not None

    # Toggle back to pending
    uncomp_resp = client.patch(f"/api/v1/tasks/{task_id}/complete", headers=auth_headers)
    assert uncomp_resp.status_code == 200
    uncomp_task = uncomp_resp.get_json()["data"]["task"]
    assert uncomp_task["status"] == "pending"
    assert uncomp_task["completed_at"] is None


def test_delete_task(client, auth_headers):
    """Test deleting task."""
    create_resp = client.post(
        "/api/v1/tasks",
        json={"title": "Task to delete"},
        headers=auth_headers
    )
    task_id = create_resp.get_json()["data"]["task"]["id"]

    del_resp = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert del_resp.status_code == 200

    # Verify deleted
    get_resp = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_cross_user_ownership_enforcement(client, auth_headers):
    """Test that User B cannot access, modify, or delete User A's task (IDOR prevention)."""
    # User A creates a task
    create_resp = client.post(
        "/api/v1/tasks",
        json={"title": "User A Private Task"},
        headers=auth_headers
    )
    task_id = create_resp.get_json()["data"]["task"]["id"]

    # Register User B
    reg_b = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user_b_attacker@example.com",
            "password": "Password123",
            "full_name": "User B"
        }
    )
    token_b = reg_b.get_json()["data"]["tokens"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B attempts to read User A's task
    get_resp = client.get(f"/api/v1/tasks/{task_id}", headers=headers_b)
    assert get_resp.status_code == 403

    # User B attempts to update User A's task
    patch_resp = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Hacked Title"},
        headers=headers_b
    )
    assert patch_resp.status_code == 403

    # User B attempts to delete User A's task
    del_resp = client.delete(f"/api/v1/tasks/{task_id}", headers=headers_b)
    assert del_resp.status_code == 403


def test_unauthenticated_request_rejected(client):
    """Test that all task routes require valid JWT authorization."""
    assert client.get("/api/v1/tasks").status_code == 401
    assert client.post("/api/v1/tasks", json={"title": "Test"}).status_code == 401
    assert client.get("/api/v1/tasks/some-id").status_code == 401
    assert client.patch("/api/v1/tasks/some-id").status_code == 401
    assert client.delete("/api/v1/tasks/some-id").status_code == 401


def test_list_and_seed_categories(client, auth_headers):
    """Test listing categories and verify default categories are auto-seeded."""
    cat_resp = client.get("/api/v1/tasks/categories", headers=auth_headers)
    assert cat_resp.status_code == 200
    categories = cat_resp.get_json()["data"]["categories"]
    assert len(categories) >= 4
    cat_names = [c["name"] for c in categories]
    assert "Work" in cat_names
    assert "Health" in cat_names
    assert "Deep Work" in cat_names

