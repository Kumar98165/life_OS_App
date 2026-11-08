from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class UpdateProfileRequest(BaseModel):
    """Payload for updating user profile attributes."""
    model_config = ConfigDict(extra="forbid")

    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)

    @field_validator("full_name")
    @classmethod
    def sanitize_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if len(trimmed) < 2:
                raise ValueError("Full name must be at least 2 characters")
            return trimmed
        return v

    @field_validator("avatar_url")
    @classmethod
    def sanitize_avatar_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            return trimmed if trimmed else None
        return v

