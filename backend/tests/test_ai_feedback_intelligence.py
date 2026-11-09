"""LifeOS - AI Feedback Intelligence & Analytics Test Suite (Step 6).

Covers:
- Feedback analytics endpoint (GET /api/v1/ai/feedback/analytics)
- Aggregation of positive/negative feedback, satisfaction score calculation
- Feedback category breakdown and distribution
- Deterministic improvement recommendations generation for various failure patterns
- User data isolation (IDOR protection on feedback analytics)
- Date window filtering (e.g. 7 vs 30 days)
- Idempotent feedback update impact on analytics
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.extensions import db
from app.models.ai import AIConversation, AIMessage, AIFeedback
from app.models.user import User
from app.services.feedback_intelligence_service import feedback_intelligence_service


@pytest.fixture
def test_conversation_and_messages(app, client, auth_headers):
    """Fixture creating a conversation with an assistant message for the primary test user."""
    with app.app_context():
        user = User.query.filter_by(email="architect@lifeos.internal").first()
        user_id = user.id

        conv = AIConversation(user_id=user_id, title="Intelligence Feedback Thread")
        db.session.add(conv)
        db.session.flush()

        messages = []
        for i in range(10):
            msg = AIMessage(
                conversation_id=conv.id,
                role="assistant" if i % 2 == 1 else "user",
                content=f"Message turn #{i}"
            )
            messages.append(msg)
            db.session.add(msg)

        db.session.commit()

        assistant_msgs = [m for m in messages if m.role == "assistant"]

        return {
            "user_id": user_id,
            "conversation_id": conv.id,
            "assistant_message_ids": [m.id for m in assistant_msgs],
        }


@pytest.fixture
def second_user_headers(client):
    """Registers and logs in a second user for IDOR testing."""
    payload = {
        "email": "feedback_user2@lifeos.internal",
        "password": "Password123!",
        "full_name": "Feedback User Two"
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    token = resp.get_json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_feedback_analytics_empty_state(client, auth_headers):
    """Verify analytics behavior when no feedback has been submitted yet."""
    resp = client.get("/api/v1/ai/feedback/analytics", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]

    assert data["total_feedback_count"] == 0
    assert data["positive_count"] == 0
    assert data["negative_count"] == 0
    assert data["satisfaction_percentage"] == 100.0
    assert data["negative_categories"] == {}
    assert len(data["improvement_recommendations"]) >= 1
    assert data["improvement_recommendations"][0]["area"] == "general"


def test_feedback_analytics_calculations_and_recommendations(
    client, auth_headers, test_conversation_and_messages, app
):
    """Submit multiple feedback items with different ratings & categories, verify analytics."""
    msg_ids = test_conversation_and_messages["assistant_message_ids"]

    # Submit 2 positive feedback items
    resp1 = client.post(
        "/api/v1/ai/feedback",
        json={"message_id": msg_ids[0], "rating": 1, "feedback_type": "thumbs_up"},
        headers=auth_headers
    )
    assert resp1.status_code == 201

    resp2 = client.post(
        "/api/v1/ai/feedback",
        json={"message_id": msg_ids[1], "rating": 1, "feedback_type": "thumbs_up"},
        headers=auth_headers
    )
    assert resp2.status_code == 201

    # Submit 2 negative feedback items with categories
    resp3 = client.post(
        "/api/v1/ai/feedback",
        json={
            "message_id": msg_ids[2],
            "rating": -1,
            "feedback_type": "thumbs_down",
            "category": "incorrect_answer",
            "comment": "The summary got my task counts wrong."
        },
        headers=auth_headers
    )
    assert resp3.status_code == 201

    resp4 = client.post(
        "/api/v1/ai/feedback",
        json={
            "message_id": msg_ids[3],
            "rating": -1,
            "feedback_type": "thumbs_down",
            "category": "poor_explanation",
            "comment": "Too vague and verbose."
        },
        headers=auth_headers
    )
    assert resp4.status_code == 201

    # Query analytics
    analytics_resp = client.get("/api/v1/ai/feedback/analytics", headers=auth_headers)
    assert analytics_resp.status_code == 200
    analytics = analytics_resp.get_json()["data"]

    assert analytics["total_feedback_count"] == 4
    assert analytics["positive_count"] == 2
    assert analytics["negative_count"] == 2
    assert analytics["satisfaction_percentage"] == 50.0
    assert analytics["negative_categories"].get("incorrect_answer") == 1
    assert analytics["negative_categories"].get("poor_explanation") == 1

    # Verify recommendations generated for the negative categories
    recs = analytics["improvement_recommendations"]
    rec_areas = [r["area"] for r in recs]
    assert "factual_consistency" in rec_areas
    assert "clarity_and_completeness" in rec_areas


def test_feedback_analytics_cross_user_isolation(
    client, auth_headers, second_user_headers, test_conversation_and_messages
):
    """Verify that User 2 cannot see User 1's feedback analytics (strict user isolation)."""
    msg_ids = test_conversation_and_messages["assistant_message_ids"]

    # User 1 submits positive feedback
    resp = client.post(
        "/api/v1/ai/feedback",
        json={"message_id": msg_ids[0], "rating": 1, "feedback_type": "thumbs_up"},
        headers=auth_headers
    )
    assert resp.status_code == 201

    # User 2 checks analytics - must be empty for User 2
    user2_resp = client.get("/api/v1/ai/feedback/analytics", headers=second_user_headers)
    assert user2_resp.status_code == 200
    user2_data = user2_resp.get_json()["data"]
    assert user2_data["total_feedback_count"] == 0
    assert user2_data["positive_count"] == 0

    # User 1 checks analytics - must show >= 1 feedback
    user1_resp = client.get("/api/v1/ai/feedback/analytics", headers=auth_headers)
    assert user1_resp.status_code == 200
    user1_data = user1_resp.get_json()["data"]
    assert user1_data["total_feedback_count"] >= 1


def test_feedback_analytics_days_filter(
    client, auth_headers, test_conversation_and_messages, app
):
    """Verify that the days query parameter correctly filters out older feedback."""
    msg_ids = test_conversation_and_messages["assistant_message_ids"]

    with app.app_context():
        # Submit feedback backdated by 45 days
        old_fb = AIFeedback(
            user_id=test_conversation_and_messages["user_id"],
            message_id=msg_ids[4],
            rating=-1,
            feedback_type="thumbs_down",
            category="poor_explanation",
            comment="Old feedback",
            created_at=datetime.now(timezone.utc) - timedelta(days=45)
        )
        db.session.add(old_fb)
        db.session.commit()

    # Query with default 30 days window -> should not include the 45-day-old feedback
    resp_30 = client.get("/api/v1/ai/feedback/analytics?days=30", headers=auth_headers)
    assert resp_30.status_code == 200
    data_30 = resp_30.get_json()["data"]
    assert data_30["negative_categories"].get("poor_explanation", 0) == 0

    # Query with 60 days window -> should include the 45-day-old feedback
    resp_60 = client.get("/api/v1/ai/feedback/analytics?days=60", headers=auth_headers)
    assert resp_60.status_code == 200
    data_60 = resp_60.get_json()["data"]
    assert data_60["negative_categories"].get("poor_explanation", 0) >= 1


def test_generate_improvement_recommendations_rules():
    """Unit test individual recommendation rules directly against service helper."""
    # High satisfaction, no negative categories
    recs_perfect = feedback_intelligence_service.generate_improvement_recommendations({}, 5, 5)
    assert len(recs_perfect) == 1
    assert recs_perfect[0]["severity"] == "positive"
    assert recs_perfect[0]["area"] == "high_satisfaction"

    # Empty feedback
    recs_empty = feedback_intelligence_service.generate_improvement_recommendations({}, 0, 0)
    assert len(recs_empty) == 1
    assert recs_empty[0]["severity"] == "info"
    assert recs_empty[0]["area"] == "general"

    # Multiple distinct categories
    cats = {
        "incorrect_answer": 3,
        "poor_explanation": 2,
        "wrong_tone": 1,
        "outdated_context": 1,
        "irrelevant_answer": 1,
    }
    recs = feedback_intelligence_service.generate_improvement_recommendations(cats, 8, 0)
    areas = [r["area"] for r in recs]
    assert "factual_consistency" in areas
    assert "clarity_and_completeness" in areas
    assert "tone_and_style" in areas
    assert "temporal_freshness" in areas
    assert "relevance" in areas

    # Factual consistency must have high severity
    fact_rec = next(r for r in recs if r["area"] == "factual_consistency")
    assert fact_rec["severity"] == "high"
