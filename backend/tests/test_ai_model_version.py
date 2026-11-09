"""Unit and integration tests for LifeOS STEP 10 - AI Model Version Management & Rollback."""

import pytest
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.user import User
from app.models.ai import AIModelVersion, AIModelRollbackLog
from app.services.model_registry_service import ModelRegistryService
from app.repositories.ai_model_version_repository import AIModelVersionRepository
from app.ai.config import AIRuntimeConfig, get_ai_config
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    ForbiddenException,
    ConflictException,
)


@pytest.fixture
def admin_user(app):
    """Create an administrator user and return id and role."""
    with app.app_context():
        user = User(
            email="admin@lifeos.internal",
            full_name="Model Ops Admin",
            password_hash="fake_hash",
            role="admin",
        )
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def regular_user(app):
    """Create a standard user without admin privileges."""
    with app.app_context():
        user = User(
            email="user@lifeos.internal",
            full_name="Standard User",
            password_hash="fake_hash",
            role="user",
        )
        db.session.add(user)
        db.session.commit()
        return user.id


class TestModelRegistryService:
    """Tests for registration, validation, evaluation, approval, activation, and rollback."""

    def test_initialize_default_base_model(self, app):
        with app.app_context():
            service = ModelRegistryService()
            model = service.initialize_default_base_model()
            assert model.model_tag == "qwen2.5:3b"
            assert model.is_active is True
            assert model.status == "active"
            assert model.base_model == "Qwen/Qwen2.5-3B-Instruct"

    def test_register_valid_model(self, app, admin_user):
        with app.app_context():
            user = db.session.get(User, admin_user)
            service = ModelRegistryService()
            model = service.register_model(
                model_tag="qwen2.5:3b-lifeos:v1",
                version_tag="v1.0.0",
                base_model="Qwen/Qwen2.5-3B-Instruct",
                training_run_id="run_v1.0.0_20261109",
                dataset_version="v1.0.0-snapshot",
                artifact_checksum="a" * 64,
                notes="Fine-tuned candidate for LifeOS productivity",
                user=user,
            )
            assert model.id is not None
            assert model.model_tag == "qwen2.5:3b-lifeos:v1"
            assert model.status == "registered"
            assert model.is_active is False
            assert model.artifact_checksum == "a" * 64

    def test_register_invalid_version_tag_rejected(self, app, admin_user):
        with app.app_context():
            user = db.session.get(User, admin_user)
            service = ModelRegistryService()
            with pytest.raises(BadRequestException, match="semantic versioning"):
                service.register_model(
                    model_tag="qwen2.5:3b-bad",
                    version_tag="invalid_version",
                    user=user,
                )

    def test_register_invalid_checksum_rejected(self, app, admin_user):
        with app.app_context():
            user = db.session.get(User, admin_user)
            service = ModelRegistryService()
            with pytest.raises(BadRequestException, match="64-character SHA-256"):
                service.register_model(
                    model_tag="qwen2.5:3b-bad-hash",
                    version_tag="v1.0.0",
                    artifact_checksum="short_hash_123",
                    user=user,
                )

    def test_register_duplicate_model_tag_rejected(self, app, admin_user):
        with app.app_context():
            user = db.session.get(User, admin_user)
            service = ModelRegistryService()
            service.register_model(
                model_tag="qwen2.5:3b-duplicate",
                version_tag="v1.0.0",
                user=user,
            )
            with pytest.raises(ConflictException, match="already registered"):
                service.register_model(
                    model_tag="qwen2.5:3b-duplicate",
                    version_tag="v1.0.1",
                    user=user,
                )

    def test_non_admin_cannot_register_or_approve(self, app, regular_user):
        with app.app_context():
            user = db.session.get(User, regular_user)
            service = ModelRegistryService()
            with pytest.raises(ForbiddenException):
                service.register_model(
                    model_tag="qwen2.5:3b-unauthorized",
                    version_tag="v1.0.0",
                    user=user,
                )

    def test_evaluation_and_approval_workflow(self, app, admin_user):
        with app.app_context():
            user = db.session.get(User, admin_user)
            service = ModelRegistryService()
            model = service.register_model(
                model_tag="qwen2.5:3b-approved-test",
                version_tag="v1.0.0",
                user=user,
            )

            # 1. Attach evaluation report
            evaluated = service.attach_evaluation_report(
                model_id=model.id,
                evaluation_score=0.82,
                report_path="./evaluation_reports/eval_test.json",
                user=user,
            )
            assert evaluated.status == "evaluated"
            assert evaluated.evaluation_score == 0.82

            # 2. Cannot approve if score is below threshold (0.65)
            low_score_model = service.register_model(
                model_tag="qwen2.5:3b-low-score",
                version_tag="v1.0.0",
                user=user,
            )
            service.attach_evaluation_report(low_score_model.id, evaluation_score=0.50, user=user)
            with pytest.raises(BadRequestException, match="below the minimum threshold"):
                service.approve_model(low_score_model.id, user=user)

            # 3. Approve high score model
            approved = service.approve_model(model.id, user=user, notes="Benchmark exceeded baseline.")
            assert approved.status == "approved"
            assert approved.approved_by == user.id
            assert approved.approved_at is not None

    def test_activation_and_rollback_lifecycle(self, app, admin_user):
        with app.app_context():
            user = db.session.get(User, admin_user)
            service = ModelRegistryService()
            # 1. Ensure default base model is active
            base = service.initialize_default_base_model()
            assert base.is_active is True

            # 2. Register, evaluate, and approve candidate model
            candidate = service.register_model(
                model_tag="qwen2.5:3b-candidate-v1",
                version_tag="v1.1.0",
                user=user,
            )
            service.attach_evaluation_report(candidate.id, evaluation_score=0.85, user=user)
            service.approve_model(candidate.id, user=user)

            # 3. Activate candidate with mock flag
            act_log = service.activate_model(
                model_id=candidate.id,
                user=user,
                reason="Candidate outperformed base model in STEP 9 benchmark.",
                allow_offline_mock=True,
            )
            assert act_log.action == "activation"
            assert act_log.from_model_id == base.id
            assert act_log.to_model_id == candidate.id

            # Verify active state
            db.session.refresh(base)
            db.session.refresh(candidate)
            assert base.is_active is False
            assert candidate.is_active is True
            assert candidate.status == "active"
            assert get_ai_config()["model"] == "qwen2.5:3b-candidate-v1"

            # 4. Rollback back to base model
            rb_log = service.rollback_model(
                target_model_id=base.id,
                user=user,
                reason="Candidate caused unexpected latency spike.",
                allow_offline_mock=True,
            )
            assert rb_log.action == "rollback"
            assert rb_log.from_model_id == candidate.id
            assert rb_log.to_model_id == base.id

            db.session.refresh(base)
            db.session.refresh(candidate)
            assert base.is_active is True
            assert candidate.is_active is False
            assert get_ai_config()["model"] == "qwen2.5:3b"

    def test_missing_ollama_model_fails_activation_without_mock(self, app, admin_user):
        with app.app_context():
            user = db.session.get(User, admin_user)
            service = ModelRegistryService()
            model = service.register_model(
                model_tag="qwen2.5:non-existent-tag",
                version_tag="v1.0.0",
                user=user,
            )
            service.attach_evaluation_report(model.id, evaluation_score=0.90, user=user)
            service.approve_model(model.id, user=user)

            # Trying to activate a model that is not installed in Ollama must fail
            with pytest.raises(BadRequestException, match="not installed or available in Ollama"):
                service.activate_model(
                    model_id=model.id,
                    user=user,
                    reason="Test real activation gate.",
                    allow_offline_mock=False,
                )


class TestModelVersionAPI:
    """REST endpoint integration tests for /api/v1/ai/models."""

    def test_list_models_and_get_active(self, app, client, admin_user, regular_user):
        with app.app_context():
            admin_token = create_access_token(identity=admin_user)
            user_token = create_access_token(identity=regular_user)

        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # 1. Get active model
        resp = client.get("/api/v1/ai/models/active", headers=user_headers)
        assert resp.status_code == 200
        assert resp.get_json()["data"]["model_tag"] == "qwen2.5:3b"

        # 2. Register model as regular user -> Forbidden 403
        bad_reg = client.post("/api/v1/ai/models", headers=user_headers, json={
            "model_tag": "qwen2.5:3b-unauthorized",
            "version_tag": "v1.0.0"
        })
        assert bad_reg.status_code == 403

        # 3. Register model as admin -> 201 Created
        good_reg = client.post("/api/v1/ai/models", headers=admin_headers, json={
            "model_tag": "qwen2.5:3b-api-candidate",
            "version_tag": "v1.0.0",
            "base_model": "Qwen/Qwen2.5-3B-Instruct",
            "notes": "API test candidate"
        })
        assert good_reg.status_code == 201
        model_id = good_reg.get_json()["data"]["id"]

        # 4. Attach evaluation
        eval_resp = client.post(f"/api/v1/ai/models/{model_id}/evaluate", headers=admin_headers, json={
            "evaluation_score": 0.88,
            "report_path": "./reports/test.json"
        })
        assert eval_resp.status_code == 200

        # 5. Approve model
        appr_resp = client.post(f"/api/v1/ai/models/{model_id}/approve", headers=admin_headers, json={
            "notes": "Approved via API test."
        })
        assert appr_resp.status_code == 200

        # 6. Activate model (with offline mock flag)
        act_resp = client.post(f"/api/v1/ai/models/{model_id}/activate", headers=admin_headers, json={
            "reason": "Production upgrade via API test.",
            "allow_offline_mock": True
        })
        assert act_resp.status_code == 200
        assert act_resp.get_json()["data"]["action"] == "activation"

        # 7. Verify active model changed
        active_check = client.get("/api/v1/ai/models/active", headers=user_headers)
        assert active_check.get_json()["data"]["model_tag"] == "qwen2.5:3b-api-candidate"

        # 8. List audit logs
        logs_resp = client.get("/api/v1/ai/models/audit-logs", headers=user_headers)
        assert logs_resp.status_code == 200
        assert len(logs_resp.get_json()["data"]["items"]) >= 1
