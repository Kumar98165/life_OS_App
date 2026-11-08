# LifeOS Local Speech-to-Text (STT) Setup

## 1. Engine Specifications

LifeOS uses `faster-whisper` for local speech recognition:
- **Engine**: CTranslate2 implementation of OpenAI Whisper.
- **Default Model**: `tiny` (39M parameters, ~75MB disk footprint) for sub-second CPU response.
- **Compute Type**: `int8` quantization for minimal memory usage and fast CPU inference.
- **Alternative Models**: `base` (74M params) or `small` (244M params) can be configured via environment settings.

---

## 2. Dependencies & Installation

### Python Backend
```bash
pip install faster-whisper
```

### PyAV Monkey-Patch
In Windows environments running newer PyAV versions, `faster-whisper` requires stripping `metadata_errors` keyword argument from `av.open`. LifeOS automatically applies this compatibility patch inside `app/services/voice/stt_service.py`.

---

## 3. Audio Requirements

- **Supported Formats**: `wav`, `mp3`, `m4a`, `ogg`, `webm`, `flac`.
- **Sample Rate**: Automatically resampled to 16,000 Hz mono PCM.
- **Maximum File Size**: 10 MB per recording.
- **Maximum Recording Duration**: 60 seconds per turn.

---

## 4. Multi-language Support

- By default, language is auto-detected using Whisper's built-in 99-language classifier.
- Passing `language="hi"` or `language="en"` locks the decoder for faster transcription latency.
