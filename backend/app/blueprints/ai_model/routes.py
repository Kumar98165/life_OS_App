"""LifeOS - AI Model Version Management Blueprint (Step 10).

Exposes REST APIs for listing, registering, approving, activating, and rolling back
AI model versions in the registry. Restricted to authenticated administrators.
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.core.security import admin_required
from app.core.response import api_response
from app.core.exceptions import BadRequestException
from app.services.model_registry_service import ModelRegistryService
from app.repositories.ai_model_version_repository import AIModelVersionRepository
from app.models.user import User
from app.extensions import db

ai_model_bp = Blueprint("ai_model", __name__)


def _get_service() -> ModelRegistryService:
    return ModelRegistryService()


def _get_user_object(user_id: str):
    return db.session.get(User, user_id)


@ai_model_bp.route("", methods=["GET"])
@jwt_required()
def list_models():
    """List registered AI model versions with pagination and filtering."""
    status = request.args.get("status")
    base_model = request.args.get("base_model")
    limit = min(int(request.args.get("limit", 20)), 100)
    offset = int(request.args.get("offset", 0))

    repo = AIModelVersionRepository()
    items, total = repo.list_models(status=status, base_model=base_model, limit=limit, offset=offset)

    return api_response(
        data={
            "items": [m.to_dict() for m in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        },
        message="AI models retrieved successfully",
        status_code=200
    )


@ai_model_bp.route("/active", methods=["GET"])
@jwt_required()
def get_active_model():
    """Retrieve currently active runtime AI model."""
    service = _get_service()
    active = service.repo.get_active_model()
    if not active:
        active = service.initialize_default_base_model()

    return api_response(
        data=active.to_dict(),
        message="Active AI model retrieved successfully",
        status_code=200
    )


@ai_model_bp.route("", methods=["POST"])
@admin_required()
def register_model():
    """Register a new AI model version (Admin only)."""
    user_id = get_jwt_identity()
    user = _get_user_object(user_id)
    data = request.get_json(silent=True) or {}
    model_tag = data.get("model_tag")
    version_tag = data.get("version_tag")

    if not model_tag or not version_tag:
        raise BadRequestException("model_tag and version_tag are required.")

    service = _get_service()
    model = service.register_model(
        model_tag=model_tag,
        version_tag=version_tag,
        base_model=data.get("base_model", "Qwen/Qwen2.5-3B-Instruct"),
        training_run_id=data.get("training_run_id"),
        dataset_version=data.get("dataset_version"),
        artifact_checksum=data.get("artifact_checksum"),
        notes=data.get("notes"),
        user=user,
    )

    return api_response(
        data=model.to_dict(),
        message="AI model version registered successfully.",
        status_code=201
    )


@ai_model_bp.route("/<string:model_id>/evaluate", methods=["POST"])
@admin_required()
def attach_evaluation(model_id):
    """Attach benchmark evaluation results to a registered model (Admin only)."""
    user_id = get_jwt_identity()
    user = _get_user_object(user_id)
    data = request.get_json(silent=True) or {}
    score = data.get("evaluation_score")
    if score is None:
        raise BadRequestException("evaluation_score is required.")

    service = _get_service()
    model = service.attach_evaluation_report(
        model_id=model_id,
        evaluation_score=float(score),
        report_path=data.get("report_path"),
        user=user,
    )

    return api_response(
        data=model.to_dict(),
        message="Evaluation attached successfully.",
        status_code=200
    )


@ai_model_bp.route("/<string:model_id>/approve", methods=["POST"])
@admin_required()
def approve_model(model_id):
    """Approve an evaluated model version (Admin only)."""
    user_id = get_jwt_identity()
    user = _get_user_object(user_id)
    data = request.get_json(silent=True) or {}
    service = _get_service()
    model = service.approve_model(
        model_id=model_id,
        user=user,
        notes=data.get("notes")
    )

    return api_response(
        data=model.to_dict(),
        message="Model version approved successfully.",
        status_code=200
    )


@ai_model_bp.route("/<string:model_id>/activate", methods=["POST"])
@admin_required()
def activate_model(model_id):
    """Safely activate an approved model version into active runtime (Admin only)."""
    user_id = get_jwt_identity()
    user = _get_user_object(user_id)
    data = request.get_json(silent=True) or {}
    reason = data.get("reason", "Manual activation by administrator.")

    service = _get_service()
    log_entry = service.activate_model(
        model_id=model_id,
        user=user,
        reason=reason,
        allow_offline_mock=bool(data.get("allow_offline_mock", False))
    )

    return api_response(
        data=log_entry.to_dict(),
        message="Model activated successfully.",
        status_code=200
    )


@ai_model_bp.route("/rollback", methods=["POST"])
@admin_required()
def rollback_model():
    """Roll back active model to a specified previously approved model version (Admin only)."""
    user_id = get_jwt_identity()
    user = _get_user_object(user_id)
    data = request.get_json(silent=True) or {}
    target_model_id = data.get("target_model_id")
    reason = data.get("reason")

    if not target_model_id or not reason:
        raise BadRequestException("target_model_id and reason are required for model rollback.")

    service = _get_service()
    log_entry = service.rollback_model(
        target_model_id=target_model_id,
        user=user,
        reason=reason,
        allow_offline_mock=bool(data.get("allow_offline_mock", False))
    )

    return api_response(
        data=log_entry.to_dict(),
        message="Model rolled back successfully.",
        status_code=200
    )


@ai_model_bp.route("/audit-logs", methods=["GET"])
@jwt_required()
def list_audit_logs():
    """List model activation and rollback audit trail."""
    limit = min(int(request.args.get("limit", 20)), 100)
    offset = int(request.args.get("offset", 0))

    repo = AIModelVersionRepository()
    items, total = repo.list_audit_logs(limit=limit, offset=offset)

    return api_response(
        data={
            "items": [log.to_dict() for log in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        },
        message="Audit logs retrieved successfully",
        status_code=200
    )
