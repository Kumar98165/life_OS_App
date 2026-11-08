"""LifeOS - AI Prompt Versioning Blueprint Routes.

Admin-protected endpoints for creating, inspecting, listing, and activating
immutable AI system prompt versions.
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from app.schemas.ai_prompt import CreatePromptVersionRequest
from app.services.ai_prompt_service import AIPromptService
from app.core.security import admin_required
from app.core.response import api_response

ai_prompt_bp = Blueprint("ai_prompt", __name__)
prompt_service = AIPromptService()


@ai_prompt_bp.route("", methods=["POST"])
@admin_required()
def create_prompt_version():
    """Create a new immutable AI system prompt version.

    Only accessible by users possessing the 'admin' role.
    """
    admin_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreatePromptVersionRequest(**json_data)

    version = prompt_service.create_version(
        version_tag=validated.version_tag,
        prompt_template=validated.prompt_template,
        change_summary=validated.change_summary,
        created_by=admin_id,
        activate_immediately=validated.activate_immediately or False
    )

    return api_response(
        data={"prompt": version.to_dict()},
        message=f"Prompt version '{version.version_tag}' created successfully",
        status_code=201
    )


@ai_prompt_bp.route("", methods=["GET"])
@admin_required()
def list_prompt_versions():
    """List all AI prompt versions with pagination."""
    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)

    result = prompt_service.list_versions(limit=limit, offset=offset)

    return api_response(
        data=result,
        message="Prompt versions retrieved successfully"
    )


@ai_prompt_bp.route("/active", methods=["GET"])
@admin_required()
def get_active_prompt_version():
    """Retrieve the currently active prompt version.

    If no prompt has been created yet, automatically initializes and returns
    the baseline v1.0.0 prompt version.
    """
    version = prompt_service.get_active_prompt_or_initialize()

    return api_response(
        data={"prompt": version.to_dict()},
        message="Active prompt version retrieved successfully"
    )


@ai_prompt_bp.route("/<prompt_id>", methods=["GET"])
@admin_required()
def get_prompt_version(prompt_id: str):
    """Retrieve details of a specific prompt version by ID."""
    version = prompt_service.get_version_by_id(prompt_id)

    return api_response(
        data={"prompt": version.to_dict()},
        message="Prompt version retrieved successfully"
    )


@ai_prompt_bp.route("/<prompt_id>/activate", methods=["POST"])
@admin_required()
def activate_prompt_version(prompt_id: str):
    """Transactionally activate a prompt version (or roll back to an older version).

    Ensures single-active partial unique index invariant without mutating
    immutable template content.
    """
    version = prompt_service.activate_version(prompt_id)

    return api_response(
        data={"prompt": version.to_dict()},
        message=f"Prompt version '{version.version_tag}' activated successfully"
    )

