"""LifeOS - Advanced AI Automation Blueprint Routes.

REST endpoints for managing automation definitions, triggering workflow runs,
reviewing human-in-the-loop approvals, and monitoring execution logs.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from app.services.automation_service import AutomationService
from app.schemas.automation import (
    CreateAutomationRequest,
    UpdateAutomationRequest,
    ExecuteAutomationRequest,
    RejectApprovalRequest
)
from app.core.response import api_response, error_response
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    ForbiddenException,
    ConflictException
)

automations_bp = Blueprint("automations", __name__)
automation_service = AutomationService()


# -----------------------------------------------------------------------------
# Automation Definitions
# -----------------------------------------------------------------------------

@automations_bp.route("", methods=["GET"])
@jwt_required()
def list_automations():
    """List automation definitions and available system templates for authenticated user."""
    user_id = get_jwt_identity()
    items = automation_service.list_user_automations(user_id)
    return api_response(data={"automations": items}, message="Automations retrieved successfully")


@automations_bp.route("/templates", methods=["GET"])
@jwt_required()
def list_templates():
    """List all available predefined automation templates."""
    templates = automation_service.list_templates()
    return api_response(data={"templates": templates}, message="Automation templates retrieved successfully")


@automations_bp.route("", methods=["POST"])
@jwt_required()
def create_automation():
    """Create a new custom user automation definition."""
    user_id = get_jwt_identity()
    body = request.get_json(silent=True) or {}
    try:
        validated = CreateAutomationRequest(**body)
    except ValidationError as err:
        return error_response(str(err), status_code=400)

    try:
        item = automation_service.create_user_automation(
            user_id=user_id,
            title=validated.title,
            slug=validated.slug,
            description=validated.description,
            category=validated.category,
            trigger_type=validated.trigger_type,
            cron_expression=validated.cron_expression,
            scheduled_time=validated.scheduled_time,
            scheduled_days=validated.scheduled_days,
            configuration=validated.configuration,
        )
        return api_response(data={"automation": item.to_dict()}, message="Automation created successfully", status_code=201)
    except ConflictException as err:
        return error_response(str(err), status_code=409)


@automations_bp.route("/<automation_id>", methods=["GET"])
@jwt_required()
def get_automation(automation_id: str):
    """Retrieve details of a specific automation definition."""
    user_id = get_jwt_identity()
    try:
        item = automation_service.get_automation(automation_id, user_id)
        return api_response(data={"automation": item.to_dict()}, message="Automation retrieved successfully")
    except NotFoundException as err:
        return error_response(str(err), status_code=404)
    except ForbiddenException as err:
        return error_response(str(err), status_code=403)


@automations_bp.route("/<automation_id>", methods=["PATCH"])
@jwt_required()
def update_automation(automation_id: str):
    """Update settings for an existing user automation definition."""
    user_id = get_jwt_identity()
    body = request.get_json(silent=True) or {}
    try:
        validated = UpdateAutomationRequest(**body)
    except ValidationError as err:
        return error_response(str(err), status_code=400)

    try:
        updated = automation_service.update_user_automation(
            automation_id=automation_id,
            current_user_id=user_id,
            **validated.model_dump(exclude_unset=True)
        )
        return api_response(data={"automation": updated.to_dict()}, message="Automation updated successfully")
    except NotFoundException as err:
        return error_response(str(err), status_code=404)
    except ForbiddenException as err:
        return error_response(str(err), status_code=403)


@automations_bp.route("/<automation_id>", methods=["DELETE"])
@jwt_required()
def delete_automation(automation_id: str):
    """Delete a user automation definition."""
    user_id = get_jwt_identity()
    try:
        automation_service.delete_user_automation(automation_id, user_id)
        return api_response(data=None, message="Automation deleted successfully")
    except NotFoundException as err:
        return error_response(str(err), status_code=404)
    except ForbiddenException as err:
        return error_response(str(err), status_code=403)


# -----------------------------------------------------------------------------
# Execution Endpoints
# -----------------------------------------------------------------------------

@automations_bp.route("/<automation_id>/execute", methods=["POST"])
@jwt_required()
def execute_automation(automation_id: str):
    """Trigger an execution run of an automation workflow."""
    user_id = get_jwt_identity()
    body = request.get_json(silent=True) or {}
    try:
        validated = ExecuteAutomationRequest(**body)
    except ValidationError as err:
        return error_response(str(err), status_code=400)

    try:
        execution = automation_service.execute_automation(
            automation_id=automation_id,
            user_id=user_id,
            triggered_by="manual",
            user_request=validated.user_request,
            idempotency_key=validated.idempotency_key
        )
        return api_response(
            data={"execution": execution.to_dict(include_children=True)},
            message="Automation execution initiated successfully",
            status_code=200
        )
    except NotFoundException as err:
        return error_response(str(err), status_code=404)
    except BadRequestException as err:
        return error_response(str(err), status_code=400)


@automations_bp.route("/executions", methods=["GET"])
@jwt_required()
def list_executions():
    """List execution history for authenticated user."""
    user_id = get_jwt_identity()
    definition_id = request.args.get("definition_id")
    status = request.args.get("status")
    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)

    items = automation_service.list_executions(
        user_id=user_id,
        definition_id=definition_id,
        status=status,
        limit=limit,
        offset=offset
    )
    return api_response(data={"executions": items}, message="Executions retrieved successfully")


@automations_bp.route("/executions/<execution_id>", methods=["GET"])
@jwt_required()
def get_execution(execution_id: str):
    """Get full details of a specific execution including actions, approvals, and logs."""
    user_id = get_jwt_identity()
    try:
        execution = automation_service.get_execution(execution_id, user_id)
        return api_response(
            data={"execution": execution.to_dict(include_children=True)},
            message="Execution details retrieved successfully"
        )
    except NotFoundException as err:
        return error_response(str(err), status_code=404)
    except ForbiddenException as err:
        return error_response(str(err), status_code=403)


# -----------------------------------------------------------------------------
# Approval Endpoints (Human-in-the-Loop)
# -----------------------------------------------------------------------------

@automations_bp.route("/approvals/<approval_id>/approve", methods=["POST"])
@jwt_required()
def approve_action(approval_id: str):
    """Approve a pending automation action and execute it immediately."""
    user_id = get_jwt_identity()
    try:
        result = automation_service.approve_action(approval_id, user_id)
        return api_response(data=result, message="Action approved and executed successfully")
    except NotFoundException as err:
        return error_response(str(err), status_code=404)
    except BadRequestException as err:
        return error_response(str(err), status_code=400)


@automations_bp.route("/approvals/<approval_id>/reject", methods=["POST"])
@jwt_required()
def reject_action(approval_id: str):
    """Reject a pending automation action."""
    user_id = get_jwt_identity()
    body = request.get_json(silent=True) or {}
    try:
        validated = RejectApprovalRequest(**body)
    except ValidationError as err:
        return error_response(str(err), status_code=400)

    try:
        result = automation_service.reject_action(approval_id, user_id, reason=validated.reason)
        return api_response(data=result, message="Action rejected successfully")
    except NotFoundException as err:
        return error_response(str(err), status_code=404)
    except BadRequestException as err:
        return error_response(str(err), status_code=400)


# -----------------------------------------------------------------------------
# Operational Control Endpoints: Cancel, Pause, Resume
# -----------------------------------------------------------------------------

@automations_bp.route("/executions/<execution_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_execution(execution_id: str):
    """Cancel an in-flight or awaiting-approval execution."""
    user_id = get_jwt_identity()
    try:
        result = automation_service.cancel_execution(execution_id, user_id)
        return api_response(data=result, message="Execution cancelled successfully")
    except NotFoundException as err:
        return error_response(str(err), status_code=404)
    except BadRequestException as err:
        return error_response(str(err), status_code=400)


@automations_bp.route("/<automation_id>/pause", methods=["POST"])
@jwt_required()
def pause_automation(automation_id: str):
    """Pause an automation definition to halt scheduled runs."""
    user_id = get_jwt_identity()
    try:
        result = automation_service.pause_automation(automation_id, user_id)
        return api_response(data=result, message="Automation paused successfully")
    except NotFoundException as err:
        return error_response(str(err), status_code=404)
    except ForbiddenException as err:
        return error_response(str(err), status_code=403)


@automations_bp.route("/<automation_id>/resume", methods=["POST"])
@jwt_required()
def resume_automation(automation_id: str):
    """Resume a paused automation definition."""
    user_id = get_jwt_identity()
    try:
        result = automation_service.resume_automation(automation_id, user_id)
        return api_response(data=result, message="Automation resumed successfully")
    except NotFoundException as err:
        return error_response(str(err), status_code=404)
    except ForbiddenException as err:
        return error_response(str(err), status_code=403)
