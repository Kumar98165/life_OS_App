from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from app.repositories.goal_repository import GoalRepository
from app.models.goal import Goal, GoalMilestone
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.security import check_resource_ownership


class GoalService:
    """Business service coordinating goals, measurable milestones, and progress tracking."""

    def __init__(self, goal_repo: Optional[GoalRepository] = None):
        self.goal_repo = goal_repo or GoalRepository()

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
        """Create a new goal with normalized UTC target date."""
        target_utc = self._ensure_utc(target_date) if target_date else None
        return self.goal_repo.create_goal(
            user_id=user_id,
            title=title,
            description=description,
            target_date=target_utc,
            priority=priority,
            status=status,
            category=category
        )

    def get_goal(self, goal_id: str, current_user_id: str) -> Goal:
        """Retrieve goal ensuring strict user resource boundaries."""
        goal = self.goal_repo.get_by_id(goal_id)
        if not goal:
            raise NotFoundException("Goal not found")

        check_resource_ownership(goal.user_id, current_user_id)
        return goal

    def list_goals(
        self,
        user_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "target_date",
        sort_order: str = "asc",
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Goal], Dict[str, Any]]:
        """List goals for the authenticated user with filtering and pagination."""
        return self.goal_repo.list_for_user(
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

    def update_goal(
        self,
        goal_id: str,
        current_user_id: str,
        **kwargs
    ) -> Goal:
        """Update goal attributes and re-sync target_date to UTC."""
        goal = self.get_goal(goal_id, current_user_id)

        if "target_date" in kwargs and kwargs["target_date"] is not None:
            kwargs["target_date"] = self._ensure_utc(kwargs["target_date"])

        return self.goal_repo.update_goal(goal, **kwargs)

    def delete_goal(self, goal_id: str, current_user_id: str) -> None:
        """Delete goal ensuring ownership."""
        goal = self.get_goal(goal_id, current_user_id)
        self.goal_repo.delete_goal(goal)

    def create_milestone(
        self,
        goal_id: str,
        current_user_id: str,
        title: str,
        description: Optional[str] = None,
        target_date: Optional[datetime] = None,
        is_completed: bool = False,
        sort_order: Optional[int] = None
    ) -> GoalMilestone:
        """Create a milestone under a user-owned goal."""
        # Enforce goal ownership
        self.get_goal(goal_id, current_user_id)

        target_utc = self._ensure_utc(target_date) if target_date else None
        return self.goal_repo.create_milestone(
            goal_id=goal_id,
            title=title,
            description=description,
            target_date=target_utc,
            is_completed=is_completed,
            sort_order=sort_order
        )

    def get_milestone(
        self,
        goal_id: str,
        milestone_id: str,
        current_user_id: str
    ) -> GoalMilestone:
        """Retrieve a specific milestone ensuring parent goal authorization."""
        self.get_goal(goal_id, current_user_id)

        milestone = self.goal_repo.get_milestone_by_id(milestone_id)
        if not milestone or milestone.goal_id != goal_id:
            raise NotFoundException("Milestone not found for this goal")

        return milestone

    def list_milestones(
        self,
        goal_id: str,
        current_user_id: str
    ) -> List[GoalMilestone]:
        """List all milestones for a user-owned goal."""
        self.get_goal(goal_id, current_user_id)
        return self.goal_repo.list_milestones_for_goal(goal_id)

    def update_milestone(
        self,
        goal_id: str,
        milestone_id: str,
        current_user_id: str,
        **kwargs
    ) -> GoalMilestone:
        """Update a milestone with authorization."""
        milestone = self.get_milestone(goal_id, milestone_id, current_user_id)

        if "target_date" in kwargs and kwargs["target_date"] is not None:
            kwargs["target_date"] = self._ensure_utc(kwargs["target_date"])

        return self.goal_repo.update_milestone(milestone, **kwargs)

    def complete_milestone(
        self,
        goal_id: str,
        milestone_id: str,
        current_user_id: str,
        is_completed: bool
    ) -> GoalMilestone:
        """Toggle completion status for a milestone and recalculate goal progress."""
        milestone = self.get_milestone(goal_id, milestone_id, current_user_id)
        return self.goal_repo.update_milestone(milestone, is_completed=is_completed)

    def delete_milestone(
        self,
        goal_id: str,
        milestone_id: str,
        current_user_id: str
    ) -> None:
        """Delete milestone and recalculate goal progress."""
        milestone = self.get_milestone(goal_id, milestone_id, current_user_id)
        self.goal_repo.delete_milestone(milestone)

    def _ensure_utc(self, dt: datetime) -> datetime:
        """Normalize datetime to UTC timezone-aware."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

