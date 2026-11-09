"""Unit and integration tests for LifeOS STEP 11 - Continuous AI Improvement Workflow."""

import pytest
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.user import User
from app.models.ai import (
    AIDatasetVersion,
    AITrainingSample,
    AITrainingJob,
    AIModelVersion,
)
from app.services.continuous_improvement_service import (
    ContinuousImprovementService,
    MIN_DATASET_SAMPLE_THRESHOLD,
)
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    ForbiddenException,
    ConflictException,
)
from app.ai.evaluation.benchmark import BenchmarkDataset


@pytest.fixture
def admin_user(app):
    """Create an administrator user."""
    with app.app_context():
        user = User(
            email="admin@lifeos.internal",
            full_name="Improvement Admin",
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


@pytest.fixture
def ready_dataset_version(app, admin_user):
    """Create a fully compliant dataset version with 5 approved, sanitized, valid samples."""
    with app.app_context():
        version = AIDatasetVersion(
            version_name="v1.0.0-ci-ready",
            dataset_type="sft",
            sample_count=5,
            manifest_hash="b" * 64,
            created_by=admin_user,
            description="Compliant test dataset version for CI pipeline",
        )
        db.session.add(version)
        db.session.flush()

        for i in range(5):
            sample = AITrainingSample(
                user_id=admin_user,
                prompt_input=f"Task prompt number {i} for planning",
                chosen_response=f"Structured resolution for task {i}",
                category="productivity",
                dataset_type="sft",
                consent_status="granted",
                review_status="approved",
                validation_status="valid",
                sanitization_status="sanitized",
                quality_score=1.0,
                dataset_version_id=version.id,
            )
            db.session.add(sample)

        db.session.commit()
        return version.version_name


class TestDatasetReadiness:
    """Tests for dataset evaluation against configured quality, consent, and volume gates."""

    def test_dataset_readiness_passes_for_compliant_version(self, app, ready_dataset_version):
        with app.app_context():
            service = ContinuousImprovementService()
            report = service.evaluate_dataset_readiness(dataset_version_name=ready_dataset_version)

            assert report["version_name"] == ready_dataset_version
            assert report["total_samples"] == 5
            assert report["is_ready_for_training"] is True
            assert len(report["blocking_reasons"]) == 0
            assert report["duplicate_rate"] == 0.0

    def test_dataset_readiness_blocks_insufficient_sample_count(self, app, admin_user):
        with app.app_context():
            version = AIDatasetVersion(
                version_name="v0.1.0-too-few",
                dataset_type="sft",
                sample_count=2,
                manifest_hash="c" * 64,
                created_by=admin_user,
            )
            db.session.add(version)
            db.session.flush()

            for i in range(2):
                sample = AITrainingSample(
                    user_id=admin_user,
                    prompt_input=f"Prompt {i}",
                    chosen_response=f"Response {i}",
                    consent_status="granted",
                    review_status="approved",
                    validation_status="valid",
                    sanitization_status="sanitized",
                    quality_score=1.0,
                    dataset_version_id=version.id,
                )
                db.session.add(sample)
            db.session.commit()

            service = ContinuousImprovementService()
            report = service.evaluate_dataset_readiness(dataset_version_name="v0.1.0-too-few")
            assert report["is_ready_for_training"] is False
            assert any("below minimum technical threshold" in r for r in report["blocking_reasons"])
            assert report["meets_recommended_volume"] is False
            assert len(report["advisory_notes"]) > 0

    def test_dataset_readiness_blocks_revoked_consent_and_unapproved(self, app, admin_user):
        with app.app_context():
            version = AIDatasetVersion(
                version_name="v1.0.0-revoked-consent",
                dataset_type="sft",
                sample_count=5,
                manifest_hash="d" * 64,
                created_by=admin_user,
            )
            db.session.add(version)
            db.session.flush()

            for i in range(5):
                sample = AITrainingSample(
                    user_id=admin_user,
                    prompt_input=f"Prompt {i}",
                    chosen_response=f"Response {i}",
                    consent_status="revoked" if i == 0 else "granted",
                    review_status="pending" if i == 1 else "approved",
                    validation_status="valid",
                    sanitization_status="sanitized",
                    quality_score=1.0,
                    dataset_version_id=version.id,
                )
                db.session.add(sample)
            db.session.commit()

            service = ContinuousImprovementService()
            report = service.evaluate_dataset_readiness(dataset_version_name="v1.0.0-revoked-consent")
            assert report["is_ready_for_training"] is False
            assert any("revoked or missing consent" in r for r in report["blocking_reasons"])
            assert any("lack explicit approval" in r for r in report["blocking_reasons"])


class TestTrainingJobLifecycle:
    """Tests for job creation, dry-run preparation, concurrency guards, and cancellation."""

    def test_create_and_execute_training_job_dry_run(self, app, admin_user, ready_dataset_version):
        with app.app_context():
            user = db.session.get(User, admin_user)
            service = ContinuousImprovementService()

            # 1. Create job
            job = service.create_training_job(
                dataset_version_name=ready_dataset_version,
                job_name="job_qwen2.5_ci_test_1",
                candidate_model_tag="qwen2.5:3b-ci-v1",
                user=user,
            )
            assert job.id is not None
            assert job.status == "ready"
            assert job.candidate_model_tag == "qwen2.5:3b-ci-v1"

            # 2. Execute dry-run validation
            res = service.execute_dry_run_or_prepare_job(job_id=job.id, user=user)
            assert res["status"] == "dry_run_validated"
            assert res["is_real_training"] is False

            db.session.refresh(job)
            assert job.status == "dry_run_validated"
            assert job.artifact_checksum is not None
            assert job.completed_at is not None

            # 3. Dry-run cannot be evaluated or registered as a candidate
            with pytest.raises(BadRequestException, match="cannot produce production-eligible trained candidates"):
                service.post_training_evaluate_and_register(job_id=job.id, user=user)

    def test_record_real_gpu_training_completion_and_integrity(self, app, admin_user, ready_dataset_version):
        with app.app_context():
            user = db.session.get(User, admin_user)
            service = ContinuousImprovementService()

            job = service.create_training_job(
                dataset_version_name=ready_dataset_version,
                job_name="job_real_gpu_run",
                candidate_model_tag="qwen2.5:3b-real-gpu-cand",
                user=user,
            )

            # Record real GPU completion with cryptographic checksum
            real_res = service.record_gpu_training_completion(
                job_id=job.id,
                artifact_checksum="a" * 64,
                artifact_directory="/artifacts/runs/job_real_gpu_run",
                metrics={"train_loss": 0.42, "epochs": 3},
                user=user,
            )
            assert real_res["status"] == "completed"
            assert real_res["is_real_training"] is True

            db.session.refresh(job)
            assert job.status == "completed"
            assert job.artifact_checksum == "a" * 64

    def test_duplicate_concurrent_job_prevention(self, app, admin_user, ready_dataset_version):
        with app.app_context():
            user = db.session.get(User, admin_user)
            service = ContinuousImprovementService()

            service.create_training_job(
                dataset_version_name=ready_dataset_version,
                job_name="job_concurrent_1",
                candidate_model_tag="qwen2.5:3b-ci-cand-1",
                user=user,
            )

            with pytest.raises(ConflictException, match="already active for dataset version"):
                service.create_training_job(
                    dataset_version_name=ready_dataset_version,
                    job_name="job_concurrent_2",
                    candidate_model_tag="qwen2.5:3b-ci-cand-2",
                    user=user,
                )

    def test_cancel_training_job(self, app, admin_user, ready_dataset_version):
        with app.app_context():
            user = db.session.get(User, admin_user)
            service = ContinuousImprovementService()

            job = service.create_training_job(
                dataset_version_name=ready_dataset_version,
                job_name="job_to_cancel",
                candidate_model_tag="qwen2.5:3b-cancel-cand",
                user=user,
            )
            assert job.status == "ready"

            cancelled = service.cancel_job(job_id=job.id, user=user, reason="Operator abort")
            assert cancelled.status == "cancelled"
            assert "Operator abort" in cancelled.error_message


class TestPostTrainingEvaluationAndRegistry:
    """Tests for post-training benchmark evaluation and candidate model registry integration."""

    def test_post_training_evaluation_and_candidate_registration(self, app, admin_user, ready_dataset_version):
        with app.app_context():
            user = db.session.get(User, admin_user)
            service = ContinuousImprovementService()

            job = service.create_training_job(
                dataset_version_name=ready_dataset_version,
                job_name="job_post_train_eval",
                candidate_model_tag="qwen2.5:3b-post-cand",
                user=user,
            )
            # Record completed real training
            service.record_gpu_training_completion(
                job_id=job.id,
                artifact_checksum="c" * 64,
                artifact_directory="/artifacts/runs/job_post_train_eval",
                metrics={"train_loss": 0.35, "epochs": 3},
                user=user,
            )

            # Post-training evaluate and register with mock responses
            all_items = BenchmarkDataset.get_all_items()
            mock_responses = {
                item["id"]: (
                    f"1. Focus time at 9:00 with lunch break. "
                    f"2. Urgent production crash is Quadrant 1, spam is Quadrant 3. "
                    f"3. Water habit cue routine reward with specific measurable SMART milestones. "
                    f"4. Pomodoro 25 minutes with 5 minute break. {item['prompt']}"
                )
                for item in all_items
            }
            res = service.post_training_evaluate_and_register(
                job_id=job.id,
                user=user,
                mock_eval_responses=mock_responses,
            )

            assert res["candidate_model_tag"] == "qwen2.5:3b-post-cand"
            assert res["registered_model_id"] is not None
            assert res["model_status"] == "evaluated"

            # Verify registered in Step 10 model registry
            registered = service.registry_service.repo.get_by_id(res["registered_model_id"])
            assert registered is not None
            assert registered.model_tag == "qwen2.5:3b-post-cand"
            assert registered.status == "evaluated"
            assert registered.is_active is False  # Must NOT automatically replace active model


class TestImprovementAPI:
    """REST endpoint integration tests for /api/v1/ai/improvement."""

    def test_dashboard_and_readiness_endpoints(self, app, client, admin_user, regular_user, ready_dataset_version):
        with app.app_context():
            admin_token = create_access_token(identity=admin_user)
            user_token = create_access_token(identity=regular_user)

        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # 1. Get dashboard
        dash_resp = client.get("/api/v1/ai/improvement/dashboard", headers=user_headers)
        assert dash_resp.status_code == 200
        assert "active_runtime_model" in dash_resp.get_json()["data"]

        # 2. Check dataset readiness
        readiness_resp = client.get(
            f"/api/v1/ai/improvement/datasets/{ready_dataset_version}/readiness",
            headers=user_headers
        )
        assert readiness_resp.status_code == 200
        assert readiness_resp.get_json()["data"]["is_ready_for_training"] is True

        # 3. Create job as non-admin -> Forbidden 403
        bad_job = client.post("/api/v1/ai/improvement/jobs", headers=user_headers, json={
            "dataset_version_name": ready_dataset_version,
            "job_name": "unauthorized_job",
            "candidate_model_tag": "qwen2.5:3b-unauth"
        })
        assert bad_job.status_code == 403

        # 4. Create job as admin -> 201 Created
        good_job = client.post("/api/v1/ai/improvement/jobs", headers=admin_headers, json={
            "dataset_version_name": ready_dataset_version,
            "job_name": "api_test_job_1",
            "candidate_model_tag": "qwen2.5:3b-api-candidate-1"
        })
        assert good_job.status_code == 201
        job_id = good_job.get_json()["data"]["id"]

        # 5. Execute dry-run validation
        exec_resp = client.post(f"/api/v1/ai/improvement/jobs/{job_id}/execute", headers=admin_headers)
        assert exec_resp.status_code == 200
        assert exec_resp.get_json()["data"]["status"] == "dry_run_validated"
        assert exec_resp.get_json()["data"]["is_real_training"] is False

        # 6. List jobs
        list_jobs = client.get("/api/v1/ai/improvement/jobs", headers=user_headers)
        assert list_jobs.status_code == 200
        assert len(list_jobs.get_json()["data"]["items"]) >= 1

        # 7. Record real GPU training completion via API
        rec_resp = client.post(f"/api/v1/ai/improvement/jobs/{job_id}/record-completion", headers=admin_headers, json={
            "artifact_checksum": "e" * 64,
            "artifact_directory": "/artifacts/trained/api_test_job_1",
            "metrics": {"loss": 0.29}
        })
        assert rec_resp.status_code == 200
        assert rec_resp.get_json()["data"]["status"] == "completed"
        assert rec_resp.get_json()["data"]["is_real_training"] is True
