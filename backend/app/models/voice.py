"""LifeOS - Voice Preference and Settings Data Model.

Stores user-specific voice assistant preferences including:
- Preferred language (en, hi, hinglish)
- Voice identifier/name
- Speech rate (speed multiplier: 0.5 to 2.0)
- Pitch adjustment
- Auto-play audio response toggle
- Voice confirmation threshold (auto-approval safety setting)
- Audio privacy settings (never retain raw audio files)
"""
from typing import Dict, Any, Optional
from sqlalchemy import String, Boolean, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class VoicePreference(BaseModel):
    """User-specific voice synthesis, recognition, and privacy preferences."""
    __tablename__ = "voice_preferences"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    # Language preferences: 'en' (English), 'hi' (Hindi), 'hinglish' (Bilingual)
    language: Mapped[str] = mapped_column(
        String(20),
        default="en",
        nullable=False
    )

    # Voice identifier (e.g. system voice ID or friendly name)
    voice_name: Mapped[str] = mapped_column(
        String(100),
        default="default",
        nullable=False
    )

    # Speech rate multiplier: 0.5 (slow) to 2.0 (fast). 1.0 is standard.
    speech_rate: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False
    )

    # Speech pitch multiplier: 0.5 to 1.5
    speech_pitch: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False
    )

    # Auto-play audio response in mobile UI
    auto_play_response: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Audio privacy: true = delete audio files immediately after processing (Zero Audio Retention)
    audio_privacy_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Voice input confirmation prompts enabled
    confirm_actions_via_voice: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="voice_preference")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize voice preferences to dict."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "language": self.language,
            "voice_name": self.voice_name,
            "speech_rate": self.speech_rate,
            "speech_pitch": self.speech_pitch,
            "auto_play_response": self.auto_play_response,
            "audio_privacy_enabled": self.audio_privacy_enabled,
            "confirm_actions_via_voice": self.confirm_actions_via_voice,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
