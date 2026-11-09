"""LifeOS - Personalization Pydantic Schemas.

Validates:
- General personalization settings (identity, language, date/time formatting, productivity style, AI style)
- Dashboard customization (widget visibility, ordering, density)
- Daily routine (working hours, focus/break blocks, rituals, planning time)
- Privacy controls & targeted preference resets
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DashboardWidgetItem(BaseModel):
    id: str = Field(..., min_length=1, max_length=50)
    visible: bool = True
    order: int = Field(0, ge=0)
    title: str = Field(..., min_length=1, max_length=100)


class UpdateDashboardPreferencesRequest(BaseModel):
    dashboard_widgets: Optional[List[DashboardWidgetItem]] = None
    dashboard_density: Optional[str] = Field(None, pattern="^(compact|comfortable)$")


class UpdatePersonalizationRequest(BaseModel):
    preferred_name: Optional[str] = Field(None, max_length=100)
    preferred_language: Optional[str] = Field(None, pattern="^(en|hi|hinglish|es|fr|de)$")
    timezone: Optional[str] = Field(None, max_length=50)
    date_format: Optional[str] = Field(None, pattern="^(YYYY-MM-DD|DD/MM/YYYY|MM/DD/YYYY)$")
    time_format: Optional[str] = Field(None, pattern="^(12h|24h)$")
    week_start_day: Optional[str] = Field(None, pattern="^(monday|sunday)$")
    productivity_style: Optional[str] = Field(None, pattern="^(structured|flexible|pomodoro|deep_work)$")
    task_priority_strategy: Optional[str] = Field(None, pattern="^(eisenhower|deadline_first|impact_first|quick_wins)$")
    ai_response_style: Optional[str] = Field(None, pattern="^(concise|detailed|motivational|formal)$")
    ai_response_length: Optional[str] = Field(None, pattern="^(short|medium|comprehensive)$")
    personalization_enabled: Optional[bool] = None


class UpdateDailyRoutineRequest(BaseModel):
    wake_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    sleep_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    work_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    work_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    work_days: Optional[List[str]] = None
    focus_block_duration_minutes: Optional[int] = Field(None, ge=15, le=180)
    break_duration_minutes: Optional[int] = Field(None, ge=5, le=60)
    lunch_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    lunch_duration_minutes: Optional[int] = Field(None, ge=15, le=120)
    morning_routine_enabled: Optional[bool] = None
    evening_routine_enabled: Optional[bool] = None
    preferred_planning_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    routine_reminders_enabled: Optional[bool] = None


class ResetPreferencesRequest(BaseModel):
    target: str = Field(..., pattern="^(all|dashboard|routine|identity|ai_style)$")
