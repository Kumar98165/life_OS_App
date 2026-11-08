from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from app.repositories.task_repository import TaskRepository
from app.models.task import Task, TaskCategory
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.core.security import check_resource_ownership


DEFAULT_CATEGORIES = [
    {"name": "Work", "color_hex": "#6C63FF", "icon": "briefcase-outline"},
    {"name": "Personal", "color_hex": "#22C55E", "icon": "person-outline"},
    {"name": "Health", "color_hex": "#EF4444", "icon": "fitness-outline"},
    {"name": "Deep Work", "color_hex": "#F59E0B", "icon": "flash-outline"},
]


class TaskService:
    """Business service coordinating task workflows, validation, and ownership boundaries."""

    def __init__(self, task_repo: Optional[TaskRepository] = None):
        self.task_repo = task_repo or TaskRepository()

    def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        category_id: Optional[str] = None,
        priority: str = "medium",
        status: str = "pending",
        due_date: Optional[datetime] = None,
        estimated_minutes: Optional[int] = None
    ) -> Task:
        """Create a new task with category ownership validation."""
        if category_id:
            category = self.task_repo.get_category_by_id(category_id)
            if not category or category.user_id != user_id:
                raise BadRequestException("Invalid category_id specified")

        return self.task_repo.create(
            user_id=user_id,
            title=title,
            description=description,
            category_id=category_id,
            priority=priority,
            status=status,
            due_date=due_date,
            estimated_minutes=estimated_minutes
        )

    def get_task(self, task_id: str, current_user_id: str) -> Task:
        """Fetch task ensuring user authorization."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")

        check_resource_ownership(task.user_id, current_user_id)
        return task

    def list_tasks(
        self,
        user_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category_id: Optional[str] = None,
        search: Optional[str] = None,
        due_date_filter: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Task], Dict[str, Any]]:
        """List tasks owned by authenticated user."""
        return self.task_repo.list_for_user(
            user_id=user_id,
            status=status,
            priority=priority,
            category_id=category_id,
            search=search,
            due_date_filter=due_date_filter,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page
        )

    def update_task(
        self,
        task_id: str,
        current_user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        category_id: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        due_date: Optional[datetime] = None,
        estimated_minutes: Optional[int] = None,
        is_archived: Optional[bool] = None
    ) -> Task:
        """Update task properties with ownership verification."""
        task = self.get_task(task_id, current_user_id)

        update_kwargs: Dict[str, Any] = {}
        if title is not None:
            update_kwargs["title"] = title
        if description is not None:
            update_kwargs["description"] = description
        if priority is not None:
            update_kwargs["priority"] = priority
        if due_date is not None:
            update_kwargs["due_date"] = due_date
        if estimated_minutes is not None:
            update_kwargs["estimated_minutes"] = estimated_minutes
        if is_archived is not None:
            update_kwargs["is_archived"] = is_archived

        if category_id is not None:
            if category_id != "":
                category = self.task_repo.get_category_by_id(category_id)
                if not category or category.user_id != current_user_id:
                    raise BadRequestException("Invalid category_id specified")
                update_kwargs["category_id"] = category_id
            else:
                update_kwargs["category_id"] = None

        if status is not None:
            update_kwargs["status"] = status
            if status == "completed":
                update_kwargs["completed_at"] = datetime.now(timezone.utc)
            elif task.status == "completed":
                update_kwargs["completed_at"] = None

        return self.task_repo.update(task, **update_kwargs)

    def toggle_complete_task(self, task_id: str, current_user_id: str) -> Task:
        """Toggle task completion state."""
        task = self.get_task(task_id, current_user_id)

        if task.status == "completed":
            task.status = "pending"
            task.completed_at = None
        else:
            task.status = "completed"
            task.completed_at = datetime.now(timezone.utc)

        return self.task_repo.update(task, status=task.status, completed_at=task.completed_at)

    def delete_task(self, task_id: str, current_user_id: str) -> bool:
        """Delete task after ownership check."""
        task = self.get_task(task_id, current_user_id)
        return self.task_repo.delete(task)

    def list_or_seed_categories(self, user_id: str) -> List[TaskCategory]:
        """Fetch categories for user, automatically seeding default categories if none exist."""
        categories = self.task_repo.list_categories(user_id)
        if not categories:
            for default_cat in DEFAULT_CATEGORIES:
                self.task_repo.create_category(
                    user_id=user_id,
                    name=default_cat["name"],
                    color_hex=default_cat["color_hex"],
                    icon=default_cat["icon"]
                )
            categories = self.task_repo.list_categories(user_id)
        return categories

    def create_category(
        self,
        user_id: str,
        name: str,
        color_hex: str = "#6C63FF",
        icon: Optional[str] = None
    ) -> TaskCategory:
        """Create a custom category for user."""
        existing = self.task_repo.get_category_by_name(user_id, name)
        if existing:
            raise BadRequestException(f"A category named '{name}' already exists")

        return self.task_repo.create_category(
            user_id=user_id,
            name=name,
            color_hex=color_hex,
            icon=icon
        )

