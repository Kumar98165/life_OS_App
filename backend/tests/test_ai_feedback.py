"""LifeOS - AI Feedback & Training Consent Test Suite.

Comprehensive tests covering:
- Positive feedback (+1 thumbs up)
- Negative feedback (-1 thumbs down) with categories & comments
- Feedback with suggested response corrections
- All supported categories validation
- Feedback update (PATCH)
- Feedback deletion (DELETE)
- Idempotent duplicate submissions (no duplicate rows)
- Invalid ratings rejection
- Invalid message reference (404)
- Feedback rejected on non-assistant messages (400)
- Cross-user IDOR defense (403)
- Unauthorized request handling (401)
- Training consent defaults to False
- Training consent opt-in and withdrawal
- Consent withdrawal transactionally invalidates training samples
- AI chat response exposes message_id
- Memory system backward compatibility
"""
import pytest
from unittest.mock import patch, MagicMock
from app.extensions import db
from app.models.ai import AIConversation, AIMessage, AIFeedback, AITrainingSample
from app.models.user_preference import UserPreference
from app.schemas.ai_feedback import SUPPORTED_FEEDBACK_CATEGORIES


@pytest.fixture
def test_conversation_and_messages(app, client, auth_headers):
    """Fixture creating a conversation with a user message and an assistant message."""
    with app.app_context():
        from app.models.user import User
        user = User.query.filter_by(email="architect@lifeos.internal").first()
        user_id = user.id

        conv = AIConversation(user_id=user_id, title="Test Interaction Thread")
        db.session.add(conv)
        db.session.flush()

        user_msg = AIMessage(
            conversation_id=conv.id,
            role="user",
            content="Can you summarize my tasks for today?"
        )
        assistant_msg = AIMessage(
            conversation_id=conv.id,
            role="assistant",
            content="You have 3 tasks scheduled today: Deep work, Standup, and Code review."
        )
        db.session.add_all([user_msg, assistant_msg])
        db.session.commit()

        return {
            "user_id": user_id,
            "conversation_id": conv.id,
            "user_message_id": user_msg.id,
            "assistant_message_id": assistant_msg.id,
        }


@pytest.fixture
def second_user_headers(client):
    """Registers and logs in a second user for IDOR testing."""
    payload = {
        "email": "secondary@lifeos.internal",
        "password": "Password123!",
        "full_name": "Secondary User"
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    token = resp.get_json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------
# Feedback Submission & Verification Tests
# ---------------------------------------------------------

def test_submit_positive_feedback(client, auth_headers, test_conversation_and_messages):
    """Verify submitting a thumbs-up (+1) rating on an assistant message."""
    msg_id = test_conversation_and_messages["assistant_message_id"]

    payload = {
        "message_id": msg_id,
        "rating": 1,
        "comment": "Accurate and concise!"
    }
    resp = client.post("/api/v1/ai/feedback", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()["data"]["feedback"]
    assert data["message_id"] == msg_id
    assert data["rating"] == 1
    assert data["feedback_type"] == "thumbs_up"
    assert data["comment"] == "Accurate and concise!"
    assert data["id"] is not None

    # Query by message endpoint
    msg_fb_resp = client.get(f"/api/v1/ai/messages/{msg_id}/feedback", headers=auth_headers)
    assert msg_fb_resp.status_code == 200
    assert msg_fb_resp.get_json()["data"]["feedback"]["id"] == data["id"]


def test_submit_negative_feedback_with_category(client, auth_headers, test_conversation_and_messages):
    """Verify submitting a thumbs-down (-1) rating with category and explanation."""
    msg_id = test_conversation_and_messages["assistant_message_id"]

    payload = {
        "message_id": msg_id,
        "rating": -1,
        "category": "incorrect_answer",
        "comment": "The task count was off by one."
    }
    resp = client.post("/api/v1/ai/feedback", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()["data"]["feedback"]
    assert data["rating"] == -1
    assert data["feedback_type"] == "thumbs_down"
    assert data["category"] == "incorrect_answer"
    assert data["comment"] == "The task count was off by one."


def test_submit_feedback_with_suggested_correction(client, auth_headers, test_conversation_and_messages):
    """Verify submitting user-corrected text sets feedback_type to 'correction'."""
    msg_id = test_conversation_and_messages["assistant_message_id"]

    payload = {
        "message_id": msg_id,
        "rating": -1,
        "category": "poor_explanation",
        "suggested_response": "You actually have 2 tasks: Deep work and Code review."
    }
    resp = client.post("/api/v1/ai/feedback", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()["data"]["feedback"]
    assert data["rating"] == -1
    assert data["feedback_type"] == "correction"
    assert data["suggested_response"] == "You actually have 2 tasks: Deep work and Code review."


def test_all_supported_feedback_categories(client, auth_headers, test_conversation_and_messages, app):
    """Verify that all 7 supported categories are accepted and validated."""
    conv_id = test_conversation_and_messages["conversation_id"]

    for cat in SUPPORTED_FEEDBACK_CATEGORIES:
        with app.app_context():
            # Create a separate assistant message per category test
            msg = AIMessage(conversation_id=conv_id, role="assistant", content=f"Sample message for {cat}")
            db.session.add(msg)
            db.session.commit()
            msg_id = msg.id

        payload = {
            "message_id": msg_id,
            "rating": -1,
            "category": cat
        }
        resp = client.post("/api/v1/ai/feedback", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.get_json()["data"]["feedback"]["category"] == cat


def test_update_feedback(client, auth_headers, test_conversation_and_messages):
    """Verify editing an existing feedback record via PATCH."""
    msg_id = test_conversation_and_messages["assistant_message_id"]

    # Create initial feedback
    create_resp = client.post(
        "/api/v1/ai/feedback",
        json={"message_id": msg_id, "rating": 1, "comment": "Good"},
        headers=auth_headers
    )
    fb_id = create_resp.get_json()["data"]["feedback"]["id"]

    # Update feedback
    patch_resp = client.patch(
        f"/api/v1/ai/feedback/{fb_id}",
        json={"rating": -1, "category": "outdated_context", "comment": "Changed mind, outdated info"},
        headers=auth_headers
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.get_json()["data"]["feedback"]
    assert updated["rating"] == -1
    assert updated["category"] == "outdated_context"
    assert updated["comment"] == "Changed mind, outdated info"


def test_delete_feedback(client, auth_headers, test_conversation_and_messages):
    """Verify deleting a feedback record via DELETE."""
    msg_id = test_conversation_and_messages["assistant_message_id"]

    create_resp = client.post(
        "/api/v1/ai/feedback",
        json={"message_id": msg_id, "rating": 1},
        headers=auth_headers
    )
    fb_id = create_resp.get_json()["data"]["feedback"]["id"]

    # Delete
    del_resp = client.delete(f"/api/v1/ai/feedback/{fb_id}", headers=auth_headers)
    assert del_resp.status_code == 200

    # Ensure it no longer exists
    get_resp = client.get(f"/api/v1/ai/feedback/{fb_id}", headers=auth_headers)
    assert get_resp.status_code == 404

    # Message query should now return 404
    msg_get_resp = client.get(f"/api/v1/ai/messages/{msg_id}/feedback", headers=auth_headers)
    assert msg_get_resp.status_code == 404


def test_duplicate_submission_updates_existing_record(client, auth_headers, test_conversation_and_messages, app):
    """Submitting feedback for the same message must update the record without creating duplicate rows."""
    msg_id = test_conversation_and_messages["assistant_message_id"]

    # 1. First submission
    resp1 = client.post(
        "/api/v1/ai/feedback",
        json={"message_id": msg_id, "rating": 1, "comment": "Initial thumb up"},
        headers=auth_headers
    )
    assert resp1.status_code == 201
    fb_id1 = resp1.get_json()["data"]["feedback"]["id"]

    # 2. Second submission on SAME message
    resp2 = client.post(
        "/api/v1/ai/feedback",
        json={"message_id": msg_id, "rating": -1, "comment": "Overwritten thumb down", "category": "wrong_tone"},
        headers=auth_headers
    )
    assert resp2.status_code == 200  # 200 OK because updated
    fb_id2 = resp2.get_json()["data"]["feedback"]["id"]

    assert fb_id1 == fb_id2
    assert resp2.get_json()["data"]["feedback"]["rating"] == -1
    assert resp2.get_json()["data"]["feedback"]["comment"] == "Overwritten thumb down"

    with app.app_context():
        count = AIFeedback.query.filter_by(message_id=msg_id).count()
        assert count == 1


# ---------------------------------------------------------
# Validation & Error Handling Tests
# ---------------------------------------------------------

def test_invalid_ratings_rejected(client, auth_headers, test_conversation_and_messages):
    """Verify that ratings other than +1 or -1 are rejected."""
    msg_id = test_conversation_and_messages["assistant_message_id"]

    for invalid_rating in [0, 2, -2, 5]:
        resp = client.post(
            "/api/v1/ai/feedback",
            json={"message_id": msg_id, "rating": invalid_rating},
            headers=auth_headers
        )
        assert resp.status_code in (400, 422)


def test_invalid_category_rejected(client, auth_headers, test_conversation_and_messages):
    """Verify invalid categories are rejected."""
    msg_id = test_conversation_and_messages["assistant_message_id"]

    resp = client.post(
        "/api/v1/ai/feedback",
        json={"message_id": msg_id, "rating": -1, "category": "non_existent_category"},
        headers=auth_headers
    )
    assert resp.status_code in (400, 422)


def test_feedback_on_non_existent_message(client, auth_headers):
    """Submitting feedback for a non-existent message returns 404."""
    resp = client.post(
        "/api/v1/ai/feedback",
        json={"message_id": "00000000-0000-0000-0000-000000000000", "rating": 1},
        headers=auth_headers
    )
    assert resp.status_code == 404


def test_feedback_rejected_on_user_message(client, auth_headers, test_conversation_and_messages):
    """Submitting feedback on a user-role message must be rejected with 400."""
    user_msg_id = test_conversation_and_messages["user_message_id"]

    resp = client.post(
        "/api/v1/ai/feedback",
        json={"message_id": user_msg_id, "rating": 1},
        headers=auth_headers
    )
    assert resp.status_code == 400
    assert "Feedback can only be submitted for assistant messages" in resp.get_json()["message"]


# ---------------------------------------------------------
# IDOR & Privacy Boundary Tests
# ---------------------------------------------------------

def test_cross_user_idor_prevention(client, auth_headers, second_user_headers, test_conversation_and_messages):
    """Secondary user cannot submit, view, modify, or delete primary user's feedback or messages."""
    user1_msg_id = test_conversation_and_messages["assistant_message_id"]

    # 1. User 1 submits feedback
    fb_resp = client.post(
        "/api/v1/ai/feedback",
        json={"message_id": user1_msg_id, "rating": 1, "comment": "Private feedback"},
        headers=auth_headers
    )
    fb_id = fb_resp.get_json()["data"]["feedback"]["id"]

    # 2. User 2 attempts to submit feedback on User 1's message -> 403 Forbidden
    cross_post = client.post(
        "/api/v1/ai/feedback",
        json={"message_id": user1_msg_id, "rating": -1},
        headers=second_user_headers
    )
    assert cross_post.status_code == 403

    # 3. User 2 attempts to GET User 1's feedback -> 403 Forbidden
    cross_get = client.get(f"/api/v1/ai/feedback/{fb_id}", headers=second_user_headers)
    assert cross_get.status_code == 403

    # 4. User 2 attempts to PATCH User 1's feedback -> 403 Forbidden
    cross_patch = client.patch(
        f"/api/v1/ai/feedback/{fb_id}",
        json={"rating": -1},
        headers=second_user_headers
    )
    assert cross_patch.status_code == 403

    # 5. User 2 attempts to DELETE User 1's feedback -> 403 Forbidden
    cross_del = client.delete(f"/api/v1/ai/feedback/{fb_id}", headers=second_user_headers)
    assert cross_del.status_code == 403

    # 6. User 2 attempts to query feedback for User 1's message -> 403 Forbidden
    cross_msg_get = client.get(f"/api/v1/ai/messages/{user1_msg_id}/feedback", headers=second_user_headers)
    assert cross_msg_get.status_code == 403


def test_unauthorized_requests_rejected(client, test_conversation_and_messages):
    """All endpoints require valid JWT authentication."""
    msg_id = test_conversation_and_messages["assistant_message_id"]

    assert client.get("/api/v1/ai/feedback").status_code == 401
    assert client.post("/api/v1/ai/feedback", json={"message_id": msg_id, "rating": 1}).status_code == 401
    assert client.get(f"/api/v1/ai/feedback/{msg_id}").status_code == 401
    assert client.patch(f"/api/v1/ai/feedback/{msg_id}", json={"rating": 1}).status_code == 401
    assert client.delete(f"/api/v1/ai/feedback/{msg_id}").status_code == 401
    assert client.get(f"/api/v1/ai/messages/{msg_id}/feedback").status_code == 401
    assert client.get("/api/v1/ai/learning/consent").status_code == 401
    assert client.patch("/api/v1/ai/learning/consent", json={"ai_training_consent": True}).status_code == 401


# ---------------------------------------------------------
# Training Privacy & Consent API Tests
# ---------------------------------------------------------

def test_training_consent_defaults_to_false(client, auth_headers):
    """Verify that user AI training consent defaults to False."""
    resp = client.get("/api/v1/ai/learning/consent", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["ai_training_consent"] is False
    assert "privacy_notice" in data


def test_training_consent_toggle_lifecycle(client, auth_headers):
    """Verify opting in and out of training consent."""
    # 1. Opt-in
    enable_resp = client.patch(
        "/api/v1/ai/learning/consent",
        json={"ai_training_consent": True},
        headers=auth_headers
    )
    assert enable_resp.status_code == 200
    assert enable_resp.get_json()["data"]["ai_training_consent"] is True

    # Check persistence via GET
    get_resp = client.get("/api/v1/ai/learning/consent", headers=auth_headers)
    assert get_resp.get_json()["data"]["ai_training_consent"] is True

    # 2. Opt-out
    disable_resp = client.patch(
        "/api/v1/ai/learning/consent",
        json={"ai_training_consent": False},
        headers=auth_headers
    )
    assert disable_resp.status_code == 200
    assert disable_resp.get_json()["data"]["ai_training_consent"] is False


def test_consent_withdrawal_invalidates_training_samples(client, auth_headers, test_conversation_and_messages, app):
    """When a user withdraws consent, all existing training samples are revoked, but feedback remains."""
    user_id = test_conversation_and_messages["user_id"]
    msg_id = test_conversation_and_messages["assistant_message_id"]

    # First enable consent via API
    enable_resp = client.patch(
        "/api/v1/ai/learning/consent",
        json={"ai_training_consent": True},
        headers=auth_headers
    )
    assert enable_resp.status_code == 200

    with app.app_context():
        # Submit feedback
        fb = AIFeedback(
            user_id=user_id,
            message_id=msg_id,
            rating=1,
            feedback_type="thumbs_up"
        )
        db.session.add(fb)
        db.session.flush()

        # Add candidate training samples for this user
        s1 = AITrainingSample(
            user_id=user_id,
            source_feedback_id=fb.id,
            source_message_id=msg_id,
            prompt_input="Summarize tasks",
            chosen_response="You have 3 tasks.",
            consent_status="pending",
            review_status="approved",
            quality_score=0.9
        )
        s2 = AITrainingSample(
            user_id=user_id,
            source_feedback_id=fb.id,
            source_message_id=msg_id,
            prompt_input="Check schedule",
            chosen_response="You are free at 3 PM.",
            consent_status="granted",
            review_status="approved",
            quality_score=0.95
        )
        db.session.add_all([s1, s2])
        db.session.commit()
        fb_id = fb.id

    # User withdraws consent via API
    withdraw_resp = client.patch(
        "/api/v1/ai/learning/consent",
        json={"ai_training_consent": False},
        headers=auth_headers
    )
    assert withdraw_resp.status_code == 200
    assert withdraw_resp.get_json()["data"]["ai_training_consent"] is False
    assert withdraw_resp.get_json()["data"]["samples_revoked"] == 2

    with app.app_context():
        # Check samples are now revoked
        samples = AITrainingSample.query.filter_by(user_id=user_id).all()
        assert len(samples) == 2
        for s in samples:
            assert s.consent_status == "revoked"

        # Check that user's feedback record was PRESERVED
        feedback_record = db.session.get(AIFeedback, fb_id)
        assert feedback_record is not None
        assert feedback_record.rating == 1


# ---------------------------------------------------------
# Integration & Compatibility Tests
# ---------------------------------------------------------

def test_list_feedback_with_pagination(client, auth_headers, test_conversation_and_messages, app):
    """Test pagination and rating filtering on user feedback list."""
    conv_id = test_conversation_and_messages["conversation_id"]

    with app.app_context():
        for i in range(5):
            msg = AIMessage(conversation_id=conv_id, role="assistant", content=f"Resp {i}")
            db.session.add(msg)
            db.session.flush()
            fb = AIFeedback(
                user_id=test_conversation_and_messages["user_id"],
                message_id=msg.id,
                rating=1 if i % 2 == 0 else -1,
                feedback_type="thumbs_up" if i % 2 == 0 else "thumbs_down"
            )
            db.session.add(fb)
        db.session.commit()

    # List all
    all_resp = client.get("/api/v1/ai/feedback?limit=10", headers=auth_headers)
    assert all_resp.status_code == 200
    assert all_resp.get_json()["data"]["total"] >= 5

    # Filter rating=1
    pos_resp = client.get("/api/v1/ai/feedback?rating=1", headers=auth_headers)
    assert pos_resp.status_code == 200
    for item in pos_resp.get_json()["data"]["feedback"]:
        assert item["rating"] == 1


def test_ai_chat_response_serialization_exposes_message_id(client, auth_headers):
    """Verify that chat responses include message_id and assistant_message.id for direct feedback referencing."""
    with patch("app.services.ai_service.lifeos_agent_graph.invoke") as mock_invoke:
        mock_invoke.return_value = {
            "intent": "general_chat",
            "response": "Hello! How can I help you today?",
            "memories_used": []
        }

        chat_resp = client.post(
            "/api/v1/ai/chat",
            json={"message": "Hello assistant"},
            headers=auth_headers
        )
        assert chat_resp.status_code == 200
        data = chat_resp.get_json()["data"]

        # Ensure stable message ID is exposed
        assert "message_id" in data
        assert "assistant_message" in data
        assert data["assistant_message"]["id"] == data["message_id"]

        # Immediate feedback can be posted using this exact message_id
        fb_resp = client.post(
            "/api/v1/ai/feedback",
            json={"message_id": data["message_id"], "rating": 1},
            headers=auth_headers
        )
        assert fb_resp.status_code == 201


def test_existing_ai_memory_compatibility(client, auth_headers):
    """Verify that Step 13 digital brain memory endpoints function alongside feedback."""
    mem_resp = client.post(
        "/api/v1/ai/memories",
        json={
            "memory_key": "Continuous Learning Validation",
            "memory_value": "Feedback engine operational.",
            "memory_type": "fact",
            "confidence": 1.0
        },
        headers=auth_headers
    )
    assert mem_resp.status_code == 201
    mem_id = mem_resp.get_json()["data"]["memory"]["id"]

    get_mem = client.get(f"/api/v1/ai/memories/{mem_id}", headers=auth_headers)
    assert get_mem.status_code == 200
    assert get_mem.get_json()["data"]["memory"]["memory_key"] == "Continuous Learning Validation"
