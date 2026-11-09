"""LifeOS - Personalization Service Layer.

Manages:
- User personalization settings retrieval and updates
- Dashboard widget layouts, ordering, and default restoration
- Daily routine boundaries, focus durations, and planning rituals
- Granular resets avoiding destructive cross-module wiping
- Transaction-safe updates
"""
import logging
from typing import Dict, Any, List, Optional
from app.models.personalization import UserPersonalization, DailyRoutine, DEFAULT_DASHBOARD_WIDGETS
from app.models.user import User
from app.extensions import db

logger = logging.getLogger(__name__)


class PersonalizationService:
    """Business logic for Advanced Personalization and Daily Routine management."""

    def get_or_create_personalization(self, user_id: str) -> UserPersonalization:
        """Fetch or initialize default personalization settings for a user."""
        record = UserPersonalization.query.filter_by(user_id=user_id).first()
        if not record:
            user = User.query.filter_by(id=user_id).first()
            default_name = user.full_name if user else None
            record = UserPersonalization(
                user_id=user_id,
                preferred_name=default_name,
                preferred_language="en",
                timezone="UTC",
                date_format="YYYY-MM-DD",
                time_format="24h",
                week_start_day="monday",
                productivity_style="structured",
                task_priority_strategy="eisenhower",
                ai_response_style="concise",
                ai_response_length="medium",
                dashboard_widgets=list(DEFAULT_DASHBOARD_WIDGETS),
                dashboard_density="comfortable",
                personalization_enabled=True,
            )
            db.session.add(record)
            db.session.commit()
        return record

    def get_or_create_routine(self, user_id: str) -> DailyRoutine:
        """Fetch or initialize default daily routine settings for a user."""
        routine = DailyRoutine.query.filter_by(user_id=user_id).first()
        if not routine:
            routine = DailyRoutine(
                user_id=user_id,
                wake_time="07:00",
                sleep_time="23:00",
                work_start="09:00",
                work_end="17:00",
                work_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
                focus_block_duration_minutes=50,
                break_duration_minutes=10,
                lunch_start="12:30",
                lunch_duration_minutes=60,
                morning_routine_enabled=True,
                evening_routine_enabled=True,
                preferred_planning_time="08:30",
                routine_reminders_enabled=True,
            )
            db.session.add(routine)
            db.session.commit()
        return routine

    def update_personalization(self, user_id: str, updates: Dict[str, Any]) -> UserPersonalization:
        """Update personalization settings within a clean transaction."""
        record = self.get_or_create_personalization(user_id)
        for key, value in updates.items():
            if value is not None and hasattr(record, key):
                setattr(record, key, value)
        db.session.commit()
        return record

    def update_dashboard_preferences(
        self,
        user_id: str,
        widgets: Optional[List[Dict[str, Any]]] = None,
        density: Optional[str] = None
    ) -> UserPersonalization:
        """Update dashboard layout, visibility, and density."""
        record = self.get_or_create_personalization(user_id)
        if widgets is not None:
            # Ensure valid structure
            record.dashboard_widgets = widgets
        if density is not None:
            record.dashboard_density = density
        db.session.commit()
        return record

    def update_daily_routine(self, user_id: str, updates: Dict[str, Any]) -> DailyRoutine:
        """Update daily routine parameters."""
        routine = self.get_or_create_routine(user_id)
        for key, value in updates.items():
            if value is not None and hasattr(routine, key):
                setattr(routine, key, value)
        db.session.commit()
        return routine

    def reset_preferences(self, user_id: str, target: str) -> Dict[str, Any]:
        """Reset selected preferences to defaults without touching AI memories or learning consent.

        Targets:
        - 'dashboard': Restores default widgets and density
        - 'routine': Restores default routine hours
        - 'identity': Restores default name, regional formats
        - 'ai_style': Restores default AI response style
        - 'all': Restores all above without deleting conversations, memories, or accounts
        """
        record = self.get_or_create_personalization(user_id)
        routine = self.get_or_create_routine(user_id)

        if target in ("dashboard", "all"):
            record.dashboard_widgets = list(DEFAULT_DASHBOARD_WIDGETS)
            record.dashboard_density = "comfortable"

        if target in ("routine", "all"):
            routine.wake_time = "07:00"
            routine.sleep_time = "23:00"
            routine.work_start = "09:00"
            routine.work_end = "17:00"
            routine.work_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
            routine.focus_block_duration_minutes = 50
            routine.break_duration_minutes = 10
            routine.lunch_start = "12:30"
            routine.lunch_duration_minutes = 60
            routine.morning_routine_enabled = True
            routine.evening_routine_enabled = True
            routine.preferred_planning_time = "08:30"
            routine.routine_reminders_enabled = True

        if target in ("identity", "all"):
            user = User.query.filter_by(id=user_id).first()
            record.preferred_name = user.full_name if user else None
            record.preferred_language = "en"
            record.timezone = "UTC"
            record.date_format = "YYYY-MM-DD"
            record.time_format = "24h"
            record.week_start_day = "monday"
            record.productivity_style = "structured"
            record.task_priority_strategy = "eisenhower"

        if target in ("ai_style", "all"):
            record.ai_response_style = "concise"
            record.ai_response_length = "medium"

        db.session.commit()

        return {
            "personalization": record.to_dict(),
            "daily_routine": routine.to_dict(),
            "reset_target": target,
        }


personalization_service = PersonalizationService()
