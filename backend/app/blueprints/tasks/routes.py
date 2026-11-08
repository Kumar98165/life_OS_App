from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.task import CreateTaskRequest, UpdateTaskRequest, CreateCategoryRequest
from app.services.task_service import TaskService
from app.core.response import api_response

tasks_bp = Blueprint("tasks", __name__)
task_service = TaskService()


@tasks_bp.route("", methods=["POST"])
@jwt_required()
def create_task():
    """Create a new task for the authenticated user."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateTaskRequest(**json_data)

    task = task_service.create_task(
        user_id=user_id,
        title=validated.title,
        description=validated.description,
        category_id=validated.category_id,
        priority=validated.priority,
        status=validated.status,
        due_date=validated.due_date,
        estimated_minutes=validated.estimated_minutes
    )

    return api_response(
        data={"task": task.to_dict()},
        message="Task created successfully",
        status_code=201
    )


@tasks_bp.route("", methods=["GET"])
@jwt_required()
def list_tasks():
    """List tasks belonging to authenticated user with filtering, search, and pagination."""
    user_id = get_jwt_identity()

    status = request.args.get("status")
    priority = request.args.get("priority")
    category_id = request.args.get("category_id")
    search = request.args.get("search")
    due_date = request.args.get("due_date")
    sort_by = request.args.get("sort_by", "created_at")
    sort_order = request.args.get("sort_order", "desc")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    tasks, meta = task_service.list_tasks(
        user_id=user_id,
        status=status,
        priority=priority,
        category_id=category_id,
        search=search,
        due_date_filter=due_date,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page
    )

    return api_response(
        data={"tasks": [t.to_dict() for t in tasks]},
        meta=meta,
        message="Tasks retrieved successfully"
    )


@tasks_bp.route("/categories", methods=["GET"])
@jwt_required()
def list_categories():
    """List all categories available to authenticated user."""
    user_id = get_jwt_identity()
    categories = task_service.list_or_seed_categories(user_id)

    return api_response(
        data={"categories": [c.to_dict() for c in categories]},
        message="Categories retrieved successfully"
    )


@tasks_bp.route("/categories", methods=["POST"])
@jwt_required()
def create_category():
    """Create a new custom category for authenticated user."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateCategoryRequest(**json_data)

    category = task_service.create_category(
        user_id=user_id,
        name=validated.name,
        color_hex=validated.color_hex,
        icon=validated.icon
    )

    return api_response(
        data={"category": category.to_dict()},
        message="Category created successfully",
        status_code=201
    )


@tasks_bp.route("/<task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id: str):
    """Retrieve details for a single task ensuring user ownership."""
    user_id = get_jwt_identity()
    task = task_service.get_task(task_id, current_user_id=user_id)

    return api_response(
        data={"task": task.to_dict()},
        message="Task retrieved successfully"
    )


@tasks_bp.route("/<task_id>", methods=["PATCH"])
@jwt_required()
def update_task(task_id: str):
    """Update task properties with strict authorization."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = UpdateTaskRequest(**json_data)

    task = task_service.update_task(
        task_id=task_id,
        current_user_id=user_id,
        **validated.model_dump(exclude_unset=True)
    )

    return api_response(
        data={"task": task.to_dict()},
        message="Task updated successfully"
    )


@tasks_bp.route("/<task_id>/complete", methods=["PATCH"])
@jwt_required()
def toggle_complete_task(task_id: str):
    """Toggle completion status for a task."""
    user_id = get_jwt_identity()
    task = task_service.toggle_complete_task(task_id, current_user_id=user_id)

    return api_response(
        data={"task": task.to_dict()},
        message="Task completion state updated successfully"
    )


@tasks_bp.route("/<task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id: str):
    """Delete a task permanently after ownership verification."""
    user_id = get_jwt_identity()
    task_service.delete_task(task_id, current_user_id=user_id)

    return api_response(
        data={"id": task_id},
        message="Task deleted successfully"
    )

