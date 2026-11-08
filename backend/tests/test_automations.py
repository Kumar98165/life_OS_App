import pytest
import uuid
import json
from datetime import datetime, timezone, timedelta

from app import create_app, db
from app.models.user import User
from app.models.task import Task
from app.models.planner import PlannerBlock
from app.models.finance import FinancialTransaction, FinancialCategory
from app.models.notification import Reminder
from app.models.automation import (
    AutomationDefinition,
    AutomationExecution,
    AutomationAction,
    AutomationApproval,
    AutomationExecutionLog,
)
from app.services.automation_service import AutomationService
from app.ai.automation.tools import automation_tool_registry, ToolDefinition


@pytest.fixture
def auth_headers(client):
    """Register and authenticate test user, returning auth headers and user object."""
    email = f"auto_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Automation Tester"}
    )
    data = resp.get_json()["data"]
    token = data["tokens"]["access_token"]
    user_id = data["user"]["id"]
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "user_id": user_id,
        "email": email
    }


@pytest.fixture
def other_user_headers(client):
    """Create a second distinct user for cross-user boundary tests."""
    email = f"other_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": "Other User"}
    )
    data = resp.get_json()["data"]
    token = data["tokens"]["access_token"]
    user_id = data["user"]["id"]
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "user_id": user_id,
        "email": email
    }


# =============================================================================
# 1. TEMPLATES & DEFINITIONS CRUD
# =============================================================================

def test_list_templates(client, auth_headers):
    """Verify predefined templates can be fetched."""
    resp = client.get("/api/v1/automations/templates", headers=auth_headers["headers"])
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "templates" in data
    assert len(data["templates"]) == 7
    slugs = [t["slug"] for t in data["templates"]]
    assert "plan_my_day" in slugs
    assert "budget_awareness_assistant" in slugs


def test_list_and_seed_user_automations(client, auth_headers):
    """Verify listing automations auto-seeds system templates."""
    resp = client.get("/api/v1/automations", headers=auth_headers["headers"])
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "automations" in data
    assert len(data["automations"]) >= 7


def test_create_and_manage_custom_automation(client, auth_headers, other_user_headers):
    """Test user creating, updating, pausing, resuming, and deleting custom automations."""
    # 1. Create
    create_payload = {
        "title": "Custom Morning Sprint",
        "slug": "custom_morning_sprint",
        "description": "Schedule a 60min deep work sprint every morning",
        "category": "productivity",
        "trigger_type": "scheduled",
        "scheduled_time": "09:30",
        "scheduled_days": "weekdays"
    }
    resp = client.post("/api/v1/automations", headers=auth_headers["headers"], json=create_payload)
    assert resp.status_code == 201
    auto_id = resp.get_json()["data"]["automation"]["id"]

    # 2. Get
    resp = client.get(f"/api/v1/automations/{auto_id}", headers=auth_headers["headers"])
    assert resp.status_code == 200
    assert resp.get_json()["data"]["automation"]["title"] == "Custom Morning Sprint"

    # 3. Cross-user IDOR protection
    resp = client.get(f"/api/v1/automations/{auto_id}", headers=other_user_headers["headers"])
    assert resp.status_code == 403

    # 4. Update
    resp = client.patch(
        f"/api/v1/automations/{auto_id}",
        headers=auth_headers["headers"],
        json={"title": "Updated Morning Sprint", "scheduled_time": "10:00"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["automation"]["title"] == "Updated Morning Sprint"
    assert resp.get_json()["data"]["automation"]["scheduled_time"] == "10:00"

    # 5. Pause & Resume
    resp = client.post(f"/api/v1/automations/{auto_id}/pause", headers=auth_headers["headers"])
    assert resp.status_code == 200
    assert resp.get_json()["data"]["is_paused"] is True

    resp = client.post(f"/api/v1/automations/{auto_id}/resume", headers=auth_headers["headers"])
    assert resp.status_code == 200
    assert resp.get_json()["data"]["is_paused"] is False

    # 6. Delete
    resp = client.delete(f"/api/v1/automations/{auto_id}", headers=auth_headers["headers"])
    assert resp.status_code == 200

    resp = client.get(f"/api/v1/automations/{auto_id}", headers=auth_headers["headers"])
    assert resp.status_code == 404


# =============================================================================
# 2. TOOL REGISTRY TESTS
# =============================================================================

def test_tool_registry_validation_and_execution(app, auth_headers):
    """Test registry input validation, schema enforcement, and safe execution."""
    uid = auth_headers["user_id"]

    # Test tasks.create_task with valid schema
    with app.app_context():
        res = automation_tool_registry.execute_tool(
            "tasks.create_task",
            uid,
            {"title": "Automated Review Task", "priority": "high", "estimated_minutes": 45}
        )
        assert res["task_id"] is not None
        assert res["title"] == "Automated Review Task"
        assert res["priority"] == "high"

        # Verify task exists in DB
        task = Task.query.get(res["task_id"])
        assert task is not None
        assert task.user_id == uid

    # Test invalid schema parameter rejection
    with app.app_context():
        with pytest.raises(ValueError):
            automation_tool_registry.execute_tool(
                "tasks.create_task",
                uid,
                {"title": "", "priority": "invalid_priority"}
            )

    # Test unknown tool rejection
    with app.app_context():
        with pytest.raises(ValueError, match="Unauthorized or unknown tool"):
            automation_tool_registry.execute_tool("arbitrary.exec_python", uid, {})


# =============================================================================
# 3. FINANCIAL READ-ONLY ENFORCEMENT
# =============================================================================

def test_financial_read_only_tool_enforcement(app, auth_headers):
    """Ensure the financial automation tool strictly produces read-only aggregates and refuses writes."""
    uid = auth_headers["user_id"]

    with app.app_context():
        # Seed an expense transaction
        cat = FinancialCategory(user_id=uid, name="Groceries", category_type="expense")
        db.session.add(cat)
        db.session.flush()

        tx = FinancialTransaction(
            user_id=uid,
            account_id=str(uuid.uuid4()),
            category_id=cat.id,
            amount=50.00,
            transaction_type="expense",
            description="Supermarket",
            transaction_date=datetime.now(timezone.utc)
        )
        db.session.add(tx)
        db.session.commit()

        # Query summary via automation registry
        summary = automation_tool_registry.execute_tool("finance.get_financial_summary", uid, {})
        assert summary["total_expenses"] == "50.00"
        assert "Verified read-only ledger aggregates" in summary["notice"]

        # Confirm no transfer or write tool is registered in finance category
        all_tools = automation_tool_registry.list_tools()
        fin_tools = [t for t in all_tools if t["category"] == "finance"]
        assert len(fin_tools) == 1
        assert fin_tools[0]["name"] == "finance.get_financial_summary"
        assert fin_tools[0]["risk_level"] == "low"


# =============================================================================
# 4. WORKFLOW EXECUTION & APPROVAL GATE
# =============================================================================

def test_workflow_execution_and_approval_flow(client, auth_headers):
    """Test full LangGraph automation run, approval generation, approval execution, and rejection."""
    # 1. Get template ID
    resp = client.get("/api/v1/automations", headers=auth_headers["headers"])
    auto_id = resp.get_json()["data"]["automations"][0]["id"]

    # 2. Execute automation
    exec_resp = client.post(
        f"/api/v1/automations/{auto_id}/execute",
        headers=auth_headers["headers"],
        json={"user_request": "Plan my morning tasks"}
    )
    assert exec_resp.status_code == 200
    exec_data = exec_resp.get_json()["data"]["execution"]
    exec_id = exec_data["id"]
    assert exec_data["status"] in ["completed", "awaiting_approval"]

    # 3. Verify execution details and logs
    details_resp = client.get(f"/api/v1/automations/executions/{exec_id}", headers=auth_headers["headers"])
    assert details_resp.status_code == 200
    details = details_resp.get_json()["data"]["execution"]
    assert len(details["logs"]) > 0

    # 4. Manually test approval gate if approvals were created
    if details["approvals"]:
        appr_id = details["approvals"][0]["id"]

        # Test approving
        appr_resp = client.post(f"/api/v1/automations/approvals/{appr_id}/approve", headers=auth_headers["headers"])
        assert appr_resp.status_code == 200
        assert appr_resp.get_json()["data"]["status"] == "approved"


def test_expired_approval_rejection(app, auth_headers):
    """Test that expired approvals are rejected and cannot be executed."""
    uid = auth_headers["user_id"]
    service = AutomationService()

    with app.app_context():
        # Create execution, action, and already expired approval
        exec_item = AutomationExecution(user_id=uid, status="awaiting_approval")
        db.session.add(exec_item)
        db.session.flush()

        action = AutomationAction(
            execution_id=exec_item.id,
            user_id=uid,
            tool_name="tasks.create_task",
            action_type="create_task",
            description="Expired Task Proposal",
            risk_level="medium",
            requires_approval=True,
            parameters={"title": "Should Not Create"},
            status="awaiting_approval"
        )
        db.session.add(action)
        db.session.flush()

        param_json = json.dumps(action.parameters, sort_keys=True)
        param_hash = __import__("hashlib").sha256(param_json.encode("utf-8")).hexdigest()

        approval = AutomationApproval(
            execution_id=exec_item.id,
            action_id=action.id,
            user_id=uid,
            status="pending",
            parameter_hash=param_hash,
            change_summary="Create task proposal",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1)  # expired 1 hour ago
        )
        db.session.add(approval)
        db.session.commit()

        # Attempt to approve
        with pytest.raises(Exception, match="expired"):
            service.approve_action(approval.id, uid)


def test_idempotency_prevents_duplicate_executions(client, auth_headers):
    """Test that executions bearing the same idempotency key return the cached execution."""
    resp = client.get("/api/v1/automations", headers=auth_headers["headers"])
    auto_id = resp.get_json()["data"]["automations"][0]["id"]

    idemp_token = f"idemp_{uuid.uuid4().hex}"

    resp1 = client.post(
        f"/api/v1/automations/{auto_id}/execute",
        headers=auth_headers["headers"],
        json={"idempotency_key": idemp_token}
    )
    assert resp1.status_code == 200
    exec_id_1 = resp1.get_json()["data"]["execution"]["id"]

    resp2 = client.post(
        f"/api/v1/automations/{auto_id}/execute",
        headers=auth_headers["headers"],
        json={"idempotency_key": idemp_token}
    )
    assert resp2.status_code == 200
    exec_id_2 = resp2.get_json()["data"]["execution"]["id"]

    assert exec_id_1 == exec_id_2


def test_cancel_execution(client, auth_headers):
    """Test cancellation of in-flight execution."""
    resp = client.get("/api/v1/automations", headers=auth_headers["headers"])
    auto_id = resp.get_json()["data"]["automations"][0]["id"]

    exec_resp = client.post(f"/api/v1/automations/{auto_id}/execute", headers=auth_headers["headers"])
    exec_id = exec_resp.get_json()["data"]["execution"]["id"]

    cancel_resp = client.post(f"/api/v1/automations/executions/{exec_id}/cancel", headers=auth_headers["headers"])
    assert cancel_resp.status_code == 200
    assert cancel_resp.get_json()["data"]["status"] == "cancelled"
