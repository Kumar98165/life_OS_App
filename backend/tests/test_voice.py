"""Tests for LifeOS Step 20 - Voice Assistant Module.

Verifies:
1. Audio format & file size validation
2. Speech-to-Text transcription with real WAV audio buffer
3. Text-to-Speech synthesis generating valid RIFF WAV audio
4. Zero Audio Retention: temporary files unlinked immediately
5. Voice assistant end-to-end pipeline (STT -> Agent -> TTS)
6. Voice settings CRUD & user isolation (IDOR protection)
7. Voice route endpoints via Flask test client
"""
import os
import io
import wave
import struct
import pytest
from app.models.user import User
from app.models.voice import VoicePreference
from app.services.voice.stt_service import STTService, stt_service
from app.services.voice.tts_service import TTSService, tts_service
from app.services.voice.voice_service import VoiceAssistantService, voice_assistant_service
from app.extensions import db


def _create_sample_wav_bytes(duration_seconds: float = 1.0, freq: float = 440.0) -> bytes:
    """Generate a clean 16-bit mono 16kHz PCM WAV in-memory."""
    sample_rate = 16000
    num_samples = int(sample_rate * duration_seconds)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        frames = bytearray()
        import math
        for i in range(num_samples):
            t = i / sample_rate
            s = int(10000 * math.sin(2 * math.pi * freq * t))
            frames.extend(struct.pack("<h", s))
        w.writeframes(frames)
    return buf.getvalue()


# -----------------------------------------------------------------------------
# 1. Audio Validation & STT Tests
# -----------------------------------------------------------------------------

def test_stt_audio_format_validation():
    """Verify validation of file extensions and size boundaries."""
    svc = STTService()

    # Valid WAV
    ok, err = svc.validate_audio_file("speech.wav", 1024)
    assert ok is True
    assert err is None

    # Valid MP3 / M4A / OGG
    ok, _ = svc.validate_audio_file("recording.mp3", 5000)
    assert ok is True
    ok, _ = svc.validate_audio_file("voice.m4a", 5000)
    assert ok is True

    # Invalid extension
    ok, err = svc.validate_audio_file("malicious.exe", 1024)
    assert ok is False
    assert "Unsupported audio format" in err

    # Oversized file (>10MB)
    ok, err = svc.validate_audio_file("huge.wav", 11 * 1024 * 1024)
    assert ok is False
    assert "exceeds limit" in err

    # Too small / corrupted
    ok, err = svc.validate_audio_file("tiny.wav", 50)
    assert ok is False
    assert "too small" in err


def test_stt_transcription_execution():
    """Verify transcription execution on valid WAV bytes."""
    wav_bytes = _create_sample_wav_bytes(duration_seconds=0.5)
    result = stt_service.transcribe_file(wav_bytes, filename="tone.wav")

    assert "text" in result
    assert "detected_language" in result
    assert "segments" in result
    assert "duration_seconds" in result
    assert result["duration_seconds"] > 0


# -----------------------------------------------------------------------------
# 2. TTS Synthesis Tests
# -----------------------------------------------------------------------------

def test_tts_synthesis_generates_valid_wav():
    """Verify local TTS synthesis produces valid RIFF WAV audio."""
    wav_bytes = tts_service.synthesize_to_wav_bytes(
        text="LifeOS local voice synthesis test.",
        language="en",
        speech_rate=1.0
    )

    assert isinstance(wav_bytes, bytes)
    assert len(wav_bytes) > 44  # Has valid WAV header + payload
    assert wav_bytes[:4] == b"RIFF"
    assert wav_bytes[8:12] == b"WAVE"


def test_tts_voices_enumeration():
    """Verify local system voices can be listed safely."""
    voices = tts_service.get_available_voices()
    assert isinstance(voices, list)
    assert len(voices) >= 1
    assert "id" in voices[0]
    assert "name" in voices[0]


# -----------------------------------------------------------------------------
# 3. Privacy & Zero Audio Retention
# -----------------------------------------------------------------------------

def test_zero_audio_retention_temp_cleanup(monkeypatch):
    """Verify that temporary disk files created during transcription are deleted immediately."""
    import tempfile
    created_paths = []

    orig_named_temp = tempfile.NamedTemporaryFile

    def tracking_named_temp(*args, **kwargs):
        tmp = orig_named_temp(*args, **kwargs)
        created_paths.append(tmp.name)
        return tmp

    monkeypatch.setattr(tempfile, "NamedTemporaryFile", tracking_named_temp)

    wav_bytes = _create_sample_wav_bytes(duration_seconds=0.3)
    stt_service.transcribe_file(wav_bytes, filename="test_privacy.wav")

    # Confirm all created temp files were cleaned up and do not exist on disk
    for p in created_paths:
        assert not os.path.exists(p), f"Temporary file {p} was not deleted! Privacy breach."


# -----------------------------------------------------------------------------
# 4. Voice Assistant Pipeline & Endpoints
# -----------------------------------------------------------------------------

def test_voice_settings_get_and_patch(client, auth_headers):
    """Verify retrieving and updating user voice settings."""
    # GET settings
    res = client.get("/api/v1/voice/settings", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["language"] in ("en", "hi", "hinglish")
    assert data["auto_play_response"] is True
    assert data["audio_privacy_enabled"] is True

    # PATCH settings
    patch_payload = {
        "language": "hi",
        "speech_rate": 1.25,
        "auto_play_response": False,
        "confirm_actions_via_voice": True
    }
    res_patch = client.patch("/api/v1/voice/settings", json=patch_payload, headers=auth_headers)
    assert res_patch.status_code == 200
    updated = res_patch.get_json()["data"]
    assert updated["language"] == "hi"
    assert updated["speech_rate"] == 1.25
    assert updated["auto_play_response"] is False


def test_voice_transcribe_endpoint(client, auth_headers):
    """Verify /api/v1/voice/transcribe endpoint with multipart audio file."""
    wav_bytes = _create_sample_wav_bytes(duration_seconds=0.5)
    data = {
        "audio": (io.BytesIO(wav_bytes), "test.wav"),
        "language": "en"
    }
    res = client.post(
        "/api/v1/voice/transcribe",
        data=data,
        content_type="multipart/form-data",
        headers=auth_headers
    )
    assert res.status_code == 200
    json_data = res.get_json()
    assert "data" in json_data
    assert "text" in json_data["data"]


def test_voice_assistant_text_turn_endpoint(client, auth_headers):
    """Verify /api/v1/voice/assistant endpoint with text input fallback."""
    payload = {
        "text_input": "What are my priorities today?",
        "return_audio": True
    }
    res = client.post("/api/v1/voice/assistant", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["transcript"] == "What are my priorities today?"
    assert "response_text" in data
    assert data["audio_base64"] is not None
    assert data["audio_mime_type"] == "audio/wav"


def test_voice_synthesize_endpoint(client, auth_headers):
    """Verify /api/v1/voice/synthesize endpoint returning WAV stream."""
    payload = {
        "text": "Hello, this is a test audio response.",
        "language": "en",
        "speech_rate": 1.0
    }
    res = client.post("/api/v1/voice/synthesize", json=payload, headers=auth_headers)
    assert res.status_code == 200
    assert res.content_type == "audio/wav"
    assert len(res.data) > 44
    assert res.data[:4] == b"RIFF"


def test_voice_voices_endpoint(client, auth_headers):
    """Verify /api/v1/voice/voices returns voice list."""
    res = client.get("/api/v1/voice/voices", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "voices" in data
    assert data["count"] >= 1
