"""LifeOS - Personalization & Daily Routine Data Models.

Defines:
1. UserPersonalization: Personal identity, regional formatting, productivity & AI style, dashboard configuration.
2. DailyRoutine: Typical schedule boundaries, work hours, focus blocks, morning/evening rituals, and planning preferences.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy import String, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


DEFAULT_DASHBOARD_WIDGETS = [
    {"id": "daily_overview", "visible": True, "order": 0, "title": "Daily Overview"},
    {"id": "quick_actions", "visible": True, "order": 1, "title": "Quick Actions"},
    {"id": "upcoming_schedule", "visible": True, "order": 2, "title": "Upcoming Schedule"},
    {"id": "today_tasks", "visible": True, "order": 3, "title": "Today's Tasks"},
    {"id": "active_goals", "visible": True, "order": 4, "title": "Active Goals"},
    {"id": "habit_summary", "visible": True, "order": 5, "title": "Habits & Streaks"},
    {"id": "finance_quick", "visible": True, "order": 6, "title": "Money Management"},
    {"id": "analytics_quick", "visible": True, "order": 7, "title": "Life Analytics"},
]


class UserPersonalization(BaseModel):
    """Personalized user preferences, identity styling, AI behavior, and dashboard layouts."""
    __tablename__ = "user_personalizations"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    # 1. Identity & Regional Preferences
    preferred_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(20), default="en", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    date_format: Mapped[str] = mapped_column(String(20), default="YYYY-MM-DD", nullable=False)  # YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY
    time_format: Mapped[str] = mapped_column(String(10), default="24h", nullable=False)  # 12h, 24h
    week_start_day: Mapped[str] = mapped_column(String(10), default="monday", nullable=False)  # monday, sunday

    # 2. Productivity & Strategy Styles
    productivity_style: Mapped[str] = mapped_column(
        String(30), default="structured", nullable=False
    )  # structured, flexible, pomodoro, deep_work
    task_priority_strategy: Mapped[str] = mapped_column(
        String(30), default="eisenhower", nullable=False
    )  # eisenhower, deadline_first, impact_first, quick_wins

    # 3. AI Assistant Response Style
    ai_response_style: Mapped[str] = mapped_column(
        String(30), default="concise", nullable=False
    )  # concise, detailed, motivational, formal
    ai_response_length: Mapped[str] = mapped_column(
        String(20), default="medium", nullable=False
    )  # short, medium, comprehensive

    # 4. Dashboard Customization
    dashboard_widgets: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON, default=DEFAULT_DASHBOARD_WIDGETS, nullable=False
    )
    dashboard_density: Mapped[str] = mapped_column(
        String(20), default="comfortable", nullable=False
    )  # compact, comfortable

    # 5. Independent Privacy & Personalization Controls
    personalization_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="personalization")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize personalization settings."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "preferred_name": self.preferred_name,
            "preferred_language": self.preferred_language,
            "timezone": self.timezone,
            "date_format": self.date_format,
            "time_format": self.time_format,
            "week_start_day": self.week_start_day,
            "productivity_style": self.productivity_style,
            "task_priority_strategy": self.task_priority_strategy,
            "ai_response_style": self.ai_response_style,
            "ai_response_length": self.ai_response_length,
            "dashboard_widgets": self.dashboard_widgets,
            "dashboard_density": self.dashboard_density,
            "personalization_enabled": self.personalization_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DailyRoutine(BaseModel):
    """User-configured daily rhythm, schedule boundaries, focus windows, and rituals."""
    __tablename__ = "daily_routines"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    # Typical Sleep / Wake boundaries (HH:MM 24h format)
    wake_time: Mapped[str] = mapped_column(String(10), default="07:00", nullable=False)
    sleep_time: Mapped[str] = mapped_column(String(10), default="23:00", nullable=False)

    # Working hours
    work_start: Mapped[str] = mapped_column(String(10), default="09:00", nullable=False)
    work_end: Mapped[str] = mapped_column(String(10), default="17:00", nullable=False)
    work_days: Mapped[List[str]] = mapped_column(
        JSON,
        default=["monday", "tuesday", "wednesday", "thursday", "friday"],
        nullable=False
    )

    # Focus & Breaks
    focus_block_duration_minutes: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    break_duration_minutes: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    lunch_start: Mapped[str] = mapped_column(String(10), default="12:30", nullable=False)
    lunch_duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)

    # Rituals and Planning preferences
    morning_routine_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    evening_routine_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    preferred_planning_time: Mapped[str] = mapped_column(String(10), default="08:30", nullable=False)
    routine_reminders_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="daily_routine")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize daily routine configuration."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "wake_time": self.wake_time,
            "sleep_time": self.sleep_time,
            "work_start": self.work_start,
            "work_end": self.work_end,
            "work_days": self.work_days,
            "focus_block_duration_minutes": self.focus_block_duration_minutes,
            "break_duration_minutes": self.break_duration_minutes,
            "lunch_start": self.lunch_start,
            "lunch_duration_minutes": self.lunch_duration_minutes,
            "morning_routine_enabled": self.morning_routine_enabled,
            "evening_routine_enabled": self.evening_routine_enabled,
            "preferred_planning_time": self.preferred_planning_time,
            "routine_reminders_enabled": self.routine_reminders_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
