import pytest
from datetime import datetime, timezone, timedelta


def test_create_planner_block_success(client, auth_headers):
    """Test creating a valid standalone planner block."""
    now = datetime.now(timezone.utc)
    start_time = (now + timedelta(hours=1)).isoformat()
    end_time = (now + timedelta(hours=2)).isoformat()

    payload = {
        "title": "Deep Work - Architecture",
        "description": "Design modular planner and calendar system",
        "start_time": start_time,
        "end_time": end_time,
        "block_type": "work",
        "status": "scheduled",
        "color_hex": "#6C63FF"
    }

    resp = client.post("/api/v1/planner/blocks", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert "block" in data
    block = data["block"]
    assert block["title"] == "Deep Work - Architecture"
    assert block["block_type"] == "work"
    assert block["status"] == "scheduled"
    assert block["color_hex"] == "#6C63FF"
    assert block["task_id"] is None


def test_create_block_with_linked_task(client, auth_headers):
    """Test creating a planner block linked to a user's task."""
    task_resp = client.post("/api/v1/tasks", json={"title": "Write Unit Tests"}, headers=auth_headers)
    task_id = task_resp.get_json()["data"]["task"]["id"]

    now = datetime.now(timezone.utc)
    start_time = (now + timedelta(hours=3)).isoformat()
    end_time = (now + timedelta(hours=4)).isoformat()

    payload = {
        "title": "Execute Task: Write Unit Tests",
        "start_time": start_time,
        "end_time": end_time,
        "block_type": "task",
        "task_id": task_id
    }

    resp = client.post("/api/v1/planner/blocks", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    block = resp.get_json()["data"]["block"]
    assert block["task_id"] == task_id
    assert block["task"]["title"] == "Write Unit Tests"


def test_create_block_with_unowned_task_rejected(client, auth_headers):
    """Test that a user cannot link another user's task (IDOR protection)."""
    # Create another user and their task
    reg = client.post("/api/v1/auth/register", json={
        "email": "user2@lifeos.internal",
        "password": "Password123!",
        "full_name": "User Two"
    })
    user2_token = reg.get_json()["data"]["tokens"]["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    task_resp = client.post("/api/v1/tasks", json={"title": "Private Task"}, headers=user2_headers)
    user2_task_id = task_resp.get_json()["data"]["task"]["id"]

    now = datetime.now(timezone.utc)
    start_time = (now + timedelta(hours=5)).isoformat()
    end_time = (now + timedelta(hours=6)).isoformat()

    # User 1 attempts to link User 2's task
    payload = {
        "title": "Steal Task",
        "start_time": start_time,
        "end_time": end_time,
        "task_id": user2_task_id
    }
    resp = client.post("/api/v1/planner/blocks", json=payload, headers=auth_headers)
    assert resp.status_code == 400
    assert "does not belong" in resp.get_json()["message"]


def test_create_block_invalid_time_range(client, auth_headers):
    """Test that end_time <= start_time is rejected."""
    now = datetime.now(timezone.utc)
    start_time = (now + timedelta(hours=2)).isoformat()
    end_time = (now + timedelta(hours=1)).isoformat()  # End before start

    payload = {
        "title": "Impossible Time",
        "start_time": start_time,
        "end_time": end_time
    }
    resp = client.post("/api/v1/planner/blocks", json=payload, headers=auth_headers)
    assert resp.status_code == 422


def test_conflict_detection_overlapping_block_rejected(client, auth_headers):
    """Test that overlapping block times for the same user trigger HTTP 409 Conflict."""
    base_time = datetime(2026, 12, 1, 9, 0, 0, tzinfo=timezone.utc)
    block1_start = base_time.isoformat()
    block1_end = (base_time + timedelta(hours=1)).isoformat()  # 09:00 - 10:00

    resp1 = client.post("/api/v1/planner/blocks", json={
        "title": "Block A",
        "start_time": block1_start,
        "end_time": block1_end
    }, headers=auth_headers)
    assert resp1.status_code == 201

    # Overlapping block: 09:30 - 10:30
    overlap_start = (base_time + timedelta(minutes=30)).isoformat()
    overlap_end = (base_time + timedelta(minutes=90)).isoformat()

    resp2 = client.post("/api/v1/planner/blocks", json={
        "title": "Conflicting Block",
        "start_time": overlap_start,
        "end_time": overlap_end
    }, headers=auth_headers)
    assert resp2.status_code == 409
    assert resp2.get_json()["code"] == "CONFLICT"


def test_adjacent_blocks_allowed(client, auth_headers):
    """Test that adjacent non-overlapping blocks (09:00-10:00 and 10:00-11:00) succeed."""
    base_time = datetime(2026, 12, 2, 9, 0, 0, tzinfo=timezone.utc)
    block1_start = base_time.isoformat()
    block1_end = (base_time + timedelta(hours=1)).isoformat()  # 09:00 - 10:00

    resp1 = client.post("/api/v1/planner/blocks", json={
        "title": "Slot 1",
        "start_time": block1_start,
        "end_time": block1_end
    }, headers=auth_headers)
    assert resp1.status_code == 201

    # Adjacent block: 10:00 - 11:00 (exact boundary touch)
    block2_start = block1_end
    block2_end = (base_time + timedelta(hours=2)).isoformat()

    resp2 = client.post("/api/v1/planner/blocks", json={
        "title": "Slot 2 Adjacent",
        "start_time": block2_start,
        "end_time": block2_end
    }, headers=auth_headers)
    assert resp2.status_code == 201


def test_conflict_check_ignores_cancelled_blocks(client, auth_headers):
    """Test that cancelled blocks do not prevent scheduling a new block at the same time."""
    base_time = datetime(2026, 12, 3, 14, 0, 0, tzinfo=timezone.utc)
    block_start = base_time.isoformat()
    block_end = (base_time + timedelta(hours=1)).isoformat()

    # Create block and mark it cancelled
    resp = client.post("/api/v1/planner/blocks", json={
        "title": "Will Cancel",
        "start_time": block_start,
        "end_time": block_end,
        "status": "cancelled"
    }, headers=auth_headers)
    assert resp.status_code == 201

    # Now create active block in the same slot
    resp2 = client.post("/api/v1/planner/blocks", json={
        "title": "Active Replacement",
        "start_time": block_start,
        "end_time": block_end,
        "status": "scheduled"
    }, headers=auth_headers)
    assert resp2.status_code == 201


def test_list_planner_blocks_with_date_range(client, auth_headers):
    """Test querying planner blocks by date range filter."""
    base_time = datetime(2026, 12, 4, 8, 0, 0, tzinfo=timezone.utc)
    for i in range(3):
        start = (base_time + timedelta(hours=i*2)).isoformat()
        end = (base_time + timedelta(hours=i*2 + 1)).isoformat()
        client.post("/api/v1/planner/blocks", json={
            "title": f"Range Block {i}",
            "start_time": start,
            "end_time": end
        }, headers=auth_headers)

    query_start = base_time.isoformat()
    query_end = (base_time + timedelta(hours=3)).isoformat()

    resp = client.get(
        f"/api/v1/planner/blocks?start_date={query_start}&end_date={query_end}",
        headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data["blocks"]) >= 1


def test_get_and_update_planner_block(client, auth_headers):
    """Test retrieving and updating block title, description, and status."""
    base_time = datetime(2026, 12, 5, 10, 0, 0, tzinfo=timezone.utc)
    resp = client.post("/api/v1/planner/blocks", json={
        "title": "Initial Title",
        "start_time": base_time.isoformat(),
        "end_time": (base_time + timedelta(hours=1)).isoformat()
    }, headers=auth_headers)
    block_id = resp.get_json()["data"]["block"]["id"]

    # Get block
    get_resp = client.get(f"/api/v1/planner/blocks/{block_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.get_json()["data"]["block"]["title"] == "Initial Title"

    # Update block
    patch_resp = client.patch(f"/api/v1/planner/blocks/{block_id}", json={
        "title": "Updated Block Title",
        "block_type": "learning"
    }, headers=auth_headers)
    assert patch_resp.status_code == 200
    updated = patch_resp.get_json()["data"]["block"]
    assert updated["title"] == "Updated Block Title"
    assert updated["block_type"] == "learning"


def test_update_block_status(client, auth_headers):
    """Test updating status to completed, skipped, cancelled."""
    base_time = datetime(2026, 12, 6, 11, 0, 0, tzinfo=timezone.utc)
    resp = client.post("/api/v1/planner/blocks", json={
        "title": "Status Test Block",
        "start_time": base_time.isoformat(),
        "end_time": (base_time + timedelta(hours=1)).isoformat()
    }, headers=auth_headers)
    block_id = resp.get_json()["data"]["block"]["id"]

    # Update to completed
    stat_resp = client.patch(
        f"/api/v1/planner/blocks/{block_id}/status",
        json={"status": "completed"},
        headers=auth_headers
    )
    assert stat_resp.status_code == 200
    assert stat_resp.get_json()["data"]["block"]["status"] == "completed"
    assert stat_resp.get_json()["data"]["block"]["is_completed"] is True


def test_delete_planner_block(client, auth_headers):
    """Test deleting a planner block."""
    base_time = datetime(2026, 12, 7, 15, 0, 0, tzinfo=timezone.utc)
    resp = client.post("/api/v1/planner/blocks", json={
        "title": "To Delete",
        "start_time": base_time.isoformat(),
        "end_time": (base_time + timedelta(hours=1)).isoformat()
    }, headers=auth_headers)
    block_id = resp.get_json()["data"]["block"]["id"]

    del_resp = client.delete(f"/api/v1/planner/blocks/{block_id}", headers=auth_headers)
    assert del_resp.status_code == 200

    # Verify not found
    get_resp = client.get(f"/api/v1/planner/blocks/{block_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_cross_user_isolation(client, auth_headers):
    """Test that User B cannot read, update, or delete User A's planner block."""
    base_time = datetime(2026, 12, 8, 9, 0, 0, tzinfo=timezone.utc)
    resp = client.post("/api/v1/planner/blocks", json={
        "title": "User A Private Block",
        "start_time": base_time.isoformat(),
        "end_time": (base_time + timedelta(hours=1)).isoformat()
    }, headers=auth_headers)
    block_id = resp.get_json()["data"]["block"]["id"]

    # Register User B
    reg = client.post("/api/v1/auth/register", json={
        "email": "userb@lifeos.internal",
        "password": "Password123!",
        "full_name": "User B"
    })
    user_b_token = reg.get_json()["data"]["tokens"]["access_token"]
    user_b_headers = {"Authorization": f"Bearer {user_b_token}"}

    # User B read
    assert client.get(f"/api/v1/planner/blocks/{block_id}", headers=user_b_headers).status_code == 403
    # User B update
    assert client.patch(f"/api/v1/planner/blocks/{block_id}", json={"title": "Hacked"}, headers=user_b_headers).status_code == 403
    # User B delete
    assert client.delete(f"/api/v1/planner/blocks/{block_id}", headers=user_b_headers).status_code == 403


def test_daily_planner_summary(client, auth_headers):
    """Test retrieving daily planner summary metrics."""
    target_date = "2026-12-09"
    start_time = f"{target_date}T09:00:00Z"
    end_time = f"{target_date}T10:30:00Z"

    client.post("/api/v1/planner/blocks", json={
        "title": "Daily Summary Task",
        "start_time": start_time,
        "end_time": end_time,
        "block_type": "work"
    }, headers=auth_headers)

    resp = client.get(f"/api/v1/planner/summary/daily?date={target_date}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["date"] == target_date
    assert data["total_blocks"] >= 1
    assert data["total_scheduled_minutes"] == 90

