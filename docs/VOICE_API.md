# LifeOS Voice API Reference

Base URL: `/api/v1/voice`  
Authentication: `Authorization: Bearer <JWT_ACCESS_TOKEN>`

---

## 1. POST /api/v1/voice/transcribe
Uploads an audio file and returns text transcription.

### Request
- `Content-Type`: `multipart/form-data`
- Body fields:
  - `audio`: Audio file (wav, mp3, m4a, ogg, webm) (Required)
  - `language`: `en` or `hi` (Optional)

### Response (200 OK)
```json
{
  "status": "success",
  "data": {
    "text": "Plan my day for tomorrow morning",
    "detected_language": "en",
    "language_probability": 0.985,
    "duration_seconds": 2.8,
    "segments": [
      {
        "id": 0,
        "start": 0.0,
        "end": 2.8,
        "text": "Plan my day for tomorrow morning"
      }
    ],
    "model": "faster-whisper-tiny"
  }
}
```

---

## 2. POST /api/v1/voice/assistant
Executes a complete voice turn. Accepts either audio file upload or text prompt fallback.

### Request (Multipart or JSON)
- `audio`: File (optional if text_input provided)
- `text_input`: String (optional if audio provided)
- `conversation_id`: String (optional)
- `return_audio`: Boolean (default `true`)

### Response (200 OK)
```json
{
  "status": "success",
  "data": {
    "transcript": "What are my priorities today?",
    "detected_language": "en",
    "response_text": "You have 3 tasks pending: Finish budget audit, Review habit streaks, and Team standup at 2 PM.",
    "conversation_id": "conv-1234",
    "requires_approval": false,
    "action_proposals": [],
    "audio_base64": "UklGRi4AAABXQVZF...",
    "audio_mime_type": "audio/wav"
  }
}
```

---

## 3. POST /api/v1/voice/synthesize
Generates raw audio bytes from text.

### Request
- `Content-Type`: `application/json`
```json
{
  "text": "LifeOS voice synthesis completed.",
  "language": "en",
  "speech_rate": 1.0,
  "voice_name": "default"
}
```

### Response (200 OK)
- `Content-Type`: `audio/wav`
- Raw binary stream of RIFF WAV file.

---

## 4. GET & PATCH /api/v1/voice/settings
Manages user voice preferences.

### GET Response
```json
{
  "status": "success",
  "data": {
    "language": "en",
    "voice_name": "default",
    "speech_rate": 1.0,
    "speech_pitch": 1.0,
    "auto_play_response": true,
    "audio_privacy_enabled": true,
    "confirm_actions_via_voice": true
  }
}
```

### PATCH Request
```json
{
  "language": "hi",
  "speech_rate": 1.25,
  "auto_play_response": false
}
```
