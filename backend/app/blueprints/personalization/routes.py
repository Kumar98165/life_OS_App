"""LifeOS - Personalization Blueprint Routes.

Endpoints:
- GET   /api/v1/personalization            (Get full personalization config)
- PATCH /api/v1/personalization            (Update personalization settings)
- GET   /api/v1/personalization/dashboard  (Get dashboard widgets & density)
- PATCH /api/v1/personalization/dashboard  (Update dashboard widgets & density)
- GET   /api/v1/personalization/routine    (Get daily routine settings)
- PATCH /api/v1/personalization/routine    (Update daily routine settings)
- POST  /api/v1/personalization/reset      (Granularly reset preferences to defaults)
"""
import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from app.core.response import api_response
from app.services.personalization_service import personalization_service
from app.schemas.personalization import (
    UpdatePersonalizationRequest,
    UpdateDashboardPreferencesRequest,
    UpdateDailyRoutineRequest,
    ResetPreferencesRequest,
)

logger = logging.getLogger(__name__)

personalization_bp = Blueprint("personalization", __name__)


# -----------------------------------------------------------------------------
# 1. General Personalization Settings
# -----------------------------------------------------------------------------

@personalization_bp.route("", methods=["GET"])
@jwt_required()
def get_personalization():
    """Retrieve full personalization settings for authenticated user."""
    user_id = get_jwt_identity()
    record = personalization_service.get_or_create_personalization(user_id)
    routine = personalization_service.get_or_create_routine(user_id)
    return api_response(
        data={
            "personalization": record.to_dict(),
            "daily_routine": routine.to_dict(),
        },
        message="Personalization settings retrieved.",
        status_code=200
    )


@personalization_bp.route("", methods=["PATCH"])
@jwt_required()
def update_personalization():
    """Update personalization preferences (language, style, formatting, AI tone)."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    try:
        validated = UpdatePersonalizationRequest(**json_data)
    except ValidationError as err:
        return api_response(
            message=f"Validation error: {err.errors()}",
            status_code=400
        )

    updates = validated.model_dump(exclude_unset=True)
    record = personalization_service.update_personalization(user_id, updates)

    return api_response(
        data=record.to_dict(),
        message="Personalization updated successfully.",
        status_code=200
    )


# -----------------------------------------------------------------------------
# 2. Dashboard Customization
# -----------------------------------------------------------------------------

@personalization_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard_preferences():
    """Get customized dashboard layout, widget order, and density."""
    user_id = get_jwt_identity()
    record = personalization_service.get_or_create_personalization(user_id)
    return api_response(
        data={
            "dashboard_widgets": record.dashboard_widgets,
            "dashboard_density": record.dashboard_density,
        },
        message="Dashboard preferences retrieved.",
        status_code=200
    )


@personalization_bp.route("/dashboard", methods=["PATCH"])
@jwt_required()
def update_dashboard_preferences():
    """Update dashboard widget ordering, visibility, and density."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    try:
        validated = UpdateDashboardPreferencesRequest(**json_data)
    except ValidationError as err:
        return api_response(
            message=f"Validation error: {err.errors()}",
            status_code=400
        )

    widgets_list = (
        [w.model_dump() for w in validated.dashboard_widgets]
        if validated.dashboard_widgets is not None
        else None
    )

    record = personalization_service.update_dashboard_preferences(
        user_id=user_id,
        widgets=widgets_list,
        density=validated.dashboard_density
    )

    return api_response(
        data={
            "dashboard_widgets": record.dashboard_widgets,
            "dashboard_density": record.dashboard_density,
        },
        message="Dashboard preferences updated successfully.",
        status_code=200
    )


# -----------------------------------------------------------------------------
# 3. Daily Routine
# -----------------------------------------------------------------------------

@personalization_bp.route("/routine", methods=["GET"])
@jwt_required()
def get_daily_routine():
    """Get configured daily routine schedule, focus durations, and planning rituals."""
    user_id = get_jwt_identity()
    routine = personalization_service.get_or_create_routine(user_id)
    return api_response(
        data=routine.to_dict(),
        message="Daily routine retrieved.",
        status_code=200
    )


@personalization_bp.route("/routine", methods=["PATCH"])
@jwt_required()
def update_daily_routine():
    """Update daily routine schedule, working hours, or rituals."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    try:
        validated = UpdateDailyRoutineRequest(**json_data)
    except ValidationError as err:
        return api_response(
            message=f"Validation error: {err.errors()}",
            status_code=400
        )

    updates = validated.model_dump(exclude_unset=True)
    routine = personalization_service.update_daily_routine(user_id, updates)

    return api_response(
        data=routine.to_dict(),
        message="Daily routine updated successfully.",
        status_code=200
    )


# -----------------------------------------------------------------------------
# 4. Granular Reset to Defaults
# -----------------------------------------------------------------------------

@personalization_bp.route("/reset", methods=["POST"])
@jwt_required()
def reset_preferences():
    """Selectively reset preferences to defaults without affecting memories or consent."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    try:
        validated = ResetPreferencesRequest(**json_data)
    except ValidationError as err:
        return api_response(
            message=f"Validation error: {err.errors()}",
            status_code=400
        )

    res = personalization_service.reset_preferences(user_id, validated.target)
    return api_response(
        data=res,
        message=f"Successfully reset '{validated.target}' preferences to defaults.",
        status_code=200
    )
