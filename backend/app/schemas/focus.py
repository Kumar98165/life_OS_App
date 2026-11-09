from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FocusGoalUpdateSchema(BaseModel):
    daily_target_minutes: Optional[int] = Field(None, ge=1, le=1440)
    weekly_target_minutes: Optional[int] = Field(None, ge=1, le=10080)
    preferred_technique: Optional[str] = Field(None, max_length=30)
    custom_work_minutes: Optional[int] = Field(None, ge=1, le=240)
    custom_break_minutes: Optional[int] = Field(None, ge=1, le=120)
    custom_long_break_minutes: Optional[int] = Field(None, ge=1, le=120)
    long_break_interval: Optional[int] = Field(None, ge=1, le=20)


class CreateFocusSessionSchema(BaseModel):
    title: Optional[str] = Field("Focus Session", max_length=255)
    session_type: str = Field("work", max_length=30)  # work, short_break, long_break
    target_duration_minutes: int = Field(25, ge=1, le=240)
    task_id: Optional[str] = Field(None, max_length=36)
    planner_block_id: Optional[str] = Field(None, max_length=36)
    notes: Optional[str] = None


class LogDistractionSchema(BaseModel):
    distraction_type: str = Field("internal", max_length=50)  # internal, external
    description: str = Field(..., min_length=1, max_length=255)


class CompleteFocusSessionSchema(BaseModel):
    actual_duration_seconds: int = Field(..., ge=0)
    notes: Optional[str] = None

