"""LifeOS - Habit Management Pydantic Schemas.

Validates payloads for habit creation, updates, and daily check-in logging.
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CreateHabitRequest(BaseModel):
    """Payload for creating a new recurring habit."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    frequency: str = Field("daily", pattern="^(daily|weekdays|weekly)$")
    target_days_per_week: int = Field(7, ge=1, le=7)
    color_hex: str = Field("#6C63FF", pattern="^#[0-9a-fA-F]{6}$")
    icon: Optional[str] = Field(None, max_length=50)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Habit title cannot be blank")
        return trimmed

    @field_validator("target_days_per_week")
    @classmethod
    def validate_target(cls, v: int, info) -> int:
        freq = info.data.get("frequency")
        if freq == "weekdays" and v > 5:
            return 5
        return v


class UpdateHabitRequest(BaseModel):
    """Payload for updating an existing habit."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    frequency: Optional[str] = Field(None, pattern="^(daily|weekdays|weekly)$")
    target_days_per_week: Optional[int] = Field(None, ge=1, le=7)
    color_hex: Optional[str] = Field(None, pattern="^#[0-9a-fA-F]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    is_archived: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Habit title cannot be blank")
            return trimmed
        return v

    model_config = {
        "extra": "forbid"
    }


class CreateHabitLogRequest(BaseModel):
    """Payload for recording a daily habit check-in."""
    log_date: Optional[date] = None
    completed: bool = True
    notes: Optional[str] = Field(None, max_length=1000)

    model_config = {
        "extra": "forbid"
    }

