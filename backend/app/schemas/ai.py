"""LifeOS - AI Request & Response Validation Schemas."""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Payload for submitting a message to the AI assistant."""
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = Field(None, max_length=36)

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Message cannot be blank")
        return trimmed

    model_config = {
        "extra": "forbid"
    }


class CreateConversationRequest(BaseModel):
    """Payload for manually starting a named conversation thread."""
    title: Optional[str] = Field(None, max_length=255)

    model_config = {
        "extra": "forbid"
    }

