"""LifeOS - Voice Assistant Pydantic Schemas.

Validates:
- STT transcription requests & responses
- TTS synthesis requests
- Voice assistant turn requests & responses
- Voice settings / preferences update requests
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class VoiceTranscriptionSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str
    avg_logprob: Optional[float] = None
    no_speech_prob: Optional[float] = None


class VoiceTranscriptionResponse(BaseModel):
    text: str
    detected_language: str
    language_probability: float
    duration_seconds: float
    segments: List[VoiceTranscriptionSegment]
    model: str


class VoiceSynthesisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    language: str = Field("en", pattern="^(en|hi|hinglish)$")
    speech_rate: Optional[float] = Field(1.0, ge=0.5, le=2.0)
    speech_pitch: Optional[float] = Field(1.0, ge=0.5, le=1.5)
    voice_name: Optional[str] = None


class VoiceAssistantTurnRequest(BaseModel):
    text_input: Optional[str] = Field(None, max_length=2000)
    conversation_id: Optional[str] = None
    return_audio: bool = True


class ActionProposal(BaseModel):
    approval_id: Optional[str] = None
    action_type: str
    risk_level: str
    summary: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class VoiceAssistantTurnResponse(BaseModel):
    transcript: str
    detected_language: str
    language_probability: Optional[float] = None
    response_text: str
    conversation_id: Optional[str] = None
    requires_approval: bool = False
    action_proposals: List[ActionProposal] = Field(default_factory=list)
    audio_base64: Optional[str] = None
    audio_mime_type: Optional[str] = None


class VoicePreferenceResponse(BaseModel):
    id: str
    user_id: str
    language: str
    voice_name: str
    speech_rate: float
    speech_pitch: float
    auto_play_response: bool
    audio_privacy_enabled: bool
    confirm_actions_via_voice: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class UpdateVoicePreferenceRequest(BaseModel):
    language: Optional[str] = Field(None, pattern="^(en|hi|hinglish)$")
    voice_name: Optional[str] = Field(None, max_length=100)
    speech_rate: Optional[float] = Field(None, ge=0.5, le=2.0)
    speech_pitch: Optional[float] = Field(None, ge=0.5, le=1.5)
    auto_play_response: Optional[bool] = None
    audio_privacy_enabled: Optional[bool] = None
    confirm_actions_via_voice: Optional[bool] = None


class VoiceInfoResponse(BaseModel):
    id: str
    name: str
    languages: List[str]
    gender: Optional[str] = "unknown"
