"""LifeOS - Habit Blueprint Routes.

Implements RESTful endpoints for habit CRUD, daily check-in logging,
historical logs, streak calculations, and daily/weekly/monthly summaries.
"""
from datetime import date
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.habit import (
    CreateHabitRequest,
    UpdateHabitRequest,
    CreateHabitLogRequest
)
from app.services.habit_service import HabitService
from app.core.response import api_response
from app.core.exceptions import BadRequestException

habits_bp = Blueprint("habits", __name__)
habit_service = HabitService()


# ---------------------------------------------------------
# Global Summary Endpoints (Placed before /<habit_id>)
# ---------------------------------------------------------

@habits_bp.route("/summary/daily", methods=["GET"])
@jwt_required()
def get_daily_summary():
    """Retrieve completion overview for all active user habits for a specific day."""
    user_id = get_jwt_identity()
    date_str = request.args.get("date")
    target_date = None
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise BadRequestException("Invalid date format. Expected YYYY-MM-DD.")

    summary = habit_service.get_daily_summary(user_id=user_id, target_date=target_date)
    return api_response(
        data=summary,
        message="Daily habit summary retrieved successfully"
    )


@habits_bp.route("/summary/weekly", methods=["GET"])
@jwt_required()
def get_weekly_summary():
    """Retrieve 7-day completion breakdown starting from Monday."""
    user_id = get_jwt_identity()
    week_start_str = request.args.get("week_start")
    week_start = None
    if week_start_str:
        try:
            week_start = date.fromisoformat(week_start_str)
        except ValueError:
            raise BadRequestException("Invalid week_start format. Expected YYYY-MM-DD.")

    summary = habit_service.get_weekly_summary(user_id=user_id, week_start=week_start)
    return api_response(
        data=summary,
        message="Weekly habit summary retrieved successfully"
    )


@habits_bp.route("/summary/monthly", methods=["GET"])
@jwt_required()
def get_monthly_summary():
    """Retrieve monthly calendar completion breakdown."""
    user_id = get_jwt_identity()
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    summary = habit_service.get_monthly_summary(user_id=user_id, year=year, month=month)
    return api_response(
        data=summary,
        message="Monthly habit summary retrieved successfully"
    )


# ---------------------------------------------------------
# Habit CRUD Endpoints
# ---------------------------------------------------------

@habits_bp.route("", methods=["POST"])
@jwt_required()
def create_habit():
    """Create a new habit for the authenticated user."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateHabitRequest(**json_data)

    habit = habit_service.create_habit(
        user_id=user_id,
        title=validated.title,
        description=validated.description,
        frequency=validated.frequency,
        target_days_per_week=validated.target_days_per_week,
        color_hex=validated.color_hex,
        icon=validated.icon
    )

    return api_response(
        data={"habit": habit.to_dict()},
        message="Habit created successfully",
        status_code=201
    )


@habits_bp.route("", methods=["GET"])
@jwt_required()
def list_habits():
    """List habits for authenticated user with today's completion status."""
    user_id = get_jwt_identity()
    include_archived = request.args.get("include_archived", "false").lower() == "true"
    frequency = request.args.get("frequency")

    habits = habit_service.list_habits(
        user_id=user_id,
        include_archived=include_archived,
        frequency=frequency
    )

    return api_response(
        data={"habits": habits},
        message="Habits retrieved successfully"
    )


@habits_bp.route("/<habit_id>", methods=["GET"])
@jwt_required()
def get_habit(habit_id: str):
    """Retrieve habit details."""
    user_id = get_jwt_identity()
    habit = habit_service.get_habit(habit_id, user_id)

    today = date.today()
    today_log = habit_service.habit_repo.get_log(habit.id, today)

    habit_dict = habit.to_dict()
    habit_dict["completed_today"] = bool(today_log and today_log.completed)
    habit_dict["today_log_id"] = today_log.id if today_log else None

    return api_response(
        data={"habit": habit_dict},
        message="Habit retrieved successfully"
    )


@habits_bp.route("/<habit_id>", methods=["PATCH"])
@jwt_required()
def update_habit(habit_id: str):
    """Update fields of an existing habit."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = UpdateHabitRequest(**json_data)

    update_fields = validated.model_dump(exclude_unset=True)
    habit = habit_service.update_habit(habit_id, user_id, update_fields)

    return api_response(
        data={"habit": habit.to_dict()},
        message="Habit updated successfully"
    )


@habits_bp.route("/<habit_id>", methods=["DELETE"])
@jwt_required()
def delete_habit(habit_id: str):
    """Delete a habit and its logs."""
    user_id = get_jwt_identity()
    habit_service.delete_habit(habit_id, user_id)

    return api_response(
        data=None,
        message="Habit deleted successfully"
    )


# ---------------------------------------------------------
# Daily Check-In Logs & Stats Endpoints
# ---------------------------------------------------------

@habits_bp.route("/<habit_id>/logs", methods=["POST"])
@jwt_required()
def log_check_in(habit_id: str):
    """Record or update a check-in log for a habit."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateHabitLogRequest(**json_data)

    log = habit_service.log_check_in(
        habit_id=habit_id,
        current_user_id=user_id,
        log_date=validated.log_date,
        completed=validated.completed,
        notes=validated.notes
    )

    habit = habit_service.get_habit(habit_id, user_id)

    return api_response(
        data={
            "log": log.to_dict(),
            "habit": habit.to_dict()
        },
        message="Check-in recorded successfully",
        status_code=201
    )


@habits_bp.route("/<habit_id>/logs", methods=["GET"])
@jwt_required()
def get_habit_logs(habit_id: str):
    """Retrieve historical logs for a habit."""
    user_id = get_jwt_identity()
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    limit = request.args.get("limit", 100, type=int)

    start_date = None
    end_date = None
    try:
        if start_date_str:
            start_date = date.fromisoformat(start_date_str)
        if end_date_str:
            end_date = date.fromisoformat(end_date_str)
    except ValueError:
        raise BadRequestException("Invalid date format. Expected YYYY-MM-DD.")

    logs = habit_service.get_habit_logs(
        habit_id=habit_id,
        current_user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )

    return api_response(
        data={"logs": [log.to_dict() for log in logs]},
        message="Habit logs retrieved successfully"
    )


@habits_bp.route("/<habit_id>/logs/<log_id>", methods=["DELETE"])
@jwt_required()
def undo_check_in(habit_id: str, log_id: str):
    """Undo a check-in log and recompute streaks."""
    user_id = get_jwt_identity()
    habit_service.undo_check_in(habit_id, log_id, user_id)
    habit = habit_service.get_habit(habit_id, user_id)

    return api_response(
        data={"habit": habit.to_dict()},
        message="Check-in removed successfully"
    )


@habits_bp.route("/<habit_id>/stats", methods=["GET"])
@jwt_required()
def get_habit_stats(habit_id: str):
    """Compute habit streak and consistency statistics."""
    user_id = get_jwt_identity()
    stats_data = habit_service.get_habit_stats(habit_id, user_id)

    return api_response(
        data=stats_data,
        message="Habit statistics calculated successfully"
    )

