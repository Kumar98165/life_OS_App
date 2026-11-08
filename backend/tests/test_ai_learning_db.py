"""LifeOS - STEP 13.5 AI Continuous Learning & Feedback Database Tests.

Covers:
- Model creation and persistence
- Foreign-key cascade and set-null integrity
- Unique constraint: one feedback record per assistant message
- Unique constraint: version_tag uniqueness on prompt versions
- Single active prompt constraint (partial unique index on is_active = True)
- Training consent defaults to False
- User role defaults to 'user'
- Training sample status and dataset types
- Backward compatibility for existing AI messages without prompt version
- Existing memory records integrity
"""
import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.ai import (
    AIConversation,
    AIMessage,
    AIMemory,
    AIPromptVersion,
    AIFeedback,
    AIEvaluationRun,
    AIEvaluationMetric,
    AITrainingSample
)


@pytest.fixture
def test_user(app):
    """Fixture providing a persisted test user."""
    with app.app_context():
        user = User(
            email="learner@lifeos.internal",
            full_name="AI Continuous Learner"
        )
        user.set_password("Password123!")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def test_conversation_and_message(app, test_user):
    """Fixture providing a conversation and assistant message."""
    with app.app_context():
        conv = AIConversation(
            user_id=test_user,
            title="Learning Test Thread",
            model_used="qwen2.5:3b"
        )
        db.session.add(conv)
        db.session.commit()

        msg = AIMessage(
            conversation_id=conv.id,
            role="assistant",
            content="Here is your structured schedule for today."
        )
        db.session.add(msg)
        db.session.commit()
        return conv.id, msg.id


def test_user_role_default(app):
    """Verify that new users default to role='user'."""
    with app.app_context():
        user = User(email="role_default@lifeos.internal", full_name="Role Test")
        user.set_password("Password123!")
        db.session.add(user)
        db.session.commit()

        assert user.role == "user"
        assert user.to_dict()["role"] == "user"


def test_user_preference_training_consent_default(app, test_user):
    """Verify that user_preferences.ai_training_consent defaults to False."""
    with app.app_context():
        pref = UserPreference(user_id=test_user)
        db.session.add(pref)
        db.session.commit()

        assert pref.ai_training_consent is False
        assert pref.ai_memory_enabled is True  # Preserved from Step 13
        assert pref.to_dict()["ai_training_consent"] is False


def test_ai_prompt_version_creation_and_uniqueness(app, test_user):
    """Verify creating prompt versions and enforcing unique version_tag."""
    with app.app_context():
        v1 = AIPromptVersion(
            version_tag="v1.0.0-baseline",
            prompt_template="You are LifeOS {context_block}",
            change_summary="Initial system prompt release",
            created_by=test_user,
            is_active=False
        )
        db.session.add(v1)
        db.session.commit()

        assert v1.id is not None
        assert v1.version_tag == "v1.0.0-baseline"
        assert v1.to_dict()["is_active"] is False

        # Attempt duplicate version_tag -> must raise IntegrityError
        v1_dup = AIPromptVersion(
            version_tag="v1.0.0-baseline",
            prompt_template="Duplicate tag prompt",
            change_summary="Should fail"
        )
        db.session.add(v1_dup)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_single_active_prompt_constraint(app):
    """Verify partial unique index: only ONE prompt version may have is_active=True."""
    with app.app_context():
        # First active prompt -> OK
        active1 = AIPromptVersion(
            version_tag="v1.1.0-active",
            prompt_template="Active template",
            change_summary="Current production prompt",
            is_active=True
        )
        # Multiple inactive prompts -> OK
        inactive1 = AIPromptVersion(
            version_tag="v1.0.0-archived",
            prompt_template="Archived template 1",
            change_summary="Retired prompt",
            is_active=False
        )
        inactive2 = AIPromptVersion(
            version_tag="v0.9.0-legacy",
            prompt_template="Archived template 2",
            change_summary="Old prompt",
            is_active=False
        )
        db.session.add_all([active1, inactive1, inactive2])
        db.session.commit()

        # Attempt to insert a second active prompt -> MUST fail unique constraint
        active2 = AIPromptVersion(
            version_tag="v1.2.0-conflict",
            prompt_template="Conflicting active template",
            change_summary="Should be rejected",
            is_active=True
        )
        db.session.add(active2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_ai_feedback_creation_and_uniqueness_per_message(app, test_user, test_conversation_and_message):
    """Verify creating feedback on an assistant message and preventing duplicate feedback on same message."""
    conv_id, msg_id = test_conversation_and_message

    with app.app_context():
        feedback = AIFeedback(
            user_id=test_user,
            message_id=msg_id,
            rating=1,
            feedback_type="thumbs_up",
            category="accuracy",
            comment="Very helpful daily schedule."
        )
        db.session.add(feedback)
        db.session.commit()

        assert feedback.id is not None
        assert feedback.rating == 1
        assert feedback.message_id == msg_id
        assert feedback.to_dict()["rating"] == 1

        # Attempt duplicate feedback on same message -> must raise IntegrityError
        duplicate_feedback = AIFeedback(
            user_id=test_user,
            message_id=msg_id,
            rating=-1,
            feedback_type="thumbs_down"
        )
        db.session.add(duplicate_feedback)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_ai_feedback_cascade_deletion_with_message(app, test_user, test_conversation_and_message):
    """Verify that deleting an assistant message cascade-deletes its feedback."""
    conv_id, msg_id = test_conversation_and_message

    with app.app_context():
        feedback = AIFeedback(
            user_id=test_user,
            message_id=msg_id,
            rating=-1,
            feedback_type="thumbs_down",
            category="inaccurate_schedule",
            comment="Task was already completed."
        )
        db.session.add(feedback)
        db.session.commit()
        fb_id = feedback.id

        # Delete message
        msg = db.session.get(AIMessage, msg_id)
        db.session.delete(msg)
        db.session.commit()

        # Feedback should be cascade-deleted
        assert db.session.get(AIFeedback, fb_id) is None


def test_ai_evaluation_run_and_metrics_hierarchy(app, test_conversation_and_message):
    """Verify parent evaluation run and child metric breakdown."""
    conv_id, msg_id = test_conversation_and_message

    with app.app_context():
        run = AIEvaluationRun(
            message_id=msg_id,
            model_name="qwen2.5:3b",
            passed=True,
            overall_score=0.92,
            notes="Benchmark run passed."
        )
        db.session.add(run)
        db.session.commit()

        # Child metrics
        m1 = AIEvaluationMetric(
            run_id=run.id,
            metric_name="relevance",
            score=0.95,
            passed=True,
            reasoning="Directly answered user inquiry."
        )
        m2 = AIEvaluationMetric(
            run_id=run.id,
            metric_name="factual_consistency",
            score=0.90,
            passed=True,
            reasoning="Matches database records."
        )
        m3 = AIEvaluationMetric(
            run_id=run.id,
            metric_name="hallucination_risk",
            score=0.98,
            passed=True,
            reasoning="No invented tasks detected."
        )
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        # Query parent and verify children
        queried_run = db.session.get(AIEvaluationRun, run.id)
        assert len(queried_run.metrics) == 3
        serialized = queried_run.to_dict()
        assert len(serialized["metrics"]) == 3
        assert serialized["overall_score"] == 0.92

        # Cascade delete run -> deletes metrics
        db.session.delete(queried_run)
        db.session.commit()
        assert db.session.get(AIEvaluationMetric, m1.id) is None


def test_ai_training_sample_creation_and_status(app, test_user, test_conversation_and_message):
    """Verify training sample with SFT / DPO pairings, consent status, and quality score."""
    conv_id, msg_id = test_conversation_and_message

    with app.app_context():
        sample = AITrainingSample(
            user_id=test_user,
            source_message_id=msg_id,
            prompt_input="What are my priority tasks for today?",
            chosen_response="1. Fix bug #42\n2. Prepare quarterly review",
            rejected_response="You have tasks to do.",
            dataset_type="dpo",
            consent_status="granted",
            review_status="approved",
            quality_score=0.95
        )
        db.session.add(sample)
        db.session.commit()

        assert sample.id is not None
        assert sample.dataset_type == "dpo"
        assert sample.consent_status == "granted"
        assert sample.review_status == "approved"
        assert sample.to_dict()["quality_score"] == 0.95


def test_existing_ai_message_compatibility_and_metadata(app, test_user):
    """Verify backward compatibility: AIMessage works with or without prompt_version_id and latency_ms."""
    with app.app_context():
        conv = AIConversation(user_id=test_user, title="Compatibility Thread")
        db.session.add(conv)
        db.session.commit()

        # Message without new optional fields
        legacy_msg = AIMessage(
            conversation_id=conv.id,
            role="assistant",
            content="Message without prompt version"
        )
        # Message with new optional fields
        pv = AIPromptVersion(
            version_tag="v1.0.0-compat",
            prompt_template="Template",
            change_summary="Compat test"
        )
        db.session.add(pv)
        db.session.commit()

        modern_msg = AIMessage(
            conversation_id=conv.id,
            prompt_version_id=pv.id,
            role="assistant",
            content="Message with prompt version",
            latency_ms=1240,
            tokens_used=180
        )
        db.session.add_all([legacy_msg, modern_msg])
        db.session.commit()

        assert legacy_msg.prompt_version_id is None
        assert legacy_msg.latency_ms is None
        assert modern_msg.prompt_version_id == pv.id
        assert modern_msg.latency_ms == 1240
        assert modern_msg.tokens_used == 180


def test_existing_memory_records_preserved(app, test_user):
    """Verify that STEP 13 AIMemory model remains completely functional and unaffected."""
    with app.app_context():
        mem = AIMemory(
            user_id=test_user,
            memory_key="Prefers morning deep work",
            memory_value="8 AM - 10 AM focus window",
            memory_type="preference",
            confidence=0.95,
            status="confirmed"
        )
        db.session.add(mem)
        db.session.commit()

        assert mem.id is not None
        assert mem.status == "confirmed"
        assert mem.to_dict()["memory_key"] == "Prefers morning deep work"

