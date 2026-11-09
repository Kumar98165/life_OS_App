"""LifeOS - Voice Assistant Blueprint Routes.

Endpoints:
- POST  /api/v1/voice/transcribe  (Multipart audio file -> STT transcript)
- POST  /api/v1/voice/assistant   (Multipart audio file OR text -> deterministic voice response + TTS audio)
- POST  /api/v1/voice/synthesize  (JSON text -> audio/wav bytes)
- GET   /api/v1/voice/voices      (List available local system voices)
- GET   /api/v1/voice/settings    (Get authenticated user voice preferences)
- PATCH /api/v1/voice/settings    (Update user voice preferences)
"""
import io
import logging
from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from app.core.response import api_response
from app.services.voice import stt_service, tts_service, voice_assistant_service
from app.schemas.voice import (
    VoiceSynthesisRequest,
    UpdateVoicePreferenceRequest,
)
from app.extensions import db

logger = logging.getLogger(__name__)

voice_bp = Blueprint("voice", __name__)


# -----------------------------------------------------------------------------
# 1. Speech-to-Text Transcription
# -----------------------------------------------------------------------------

@voice_bp.route("/transcribe", methods=["POST"])
@jwt_required()
def transcribe_audio():
    """Transcribe uploaded audio file using local STT (Whisper)."""
    if "audio" not in request.files:
        return api_response(
            message="No audio file provided in request. Key must be 'audio'.",
            status_code=400
        )

    audio_file = request.files["audio"]
    if not audio_file.filename:
        return api_response(
            message="Uploaded audio file has empty filename.",
            status_code=400
        )

    language = request.form.get("language")

    try:
        result = stt_service.transcribe_file(
            audio_stream_or_bytes=audio_file.stream,
            filename=audio_file.filename,
            language=language
        )
        return api_response(
            data=result,
            message="Speech transcribed successfully.",
            status_code=200
        )
    except ValueError as val_err:
        return api_response(
            message=str(val_err),
            status_code=400
        )
    except Exception as e:
        logger.error("STT error: %s", e, exc_info=True)
        return api_response(
            message=f"Transcription error: {str(e)}",
            status_code=500
        )


# -----------------------------------------------------------------------------
# 2. Voice Assistant Turn
# -----------------------------------------------------------------------------

@voice_bp.route("/assistant", methods=["POST"])
@jwt_required()
def voice_assistant_turn():
    """Execute complete voice assistant turn with local STT and TTS."""
    user_id = get_jwt_identity()

    # Supports both multipart/form-data (audio file + form fields) and application/json (text fallback)
    audio_stream = None
    filename = "recording.wav"
    text_input = None
    conversation_id = None
    return_audio = True

    if request.content_type and "multipart/form-data" in request.content_type:
        if "audio" in request.files:
            audio_file = request.files["audio"]
            audio_stream = audio_file.stream
            filename = audio_file.filename or filename
        text_input = request.form.get("text_input")
        conversation_id = request.form.get("conversation_id")
        return_audio = request.form.get("return_audio", "true").lower() in ("true", "1", "yes")
    else:
        json_data = request.get_json(silent=True) or {}
        text_input = json_data.get("text_input")
        conversation_id = json_data.get("conversation_id")
        return_audio = json_data.get("return_audio", True)

    try:
        turn_result = voice_assistant_service.process_voice_turn(
            user_id=user_id,
            audio_stream_or_bytes=audio_stream,
            filename=filename,
            text_input=text_input,
            conversation_id=conversation_id,
            return_audio=return_audio
        )
        return api_response(
            data=turn_result,
            message="Voice turn processed successfully.",
            status_code=200
        )
    except ValueError as val_err:
        return api_response(
            message=str(val_err),
            status_code=400
        )
    except Exception as e:
        logger.error("Voice assistant error: %s", e, exc_info=True)
        return api_response(
            message=f"Voice assistant processing error: {str(e)}",
            status_code=500
        )


# -----------------------------------------------------------------------------
# 3. Text-to-Speech Synthesis Direct Stream
# -----------------------------------------------------------------------------

@voice_bp.route("/synthesize", methods=["POST"])
@jwt_required()
def synthesize_speech():
    """Synthesize text to speech audio WAV stream."""
    json_data = request.get_json(silent=True) or {}
    try:
        validated = VoiceSynthesisRequest(**json_data)
    except ValidationError as err:
        return api_response(
            message=f"Validation error: {err.errors()}",
            status_code=400
        )

    try:
        wav_bytes = tts_service.synthesize_to_wav_bytes(
            text=validated.text,
            language=validated.language,
            speech_rate=validated.speech_rate or 1.0,
            voice_id=validated.voice_name
        )
        return send_file(
            io.BytesIO(wav_bytes),
            mimetype="audio/wav",
            as_attachment=False,
            download_name="speech.wav"
        )
    except Exception as e:
        logger.error("Synthesis error: %s", e, exc_info=True)
        return api_response(
            message=f"Synthesis error: {str(e)}",
            status_code=500
        )


# -----------------------------------------------------------------------------
# 4. Voice Enumeration
# -----------------------------------------------------------------------------

@voice_bp.route("/voices", methods=["GET"])
@jwt_required()
def get_available_voices():
    """List local system voices available for synthesis."""
    voices = tts_service.get_available_voices()
    return api_response(
        data={"voices": voices, "count": len(voices)},
        message="Available voices retrieved.",
        status_code=200
    )


# -----------------------------------------------------------------------------
# 5. User Voice Preferences
# -----------------------------------------------------------------------------

@voice_bp.route("/settings", methods=["GET"])
@jwt_required()
def get_voice_settings():
    """Retrieve voice settings for authenticated user."""
    user_id = get_jwt_identity()
    prefs = voice_assistant_service.get_or_create_voice_preferences(user_id)
    return api_response(
        data=prefs.to_dict(),
        message="Voice preferences retrieved.",
        status_code=200
    )


@voice_bp.route("/settings", methods=["PATCH"])
@jwt_required()
def update_voice_settings():
    """Update voice preferences for authenticated user."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}

    try:
        validated = UpdateVoicePreferenceRequest(**json_data)
    except ValidationError as err:
        return api_response(
            message=f"Validation error: {err.errors()}",
            status_code=400
        )

    prefs = voice_assistant_service.get_or_create_voice_preferences(user_id)

    update_fields = validated.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        if value is not None and hasattr(prefs, key):
            setattr(prefs, key, value)

    db.session.commit()

    return api_response(
        data=prefs.to_dict(),
        message="Voice preferences updated successfully.",
        status_code=200
    )
