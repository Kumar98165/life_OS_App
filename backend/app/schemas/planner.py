from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class CreatePlannerBlockRequest(BaseModel):
    """Payload for scheduling a new planner block."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    start_time: datetime
    end_time: datetime
    block_type: str = Field("task", pattern="^(task|personal|work|break|learning|meeting|other|focus|routine)$")
    status: str = Field("scheduled", pattern="^(scheduled|completed|cancelled|skipped)$")
    task_id: Optional[str] = None
    color_hex: Optional[str] = Field(None, pattern="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Planner block title cannot be blank")
        return trimmed

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be strictly earlier than end_time")
        return self


class UpdatePlannerBlockRequest(BaseModel):
    """Payload for updating an existing planner block."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    block_type: Optional[str] = Field(None, pattern="^(task|personal|work|break|learning|meeting|other|focus|routine)$")
    status: Optional[str] = Field(None, pattern="^(scheduled|completed|cancelled|skipped)$")
    task_id: Optional[str] = None
    color_hex: Optional[str] = Field(None, pattern="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Planner block title cannot be blank")
            return trimmed
        return v

    model_config = {
        "extra": "forbid"
    }


class UpdateBlockStatusRequest(BaseModel):
    """Payload for updating planner block status."""
    status: str = Field(..., pattern="^(scheduled|completed|cancelled|skipped)$")

