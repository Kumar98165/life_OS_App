"""LifeOS - Life Analytics & Personal Insights Blueprint Routes.

REST endpoints providing multi-domain analytics across Productivity, Habits,
Goals, and Finance, along with the composite Life Score and local AI insights.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import DateRangeParams
from app.core.response import api_response, error_response

analytics_bp = Blueprint("analytics", __name__)
analytics_service = AnalyticsService()


def _get_validated_date_params():
    """Extract and validate common date range query parameters."""
    period = request.args.get("period", "week")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    tz = request.args.get("timezone", "UTC")

    params = DateRangeParams(
        period=period,
        start_date=start_date,
        end_date=end_date,
        timezone=tz,
    )
    return params


@analytics_bp.route("/overview", methods=["GET"])
@jwt_required()
def get_analytics_overview():
    """Retrieve high-level cross-domain dashboard summary."""
    user_id = get_jwt_identity()
    try:
        params = _get_validated_date_params()
    except (ValidationError, ValueError) as err:
        return error_response(str(err), status_code=400)

    data = analytics_service.get_analytics_overview(
        user_id=user_id,
        period=params.period or "week",
        start_date=params.start_date,
        end_date=params.end_date,
        timezone=params.timezone,
    )
    return api_response(data=data, message="Analytics overview retrieved successfully")


@analytics_bp.route("/productivity", methods=["GET"])
@jwt_required()
def get_productivity_analytics():
    """Retrieve task and planner execution analytics."""
    user_id = get_jwt_identity()
    try:
        params = _get_validated_date_params()
    except (ValidationError, ValueError) as err:
        return error_response(str(err), status_code=400)

    data = analytics_service.get_productivity_analytics(
        user_id=user_id,
        period=params.period or "week",
        start_date=params.start_date,
        end_date=params.end_date,
        timezone=params.timezone,
    )
    return api_response(data=data, message="Productivity analytics retrieved successfully")


@analytics_bp.route("/habits", methods=["GET"])
@jwt_required()
def get_habit_analytics():
    """Retrieve habit adherence, streaks, and consistency metrics."""
    user_id = get_jwt_identity()
    try:
        params = _get_validated_date_params()
    except (ValidationError, ValueError) as err:
        return error_response(str(err), status_code=400)

    data = analytics_service.get_habit_analytics(
        user_id=user_id,
        period=params.period or "week",
        start_date=params.start_date,
        end_date=params.end_date,
        timezone=params.timezone,
    )
    return api_response(data=data, message="Habit analytics retrieved successfully")


@analytics_bp.route("/goals", methods=["GET"])
@jwt_required()
def get_goal_analytics():
    """Retrieve goals velocity, milestone completion, and upcoming deadlines."""
    user_id = get_jwt_identity()
    data = analytics_service.get_goal_analytics(user_id=user_id)
    return api_response(data=data, message="Goal analytics retrieved successfully")


@analytics_bp.route("/finance", methods=["GET"])
@jwt_required()
def get_finance_analytics():
    """Retrieve personal cash flow, savings rate, and budget adherence."""
    user_id = get_jwt_identity()
    try:
        params = _get_validated_date_params()
    except (ValidationError, ValueError) as err:
        return error_response(str(err), status_code=400)

    data = analytics_service.get_financial_analytics(
        user_id=user_id,
        period=params.period or "month",
        start_date=params.start_date,
        end_date=params.end_date,
        timezone=params.timezone,
    )
    return api_response(data=data, message="Financial analytics retrieved successfully")


@analytics_bp.route("/trends", methods=["GET"])
@jwt_required()
def get_trends_analytics():
    """Retrieve multi-domain daily completion trends for charting."""
    user_id = get_jwt_identity()
    try:
        params = _get_validated_date_params()
    except (ValidationError, ValueError) as err:
        return error_response(str(err), status_code=400)

    data = analytics_service.get_trends_analytics(
        user_id=user_id,
        period=params.period or "week",
        start_date=params.start_date,
        end_date=params.end_date,
        timezone=params.timezone,
    )
    return api_response(data=data, message="Trend analytics retrieved successfully")


@analytics_bp.route("/life-score", methods=["GET"])
@jwt_required()
def get_life_score():
    """Calculate transparent 4-pillar Life Score with dynamic weight re-normalization."""
    user_id = get_jwt_identity()
    try:
        params = _get_validated_date_params()
    except (ValidationError, ValueError) as err:
        return error_response(str(err), status_code=400)

    data = analytics_service.calculate_life_score(
        user_id=user_id,
        period=params.period or "week",
        start_date=params.start_date,
        end_date=params.end_date,
        timezone=params.timezone,
    )
    return api_response(data=data, message="Life score calculated successfully")


@analytics_bp.route("/insights", methods=["GET"])
@jwt_required()
def get_ai_insights():
    """Synthesize personal narrative insights and suggestions via local Ollama LLM."""
    user_id = get_jwt_identity()
    try:
        params = _get_validated_date_params()
    except (ValidationError, ValueError) as err:
        return error_response(str(err), status_code=400)

    data = analytics_service.generate_ai_insights(
        user_id=user_id,
        period=params.period or "week",
        start_date=params.start_date,
        end_date=params.end_date,
        timezone=params.timezone,
    )
    return api_response(data=data, message="AI personal insights generated successfully")

