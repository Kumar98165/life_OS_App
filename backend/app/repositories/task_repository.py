from datetime import datetime, date, timezone
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import or_, func, desc, asc
from sqlalchemy.orm import joinedload
from app.extensions import db
from app.models.task import Task, TaskCategory
from app.core.pagination import paginate_query


class TaskRepository:
    """Repository handling all database queries and transactions for tasks and categories."""

    def create(
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
        """Create and persist a new task record."""
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            category_id=category_id,
            priority=priority,
            status=status,
            due_date=due_date,
            estimated_minutes=estimated_minutes
        )
        db.session.add(task)
        db.session.commit()
        return task

    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Retrieve task by ID with eager-loaded category relation."""
        return Task.query.options(joinedload(Task.category)).filter_by(id=task_id).first()

    def list_for_user(
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
        """List tasks belonging to authenticated user with filters, search, and pagination."""
        query = Task.query.options(joinedload(Task.category)).filter(Task.user_id == user_id)

        # Filter by status
        if status:
            if status == "pending":
                query = query.filter(Task.status.in_(["pending", "todo"]))
            else:
                query = query.filter(Task.status == status)

        # Filter by priority
        if priority:
            query = query.filter(Task.priority == priority)

        # Filter by category
        if category_id:
            query = query.filter(Task.category_id == category_id)

        # Filter by search term in title or description
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern)
                )
            )

        # Filter by due date
        if due_date_filter:
            if due_date_filter == "today":
                today = datetime.now(timezone.utc).date()
                query = query.filter(func.date(Task.due_date) == today)
            elif due_date_filter == "overdue":
                now = datetime.now(timezone.utc)
                query = query.filter(Task.due_date < now, Task.status.notin_(["completed", "cancelled", "archived"]))
            elif due_date_filter == "upcoming":
                now = datetime.now(timezone.utc)
                query = query.filter(Task.due_date >= now)

        # Sorting
        sort_col = getattr(Task, sort_by, Task.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        return paginate_query(query, page=page, per_page=per_page)

    def update(self, task: Task, **kwargs) -> Task:
        """Update permitted attributes on a task entity."""
        for key, value in kwargs.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)

        db.session.commit()
        return task

    def delete(self, task: Task) -> bool:
        """Delete task entity from database."""
        db.session.delete(task)
        db.session.commit()
        return True

    # Category operations
    def list_categories(self, user_id: str) -> List[TaskCategory]:
        """Fetch all categories created by or assigned to user."""
        return TaskCategory.query.filter_by(user_id=user_id).order_by(TaskCategory.name.asc()).all()

    def get_category_by_id(self, category_id: str) -> Optional[TaskCategory]:
        """Fetch category by ID."""
        return TaskCategory.query.filter_by(id=category_id).first()

    def get_category_by_name(self, user_id: str, name: str) -> Optional[TaskCategory]:
        """Find category by user and name."""
        return TaskCategory.query.filter_by(user_id=user_id, name=name).first()

    def create_category(
        self,
        user_id: str,
        name: str,
        color_hex: str = "#6C63FF",
        icon: Optional[str] = None
    ) -> TaskCategory:
        """Create a new task category."""
        category = TaskCategory(
            user_id=user_id,
            name=name,
            color_hex=color_hex,
            icon=icon
        )
        db.session.add(category)
        db.session.commit()
        return category

