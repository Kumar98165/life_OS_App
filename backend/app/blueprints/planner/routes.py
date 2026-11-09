from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.planner import (
    CreatePlannerBlockRequest,
    UpdatePlannerBlockRequest,
    UpdateBlockStatusRequest
)
from app.services.planner_service import PlannerService
from app.core.response import api_response
from app.core.exceptions import BadRequestException

planner_bp = Blueprint("planner", __name__)
planner_service = PlannerService()


def parse_iso_datetime(dt_str: str) -> datetime:
    """Safely parse ISO 8601 datetime handling URL-decoded spaces and Z suffixes."""
    val = dt_str.strip().replace("Z", "+00:00")
    # If URL decoding replaced '+' with ' ', restore '+' for timezone offset
    if " " in val and "+" not in val and "-" not in val[10:]:
        val = val.replace(" ", "+")
    return datetime.fromisoformat(val)


@planner_bp.route("/blocks", methods=["POST"])
@jwt_required()
def create_block():
    """Create a new planner block for the authenticated user."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreatePlannerBlockRequest(**json_data)

    block = planner_service.create_block(
        user_id=user_id,
        title=validated.title,
        start_time=validated.start_time,
        end_time=validated.end_time,
        description=validated.description,
        block_type=validated.block_type,
        status=validated.status,
        task_id=validated.task_id,
        color_hex=validated.color_hex,
        recurrence_rule=validated.recurrence_rule,
        reminder_minutes_before=validated.reminder_minutes_before,
        timezone=validated.timezone
    )

    return api_response(
        data={"block": block.to_dict()},
        message="Planner block scheduled successfully",
        status_code=201
    )


@planner_bp.route("/blocks", methods=["GET"])
@jwt_required()
def list_blocks():
    """List planner blocks for authenticated user within date range."""
    user_id = get_jwt_identity()

    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    status = request.args.get("status")
    block_type = request.args.get("block_type")
    task_id = request.args.get("task_id")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    start_date = None
    if start_date_str:
        try:
            start_date = parse_iso_datetime(start_date_str)
        except ValueError:
            raise BadRequestException("Invalid start_date ISO format")

    end_date = None
    if end_date_str:
        try:
            end_date = parse_iso_datetime(end_date_str)
        except ValueError:
            raise BadRequestException("Invalid end_date ISO format")

    blocks, meta = planner_service.list_blocks(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
        block_type=block_type,
        task_id=task_id,
        page=page,
        per_page=per_page
    )

    return api_response(
        data={"blocks": [b.to_dict() for b in blocks]},
        message="Planner blocks retrieved successfully",
        meta=meta
    )


@planner_bp.route("/blocks/<block_id>", methods=["GET"])
@jwt_required()
def get_block(block_id: str):
    """Retrieve details of a specific planner block."""
    user_id = get_jwt_identity()
    block = planner_service.get_block(block_id, user_id)

    return api_response(
        data={"block": block.to_dict()},
        message="Planner block retrieved successfully"
    )


@planner_bp.route("/blocks/<block_id>", methods=["PATCH"])
@jwt_required()
def update_block(block_id: str):
    """Update fields of an existing planner block."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = UpdatePlannerBlockRequest(**json_data)

    update_fields = validated.model_dump(exclude_unset=True)
    block = planner_service.update_block(block_id, user_id, **update_fields)

    return api_response(
        data={"block": block.to_dict()},
        message="Planner block updated successfully"
    )


@planner_bp.route("/blocks/<block_id>", methods=["DELETE"])
@jwt_required()
def delete_block(block_id: str):
    """Delete a planner block."""
    user_id = get_jwt_identity()
    planner_service.delete_block(block_id, user_id)

    return api_response(
        data={},
        message="Planner block deleted successfully"
    )


@planner_bp.route("/blocks/<block_id>/status", methods=["PATCH"])
@jwt_required()
def update_block_status(block_id: str):
    """Update status of a planner block (scheduled, completed, cancelled, skipped)."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = UpdateBlockStatusRequest(**json_data)

    block = planner_service.update_block_status(block_id, user_id, validated.status)

    return api_response(
        data={"block": block.to_dict()},
        message="Planner block status updated successfully"
    )


@planner_bp.route("/summary/daily", methods=["GET"])
@jwt_required()
def get_daily_summary():
    """Retrieve daily planner summary metrics for a calendar day."""
    user_id = get_jwt_identity()
    date_str = request.args.get("date")  # Format: YYYY-MM-DD
    tz_offset = request.args.get("tz_offset", 0.0, type=float)

    summary = planner_service.get_daily_summary(
        user_id=user_id,
        target_date_str=date_str,
        utc_offset_hours=tz_offset
    )

    return api_response(
        data=summary,
        message="Daily planner summary retrieved successfully"
    )


@planner_bp.route("/free-time", methods=["GET"])
@jwt_required()
def get_free_time():
    """Calculate non-overlapping available free time slots for a day."""
    user_id = get_jwt_identity()
    date_str = request.args.get("date")
    if not date_str:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
    start_hour = request.args.get("start_hour", 8, type=int)
    end_hour = request.args.get("end_hour", 20, type=int)
    tz_offset = request.args.get("tz_offset", 0.0, type=float)

    slots = planner_service.get_free_time_slots(
        user_id=user_id,
        target_date_str=date_str,
        start_hour=start_hour,
        end_hour=end_hour,
        utc_offset_hours=tz_offset
    )
    return api_response(data={"free_slots": slots, "date": date_str}, message="Free time slots calculated")


@planner_bp.route("/export.ics", methods=["GET"])
@jwt_required()
def export_calendar_ics():
    """Export all scheduled planner events into an iCalendar (.ics) stream."""
    from flask import Response
    user_id = get_jwt_identity()
    ical_content = planner_service.export_ical(user_id)
    return Response(
        ical_content,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=lifeos_calendar.ics"}
    )
