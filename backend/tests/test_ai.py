"""LifeOS - AI Personal Assistant and LangGraph Integration Tests."""
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage as LcAIMessage


def test_ai_health_endpoint(client):
    """Test AI health check endpoint returns status information."""
    resp = client.get("/api/v1/ai/health")
    assert resp.status_code in [200, 503]
    data = resp.get_json()["data"]
    assert "healthy" in data
    assert "model" in data
    assert "base_url" in data
def test_create_and_list_conversations(client, auth_headers):
    """Test creating conversation and listing user conversations."""
    create_resp = client.post(
        "/api/v1/ai/conversations",
        json={"title": "Weekly Planning Thread"},
        headers=auth_headers
    )
    assert create_resp.status_code == 201
    conv = create_resp.get_json()["data"]["conversation"]
    assert conv["title"] == "Weekly Planning Thread"
    assert "id" in conv

    list_resp = client.get("/api/v1/ai/conversations", headers=auth_headers)
    assert list_resp.status_code == 200
    convs = list_resp.get_json()["data"]["conversations"]
    assert any(c["id"] == conv["id"] for c in convs)


def test_chat_validation_errors(client, auth_headers):
    """Test that blank or empty chat messages are rejected."""
    resp1 = client.post("/api/v1/ai/chat", json={"message": "   "}, headers=auth_headers)
    assert resp1.status_code == 422

    resp2 = client.post("/api/v1/ai/chat", json={}, headers=auth_headers)
    assert resp2.status_code == 422


@patch("app.ai.workflow.get_llm")
def test_chat_turn_mocked_execution(mock_get_llm, client, auth_headers):
    """Test full chat turn with mocked LLM: creates conversation and persists messages."""
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = LcAIMessage(
        content="You have 2 pending tasks and 1 goal in progress today."
    )
    mock_get_llm.return_value = mock_llm

    payload = {"message": "What should I focus on today?"}
    resp = client.post("/api/v1/ai/chat", json=payload, headers=auth_headers)
    assert resp.status_code == 200

    data = resp.get_json()["data"]
    assert "conversation_id" in data
    assert "response" in data
    assert "You have 2 pending tasks" in data["response"]
    assert data["intent"] in ["tasks_inquiry", "daily_overview", "general_chat", "schedule_inquiry"]
    assert data["user_message"]["role"] == "user"
    assert data["assistant_message"]["role"] == "assistant"

    conv_id = data["conversation_id"]

    # Verify conversation history has both messages
    hist_resp = client.get(f"/api/v1/ai/conversations/{conv_id}", headers=auth_headers)
    assert hist_resp.status_code == 200
    hist_data = hist_resp.get_json()["data"]
    assert len(hist_data["messages"]) == 2
    assert hist_data["messages"][0]["role"] == "user"
    assert hist_data["messages"][1]["role"] == "assistant"


@patch("app.ai.workflow.get_llm")
def test_chat_multi_turn_continuity(mock_get_llm, client, auth_headers):
    """Test sending a follow-up message to the same conversation thread."""
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = [
        LcAIMessage(content="First response"),
        LcAIMessage(content="Second response with context"),
    ]
    mock_get_llm.return_value = mock_llm

    # Turn 1
    resp1 = client.post("/api/v1/ai/chat", json={"message": "Hello LifeOS"}, headers=auth_headers)
    assert resp1.status_code == 200
    conv_id = resp1.get_json()["data"]["conversation_id"]

    # Turn 2
    resp2 = client.post(
        "/api/v1/ai/chat",
        json={"message": "Can you elaborate?", "conversation_id": conv_id},
        headers=auth_headers
    )
    assert resp2.status_code == 200
    assert resp2.get_json()["data"]["conversation_id"] == conv_id

    # Verify history contains 4 messages (2 user + 2 assistant)
    hist_resp = client.get(f"/api/v1/ai/conversations/{conv_id}", headers=auth_headers)
    assert len(hist_resp.get_json()["data"]["messages"]) == 4


def test_delete_conversation(client, auth_headers):
    """Test deleting conversation and cascade-deleting its messages."""
    create_resp = client.post(
        "/api/v1/ai/conversations",
        json={"title": "Delete Me"},
        headers=auth_headers
    )
    conv_id = create_resp.get_json()["data"]["conversation"]["id"]

    del_resp = client.delete(f"/api/v1/ai/conversations/{conv_id}", headers=auth_headers)
    assert del_resp.status_code == 200

    get_resp = client.get(f"/api/v1/ai/conversations/{conv_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_cross_user_isolation(client, auth_headers):
    """Test that User B cannot read, chat in, or delete User A's conversation."""
    # User A creates conversation
    create_resp = client.post(
        "/api/v1/ai/conversations",
        json={"title": "User A Private Chat"},
        headers=auth_headers
    )
    conv_id = create_resp.get_json()["data"]["conversation"]["id"]

    # Register and authenticate User B
    client.post("/api/v1/auth/register", json={
        "email": "userb_ai@example.com",
        "password": "Password123!",
        "full_name": "User B"
    })
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "userb_ai@example.com",
        "password": "Password123!"
    })
    token_b = login_resp.get_json()["data"]["tokens"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B cannot access User A's conversation
    get_resp = client.get(f"/api/v1/ai/conversations/{conv_id}", headers=headers_b)
    assert get_resp.status_code in [403, 404]

    # User B cannot chat into User A's conversation
    chat_resp = client.post(
        "/api/v1/ai/chat",
        json={"message": "Sneaky message", "conversation_id": conv_id},
        headers=headers_b
    )
    assert chat_resp.status_code in [403, 404]

    # User B cannot delete User A's conversation
    del_resp = client.delete(f"/api/v1/ai/conversations/{conv_id}", headers=headers_b)
    assert del_resp.status_code in [403, 404]


def test_live_local_ollama_integration(client, auth_headers):
    """Actual live integration test calling the real local Qwen model via Ollama."""
    health_resp = client.get("/api/v1/ai/health")
    data = health_resp.get_json()["data"]
    if not data.get("healthy") or not data.get("model_available"):
        pytest.skip("Local Ollama runtime or target model not currently reachable")

    payload = {"message": "Hello! Reply with exactly 'LifeOS Online'"}
    resp = client.post("/api/v1/ai/chat", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    res_data = resp.get_json()["data"]
    assert "response" in res_data
    assert len(res_data["response"]) > 0

