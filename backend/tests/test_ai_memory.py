"""LifeOS - AI Memory System & Personal Digital Brain Unit Tests.

Covers:
- Manual memory creation, update, archive, and deletion
- Listing confirmed memories with search and category filtering
- Pending candidate suggestion lifecycle (review, edit-on-approve, reject)
- Memory personalization settings toggle and privacy
- Deterministic retrieval and scoring
- IDOR cross-user privacy boundaries
- Sensitive pattern filtering
"""
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage as LcAIMessage
from app.models.ai import AIMemory
from app.ai.memory.extractor import MemoryExtractionEngine, _is_sensitive_content, _is_trivial_message
from app.ai.memory.retriever import MemoryRetrievalEngine


def test_create_and_list_confirmed_memories(client, auth_headers):
    """Test creating a confirmed memory manually and listing it."""
    payload = {
        "memory_key": "Prefers early morning deep work",
        "memory_value": "Focus sessions best between 8 AM and 10 AM before standup.",
        "memory_type": "preference",
        "confidence": 0.95
    }
    create_resp = client.post("/api/v1/ai/memories", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    mem_data = create_resp.get_json()["data"]["memory"]
    assert mem_data["memory_key"] == payload["memory_key"]
    assert mem_data["status"] == "confirmed"
    assert mem_data["memory_type"] == "preference"

    # List confirmed
    list_resp = client.get("/api/v1/ai/memories", headers=auth_headers)
    assert list_resp.status_code == 200
    res_data = list_resp.get_json()["data"]
    assert res_data["total"] >= 1
    assert any(m["id"] == mem_data["id"] for m in res_data["memories"])

    # Filter by category
    cat_resp = client.get("/api/v1/ai/memories?category=preference", headers=auth_headers)
    assert cat_resp.status_code == 200
    assert len(cat_resp.get_json()["data"]["memories"]) >= 1

    empty_cat_resp = client.get("/api/v1/ai/memories?category=goal_decision", headers=auth_headers)
    assert empty_cat_resp.status_code == 200
    assert len(empty_cat_resp.get_json()["data"]["memories"]) == 0

    # Search keyword
    search_resp = client.get("/api/v1/ai/memories?search=deep+work", headers=auth_headers)
    assert search_resp.status_code == 200
    assert len(search_resp.get_json()["data"]["memories"]) >= 1


def test_update_and_archive_memory(client, auth_headers):
    """Test editing memory details and archiving it."""
    # 1. Create
    create_resp = client.post("/api/v1/ai/memories", json={
        "memory_key": "Favorite IDE",
        "memory_value": "Prefers VS Code with dark theme",
        "memory_type": "preference"
    }, headers=auth_headers)
    mem_id = create_resp.get_json()["data"]["memory"]["id"]

    # 2. Update
    patch_resp = client.patch(f"/api/v1/ai/memories/{mem_id}", json={
        "memory_value": "Prefers Cursor or VS Code with glass theme",
        "confidence": 0.9
    }, headers=auth_headers)
    assert patch_resp.status_code == 200
    updated = patch_resp.get_json()["data"]["memory"]
    assert "glass theme" in updated["memory_value"]
    assert updated["confidence"] == 0.9

    # 3. Archive
    archive_resp = client.post(f"/api/v1/ai/memories/{mem_id}/archive", headers=auth_headers)
    assert archive_resp.status_code == 200
    archived = archive_resp.get_json()["data"]["memory"]
    assert archived["status"] == "archived"

    # Confirmed list should no longer include archived memory
    list_resp = client.get("/api/v1/ai/memories", headers=auth_headers)
    assert not any(m["id"] == mem_id for m in list_resp.get_json()["data"]["memories"])


def test_delete_memory(client, auth_headers):
    """Test permanently deleting a memory."""
    create_resp = client.post("/api/v1/ai/memories", json={
        "memory_key": "Temporary memory",
        "memory_value": "Delete this note soon",
        "memory_type": "fact"
    }, headers=auth_headers)
    mem_id = create_resp.get_json()["data"]["memory"]["id"]

    del_resp = client.delete(f"/api/v1/ai/memories/{mem_id}", headers=auth_headers)
    assert del_resp.status_code == 200

    get_resp = client.get(f"/api/v1/ai/memories/{mem_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_pending_suggestion_approval_workflow(client, auth_headers):
    """Test candidate suggestion lifecycle: pending -> approve (with edit) -> confirmed."""
    # Direct creation of a pending memory (simulating extraction engine output)
    from app.services.ai_memory_service import AIMemoryService
    service = AIMemoryService()

    # Get user_id from token
    prof_resp = client.get("/api/v1/users/me", headers=auth_headers)
    user_id = prof_resp.get_json()["data"]["user"]["id"]

    pending_mem = service.create_memory(
        user_id=user_id,
        memory_key="Drinks Oat Milk Matcha Latte",
        memory_value="Prefers oat milk in morning beverages.",
        memory_type="preference",
        confidence=0.85,
        status="pending"
    )

    # 1. Inspect pending suggestions
    pending_resp = client.get("/api/v1/ai/memories/pending", headers=auth_headers)
    assert pending_resp.status_code == 200
    suggestions = pending_resp.get_json()["data"]["suggestions"]
    assert any(s["id"] == pending_mem.id for s in suggestions)

    # 2. Approve with custom edits
    approve_resp = client.post(
        f"/api/v1/ai/memories/{pending_mem.id}/approve",
        json={
            "memory_key": "Prefers Oat Milk Matcha",
            "memory_value": "Drinks iced matcha latte with oat milk every morning.",
            "memory_type": "routine_pattern"
        },
        headers=auth_headers
    )
    assert approve_resp.status_code == 200
    approved = approve_resp.get_json()["data"]["memory"]
    assert approved["status"] == "confirmed"
    assert approved["memory_key"] == "Prefers Oat Milk Matcha"
    assert approved["memory_type"] == "routine_pattern"

    # 3. Should no longer appear in pending
    pending_resp2 = client.get("/api/v1/ai/memories/pending", headers=auth_headers)
    assert not any(s["id"] == pending_mem.id for s in pending_resp2.get_json()["data"]["suggestions"])

    # 4. Should now appear in confirmed list
    confirmed_resp = client.get("/api/v1/ai/memories", headers=auth_headers)
    assert any(m["id"] == pending_mem.id for m in confirmed_resp.get_json()["data"]["memories"])


def test_pending_suggestion_rejection(client, auth_headers):
    """Test rejecting a pending suggestion dismisses and removes it."""
    from app.services.ai_memory_service import AIMemoryService
    service = AIMemoryService()

    prof_resp = client.get("/api/v1/users/me", headers=auth_headers)
    user_id = prof_resp.get_json()["data"]["user"]["id"]

    pending_mem = service.create_memory(
        user_id=user_id,
        memory_key="Irrelevant fact",
        memory_value="User said they saw a blue car.",
        memory_type="fact",
        confidence=0.7,
        status="pending"
    )

    reject_resp = client.post(f"/api/v1/ai/memories/{pending_mem.id}/reject", headers=auth_headers)
    assert reject_resp.status_code == 200

    # Verify gone from both pending and confirmed
    pending_resp = client.get("/api/v1/ai/memories/pending", headers=auth_headers)
    assert not any(s["id"] == pending_mem.id for s in pending_resp.get_json()["data"]["suggestions"])

    get_resp = client.get(f"/api/v1/ai/memories/{pending_mem.id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_memory_settings_toggle(client, auth_headers):
    """Test enabling and disabling memory personalization."""
    # 1. Check default settings
    get_resp = client.get("/api/v1/ai/memories/settings", headers=auth_headers)
    assert get_resp.status_code == 200
    data = get_resp.get_json()["data"]
    assert data["ai_memory_enabled"] is True

    # 2. Disable
    patch_resp = client.patch(
        "/api/v1/ai/memories/settings",
        json={"ai_memory_enabled": False},
        headers=auth_headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.get_json()["data"]["ai_memory_enabled"] is False

    # Verify reflected
    get_resp2 = client.get("/api/v1/ai/memories/settings", headers=auth_headers)
    assert get_resp2.get_json()["data"]["ai_memory_enabled"] is False

    # 3. Re-enable
    patch_resp2 = client.patch(
        "/api/v1/ai/memories/settings",
        json={"ai_memory_enabled": True},
        headers=auth_headers
    )
    assert patch_resp2.status_code == 200
    assert patch_resp2.get_json()["data"]["ai_memory_enabled"] is True


def test_retriever_respects_personalization_toggle(client, auth_headers):
    """Test that MemoryRetrievalEngine returns empty list when personalization is disabled."""
    from app.services.ai_memory_service import AIMemoryService
    service = AIMemoryService()
    retriever = MemoryRetrievalEngine()

    prof_resp = client.get("/api/v1/users/me", headers=auth_headers)
    user_id = prof_resp.get_json()["data"]["user"]["id"]

    # Ensure a confirmed memory exists
    service.create_memory(
        user_id=user_id,
        memory_key="Core Objective",
        memory_value="Preparing for AWS Certified DevOps exam",
        memory_type="goal_decision",
        status="confirmed"
    )

    # With enabled toggle: retrieved
    results_enabled = retriever.retrieve_relevant_memories(user_id=user_id, query="AWS devops study")
    assert len(results_enabled) >= 1
    assert "AWS" in results_enabled[0].memory_value

    # Turn off personalization
    client.patch("/api/v1/ai/memories/settings", json={"ai_memory_enabled": False}, headers=auth_headers)

    # With disabled toggle: empty
    results_disabled = retriever.retrieve_relevant_memories(user_id=user_id, query="AWS devops study")
    assert len(results_disabled) == 0

    # Restore
    client.patch("/api/v1/ai/memories/settings", json={"ai_memory_enabled": True}, headers=auth_headers)


def test_cross_user_isolation(client, auth_headers):
    """Test that User B cannot read, edit, approve, or delete User A's memories."""
    # User A creates memory
    create_resp = client.post("/api/v1/ai/memories", json={
        "memory_key": "Secret Project Codename",
        "memory_value": "Project Titan launches in Q4",
        "memory_type": "fact"
    }, headers=auth_headers)
    mem_id = create_resp.get_json()["data"]["memory"]["id"]

    # Register & login User B
    client.post("/api/v1/auth/register", json={
        "email": "userb_mem@example.com",
        "password": "Password123!",
        "full_name": "User B Memory"
    })
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "userb_mem@example.com",
        "password": "Password123!"
    })
    token_b = login_resp.get_json()["data"]["tokens"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B cannot read User A's memory
    get_resp = client.get(f"/api/v1/ai/memories/{mem_id}", headers=headers_b)
    assert get_resp.status_code in [403, 404]

    # User B cannot list User A's memory
    list_resp = client.get("/api/v1/ai/memories", headers=headers_b)
    assert not any(m["id"] == mem_id for m in list_resp.get_json()["data"]["memories"])

    # User B cannot update User A's memory
    patch_resp = client.patch(f"/api/v1/ai/memories/{mem_id}", json={"memory_value": "Hacked"}, headers=headers_b)
    assert patch_resp.status_code in [403, 404]

    # User B cannot delete User A's memory
    del_resp = client.delete(f"/api/v1/ai/memories/{mem_id}", headers=headers_b)
    assert del_resp.status_code in [403, 404]


def test_sensitive_pattern_filtering():
    """Test that passwords, keys, tokens, and cards are detected as sensitive."""
    assert _is_sensitive_content("My password is supersecret123") is True
    assert _is_sensitive_content("Here is the api_key: ak_test_12345") is True
    assert _is_sensitive_content("Credit card: 4111 2222 3333 4444") is True
    assert _is_sensitive_content("JWT token bearer eyJhbGciOi") is True
    assert _is_sensitive_content("I prefer working with TypeScript and React Native") is False


def test_trivial_message_filtering():
    """Test that trivial greetings and short responses are ignored by extractor."""
    assert _is_trivial_message("hi") is True
    assert _is_trivial_message("hello") is True
    assert _is_trivial_message("good morning") is True
    assert _is_trivial_message("ok") is True
    assert _is_trivial_message("I usually do my workout at 7:00 AM before starting work.") is False


def test_duplicate_and_contradiction_detection(app, client, auth_headers):
    """Test exact duplicate exclusion and contradiction detection in memory candidates."""
    from app.services.ai_memory_service import AIMemoryService
    from app.ai.memory.comparison import memory_comparison_engine
    from app.models.ai import AIMemory
    from app.models.user import User

    prof_resp = client.get("/api/v1/users/me", headers=auth_headers)
    uid = prof_resp.get_json()["data"]["user"]["id"]
    service = AIMemoryService()

    with app.app_context():
        # Seed an existing confirmed memory
        m1 = service.create_memory(
            user_id=uid,
            memory_key="AI Response Length",
            memory_value="User prefers short responses",
            memory_type="preference",
            status="confirmed"
        )

        existing_list = [m1]

        # 1. Exact duplicate check
        dup_res = memory_comparison_engine.check_duplicate_or_contradiction(
            candidate_key="AI Response Length",
            candidate_value="User prefers short responses",
            candidate_type="preference",
            existing_memories=existing_list
        )
        assert dup_res["is_duplicate"] is True
        assert dup_res["duplicate_memory_id"] == m1.id

        # 2. Contradiction check (short vs detailed)
        contra_res = memory_comparison_engine.check_duplicate_or_contradiction(
            candidate_key="AI Response Length",
            candidate_value="User now prefers detailed responses",
            candidate_type="preference",
            existing_memories=existing_list
        )
        assert contra_res["is_contradiction"] is True
        assert contra_res["contradicting_memory_id"] == m1.id

        # 3. User approves candidate and supersedes old memory
        m_pending = service.memory_repo.create_memory(
            user_id=uid,
            memory_key="AI Response Length",
            memory_value="User now prefers detailed responses",
            memory_type="preference",
            status="pending",
            embedding={"contradiction": {"contradicting_memory_id": m1.id}}
        )

        approved = service.approve_suggestion(
            memory_id=m_pending.id,
            current_user_id=uid,
            supersede_existing_id=m1.id
        )
        assert approved.status == "confirmed"
        assert approved.memory_value == "User now prefers detailed responses"

        # Verify old memory was safely archived, not destroyed or silently overwritten
        old_refreshed = service.memory_repo.get_by_id(m1.id)
        assert old_refreshed.status == "archived"


def test_false_positive_duplicate_and_contradiction_guards():
    """Verify that unrelated statements sharing common words are not marked as duplicate or contradictory."""
    from app.ai.memory.comparison import memory_comparison_engine
    from app.models.ai import AIMemory

    existing = AIMemory(
        id="mem-1",
        user_id="user-1",
        memory_key="Morning Routine",
        memory_value="Enjoys drinking black coffee in the morning",
        memory_type="routine_pattern",
        status="confirmed"
    )

    # 1. Unrelated statement that shares the word "morning" and "evening"
    # Candidate: "Prefers evening walks with the dog"
    # Neither key nor full meaning is conflicting.
    res_unrelated = memory_comparison_engine.check_duplicate_or_contradiction(
        candidate_key="Dog Walking",
        candidate_value="Prefers evening walks with the dog",
        candidate_type="routine_pattern",
        existing_memories=[existing]
    )
    assert res_unrelated["is_duplicate"] is False
    assert res_unrelated["is_contradiction"] is False

    # 2. Similar keywords but completely different meaning
    # Existing: "Prefers light roast beans for coffee"
    # Candidate: "Works in a dark room with monitor backlight"
    coffee_mem = AIMemory(
        id="mem-2",
        user_id="user-1",
        memory_key="Coffee Roasting",
        memory_value="Prefers light roast beans for coffee",
        memory_type="preference",
        status="confirmed"
    )
    res_dark = memory_comparison_engine.check_duplicate_or_contradiction(
        candidate_key="Work Environment",
        candidate_value="Works in a dark room with monitor backlight",
        candidate_type="preference",
        existing_memories=[coffee_mem]
    )
    assert res_dark["is_duplicate"] is False
    assert res_dark["is_contradiction"] is False


def test_cross_user_supersede_idor_rejected(client, auth_headers):
    """Verify a user cannot pass another user's memory ID in supersede_existing_id."""
    # Register user B
    client.post("/api/v1/auth/register", json={
        "email": "victim_mem@example.com",
        "password": "Password123!",
        "full_name": "Victim User"
    })
    login_b = client.post("/api/v1/auth/login", json={
        "email": "victim_mem@example.com",
        "password": "Password123!"
    })
    token_b = login_b.get_json()["data"]["tokens"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B creates a confirmed memory
    resp_b = client.post("/api/v1/ai/memories", json={
        "memory_key": "Victim Bank",
        "memory_value": "Important Account Info",
        "memory_type": "fact"
    }, headers=headers_b)
    victim_mem_id = resp_b.get_json()["data"]["memory"]["id"]

    # User A creates a memory manually then attempts to supersede User B's memory
    create_a = client.post("/api/v1/ai/memories", json={
        "memory_key": "Attacker Candidate",
        "memory_value": "Attempting unauthorized supersede",
        "memory_type": "fact"
    }, headers=auth_headers)
    assert create_a.status_code == 201
    mem_a_id = create_a.get_json()["data"]["memory"]["id"]

    # In pending state, attempt to approve with supersede_existing_id=victim_mem_id
    from app.services.ai_memory_service import AIMemoryService
    service = AIMemoryService()
    # Temporarily set to pending to test approval gate
    with client.application.app_context():
        mem_rec = service.memory_repo.get_by_id(mem_a_id)
        mem_rec.status = "pending"
        from app.extensions import db
        db.session.commit()

    # User A approves with supersede targeting User B
    appr_resp = client.post(f"/api/v1/ai/memories/{mem_a_id}/approve", json={
        "supersede_existing_id": victim_mem_id
    }, headers=auth_headers)

    # Must be forbidden or rejected
    assert appr_resp.status_code in [403, 404]

    # Verify User B's memory was NOT archived
    verify_b = client.get(f"/api/v1/ai/memories/{victim_mem_id}", headers=headers_b)
    assert verify_b.status_code == 200
    assert verify_b.get_json()["data"]["memory"]["status"] == "confirmed"



