"""LifeOS - AI Memory Blueprint Routes.

Endpoints for inspecting, approving, editing, deleting, and archiving
personal digital brain memories.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.ai_memory import (
    CreateMemoryRequest,
    UpdateMemoryRequest,
    ApproveSuggestionRequest,
    MemorySettingsRequest
)
from app.services.ai_memory_service import AIMemoryService
from app.core.response import api_response

ai_memory_bp = Blueprint("ai_memory", __name__)
memory_service = AIMemoryService()


# ---------------------------------------------------------
# Static Settings & Pending Routes (Placed before /<id>)
# ---------------------------------------------------------

@ai_memory_bp.route("/settings", methods=["GET"])
@jwt_required()
def get_memory_settings():
    """Retrieve memory personalization settings."""
    user_id = get_jwt_identity()
    settings = memory_service.get_settings(user_id)
    return api_response(data=settings, message="Memory settings retrieved successfully")


@ai_memory_bp.route("/settings", methods=["PATCH"])
@jwt_required()
def update_memory_settings():
    """Enable or disable memory personalization."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = MemorySettingsRequest(**json_data)

    result = memory_service.update_settings(user_id, validated.ai_memory_enabled)
    return api_response(data=result, message="Memory settings updated successfully")


@ai_memory_bp.route("/pending", methods=["GET"])
@jwt_required()
def list_pending_suggestions():
    """List candidate memory suggestions waiting for user approval."""
    user_id = get_jwt_identity()
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)

    result = memory_service.list_pending_suggestions(user_id=user_id, limit=limit, offset=offset)
    return api_response(data=result, message="Pending suggestions retrieved successfully")


# ---------------------------------------------------------
# Memory CRUD Endpoints
# ---------------------------------------------------------

@ai_memory_bp.route("", methods=["POST"])
@jwt_required()
def create_memory():
    """Manually add a confirmed memory."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateMemoryRequest(**json_data)

    memory = memory_service.create_memory(
        user_id=user_id,
        memory_key=validated.memory_key,
        memory_value=validated.memory_value,
        memory_type=validated.memory_type,
        confidence=validated.confidence,
        status="confirmed",
        expires_at=validated.expires_at
    )

    return api_response(
        data={"memory": memory.to_dict()},
        message="Memory created successfully",
        status_code=201
    )


@ai_memory_bp.route("", methods=["GET"])
@jwt_required()
def list_confirmed_memories():
    """List confirmed memories for the user with search and category filters."""
    user_id = get_jwt_identity()
    category = request.args.get("category")
    search = request.args.get("search")
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)

    result = memory_service.list_confirmed_memories(
        user_id=user_id,
        category=category,
        search=search,
        limit=limit,
        offset=offset
    )

    return api_response(data=result, message="Memories retrieved successfully")


@ai_memory_bp.route("/<memory_id>", methods=["GET"])
@jwt_required()
def get_memory(memory_id: str):
    """Retrieve details for a single memory record."""
    user_id = get_jwt_identity()
    memory = memory_service.get_memory(memory_id, user_id)
    return api_response(data={"memory": memory.to_dict()}, message="Memory retrieved successfully")


@ai_memory_bp.route("/<memory_id>", methods=["PATCH"])
@jwt_required()
def update_memory(memory_id: str):
    """Edit memory key, value, or category."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = UpdateMemoryRequest(**json_data)

    updates = validated.model_dump(exclude_unset=True)
    memory = memory_service.update_memory(memory_id, user_id, updates)

    return api_response(data={"memory": memory.to_dict()}, message="Memory updated successfully")


@ai_memory_bp.route("/<memory_id>", methods=["DELETE"])
@jwt_required()
def delete_memory(memory_id: str):
    """Permanently delete a memory record."""
    user_id = get_jwt_identity()
    memory_service.delete_memory(memory_id, user_id)
    return api_response(data=None, message="Memory deleted successfully")


# ---------------------------------------------------------
# Approval Workflow Endpoints
# ---------------------------------------------------------

@ai_memory_bp.route("/<memory_id>/approve", methods=["POST"])
@jwt_required()
def approve_suggestion(memory_id: str):
    """Approve a pending memory suggestion (with optional edits)."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = ApproveSuggestionRequest(**json_data)

    memory = memory_service.approve_suggestion(
        memory_id=memory_id,
        current_user_id=user_id,
        edited_key=validated.get_resolved_key(),
        edited_value=validated.get_resolved_value(),
        edited_type=validated.get_resolved_type()
    )

    return api_response(
        data={"memory": memory.to_dict()},
        message="Memory approved and confirmed successfully"
    )


@ai_memory_bp.route("/<memory_id>/reject", methods=["POST"])
@jwt_required()
def reject_suggestion(memory_id: str):
    """Reject and dismiss a pending memory suggestion."""
    user_id = get_jwt_identity()
    memory_service.reject_suggestion(memory_id, user_id)
    return api_response(data=None, message="Suggestion rejected and dismissed successfully")


@ai_memory_bp.route("/<memory_id>/archive", methods=["POST"])
@jwt_required()
def archive_memory(memory_id: str):
    """Archive a confirmed memory to exclude it from future retrieval."""
    user_id = get_jwt_identity()
    memory = memory_service.archive_memory(memory_id, user_id)
    return api_response(data={"memory": memory.to_dict()}, message="Memory archived successfully")
