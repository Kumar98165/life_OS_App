from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.focus_service import FocusService
from app.schemas.focus import (
    FocusGoalUpdateSchema,
    CreateFocusSessionSchema,
    LogDistractionSchema,
    CompleteFocusSessionSchema
)
from app.core.response import api_response

focus_bp = Blueprint("focus", __name__)
focus_service = FocusService()


@focus_bp.route("/goal", methods=["GET"])
@jwt_required()
def get_goal():
    user_id = get_jwt_identity()
    goal = focus_service.get_or_create_goal(user_id)
    return api_response(data={"goal": goal.to_dict()}, message="Focus goal retrieved")


@focus_bp.route("/goal", methods=["PATCH", "PUT"])
@jwt_required()
def update_goal():
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = FocusGoalUpdateSchema(**json_data)
    goal = focus_service.update_goal(user_id, validated.model_dump(exclude_unset=True))
    return api_response(data={"goal": goal.to_dict()}, message="Focus goal updated")


@focus_bp.route("/sessions/active", methods=["GET"])
@jwt_required()
def get_active_session():
    user_id = get_jwt_identity()
    session = focus_service.get_active_session(user_id)
    return api_response(
        data={"session": session.to_dict() if session else None},
        message="Active session retrieved"
    )


@focus_bp.route("/sessions", methods=["POST"])
@jwt_required()
def start_session():
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateFocusSessionSchema(**json_data)
    session = focus_service.start_session(
        user_id=user_id,
        title=validated.title or "Focus Session",
        session_type=validated.session_type,
        target_duration_minutes=validated.target_duration_minutes,
        task_id=validated.task_id,
        planner_block_id=validated.planner_block_id,
        notes=validated.notes
    )
    return api_response(data={"session": session.to_dict()}, message="Focus session started", status_code=201)


@focus_bp.route("/sessions/<session_id>/pause", methods=["POST"])
@jwt_required()
def pause_session(session_id: str):
    user_id = get_jwt_identity()
    session = focus_service.pause_session(user_id, session_id)
    return api_response(data={"session": session.to_dict()}, message="Focus session paused")


@focus_bp.route("/sessions/<session_id>/resume", methods=["POST"])
@jwt_required()
def resume_session(session_id: str):
    user_id = get_jwt_identity()
    session = focus_service.resume_session(user_id, session_id)
    return api_response(data={"session": session.to_dict()}, message="Focus session resumed")


@focus_bp.route("/sessions/<session_id>/stop", methods=["POST"])
@jwt_required()
def stop_session(session_id: str):
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CompleteFocusSessionSchema(**json_data)
    session = focus_service.stop_session(
        user_id=user_id,
        session_id=session_id,
        actual_duration_seconds=validated.actual_duration_seconds,
        status="completed",
        notes=validated.notes
    )
    return api_response(data={"session": session.to_dict()}, message="Focus session stopped and saved")


@focus_bp.route("/sessions/<session_id>/distractions", methods=["POST"])
@jwt_required()
def log_distraction(session_id: str):
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = LogDistractionSchema(**json_data)
    distraction = focus_service.log_distraction(
        user_id=user_id,
        session_id=session_id,
        distraction_type=validated.distraction_type,
        description=validated.description
    )
    return api_response(
        data={"distraction": distraction.to_dict()},
        message="Distraction logged successfully",
        status_code=201
    )


@focus_bp.route("/sessions", methods=["GET"])
@jwt_required()
def list_sessions():
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    session_type = request.args.get("session_type")

    sessions, meta = focus_service.list_sessions(
        user_id=user_id,
        page=page,
        per_page=per_page,
        session_type=session_type
    )
    return api_response(
        data={"sessions": [s.to_dict() for s in sessions]},
        message="Focus sessions retrieved",
        meta=meta
    )


@focus_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_statistics():
    user_id = get_jwt_identity()
    stats = focus_service.get_statistics(user_id)
    return api_response(data={"stats": stats}, message="Focus statistics retrieved")
