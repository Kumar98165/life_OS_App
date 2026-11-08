"""LifeOS - AI Feedback & Training Consent Schemas.

Pydantic v2 validation models for assistant response feedback collection,
rating submissions, corrections, and AI training privacy consent.
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator

SUPPORTED_FEEDBACK_CATEGORIES = (
    "incorrect_answer",
    "incomplete_answer",
    "irrelevant_answer",
    "poor_explanation",
    "wrong_tone",
    "outdated_context",
    "other",
)

SUPPORTED_FEEDBACK_TYPES = (
    "thumbs_up",
    "thumbs_down",
    "correction",
    "issue_report",
)


class SubmitFeedbackRequest(BaseModel):
    """Payload for submitting feedback on an AI assistant response turn."""
    message_id: str = Field(..., min_length=36, max_length=36, description="UUID of the assistant message")
    rating: int = Field(..., description="Feedback rating: +1 (thumbs up) or -1 (thumbs down)")
    feedback_type: Optional[str] = Field(None, max_length=30)
    category: Optional[str] = Field(None, max_length=50)
    comment: Optional[str] = Field(None, max_length=2000)
    suggested_response: Optional[str] = Field(None, max_length=5000)

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v not in (1, -1):
            raise ValueError("Rating must be +1 (thumbs up) or -1 (thumbs down)")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip().lower()
        if not trimmed:
            return None
        if trimmed not in SUPPORTED_FEEDBACK_CATEGORIES:
            raise ValueError(
                f"Invalid category '{trimmed}'. Supported categories: {', '.join(SUPPORTED_FEEDBACK_CATEGORIES)}"
            )
        return trimmed

    @field_validator("feedback_type")
    @classmethod
    def validate_feedback_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip().lower()
        if not trimmed:
            return None
        if trimmed not in SUPPORTED_FEEDBACK_TYPES:
            raise ValueError(
                f"Invalid feedback_type '{trimmed}'. Supported types: {', '.join(SUPPORTED_FEEDBACK_TYPES)}"
            )
        return trimmed

    @field_validator("comment", "suggested_response")
    @classmethod
    def sanitize_text(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        return trimmed if trimmed else None

    model_config = {
        "extra": "forbid"
    }


class UpdateFeedbackRequest(BaseModel):
    """Payload for editing existing feedback."""
    rating: Optional[int] = Field(None, description="Updated rating: +1 or -1")
    feedback_type: Optional[str] = Field(None, max_length=30)
    category: Optional[str] = Field(None, max_length=50)
    comment: Optional[str] = Field(None, max_length=2000)
    suggested_response: Optional[str] = Field(None, max_length=5000)

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in (1, -1):
            raise ValueError("Rating must be +1 (thumbs up) or -1 (thumbs down)")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip().lower()
        if not trimmed:
            return None
        if trimmed not in SUPPORTED_FEEDBACK_CATEGORIES:
            raise ValueError(
                f"Invalid category '{trimmed}'. Supported categories: {', '.join(SUPPORTED_FEEDBACK_CATEGORIES)}"
            )
        return trimmed

    @field_validator("feedback_type")
    @classmethod
    def validate_feedback_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip().lower()
        if not trimmed:
            return None
        if trimmed not in SUPPORTED_FEEDBACK_TYPES:
            raise ValueError(
                f"Invalid feedback_type '{trimmed}'. Supported types: {', '.join(SUPPORTED_FEEDBACK_TYPES)}"
            )
        return trimmed

    @field_validator("comment", "suggested_response")
    @classmethod
    def sanitize_text(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        return trimmed if trimmed else None

    model_config = {
        "extra": "forbid"
    }


class UpdateConsentRequest(BaseModel):
    """Payload for updating user AI training consent preference."""
    ai_training_consent: bool = Field(..., description="Explicit opt-in/opt-out for AI training dataset usage")

    model_config = {
        "extra": "forbid"
    }

