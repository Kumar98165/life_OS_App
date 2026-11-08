from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CreateTaskRequest(BaseModel):
    """Payload for creating a new task."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    category_id: Optional[str] = None
    priority: str = Field("medium", pattern="^(low|medium|high|urgent)$")
    status: str = Field("pending", pattern="^(pending|todo|in_progress|completed|cancelled|archived)$")
    due_date: Optional[datetime] = None
    estimated_minutes: Optional[int] = Field(None, ge=1, le=1440)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Task title cannot be empty or blank")
        return trimmed

    @field_validator("status")
    @classmethod
    def normalize_status(cls, v: str) -> str:
        # Normalize "pending" and "todo" to consistent standard
        return v.lower()


class UpdateTaskRequest(BaseModel):
    """Payload for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    category_id: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    status: Optional[str] = Field(None, pattern="^(pending|todo|in_progress|completed|cancelled|archived)$")
    due_date: Optional[datetime] = None
    estimated_minutes: Optional[int] = Field(None, ge=1, le=1440)
    is_archived: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Task title cannot be empty or blank")
            return trimmed
        return v

    model_config = {
        "extra": "forbid"
    }


class CreateCategoryRequest(BaseModel):
    """Payload for creating a task category."""
    name: str = Field(..., min_length=1, max_length=100)
    color_hex: str = Field("#6C63FF", pattern="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
    icon: Optional[str] = Field(None, max_length=50)

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Category name cannot be empty")
        return trimmed

