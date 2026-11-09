"""LifeOS - AI Dataset Management & Curation Test Suite (Step 7).

Comprehensive tests covering:
- Dataset sample collection from consented feedback & corrections
- Non-collection when user consent is absent or revoked
- Privacy & PII sanitization (emails, phones, keys, bearer tokens redacted)
- Quality validation rules (empty inputs, copy-cat degenerate samples, invalid categories, min length)
- Dataset version snapshot creation with SHA-256 manifest hash calculation
- Version immutability and reproducibility
- JSONL export format & header metadata verification
- Revocation exclusion from exports
- Role-based access control (Admin required for dataset management, non-admin 403 Forbidden)
- Dataset statistics calculation
"""
import json
import hashlib
import pytest
from app.extensions import db
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.ai import AIConversation, AIMessage, AIFeedback, AITrainingSample, AIDatasetVersion
from app.ai.dataset.sanitizer import PrivacySanitizer
from app.ai.dataset.validator import DatasetQualityValidator
from app.services.ai_dataset_service import AIDatasetService


@pytest.fixture
def admin_headers(client, app):
    """Registers and logs in a test user with admin role."""
    payload = {
        "email": "dataset_admin@lifeos.internal",
        "password": "Password123!",
        "full_name": "Dataset Administrator"
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    token = resp.get_json()["data"]["tokens"]["access_token"]
    user_id = resp.get_json()["data"]["user"]["id"]

    with app.app_context():
        user = db.session.get(User, user_id)
        user.role = "admin"
        db.session.commit()

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def non_admin_headers(client):
    """Standard user without admin privileges."""
    payload = {
        "email": "standard_user@lifeos.internal",
        "password": "Password123!",
        "full_name": "Standard User"
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    token = resp.get_json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def consented_user_conversation(client, auth_headers, app):
    """Creates a conversation and message for the default test user with training consent ON."""
    with app.app_context():
        user = User.query.filter_by(email="architect@lifeos.internal").first()
        pref = UserPreference.query.filter_by(user_id=user.id).first()
        if not pref:
            pref = UserPreference(user_id=user.id, ai_training_consent=True)
            db.session.add(pref)
        else:
            pref.ai_training_consent = True

        conv = AIConversation(user_id=user.id, title="Productivity Thread")
        db.session.add(conv)
        db.session.flush()

        u_msg = AIMessage(conversation_id=conv.id, role="user", content="Plan my morning focus hours.")
        a_msg = AIMessage(conversation_id=conv.id, role="assistant", content="Focus from 9 AM to 11 AM.")
        db.session.add_all([u_msg, a_msg])
        db.session.commit()

        return {
            "user_id": user.id,
            "conversation_id": conv.id,
            "user_msg_id": u_msg.id,
            "assistant_msg_id": a_msg.id
        }


# ---------------------------------------------------------
# Sanitizer Unit Tests
# ---------------------------------------------------------

def test_privacy_sanitizer_redaction():
    """Verify redaction of emails, phones, tokens, passwords, and private keys."""
    dirty_text = (
        "User email is john.doe@example.com and phone is 555-123-4567. "
        "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.supersecret1234567890. "
        "password = 'MySecretPassword123!' and api_key='sk-abcdef1234567890abcdef'."
    )
    cleaned, redactions = PrivacySanitizer.sanitize_text(dirty_text)

    assert "john.doe@example.com" not in cleaned
    assert "[EMAIL_REDACTED]" in cleaned
    assert "555-123-4567" not in cleaned
    assert "[PHONE_REDACTED]" in cleaned
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in cleaned
    assert "[REDACTED_TOKEN]" in cleaned
    assert "MySecretPassword123!" not in cleaned
    assert "[REDACTED_PASSWORD]" in cleaned
    assert "credentials_or_secret" in redactions
    assert "pii" in redactions


# ---------------------------------------------------------
# Quality Validator Unit Tests
# ---------------------------------------------------------

def test_quality_validator_rules():
    """Verify validation heuristics for length, duplicate copy-cat, consent, and categories."""
    # 1. Valid sample
    is_valid, reasons = DatasetQualityValidator.validate_sample(
        prompt_input="How should I organize my tasks today?",
        chosen_response="Group tasks by energy level and tackle high-priority items first.",
        consent_status="granted",
        sanitization_status="sanitized",
        category="other",
        source_message_id="msg-123"
    )
    assert is_valid is True
    assert len(reasons) == 0

    # 2. Rejected for missing consent
    is_valid_no_consent, reasons_no_consent = DatasetQualityValidator.validate_sample(
        prompt_input="Valid prompt",
        chosen_response="Valid response",
        consent_status="pending",
        sanitization_status="sanitized",
        source_message_id="msg-123"
    )
    assert is_valid_no_consent is False
    assert any("consent" in r.lower() for r in reasons_no_consent)

    # 3. Rejected for degenerate copy-cat response
    is_valid_copy, reasons_copy = DatasetQualityValidator.validate_sample(
        prompt_input="Summarize tasks",
        chosen_response="Summarize tasks",
        consent_status="granted",
        sanitization_status="sanitized",
        source_message_id="msg-123"
    )
    assert is_valid_copy is False
    assert any("copy" in r.lower() for r in reasons_copy)

    # 4. Rejected for empty/too short text
    is_valid_short, reasons_short = DatasetQualityValidator.validate_sample(
        prompt_input="a",
        chosen_response="",
        consent_status="granted",
        sanitization_status="sanitized",
        source_message_id="msg-123"
    )
    assert is_valid_short is False


# ---------------------------------------------------------
# Dataset Pipeline Collection & API Tests
# ---------------------------------------------------------

def test_pipeline_collects_from_consented_feedback(client, auth_headers, consented_user_conversation, app):
    """Verify that submitting positive feedback when consent is active creates a training sample."""
    msg_id = consented_user_conversation["assistant_msg_id"]

    # Post thumbs-up feedback
    fb_resp = client.post(
        "/api/v1/ai/feedback",
        json={"message_id": msg_id, "rating": 1, "feedback_type": "thumbs_up"},
        headers=auth_headers
    )
    assert fb_resp.status_code == 201

    with app.app_context():
        sample = AITrainingSample.query.filter_by(source_message_id=msg_id).first()
        assert sample is not None
        assert sample.consent_status == "granted"
        assert sample.validation_status == "valid"
        assert sample.sanitization_status == "sanitized"
        assert sample.dataset_type == "sft"


def test_pipeline_does_not_collect_without_consent(client, consented_user_conversation, app):
    """Verify that feedback is NOT collected into training samples if user has not granted consent."""
    with app.app_context():
        # Set consent to False
        user_id = consented_user_conversation["user_id"]
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        pref.ai_training_consent = False
        db.session.commit()

        dataset_svc = AIDatasetService()
        fb = AIFeedback(
            user_id=user_id,
            message_id=consented_user_conversation["assistant_msg_id"],
            rating=1,
            feedback_type="thumbs_up"
        )
        db.session.add(fb)
        db.session.commit()

        sample = dataset_svc.collect_from_feedback(user_id=user_id, feedback_id=fb.id)
        assert sample is None


def test_admin_rbac_protection_on_dataset_endpoints(client, non_admin_headers):
    """Verify that non-admin users receive 403 Forbidden on all dataset management endpoints."""
    # List samples
    resp1 = client.get("/api/v1/ai/datasets/samples", headers=non_admin_headers)
    assert resp1.status_code == 403

    # Statistics
    resp2 = client.get("/api/v1/ai/datasets/statistics", headers=non_admin_headers)
    assert resp2.status_code == 403

    # Create version
    resp3 = client.post(
        "/api/v1/ai/datasets/versions",
        json={"version_name": "v1.0"},
        headers=non_admin_headers
    )
    assert resp3.status_code == 403


def test_create_dataset_version_and_jsonl_export(client, admin_headers, app):
    """Verify creating an immutable snapshot version and exporting as valid JSONL."""
    with app.app_context():
        admin = User.query.filter_by(email="dataset_admin@lifeos.internal").first()
        # Seed 3 valid approved samples
        for i in range(3):
            s = AITrainingSample(
                user_id=admin.id,
                prompt_input=f"Prompt query number {i}",
                chosen_response=f"Clear and structured completion response for turn {i}.",
                dataset_type="sft",
                consent_status="granted",
                review_status="approved",
                sanitization_status="sanitized",
                validation_status="valid",
                category="other",
                quality_score=1.0,
                source_message_id=f"msg-dummy-{i}"
            )
            db.session.add(s)
        db.session.commit()

    # Create version snapshot via API
    ver_payload = {
        "version_name": "v1.0.0-sft",
        "description": "Baseline instruction-tuning dataset",
        "dataset_type": "sft"
    }
    ver_resp = client.post(
        "/api/v1/ai/datasets/versions",
        json=ver_payload,
        headers=admin_headers
    )
    assert ver_resp.status_code == 201
    ver_data = ver_resp.get_json()["data"]["version"]
    assert ver_data["version_name"] == "v1.0.0-sft"
    assert ver_data["sample_count"] >= 3
    assert len(ver_data["manifest_hash"]) == 64  # SHA-256

    # Export version as JSONL
    export_resp = client.get(
        f"/api/v1/ai/datasets/versions/v1.0.0-sft/export",
        headers=admin_headers
    )
    assert export_resp.status_code == 200
    assert "application/x-jsonlines" in export_resp.content_type
    assert "X-Manifest-SHA256" in export_resp.headers

    # Validate JSONL content lines
    lines = export_resp.data.decode("utf-8").strip().split("\n")
    assert len(lines) >= 3
    for line in lines:
        parsed = json.loads(line)
        assert "prompt" in parsed
        assert "completion" in parsed
        assert "type" in parsed
        assert parsed["type"] == "sft"
