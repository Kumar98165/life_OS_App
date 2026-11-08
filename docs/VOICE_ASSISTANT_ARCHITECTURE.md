# LifeOS Voice Assistant Architecture

## 1. System Overview

The LifeOS Voice Assistant is an end-to-end, privacy-preserving, local-first speech conversational interface. It allows users to talk directly to LifeOS to check schedules, plan their day, create reminders, review habits, and summarize finances without transmitting raw audio to cloud APIs.

```
 [User Speaks into Mobile Mic]
              │
              ▼ (Audio Stream / WAV via expo-av)
 [POST /api/v1/voice/transcribe or /voice/assistant]
              │
              ▼
   [Local STT Engine] (faster-whisper, CPU/GPU, int8)
              │ (Bilingual: English + Hindi)
              ▼
    [Transcribed Text]
              │
              ▼
  [LifeOS LangGraph Agent] ──> [Context Engine] (Tasks, Planner, Habits, Finance)
              │            ──> [Tool Registry & Risk Gate]
              ▼
    [Generated Response]
              │
              ▼
   [Local TTS Engine] (pyttsx3 / SAPI5 / Piper offline)
              │
              ▼
    [Audio WAV Stream] ──> [Mobile Auto-Play & UI Transcript Display]
```

---

## 2. Architectural Pillars

1. **Local-First & Offline**:
   - Speech-to-Text runs locally using `faster-whisper` (CTranslate2 inference on CPU with `int8` quantization).
   - Text-to-Speech runs locally via `pyttsx3` using operating system native voice synthesizers (SAPI5 on Windows, espeak on Linux, NSSpeechSynthesizer on macOS).
   - Reasoning runs locally via Ollama (`qwen2.5:3b`).

2. **Zero Audio Retention (Privacy Enforcement)**:
   - Audio files uploaded for transcription or speech generation are held in secure OS temporary memory and unlinked immediately in `finally` blocks.
   - Database stores user preferences and text transcriptions only. No audio files are ever retained on disk.

3. **Controlled Tool Registry & Human Confirmation Gate**:
   - Voice assistant queries utilize the same safety boundaries as AI Automation (Step 19).
   - Low-risk read actions (e.g. "What are my priorities today?") execute autonomously.
   - Medium and high-risk mutating actions (e.g. creating/updating tasks, rescheduling planner blocks) generate an explicit action proposal requiring user vocal or UI confirmation before execution.
   - Autonomous money movement is strictly prohibited.

---

## 3. Supported Languages & Multi-lingual Handling

- **English (`en`)**: Native transcription and speech output.
- **Hindi (`hi`)**: Devanagari script recognition and native Hindi voice synthesis when system voice packages are present.
- **Hinglish (Code-Switching)**: Mixed Hindi vocabulary with English terminology (e.g., "Mera kal ka task schedule karo").
