from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CreateGoalRequest(BaseModel):
    """Payload for creating a new goal."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    target_date: Optional[datetime] = None
    priority: str = Field("medium", pattern="^(low|medium|high)$")
    status: str = Field("in_progress", pattern="^(not_started|in_progress|completed|paused|cancelled|active|achieved|abandoned)$")
    category: Optional[str] = Field(None, max_length=50)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Goal title cannot be blank")
        return trimmed


class UpdateGoalRequest(BaseModel):
    """Payload for updating an existing goal."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    target_date: Optional[datetime] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    status: Optional[str] = Field(None, pattern="^(not_started|in_progress|completed|paused|cancelled|active|achieved|abandoned)$")
    category: Optional[str] = Field(None, max_length=50)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Goal title cannot be blank")
            return trimmed
        return v

    model_config = {
        "extra": "forbid"
    }


class CreateMilestoneRequest(BaseModel):
    """Payload for creating a milestone within a goal."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    target_date: Optional[datetime] = None
    is_completed: bool = False
    sort_order: int = Field(0, ge=0)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Milestone title cannot be blank")
        return trimmed


class UpdateMilestoneRequest(BaseModel):
    """Payload for updating an existing milestone."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    target_date: Optional[datetime] = None
    is_completed: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Milestone title cannot be blank")
            return trimmed
        return v

    model_config = {
        "extra": "forbid"
    }


class CompleteMilestoneRequest(BaseModel):
    """Payload for toggling milestone completion."""
    is_completed: bool

