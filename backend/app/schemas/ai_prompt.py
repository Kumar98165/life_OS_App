"""LifeOS - AI Prompt Version Validation Schemas.

Pydantic v2 schemas for creating, managing, and activating immutable
AI system prompt templates.
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CreatePromptVersionRequest(BaseModel):
    """Payload for creating a new immutable AI prompt version."""
    version_tag: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique semantic version tag (e.g., v1.1.0, v2.0.0-structured)"
    )
    prompt_template: str = Field(
        ...,
        min_length=10,
        max_length=20000,
        description="Complete system prompt text including context placeholders"
    )
    change_summary: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Human-readable summary of rationale and changes introduced"
    )
    activate_immediately: Optional[bool] = Field(
        False,
        description="Whether to immediately promote this version to active upon creation"
    )

    @field_validator("version_tag")
    @classmethod
    def sanitize_tag(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("version_tag cannot be blank")
        return trimmed

    @field_validator("change_summary")
    @classmethod
    def sanitize_summary(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("change_summary cannot be blank")
        return trimmed

    @field_validator("prompt_template")
    @classmethod
    def validate_template(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("prompt_template cannot be blank")
        if "{context_block}" not in trimmed:
            raise ValueError("prompt_template must include '{context_block}' placeholder for domain context injection")
        return trimmed

    model_config = {
        "extra": "forbid"
    }

