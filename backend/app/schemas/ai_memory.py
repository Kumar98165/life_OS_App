"""LifeOS - AI Memory Validation Schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class CreateMemoryRequest(BaseModel):
    """Payload for manually creating a memory."""
    memory_key: str = Field(..., min_length=1, max_length=100)
    memory_value: str = Field(..., min_length=1, max_length=5000)
    memory_type: str = Field("fact", pattern="^(preference|personal_context|goal_decision|routine_pattern|fact)$")
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    expires_at: Optional[datetime] = None

    @field_validator("memory_key", "memory_value")
    @classmethod
    def sanitize_strings(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Field cannot be blank")
        return trimmed

    model_config = {
        "extra": "forbid"
    }


class UpdateMemoryRequest(BaseModel):
    """Payload for editing a memory."""
    memory_key: Optional[str] = Field(None, min_length=1, max_length=100)
    memory_value: Optional[str] = Field(None, min_length=1, max_length=5000)
    memory_type: Optional[str] = Field(None, pattern="^(preference|personal_context|goal_decision|routine_pattern|fact)$")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    status: Optional[str] = Field(None, pattern="^(confirmed|archived|rejected)$")
    expires_at: Optional[datetime] = None

    model_config = {
        "extra": "forbid"
    }


class ApproveSuggestionRequest(BaseModel):
    """Optional edits applied while approving a pending memory suggestion."""
    edited_key: Optional[str] = Field(None, max_length=100)
    edited_value: Optional[str] = Field(None, max_length=5000)
    edited_type: Optional[str] = Field(None, pattern="^(preference|personal_context|goal_decision|routine_pattern|fact)$")

    # Also accept standard memory keys for convenience
    memory_key: Optional[str] = Field(None, max_length=100)
    memory_value: Optional[str] = Field(None, max_length=5000)
    memory_type: Optional[str] = Field(None, pattern="^(preference|personal_context|goal_decision|routine_pattern|fact)$")

    # Optional ID of an older confirmed memory to archive when approving an updated fact
    supersede_existing_id: Optional[str] = Field(None, max_length=36)

    def get_resolved_key(self) -> Optional[str]:
        return self.edited_key or self.memory_key

    def get_resolved_value(self) -> Optional[str]:
        return self.edited_value or self.memory_value

    def get_resolved_type(self) -> Optional[str]:
        return self.edited_type or self.memory_type

    model_config = {
        "extra": "forbid"
    }


class MemorySettingsRequest(BaseModel):
    """Toggle memory-based personalization."""
    ai_memory_enabled: bool

    model_config = {
        "extra": "forbid"
    }
