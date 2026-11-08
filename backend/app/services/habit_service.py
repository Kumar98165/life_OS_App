"""LifeOS - Habit Service.

Coordinates business rules, ownership validation, scheduled weekday restrictions,
and streak engine metrics for habits and daily check-in logs.
"""
from datetime import date, timedelta
from typing import Optional, List, Dict, Any
from app.repositories.habit_repository import HabitRepository
from app.models.habit import Habit, HabitLog
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.security import check_resource_ownership


class HabitService:
    """Business service coordinating habits, check-ins, and streak calculations."""

    def __init__(self, habit_repo: Optional[HabitRepository] = None):
        self.habit_repo = habit_repo or HabitRepository()

    def create_habit(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        frequency: str = "daily",
        target_days_per_week: int = 7,
        color_hex: str = "#6C63FF",
        icon: Optional[str] = None
    ) -> Habit:
        """Create a new habit for the authenticated user."""
        if frequency not in ("daily", "weekdays", "weekly"):
            raise BadRequestException("Invalid frequency. Must be 'daily', 'weekdays', or 'weekly'.")

        if frequency == "weekdays" and target_days_per_week > 5:
            target_days_per_week = 5

        return self.habit_repo.create_habit(
            user_id=user_id,
            title=title,
            description=description,
            frequency=frequency,
            target_days_per_week=target_days_per_week,
            color_hex=color_hex,
            icon=icon
        )

    def get_habit(self, habit_id: str, current_user_id: str) -> Habit:
        """Retrieve habit ensuring strict user ownership."""
        habit = self.habit_repo.get_by_id(habit_id)
        if not habit:
            raise NotFoundException("Habit not found")

        check_resource_ownership(habit.user_id, current_user_id)
        return habit

    def list_habits(
        self,
        user_id: str,
        include_archived: bool = False,
        frequency: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List habits for user decorated with today's completion status."""
        habits = self.habit_repo.list_for_user(
            user_id=user_id,
            include_archived=include_archived,
            frequency=frequency
        )

        today = date.today()
        result = []
        for h in habits:
            # Check if today has a log
            today_log = self.habit_repo.get_log(h.id, today)
            h_dict = h.to_dict()
            h_dict["completed_today"] = bool(today_log and today_log.completed)
            h_dict["today_log_id"] = today_log.id if today_log else None
            result.append(h_dict)

        return result

    def update_habit(
        self,
        habit_id: str,
        current_user_id: str,
        data: Dict[str, Any]
    ) -> Habit:
        """Update fields of an existing habit."""
        habit = self.get_habit(habit_id, current_user_id)

        if "frequency" in data:
            freq = data["frequency"]
            if freq not in ("daily", "weekdays", "weekly"):
                raise BadRequestException("Invalid frequency. Must be 'daily', 'weekdays', or 'weekly'.")
            if freq == "weekdays" and data.get("target_days_per_week", habit.target_days_per_week) > 5:
                data["target_days_per_week"] = 5

        return self.habit_repo.update_habit(habit, data)

    def delete_habit(self, habit_id: str, current_user_id: str) -> None:
        """Delete a habit and its logs."""
        habit = self.get_habit(habit_id, current_user_id)
        self.habit_repo.delete_habit(habit)

    def log_check_in(
        self,
        habit_id: str,
        current_user_id: str,
        log_date: Optional[date] = None,
        completed: bool = True,
        notes: Optional[str] = None
    ) -> HabitLog:
        """Record or update a check-in for a habit."""
        habit = self.get_habit(habit_id, current_user_id)
        target_date = log_date or date.today()

        # Validation: do not allow check-ins in the future
        if target_date > date.today():
            raise BadRequestException("Cannot log check-in for future dates")

        # Validation: prevent check-in on unscheduled weekdays if frequency is weekdays
        if habit.frequency == "weekdays" and target_date.weekday() >= 5:
            raise BadRequestException("Cannot check in on weekends for a weekday-only habit")

        return self.habit_repo.log_check_in(
            habit=habit,
            log_date=target_date,
            completed=completed,
            notes=notes
        )

    def undo_check_in(
        self,
        habit_id: str,
        log_id: str,
        current_user_id: str
    ) -> None:
        """Undo a check-in and recompute streaks."""
        habit = self.get_habit(habit_id, current_user_id)
        log = self.habit_repo.get_log_by_id(log_id)
        if not log or log.habit_id != habit.id:
            raise NotFoundException("Habit log not found")

        self.habit_repo.delete_log(habit, log)

    def get_habit_logs(
        self,
        habit_id: str,
        current_user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
    ) -> List[HabitLog]:
        """Retrieve check-in history for a habit."""
        self.get_habit(habit_id, current_user_id)
        return self.habit_repo.get_habit_logs(
            habit_id=habit_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

    def get_habit_stats(
        self,
        habit_id: str,
        current_user_id: str
    ) -> Dict[str, Any]:
        """Compute full statistical metrics and 30-day history for a habit."""
        habit = self.get_habit(habit_id, current_user_id)
        stats = self.habit_repo.calculate_streaks(habit, reference_date=date.today())

        # Include recent 30-day logs
        thirty_days_ago = date.today() - timedelta(days=29)
        recent_logs = self.habit_repo.get_habit_logs(
            habit_id=habit.id,
            start_date=thirty_days_ago,
            end_date=date.today(),
            limit=35
        )

        return {
            "habit": habit.to_dict(),
            "stats": stats,
            "recent_logs": [log.to_dict() for log in recent_logs]
        }

    def get_daily_summary(
        self,
        user_id: str,
        target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get summary of habits and completions for a single day."""
        d = target_date or date.today()
        return self.habit_repo.get_daily_summary(user_id=user_id, target_date=d)

    def get_weekly_summary(
        self,
        user_id: str,
        week_start: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get weekly summary for 7 days starting from Monday."""
        if not week_start:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        return self.habit_repo.get_weekly_summary(user_id=user_id, week_start=week_start)

    def get_monthly_summary(
        self,
        user_id: str,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get monthly calendar completion counts and percentages."""
        today = date.today()
        y = year or today.year
        m = month or today.month
        return self.habit_repo.get_monthly_summary(user_id=user_id, year=y, month=m)

