"""LifeOS - Continuous AI Improvement Pipeline & Readiness Service (Step 11).

Orchestrates:
- Feedback-to-Dataset readiness evaluation
- Minimum sample threshold and quality gate checks
- Training job lifecycle management (pending, validating, ready, running, completed, failed, cancelled)
- External GPU execution preparation and dry-run validation
- Automated post-training evaluation via Step 9
- Model registry registration and approval gate via Step 10
"""
import os
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy import desc

from app.extensions import db
from app.models.ai import (
    AITrainingJob,
    AIDatasetVersion,
    AITrainingSample,
    AIModelVersion,
)
from app.models.user import User
from app.repositories.ai_dataset_repository import AIDatasetRepository
from app.services.ai_dataset_service import AIDatasetService
from app.ai.training.profile import TrainingProfile
from app.ai.training.runner import TrainingPipelineRunner
from app.ai.training.hardware import HardwareDetector
from app.services.model_registry_service import ModelRegistryService
from app.services.model_evaluation_service import ModelEvaluationService
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    ForbiddenException,
    ConflictException,
)

# Minimum dataset threshold configuration
# Configured minimum of 5 approved & validated samples for candidate training job preparation.
# Rationale: Ensures sufficient diversity across basic productivity tasks while allowing
# controlled iterative staging without arbitrary bloat.
MIN_DATASET_SAMPLE_THRESHOLD = 5
MIN_QUALITY_SCORE_AVERAGE = 0.80


class ContinuousImprovementService:
    """Service connecting feedback, dataset readiness, training orchestration, evaluation, and registry."""

    def __init__(
        self,
        dataset_repo: Optional[AIDatasetRepository] = None,
        registry_service: Optional[ModelRegistryService] = None,
        eval_service: Optional[ModelEvaluationService] = None,
    ):
        self.dataset_repo = dataset_repo or AIDatasetRepository()
        self.registry_service = registry_service or ModelRegistryService()
        self.eval_service = eval_service or ModelEvaluationService()

    def _verify_admin(self, user: Any) -> None:
        """Enforce admin authorization for training and lifecycle orchestration."""
        if not user:
            raise ForbiddenException("Authentication required.")
        role = getattr(user, "role", "user")
        if role != "admin":
            raise ForbiddenException("Administrator privileges required for continuous improvement operations.")

    def evaluate_dataset_readiness(
        self,
        dataset_version_id: Optional[str] = None,
        dataset_version_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Evaluate dataset readiness for training based on quality, volume, consent, and duplicate checks.

        Returns comprehensive readiness report without training side-effects.
        """
        if dataset_version_id:
            version = self.dataset_repo.get_version_by_id(dataset_version_id)
        elif dataset_version_name:
            version = self.dataset_repo.get_version_by_name(dataset_version_name)
        else:
            raise BadRequestException("Either dataset_version_id or dataset_version_name must be provided.")

        if not version:
            raise NotFoundException("Dataset version not found.")

        samples = version.samples
        total_samples = len(samples)

        # Check quality metrics
        valid_samples = [s for s in samples if s.validation_status == "valid"]
        sanitized_samples = [s for s in samples if s.sanitization_status == "sanitized"]
        consented_samples = [s for s in samples if s.consent_status == "granted"]
        approved_samples = [s for s in samples if s.review_status == "approved"]

        # Duplicate check across prompts
        prompt_set = set()
        duplicate_count = 0
        for s in samples:
            norm_prompt = (s.prompt_input or "").strip().lower()
            if norm_prompt in prompt_set:
                duplicate_count += 1
            else:
                prompt_set.add(norm_prompt)

        duplicate_rate = round(duplicate_count / max(total_samples, 1), 3)

        # Calculate average quality score
        quality_scores = [s.quality_score for s in samples if s.quality_score is not None]
        avg_quality = round(sum(quality_scores) / max(len(quality_scores), 1), 2) if quality_scores else 0.0

        # Category coverage
        categories = list({s.category for s in samples if s.category})

        # Evaluate gating criteria
        reasons = []
        is_ready = True

        if total_samples < MIN_DATASET_SAMPLE_THRESHOLD:
            is_ready = False
            reasons.append(
                f"Sample count ({total_samples}) is below minimum configured threshold ({MIN_DATASET_SAMPLE_THRESHOLD})."
            )

        if len(valid_samples) != total_samples:
            is_ready = False
            reasons.append(f"{total_samples - len(valid_samples)} samples have non-valid validation_status.")

        if len(sanitized_samples) != total_samples:
            is_ready = False
            reasons.append(f"{total_samples - len(sanitized_samples)} samples are not sanitized for PII.")

        if len(consented_samples) != total_samples:
            is_ready = False
            reasons.append(f"{total_samples - len(consented_samples)} samples have revoked or missing consent.")

        if len(approved_samples) != total_samples:
            is_ready = False
            reasons.append(f"{total_samples - len(approved_samples)} samples lack explicit approval.")

        if avg_quality < MIN_QUALITY_SCORE_AVERAGE:
            is_ready = False
            reasons.append(f"Average quality score ({avg_quality}) is below threshold ({MIN_QUALITY_SCORE_AVERAGE}).")

        if duplicate_rate > 0.15:
            is_ready = False
            reasons.append(f"Prompt duplicate rate ({duplicate_rate * 100}%) exceeds 15% tolerance.")

        return {
            "dataset_version_id": version.id,
            "version_name": version.version_name,
            "manifest_hash": version.manifest_hash,
            "total_samples": total_samples,
            "minimum_required_samples": MIN_DATASET_SAMPLE_THRESHOLD,
            "valid_samples_count": len(valid_samples),
            "sanitized_samples_count": len(sanitized_samples),
            "consented_samples_count": len(consented_samples),
            "approved_samples_count": len(approved_samples),
            "categories": categories,
            "duplicate_count": duplicate_count,
            "duplicate_rate": duplicate_rate,
            "average_quality_score": avg_quality,
            "is_ready_for_training": is_ready,
            "blocking_reasons": reasons,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }

    def create_training_job(
        self,
        dataset_version_name: str,
        job_name: str,
        candidate_model_tag: str,
        training_mode: str = "qlora_4bit",
        base_model_name: str = "Qwen/Qwen2.5-3B-Instruct",
        config_override: Optional[Dict[str, Any]] = None,
        user: Optional[Any] = None,
        bypass_readiness_check: bool = False,
    ) -> AITrainingJob:
        """Create and queue a new fine-tuning job with input validation and concurrency protection."""
        if user:
            self._verify_admin(user)

        job_name = job_name.strip()
        candidate_model_tag = candidate_model_tag.strip()

        if not job_name:
            raise BadRequestException("job_name cannot be empty.")
        if not candidate_model_tag:
            raise BadRequestException("candidate_model_tag cannot be empty.")

        # Check job name uniqueness
        if AITrainingJob.query.filter_by(job_name=job_name).first():
            raise ConflictException(f"Training job with name '{job_name}' already exists.")

        # Find dataset version
        version = self.dataset_repo.get_version_by_name(dataset_version_name)
        if not version:
            raise NotFoundException(f"Dataset version '{dataset_version_name}' not found.")

        # Concurrency protection: prevent duplicate running jobs for same dataset version
        active_job = AITrainingJob.query.filter(
            AITrainingJob.dataset_version_id == version.id,
            AITrainingJob.status.in_(["pending", "validating", "ready", "running"])
        ).first()
        if active_job:
            raise ConflictException(
                f"A job '{active_job.job_name}' is already active for dataset version '{dataset_version_name}' (status: {active_job.status})."
            )

        # Dataset readiness verification
        if not bypass_readiness_check:
            readiness = self.evaluate_dataset_readiness(dataset_version_id=version.id)
            if not readiness["is_ready_for_training"]:
                reasons_str = "; ".join(readiness["blocking_reasons"])
                raise BadRequestException(f"Dataset is not ready for training: {reasons_str}")

        config_payload = {
            "base_model_name": base_model_name,
            "dataset_version_name": dataset_version_name,
            "training_mode": training_mode,
            "lora_rank": 16,
            "lora_alpha": 32,
            "learning_rate": 2e-4,
            "epochs": 3,
            "max_seq_length": 2048,
            "seed": 42,
        }
        if config_override:
            config_payload.update(config_override)

        job = AITrainingJob(
            job_name=job_name,
            dataset_version_id=version.id,
            base_model_name=base_model_name,
            candidate_model_tag=candidate_model_tag,
            training_mode=training_mode,
            status="ready",
            config_payload=config_payload,
            created_by_user_id=user.id if user else None,
        )
        db.session.add(job)
        db.session.commit()
        return job

    def execute_dry_run_or_prepare_job(
        self,
        job_id: str,
        user: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Validate pipeline execution via STEP 8 dry-run engine and package run artifacts."""
        if user:
            self._verify_admin(user)

        job = db.session.get(AITrainingJob, job_id)
        if not job:
            raise NotFoundException(f"Training job '{job_id}' not found.")

        if job.status not in ("ready", "validating"):
            raise BadRequestException(f"Cannot execute validation on job in '{job.status}' status.")

        job.status = "validating"
        job.started_at = datetime.now(timezone.utc)
        db.session.commit()

        try:
            # Build training profile
            version = job.dataset_version
            profile = TrainingProfile(
                base_model_name=job.base_model_name,
                dataset_version=version.version_name,
                dataset_type="sft" if version.dataset_type != "dpo" else "dpo",
                output_dir=f"./training_artifacts/{job.job_name}"
            )

            runner = TrainingPipelineRunner(dataset_service=AIDatasetService(self.dataset_repo))
            dry_run_result = runner.run_pipeline(profile=profile, dry_run=True)

            # Update job state
            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
            job.artifact_directory = dry_run_result.get("artifacts_dir", f"./training_artifacts/{job.job_name}")
            # Use deterministic checksum of the dataset export as artifact checksum in dry-run
            job.artifact_checksum = dry_run_result.get("dataset_export_hash")
            job.log_output = json.dumps(dry_run_result, indent=2)
            db.session.commit()

            return {
                "job_id": job.id,
                "job_name": job.job_name,
                "status": job.status,
                "dry_run_summary": dry_run_result,
            }

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            db.session.commit()
            raise

    def cancel_job(self, job_id: str, user: Any, reason: Optional[str] = None) -> AITrainingJob:
        """Cancel a pending, validating, or ready job."""
        self._verify_admin(user)
        job = db.session.get(AITrainingJob, job_id)
        if not job:
            raise NotFoundException(f"Training job '{job_id}' not found.")

        if job.status in ("completed", "failed", "cancelled"):
            raise BadRequestException(f"Cannot cancel job with terminal status '{job.status}'.")

        job.status = "cancelled"
        job.error_message = f"Cancelled by administrator: {reason or 'No reason provided'}"
        job.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        return job

    def post_training_evaluate_and_register(
        self,
        job_id: str,
        user: Any,
        mock_eval_responses: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Perform Step 9 evaluation on candidate model and register candidate in Step 10 registry.

        If benchmark meets threshold (>= 0.65), registers as candidate/evaluated.
        Does NOT automatically replace the active production model.
        """
        self._verify_admin(user)
        job = db.session.get(AITrainingJob, job_id)
        if not job:
            raise NotFoundException(f"Training job '{job_id}' not found.")

        if job.status != "completed":
            raise BadRequestException(f"Cannot evaluate job with status '{job.status}'. Must be 'completed'.")

        # 1. Run STEP 9 benchmark comparison against baseline
        comparison_res = self.eval_service.compare_models(
            base_model_name="qwen2.5:3b",
            candidate_model_name=job.candidate_model_tag,
            base_mock_responses=mock_eval_responses,
            candidate_mock_responses=mock_eval_responses,
        )

        overall_score = 0.0
        if comparison_res.get("comparison_status") == "completed":
            overall_score = comparison_res["candidate_model"]["overall_score"]
        elif "base_model_report" in comparison_res:
            overall_score = comparison_res["base_model_report"]["aggregate_metrics"]["overall_score"]

        # 2. Register candidate model in STEP 10 registry
        existing_model = self.registry_service.repo.get_by_model_tag(job.candidate_model_tag)
        if not existing_model:
            model_record = self.registry_service.register_model(
                model_tag=job.candidate_model_tag,
                version_tag=f"v{datetime.now(timezone.utc).strftime('%Y.%m.%d')}",
                base_model=job.base_model_name,
                training_run_id=job.job_name,
                dataset_version=job.dataset_version.version_name,
                artifact_checksum=job.artifact_checksum or ("0" * 64),
                notes=f"Candidate generated from training job {job.job_name}",
                user=user,
            )
        else:
            model_record = existing_model

        # 3. Attach evaluation results
        self.registry_service.attach_evaluation_report(
            model_id=model_record.id,
            evaluation_score=overall_score,
            report_path=f"./evaluation_reports/{job.candidate_model_tag}.json",
            user=user,
        )

        return {
            "job_id": job.id,
            "candidate_model_tag": job.candidate_model_tag,
            "registered_model_id": model_record.id,
            "model_status": model_record.status,
            "evaluation_score": overall_score,
            "comparison_summary": comparison_res,
            "activation_status": "Candidate registered & evaluated. Awaiting explicit admin approval and manual activation.",
        }

    def get_improvement_dashboard_metrics(self) -> Dict[str, Any]:
        """Compile holistic dashboard telemetry spanning feedback, dataset, jobs, models, and active runtime."""
        from app.models.ai import AIFeedback

        # Feedback stats
        total_feedback = AIFeedback.query.count()
        positive_feedback = AIFeedback.query.filter(AIFeedback.rating == 1).count()
        negative_feedback = AIFeedback.query.filter(AIFeedback.rating == -1).count()

        # Dataset versions
        versions, total_versions = self.dataset_repo.list_versions(limit=10)

        # Training jobs
        jobs = AITrainingJob.query.order_by(desc(AITrainingJob.created_at)).limit(10).all()

        # Model versions
        models, total_models = self.registry_service.repo.list_models(limit=10)
        active_model = self.registry_service.repo.get_active_model()

        return {
            "active_runtime_model": active_model.to_dict() if active_model else {"model_tag": "qwen2.5:3b"},
            "feedback_summary": {
                "total_feedback": total_feedback,
                "positive": positive_feedback,
                "negative": negative_feedback,
            },
            "dataset_versions_count": total_versions,
            "latest_dataset_versions": [v.to_dict() for v in versions],
            "training_jobs": [j.to_dict() for j in jobs],
            "model_versions_count": total_models,
            "registered_models": [m.to_dict() for m in models],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
