from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import or_, asc, desc, func
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.models.goal import Goal, GoalMilestone
from app.core.pagination import paginate_query


class GoalRepository:
    """Repository handling database operations for goals and milestones."""

    def create_goal(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        target_date: Optional[datetime] = None,
        priority: str = "medium",
        status: str = "in_progress",
        category: Optional[str] = None
    ) -> Goal:
        """Create and persist a new goal."""
        goal = Goal(
            user_id=user_id,
            title=title,
            description=description,
            target_date=target_date,
            priority=priority,
            status=status,
            category=category,
            progress_percent=0.0
        )
        db.session.add(goal)
        db.session.commit()
        return goal

    def get_by_id(self, goal_id: str) -> Optional[Goal]:
        """Retrieve goal by ID with eager-loaded milestones."""
        return (
            Goal.query
            .options(selectinload(Goal.milestones))
            .filter_by(id=goal_id)
            .first()
        )

    def list_for_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Goal], Dict[str, Any]]:
        """List user goals with filtering, search, and pagination."""
        query = (
            Goal.query
            .options(selectinload(Goal.milestones))
            .filter(Goal.user_id == user_id)
        )

        if status:
            # Handle aliases: active matches in_progress, achieved matches completed
            if status == "active":
                query = query.filter(Goal.status.in_(["active", "in_progress"]))
            elif status == "completed":
                query = query.filter(Goal.status.in_(["completed", "achieved"]))
            else:
                query = query.filter(Goal.status == status)

        if priority:
            query = query.filter(Goal.priority == priority)

        if category:
            query = query.filter(Goal.category == category)

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Goal.title.ilike(pattern),
                    Goal.description.ilike(pattern),
                    Goal.category.ilike(pattern)
                )
            )

        # Sorting
        sort_column = getattr(Goal, sort_by, Goal.created_at)
        if sort_order.lower() == "asc":
            # For target_date asc, place nulls last
            if sort_by == "target_date":
                query = query.order_by(sort_column.asc().nullslast())
            else:
                query = query.order_by(asc(sort_column))
        else:
            if sort_by == "target_date":
                query = query.order_by(sort_column.desc().nullslast())
            else:
                query = query.order_by(desc(sort_column))

        return paginate_query(query, page, per_page)

    def update_goal(self, goal: Goal, **kwargs) -> Goal:
        """Update goal attributes and commit."""
        for field, value in kwargs.items():
            if hasattr(goal, field) and value is not None:
                setattr(goal, field, value)

        db.session.commit()
        return goal

    def delete_goal(self, goal: Goal) -> None:
        """Delete goal (cascades to all associated milestones)."""
        db.session.delete(goal)
        db.session.commit()

    def create_milestone(
        self,
        goal_id: str,
        title: str,
        description: Optional[str] = None,
        target_date: Optional[datetime] = None,
        is_completed: bool = False,
        sort_order: Optional[int] = None
    ) -> GoalMilestone:
        """Create and persist a new milestone under a goal."""
        if sort_order is None or sort_order == 0:
            max_order = (
                db.session.query(func.max(GoalMilestone.sort_order))
                .filter_by(goal_id=goal_id)
                .scalar()
            )
            sort_order = (max_order or 0) + 1

        completed_at = datetime.now(timezone.utc) if is_completed else None

        milestone = GoalMilestone(
            goal_id=goal_id,
            title=title,
            description=description,
            target_date=target_date,
            is_completed=is_completed,
            completed_at=completed_at,
            sort_order=sort_order
        )
        db.session.add(milestone)
        db.session.commit()

        # Recalculate parent goal progress
        self.recalculate_progress(goal_id)
        return milestone

    def get_milestone_by_id(self, milestone_id: str) -> Optional[GoalMilestone]:
        """Retrieve milestone by ID with eager-loaded goal."""
        return (
            GoalMilestone.query
            .options(selectinload(GoalMilestone.goal))
            .filter_by(id=milestone_id)
            .first()
        )

    def list_milestones_for_goal(self, goal_id: str) -> List[GoalMilestone]:
        """List all milestones for a goal in sorted order."""
        return (
            GoalMilestone.query
            .filter_by(goal_id=goal_id)
            .order_by(asc(GoalMilestone.sort_order), asc(GoalMilestone.created_at))
            .all()
        )

    def update_milestone(self, milestone: GoalMilestone, **kwargs) -> GoalMilestone:
        """Update milestone attributes and sync completed_at."""
        if "is_completed" in kwargs and kwargs["is_completed"] is not None:
            new_is_completed = kwargs["is_completed"]
            if new_is_completed and not milestone.is_completed:
                milestone.completed_at = datetime.now(timezone.utc)
            elif not new_is_completed and milestone.is_completed:
                milestone.completed_at = None
            milestone.is_completed = new_is_completed

        for field, value in kwargs.items():
            if field != "is_completed" and hasattr(milestone, field) and value is not None:
                setattr(milestone, field, value)

        db.session.commit()

        # Recalculate parent goal progress
        self.recalculate_progress(milestone.goal_id)
        return milestone

    def delete_milestone(self, milestone: GoalMilestone) -> str:
        """Delete milestone and return goal_id for progress recalculation."""
        goal_id = milestone.goal_id
        db.session.delete(milestone)
        db.session.commit()

        # Recalculate parent goal progress
        self.recalculate_progress(goal_id)
        return goal_id

    def recalculate_progress(self, goal_id: str) -> float:
        """Recalculate progress percentage for a goal based on milestone completions."""
        goal = Goal.query.options(selectinload(Goal.milestones)).filter_by(id=goal_id).first()
        if not goal:
            return 0.0

        if not goal.milestones or len(goal.milestones) == 0:
            goal.progress_percent = 0.0
        else:
            completed_count = sum(1 for m in goal.milestones if m.is_completed)
            total_count = len(goal.milestones)
            goal.progress_percent = round((completed_count / total_count) * 100.0, 1)

        db.session.commit()
        return goal.progress_percent

