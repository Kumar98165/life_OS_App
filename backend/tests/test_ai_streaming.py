"""LifeOS - AI Chat SSE Streaming Test Suite.

Verifies:
- Authenticated SSE connection (`/api/v1/ai/chat/stream`)
- Proper Content-Type (`text/event-stream`)
- Emitted event sequence: start -> token(s) -> complete
- Error handling on unauthenticated or empty prompt
- Cross-user conversation protection on streaming endpoint
- Database message persistence following stream completion
- Backward compatibility with existing synchronous `/api/v1/ai/chat` endpoint
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from app.models.ai import AIConversation, AIMessage
from app.models.user import User
from app.extensions import db


def test_ai_chat_stream_unauthenticated(client):
    """Verify unauthorized requests are rejected immediately with 401."""
    resp = client.post("/api/v1/ai/chat/stream", json={"message": "Hello"})
    assert resp.status_code == 401


def test_ai_chat_stream_empty_message(client, auth_headers):
    """Verify empty message is rejected by Pydantic validation with 422 before stream begins."""
    resp = client.post("/api/v1/ai/chat/stream", json={"message": "   "}, headers=auth_headers)
    assert resp.status_code == 422
    json_data = resp.get_json()
    assert json_data["success"] is False
    assert "validation" in json_data["message"].lower()


def test_ai_chat_stream_successful_flow(client, auth_headers):
    """Verify complete streaming sequence: start -> token -> complete."""
    mock_chunks = [
        MagicMock(content="Good"),
        MagicMock(content=" morning!"),
        MagicMock(content=" You have"),
        MagicMock(content=" 2 tasks"),
        MagicMock(content=" today.")
    ]
    mock_llm = MagicMock()
    mock_llm.stream.return_value = iter(mock_chunks)

    with patch("app.ai.config.get_llm", return_value=mock_llm):
        resp = client.post(
            "/api/v1/ai/chat/stream",
            json={"message": "What is on my schedule today?"},
            headers=auth_headers
        )

        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers.get("Content-Type", "")
        stream_text = resp.get_data(as_text=True)

        # 1. Start event
        assert "event: start" in stream_text
        assert "conversation_id" in stream_text

        # 2. Token events
        assert "event: token" in stream_text
        assert '"content": "Good"' in stream_text
        assert '"content": " morning!"' in stream_text
        assert '"content": " today."' in stream_text

        # 3. Complete event
        assert "event: complete" in stream_text
        assert "message_id" in stream_text


def test_ai_chat_stream_cross_user_isolation(client, auth_headers):
    """Verify User B cannot stream messages into User A's conversation."""
    # 1. Create conversation for User A
    conv_resp = client.post("/api/v1/ai/conversations", json={"title": "User A Chat"}, headers=auth_headers)
    conv_id = conv_resp.get_json()["data"]["conversation"]["id"]

    # 2. Register User B
    reg_b = client.post("/api/v1/auth/register", json={
        "email": "user_b_stream@lifeos.io",
        "password": "Password123!",
        "full_name": "User B Stream"
    })
    token_b = reg_b.get_json()["data"]["tokens"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. User B attempts to stream into User A's conversation
    resp = client.post(
        "/api/v1/ai/chat/stream",
        json={"message": "Stealing context", "conversation_id": conv_id},
        headers=headers_b
    )
    assert resp.status_code == 200
    data = resp.get_data(as_text=True)
    assert "event: error" in data
    # Resource ownership check blocks User B
    assert "FORBIDDEN" in data or "SETUP_ERROR" in data or "permission" in data.lower()


def test_ai_chat_stream_persists_messages(client, auth_headers, app):
    """Verify both user message and completed assistant message are persisted."""
    mock_chunks = [MagicMock(content="Plan your"), MagicMock(content=" deep work.")]
    mock_llm = MagicMock()
    mock_llm.stream.return_value = iter(mock_chunks)

    with patch("app.ai.config.get_llm", return_value=mock_llm):
        resp = client.post(
            "/api/v1/ai/chat/stream",
            json={"message": "Help me focus"},
            headers=auth_headers
        )
        stream_text = resp.get_data(as_text=True)

        # Extract conversation id from start event
        conv_id = None
        for line in stream_text.splitlines():
            if line.startswith("data:") and "conversation_id" in line:
                parsed = json.loads(line.replace("data:", "").strip())
                conv_id = parsed.get("conversation_id")
                if conv_id:
                    break

        assert conv_id is not None

        # Verify DB records
        with app.app_context():
            messages = AIMessage.query.filter_by(conversation_id=conv_id).order_by(AIMessage.created_at.asc()).all()
            assert len(messages) >= 2
            assert messages[0].role == "user"
            assert messages[0].content == "Help me focus"
            assert messages[1].role == "assistant"
            assert messages[1].content == "Plan your deep work."


def test_existing_synchronous_chat_backward_compatibility(client, auth_headers):
    """Ensure existing POST /api/v1/ai/chat continues to return JSON payload unchanged."""
    from langchain_core.messages import AIMessage as LcAIMessage

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = LcAIMessage(content="Synchronous response preserved.")

    with patch("app.ai.workflow.get_llm", return_value=mock_llm):
        resp = client.post(
            "/api/v1/ai/chat",
            json={"message": "Sync test"},
            headers=auth_headers
        )
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert json_data["success"] is True
        assert json_data["data"]["response"] == "Synchronous response preserved."
        assert "conversation_id" in json_data["data"]

