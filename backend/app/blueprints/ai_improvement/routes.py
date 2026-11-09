"""LifeOS - Continuous AI Improvement Blueprint Routes (Step 11).

Exposes APIs for dataset readiness checks, training job lifecycle management,
post-training evaluation & registration, and improvement dashboard telemetry.
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.core.security import admin_required
from app.core.response import api_response
from app.core.exceptions import BadRequestException
from app.services.continuous_improvement_service import ContinuousImprovementService
from app.models.ai import AITrainingJob
from app.models.user import User
from app.extensions import db

ai_improvement_bp = Blueprint("ai_improvement", __name__)


def _get_service() -> ContinuousImprovementService:
    return ContinuousImprovementService()


def _get_user_object(user_id: str):
    return db.session.get(User, user_id)


@ai_improvement_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_improvement_dashboard():
    """Retrieve holistic dashboard telemetry across feedback, datasets, jobs, and models."""
    service = _get_service()
    data = service.get_improvement_dashboard_metrics()
    return api_response(
        data=data,
        message="Continuous improvement dashboard metrics retrieved successfully.",
        status_code=200
    )


@ai_improvement_bp.route("/datasets/<string:version_name>/readiness", methods=["GET"])
@jwt_required()
def check_dataset_readiness(version_name):
    """Evaluate dataset readiness for training (sample volume, PII, consent, duplicates, advisory notes)."""
    min_samples = request.args.get("min_samples", type=int)
    min_quality = request.args.get("min_quality", type=float)
    max_duplicates = request.args.get("max_duplicates", type=float)

    service = _get_service()
    readiness = service.evaluate_dataset_readiness(
        dataset_version_name=version_name,
        min_sample_threshold=min_samples,
        min_quality_score=min_quality,
        max_duplicate_rate=max_duplicates,
    )
    return api_response(
        data=readiness,
        message="Dataset readiness evaluation completed.",
        status_code=200
    )


@ai_improvement_bp.route("/jobs", methods=["GET"])
@jwt_required()
def list_training_jobs():
    """List historical and active model training jobs with pagination."""
    status = request.args.get("status")
    limit = min(int(request.args.get("limit", 20)), 100)
    offset = int(request.args.get("offset", 0))

    query = AITrainingJob.query
    if status:
        query = query.filter(AITrainingJob.status == status)

    total = query.count()
    items = query.order_by(AITrainingJob.created_at.desc()).offset(offset).limit(limit).all()

    return api_response(
        data={
            "items": [j.to_dict() for j in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        },
        message="Training jobs retrieved successfully.",
        status_code=200
    )


@ai_improvement_bp.route("/jobs", methods=["POST"])
@admin_required()
def create_training_job():
    """Create and queue a new training job (Admin only)."""
    user_id = get_jwt_identity()
    user = _get_user_object(user_id)
    data = request.get_json(silent=True) or {}

    dataset_version_name = data.get("dataset_version_name")
    job_name = data.get("job_name")
    candidate_model_tag = data.get("candidate_model_tag")

    if not dataset_version_name or not job_name or not candidate_model_tag:
        raise BadRequestException("dataset_version_name, job_name, and candidate_model_tag are required.")

    service = _get_service()
    job = service.create_training_job(
        dataset_version_name=dataset_version_name,
        job_name=job_name,
        candidate_model_tag=candidate_model_tag,
        training_mode=data.get("training_mode", "qlora_4bit"),
        base_model_name=data.get("base_model_name", "Qwen/Qwen2.5-3B-Instruct"),
        config_override=data.get("config_override"),
        user=user,
        bypass_readiness_check=bool(data.get("bypass_readiness_check", False)),
    )

    return api_response(
        data=job.to_dict(),
        message="Training job created and queued successfully.",
        status_code=201
    )


@ai_improvement_bp.route("/jobs/<string:job_id>/execute", methods=["POST"])
@admin_required()
def execute_training_job(job_id):
    """Execute dry-run validation and prepare training job artifacts (Admin only)."""
    user_id = get_jwt_identity()
    user = _get_user_object(user_id)

    service = _get_service()
    res = service.execute_dry_run_or_prepare_job(job_id=job_id, user=user)

    return api_response(
        data=res,
        message="Training job preparation and dry-run completed successfully.",
        status_code=200
    )


@ai_improvement_bp.route("/jobs/<string:job_id>/record-completion", methods=["POST"])
@admin_required()
def record_gpu_training_completion(job_id):
    """Record verified completion of real external GPU training with cryptographic provenance (Admin only)."""
    user_id = get_jwt_identity()
    user = _get_user_object(user_id)
    data = request.get_json(silent=True) or {}

    artifact_checksum = data.get("artifact_checksum")
    artifact_directory = data.get("artifact_directory")
    metrics = data.get("metrics") or {}

    if not artifact_checksum or not artifact_directory:
        raise BadRequestException("artifact_checksum and artifact_directory are required to record real training completion.")

    service = _get_service()
    res = service.record_gpu_training_completion(
        job_id=job_id,
        artifact_checksum=artifact_checksum,
        artifact_directory=artifact_directory,
        metrics=metrics,
        user=user,
        log_output=data.get("log_output"),
    )

    return api_response(
        data=res,
        message="Real GPU training completion recorded with verified cryptographic provenance.",
        status_code=200
    )


@ai_improvement_bp.route("/jobs/<string:job_id>/cancel", methods=["POST"])
@admin_required()
def cancel_training_job(job_id):
    """Cancel a training job (Admin only)."""
    user_id = get_jwt_identity()
    user = _get_user_object(user_id)
    data = request.get_json(silent=True) or {}

    service = _get_service()
    job = service.cancel_job(job_id=job_id, user=user, reason=data.get("reason"))

    return api_response(
        data=job.to_dict(),
        message="Training job cancelled successfully.",
        status_code=200
    )


@ai_improvement_bp.route("/jobs/<string:job_id>/post-train", methods=["POST"])
@admin_required()
def post_train_evaluate_and_register(job_id):
    """Run Step 9 benchmark on candidate and register in Step 10 registry (Admin only)."""
    user_id = get_jwt_identity()
    user = _get_user_object(user_id)
    data = request.get_json(silent=True) or {}

    service = _get_service()
    res = service.post_training_evaluate_and_register(
        job_id=job_id,
        user=user,
        mock_eval_responses=data.get("mock_eval_responses"),
    )

    return api_response(
        data=res,
        message="Post-training benchmark evaluation and candidate registration completed.",
        status_code=200
    )

