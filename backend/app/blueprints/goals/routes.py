from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.goal import (
    CreateGoalRequest,
    UpdateGoalRequest,
    CreateMilestoneRequest,
    UpdateMilestoneRequest,
    CompleteMilestoneRequest
)
from app.services.goal_service import GoalService
from app.core.response import api_response

goals_bp = Blueprint("goals", __name__)
goal_service = GoalService()


# ---------------------------------------------------------
# Goal Endpoints
# ---------------------------------------------------------

@goals_bp.route("", methods=["POST"])
@jwt_required()
def create_goal():
    """Create a new goal for the authenticated user."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateGoalRequest(**json_data)

    goal = goal_service.create_goal(
        user_id=user_id,
        title=validated.title,
        description=validated.description,
        target_date=validated.target_date,
        priority=validated.priority,
        status=validated.status,
        category=validated.category
    )

    return api_response(
        data={"goal": goal.to_dict()},
        message="Goal created successfully",
        status_code=201
    )


@goals_bp.route("", methods=["GET"])
@jwt_required()
def list_goals():
    """List goals for the authenticated user with filters and pagination."""
    user_id = get_jwt_identity()

    status = request.args.get("status")
    priority = request.args.get("priority")
    category = request.args.get("category")
    search = request.args.get("search")
    sort_by = request.args.get("sort_by", "target_date")
    sort_order = request.args.get("sort_order", "asc")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    goals, meta = goal_service.list_goals(
        user_id=user_id,
        status=status,
        priority=priority,
        category=category,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page
    )

    return api_response(
        data={"goals": [g.to_dict() for g in goals]},
        message="Goals retrieved successfully",
        meta=meta
    )


@goals_bp.route("/<goal_id>", methods=["GET"])
@jwt_required()
def get_goal(goal_id: str):
    """Retrieve details of a specific goal including all milestones."""
    user_id = get_jwt_identity()
    goal = goal_service.get_goal(goal_id, user_id)

    return api_response(
        data={"goal": goal.to_dict()},
        message="Goal retrieved successfully"
    )


@goals_bp.route("/<goal_id>", methods=["PATCH"])
@jwt_required()
def update_goal(goal_id: str):
    """Update attributes of an existing goal."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = UpdateGoalRequest(**json_data)

    update_fields = validated.model_dump(exclude_unset=True)
    goal = goal_service.update_goal(goal_id, user_id, **update_fields)

    return api_response(
        data={"goal": goal.to_dict()},
        message="Goal updated successfully"
    )


@goals_bp.route("/<goal_id>", methods=["DELETE"])
@jwt_required()
def delete_goal(goal_id: str):
    """Delete a goal and its associated milestones."""
    user_id = get_jwt_identity()
    goal_service.delete_goal(goal_id, user_id)

    return api_response(
        data={},
        message="Goal deleted successfully"
    )


# ---------------------------------------------------------
# Milestone Endpoints
# ---------------------------------------------------------

@goals_bp.route("/<goal_id>/milestones", methods=["POST"])
@jwt_required()
def create_milestone(goal_id: str):
    """Create a milestone under a user-owned goal."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateMilestoneRequest(**json_data)

    milestone = goal_service.create_milestone(
        goal_id=goal_id,
        current_user_id=user_id,
        title=validated.title,
        description=validated.description,
        target_date=validated.target_date,
        is_completed=validated.is_completed,
        sort_order=validated.sort_order
    )

    # Re-fetch updated goal for current progress percentage
    updated_goal = goal_service.get_goal(goal_id, user_id)

    return api_response(
        data={
            "milestone": milestone.to_dict(),
            "goal": updated_goal.to_dict()
        },
        message="Milestone created successfully",
        status_code=201
    )


@goals_bp.route("/<goal_id>/milestones", methods=["GET"])
@jwt_required()
def list_milestones(goal_id: str):
    """List all milestones belonging to a goal."""
    user_id = get_jwt_identity()
    milestones = goal_service.list_milestones(goal_id, user_id)

    return api_response(
        data={"milestones": [m.to_dict() for m in milestones]},
        message="Milestones retrieved successfully"
    )
@goals_bp.route("/<goal_id>/milestones/<milestone_id>", methods=["PATCH"])
@jwt_required()
def update_milestone(goal_id: str, milestone_id: str):
    """Update attributes of an existing milestone."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = UpdateMilestoneRequest(**json_data)

    update_fields = validated.model_dump(exclude_unset=True)
    milestone = goal_service.update_milestone(goal_id, milestone_id, user_id, **update_fields)
    updated_goal = goal_service.get_goal(goal_id, user_id)

    return api_response(
        data={
            "milestone": milestone.to_dict(),
            "goal": updated_goal.to_dict()
        },
        message="Milestone updated successfully"
    )


@goals_bp.route("/<goal_id>/milestones/<milestone_id>/complete", methods=["PATCH"])
@jwt_required()
def complete_milestone(goal_id: str, milestone_id: str):
    """Toggle completion status for a milestone."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CompleteMilestoneRequest(**json_data)

    milestone = goal_service.complete_milestone(
        goal_id=goal_id,
        milestone_id=milestone_id,
        current_user_id=user_id,
        is_completed=validated.is_completed
    )
    updated_goal = goal_service.get_goal(goal_id, user_id)

    return api_response(
        data={
            "milestone": milestone.to_dict(),
            "goal": updated_goal.to_dict()
        },
        message="Milestone completion updated successfully"
    )


@goals_bp.route("/<goal_id>/milestones/<milestone_id>", methods=["DELETE"])
@jwt_required()
def delete_milestone(goal_id: str, milestone_id: str):
    """Delete a milestone and update goal progress."""
    user_id = get_jwt_identity()
    goal_service.delete_milestone(goal_id, milestone_id, user_id)
    updated_goal = goal_service.get_goal(goal_id, user_id)

    return api_response(
        data={"goal": updated_goal.to_dict()},
        message="Milestone deleted successfully"
    )
