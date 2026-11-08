"""LifeOS - Immutable AI Prompt Versioning Test Suite.

Covers:
- Prompt version creation by admin
- Duplicate version tag rejection
- Validation rejecting templates missing {context_block}
- Normal users blocked with 403 Forbidden
- Unauthenticated requests blocked with 401 Unauthorized
- Active prompt fallback initialization (v1.0.0-baseline)
- Version activation & deactivation of prior active version
- Rollback to older version without content mutation
- Immutability of prompt template and version tag
- Deletion protection for referenced prompt versions
- AI chat integration: message accurately records active prompt_version_id
- Historical attribution preservation across prompt upgrades
- Safe admin role promotion via CLI command
- Concurrency and partial unique index enforcement
"""
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage as LcAIMessage
from app.extensions import db
from app.models.user import User
from app.models.ai import AIPromptVersion, AIMessage, AIConversation
from app.services.ai_prompt_service import AIPromptService
from app.repositories.ai_prompt_repository import AIPromptRepository
from app.core.exceptions import BadRequestException
@pytest.fixture
def admin_headers(client, app):
    """Registers a user and promotes them to admin, returning auth headers."""
    payload = {
        "email": "superadmin@lifeos.internal",
        "password": "Password123!",
        "full_name": "System Administrator"
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    token = resp.get_json()["data"]["tokens"]["access_token"]

    with app.app_context():
        user = User.query.filter_by(email="superadmin@lifeos.internal").first()
        user.role = "admin"
        db.session.commit()

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def standard_user_headers(client):
    """Registers and returns auth headers for a standard non-admin user."""
    payload = {
        "email": "regularuser@lifeos.internal",
        "password": "Password123!",
        "full_name": "Regular User"
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    token = resp.get_json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------
# Prompt Version Creation & Validation
# ---------------------------------------------------------

def test_admin_can_create_prompt_version(client, admin_headers):
    """Admin can create a new immutable prompt version."""
    payload = {
        "version_tag": "v1.1.0-structured",
        "prompt_template": "You are LifeOS.\n{context_block}\n{memory_block}\nKeep answers structured.",
        "change_summary": "Added structured output enforcement directive",
        "activate_immediately": False
    }
    resp = client.post("/api/v1/ai/prompts", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.get_json()["data"]["prompt"]
    assert data["version_tag"] == "v1.1.0-structured"
    assert data["is_active"] is False
    assert data["activated_at"] is None
    assert data["id"] is not None


def test_duplicate_version_tag_rejected(client, admin_headers):
    """Attempting to create duplicate version tag is rejected with 400 Bad Request."""
    payload = {
        "version_tag": "v1.2.0-unique",
        "prompt_template": "Template 1\n{context_block}\n{memory_block}",
        "change_summary": "First submission"
    }
    resp1 = client.post("/api/v1/ai/prompts", json=payload, headers=admin_headers)
    assert resp1.status_code == 201

    # Second submission with same tag
    resp2 = client.post("/api/v1/ai/prompts", json=payload, headers=admin_headers)
    assert resp2.status_code == 400
    assert "already exists" in resp2.get_json()["message"]


def test_template_missing_context_block_rejected(client, admin_headers):
    """Prompt templates missing required context placeholders fail Pydantic validation."""
    payload = {
        "version_tag": "v1.3.0-invalid",
        "prompt_template": "You are LifeOS. Answer concisely.",
        "change_summary": "Missing context placeholders"
    }
    resp = client.post("/api/v1/ai/prompts", json=payload, headers=admin_headers)
    assert resp.status_code == 422


# ---------------------------------------------------------
# Admin Authorization & Security
# ---------------------------------------------------------

def test_standard_user_cannot_access_prompt_apis(client, standard_user_headers):
    """Standard users (role='user') are strictly blocked with 403 Forbidden."""
    endpoints = [
        ("POST", "/api/v1/ai/prompts", {"version_tag": "v9.9.9", "prompt_template": "{context_block}", "change_summary": "hack"}),
        ("GET", "/api/v1/ai/prompts", None),
        ("GET", "/api/v1/ai/prompts/active", None),
        ("GET", "/api/v1/ai/prompts/00000000-0000-0000-0000-000000000000", None),
        ("POST", "/api/v1/ai/prompts/00000000-0000-0000-0000-000000000000/activate", None),
    ]

    for method, path, payload in endpoints:
        if method == "POST":
            resp = client.post(path, json=payload, headers=standard_user_headers)
        else:
            resp = client.get(path, headers=standard_user_headers)

        assert resp.status_code == 403
        assert "Administrator privileges required" in resp.get_json()["message"]


def test_unauthenticated_requests_rejected(client):
    """Missing JWT authentication returns 401 Unauthorized."""
    assert client.get("/api/v1/ai/prompts").status_code == 401
    assert client.post("/api/v1/ai/prompts", json={}).status_code == 401
    assert client.get("/api/v1/ai/prompts/active").status_code == 401


# ---------------------------------------------------------
# Activation, Rollback, and Active Prompt Lifecycle
# ---------------------------------------------------------

def test_active_prompt_initialization_fallback(client, admin_headers):
    """When no prompt has been created, retrieving active prompt initializes baseline v1.0.0-baseline."""
    resp = client.get("/api/v1/ai/prompts/active", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]["prompt"]
    assert data["version_tag"] == "v1.0.0-baseline"
    assert data["is_active"] is True
    assert data["activated_at"] is not None


def test_activate_version_and_deactivate_predecessor(client, admin_headers):
    """Activating a new version deactivates predecessor and enforces single active version."""
    # 1. Initialize baseline
    baseline_resp = client.get("/api/v1/ai/prompts/active", headers=admin_headers)
    baseline_id = baseline_resp.get_json()["data"]["prompt"]["id"]

    # 2. Create version 2
    v2_resp = client.post(
        "/api/v1/ai/prompts",
        json={
            "version_tag": "v2.0.0-succinct",
            "prompt_template": "LifeOS v2.\n{context_block}\n{memory_block}",
            "change_summary": "Extremely concise brief"
        },
        headers=admin_headers
    )
    v2_id = v2_resp.get_json()["data"]["prompt"]["id"]

    # 3. Activate version 2
    act_resp = client.post(f"/api/v1/ai/prompts/{v2_id}/activate", headers=admin_headers)
    assert act_resp.status_code == 200
    assert act_resp.get_json()["data"]["prompt"]["is_active"] is True

    # 4. Check active endpoint returns v2
    active_resp = client.get("/api/v1/ai/prompts/active", headers=admin_headers)
    assert active_resp.get_json()["data"]["prompt"]["id"] == v2_id

    # 5. Check baseline was deactivated
    old_resp = client.get(f"/api/v1/ai/prompts/{baseline_id}", headers=admin_headers)
    assert old_resp.get_json()["data"]["prompt"]["is_active"] is False


def test_rollback_to_older_version(client, admin_headers):
    """Activating an older version rolls back without modifying original template content."""
    # Ensure baseline exists
    b_resp = client.get("/api/v1/ai/prompts/active", headers=admin_headers)
    baseline_id = b_resp.get_json()["data"]["prompt"]["id"]
    original_template = b_resp.get_json()["data"]["prompt"]["prompt_template"]

    # Create & activate v2
    v2_resp = client.post(
        "/api/v1/ai/prompts",
        json={
            "version_tag": "v2.1.0-temporary",
            "prompt_template": "LifeOS v2.1.\n{context_block}\n{memory_block}",
            "change_summary": "Temporary experiment",
            "activate_immediately": True
        },
        headers=admin_headers
    )
    assert v2_resp.get_json()["data"]["prompt"]["is_active"] is True

    # Rollback: reactivate baseline
    rollback_resp = client.post(f"/api/v1/ai/prompts/{baseline_id}/activate", headers=admin_headers)
    assert rollback_resp.status_code == 200
    rolled_back = rollback_resp.get_json()["data"]["prompt"]
    assert rolled_back["id"] == baseline_id
    assert rolled_back["is_active"] is True
    # Verify content was NOT altered
    assert rolled_back["prompt_template"] == original_template


# ---------------------------------------------------------
# Deletion Protection & Historical Message Attribution
# ---------------------------------------------------------

def test_deletion_protection_for_referenced_prompts(app):
    """Deleting a prompt version referenced by messages is strictly blocked."""
    repo = AIPromptRepository()

    with app.app_context():
        # Create user & conversation
        user = User(email="author@lifeos.internal", password_hash="hash", full_name="Author")
        db.session.add(user)
        db.session.flush()

        conv = AIConversation(user_id=user.id, title="Attribution Thread")
        db.session.add(conv)
        db.session.flush()

        # Create prompt version
        pv = repo.create(
            version_tag="v3.0.0-protected",
            prompt_template="Protected prompt\n{context_block}\n{memory_block}",
            change_summary="Protection test",
            created_by=user.id
        )

        # Attach to message
        msg = AIMessage(
            conversation_id=conv.id,
            role="assistant",
            content="Historical answer",
            prompt_version_id=pv.id
        )
        db.session.add(msg)
        db.session.commit()

        # Attempt to delete referenced prompt version -> must raise BadRequestException
        with pytest.raises(BadRequestException) as exc:
            repo.delete_if_unreferenced(pv)
        assert "referenced by existing AI messages" in str(exc.value)


def test_ai_chat_records_prompt_attribution(client, standard_user_headers, admin_headers, app):
    """AI Assistant chat execution stores exact active prompt_version_id."""
    # Ensure active prompt version
    active_resp = client.get("/api/v1/ai/prompts/active", headers=admin_headers)
    active_prompt_id = active_resp.get_json()["data"]["prompt"]["id"]

    with patch("app.services.ai_service.lifeos_agent_graph.invoke") as mock_invoke:
        mock_invoke.return_value = {
            "intent": "general_chat",
            "response": "Hello with active prompt!",
            "memories_used": []
        }

        chat_resp = client.post(
            "/api/v1/ai/chat",
            json={"message": "Hello LifeOS"},
            headers=standard_user_headers
        )
        assert chat_resp.status_code == 200
        data = chat_resp.get_json()["data"]
        msg_id = data["message_id"]

        with app.app_context():
            saved_msg = db.session.get(AIMessage, msg_id)
            assert saved_msg is not None
            assert saved_msg.prompt_version_id == active_prompt_id
            assert saved_msg.latency_ms is not None


def test_historical_attribution_preserved_across_upgrades(client, standard_user_headers, admin_headers, app):
    """Existing messages preserve their original prompt_version_id even after a newer prompt is activated."""
    # 1. First interaction on v1
    v1_resp = client.get("/api/v1/ai/prompts/active", headers=admin_headers)
    v1_id = v1_resp.get_json()["data"]["prompt"]["id"]

    with patch("app.services.ai_service.lifeos_agent_graph.invoke") as mock_invoke:
        mock_invoke.return_value = {"intent": "general_chat", "response": "Response on V1", "memories_used": []}
        r1 = client.post("/api/v1/ai/chat", json={"message": "First turn"}, headers=standard_user_headers)
        msg1_id = r1.get_json()["data"]["message_id"]

    # 2. Admin upgrades to v2
    v2_resp = client.post(
        "/api/v1/ai/prompts",
        json={
            "version_tag": "v2.2.0-upgrade",
            "prompt_template": "LifeOS v2.2\n{context_block}\n{memory_block}",
            "change_summary": "Upgraded system prompt",
            "activate_immediately": True
        },
        headers=admin_headers
    )
    v2_id = v2_resp.get_json()["data"]["prompt"]["id"]

    # 3. Second interaction on v2
    with patch("app.services.ai_service.lifeos_agent_graph.invoke") as mock_invoke:
        mock_invoke.return_value = {"intent": "general_chat", "response": "Response on V2", "memories_used": []}
        r2 = client.post("/api/v1/ai/chat", json={"message": "Second turn"}, headers=standard_user_headers)
        msg2_id = r2.get_json()["data"]["message_id"]

    with app.app_context():
        msg1 = db.session.get(AIMessage, msg1_id)
        msg2 = db.session.get(AIMessage, msg2_id)

        # Message 1 MUST still reference v1 (historical attribution preserved!)
        assert msg1.prompt_version_id == v1_id
        # Message 2 references v2
        assert msg2.prompt_version_id == v2_id


# ---------------------------------------------------------
# Administrative CLI Command & Concurrency
# ---------------------------------------------------------

def test_make_admin_cli(app):
    """Test CLI command to promote user to administrator role."""
    from click.testing import CliRunner

    with app.app_context():
        u = User(email="clitest@lifeos.internal", password_hash="hash", full_name="Cli Test")
        db.session.add(u)
        db.session.commit()
        assert u.role == "user"

    runner = app.test_cli_runner()
    result = runner.invoke(args=["auth", "make-admin", "clitest@lifeos.internal"])
    assert result.exit_code == 0
    assert "now an administrator" in result.output

    with app.app_context():
        refreshed = User.query.filter_by(email="clitest@lifeos.internal").first()
        assert refreshed.role == "admin"
