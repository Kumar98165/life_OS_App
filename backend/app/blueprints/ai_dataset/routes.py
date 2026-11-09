"""LifeOS - AI Dataset Management Blueprint Routes (Step 7).

Endpoints for dataset sample listing, curation reviews, snapshot versioning,
statistics aggregation, and authorized JSONL exports.
"""
from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.core.security import admin_required
from app.core.response import api_response
from app.services.ai_dataset_service import AIDatasetService
from app.schemas.ai_dataset import (
    DatasetSampleFilterQuery,
    ReviewSampleRequest,
    CreateDatasetVersionRequest,
)

ai_dataset_bp = Blueprint("ai_dataset", __name__)
dataset_service = AIDatasetService()


# ---------------------------------------------------------
# Training Sample Listing, Review & Stats
# ---------------------------------------------------------

@ai_dataset_bp.route("/datasets/samples", methods=["GET"])
@admin_required()
def list_samples():
    """List training samples with optional category, validation, and review filters."""
    category = request.args.get("category")
    validation_status = request.args.get("validation_status")
    sanitization_status = request.args.get("sanitization_status")
    review_status = request.args.get("review_status")
    consent_status = request.args.get("consent_status")
    dataset_version_id = request.args.get("dataset_version_id")
    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)

    samples, total = dataset_service.dataset_repo.list_samples(
        category=category,
        validation_status=validation_status,
        sanitization_status=sanitization_status,
        review_status=review_status,
        consent_status=consent_status,
        dataset_version_id=dataset_version_id,
        limit=min(max(limit, 1), 100),
        offset=max(offset, 0)
    )

    return api_response(
        data={
            "samples": [s.to_dict() for s in samples],
            "total": total,
            "limit": limit,
            "offset": offset
        },
        message="Dataset samples retrieved successfully"
    )


@ai_dataset_bp.route("/datasets/samples/<sample_id>/review", methods=["PATCH"])
@admin_required()
def review_sample(sample_id: str):
    """Approve or reject a candidate training sample."""
    json_data = request.get_json(silent=True) or {}
    validated = ReviewSampleRequest(**json_data)

    updated = dataset_service.review_sample(
        sample_id=sample_id,
        review_status=validated.review_status,
        quality_score=validated.quality_score,
        validation_notes=validated.validation_notes
    )

    return api_response(
        data={"sample": updated.to_dict()},
        message=f"Sample marked as {validated.review_status}"
    )


@ai_dataset_bp.route("/datasets/samples/<sample_id>", methods=["DELETE"])
@admin_required()
def delete_sample(sample_id: str):
    """Delete an ineligible or rejected training sample."""
    dataset_service.delete_sample(sample_id)
    return api_response(
        data=None,
        message="Sample deleted successfully"
    )


@ai_dataset_bp.route("/datasets/statistics", methods=["GET"])
@admin_required()
def get_dataset_statistics():
    """Retrieve aggregate statistics on dataset samples, reviews, and categories."""
    stats = dataset_service.dataset_repo.get_dataset_statistics()
    return api_response(
        data=stats,
        message="Dataset statistics retrieved successfully"
    )


# ---------------------------------------------------------
# Dataset Versioning & Snapshots
# ---------------------------------------------------------

@ai_dataset_bp.route("/datasets/versions", methods=["POST"])
@admin_required()
def create_version_snapshot():
    """Create an immutable snapshot version of approved, validated, and sanitized records."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateDatasetVersionRequest(**json_data)

    version = dataset_service.create_version_snapshot(
        version_name=validated.version_name,
        description=validated.description,
        dataset_type=validated.dataset_type,
        categories=validated.categories,
        created_by_user_id=user_id
    )

    return api_response(
        data={"version": version.to_dict()},
        message="Dataset version snapshot created successfully",
        status_code=201
    )


@ai_dataset_bp.route("/datasets/versions", methods=["GET"])
@admin_required()
def list_versions():
    """List immutable dataset version snapshots."""
    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)

    versions, total = dataset_service.dataset_repo.list_versions(
        limit=min(max(limit, 1), 100),
        offset=max(offset, 0)
    )

    return api_response(
        data={
            "versions": [v.to_dict() for v in versions],
            "total": total,
            "limit": limit,
            "offset": offset
        },
        message="Dataset versions retrieved successfully"
    )


@ai_dataset_bp.route("/datasets/versions/<version_name>", methods=["GET"])
@admin_required()
def get_version(version_name: str):
    """Retrieve details and manifest summary of a specific dataset version."""
    version = dataset_service.dataset_repo.get_version_by_name(version_name)
    if not version:
        return api_response(message=f"Version '{version_name}' not found", status_code=404)

    return api_response(
        data={"version": version.to_dict()},
        message="Dataset version retrieved successfully"
    )


# ---------------------------------------------------------
# JSONL Export Endpoint
# ---------------------------------------------------------

@ai_dataset_bp.route("/datasets/versions/<version_name>/export", methods=["GET"])
@admin_required()
def export_version_jsonl(version_name: str):
    """Export a version snapshot as a validated JSONL payload."""
    content, manifest_hash, metadata = dataset_service.export_version_jsonl(version_name)

    # Return as downloadable text/plain or json lines with manifest headers
    response = Response(content, mimetype="application/x-jsonlines")
    response.headers["Content-Disposition"] = f'attachment; filename="{version_name}.jsonl"'
    response.headers["X-Manifest-SHA256"] = manifest_hash
    response.headers["X-Sample-Count"] = str(metadata["sample_count"])
    return response
