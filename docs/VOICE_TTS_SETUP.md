# LifeOS Local Text-to-Speech (TTS) Setup

## 1. Engine Specifications

LifeOS uses `pyttsx3` backed by system native voice drivers:
- **Windows**: Microsoft Speech API (SAPI5) natively supported with zero additional binary downloads.
- **macOS**: NSSpeechSynthesizer.
- **Linux**: eSpeak / eSpeak-ng.

---

## 2. Voice Customization

- **Speaking Rate (WPM)**: Configurable from `0.5x` (slow) to `2.0x` (fast). Standard rate is 175 WPM (`1.0x`).
- **Pitch**: Normalized pitch adjustment.
- **Voice Selection**: Users can inspect and pick from all installed voices on the operating system via `GET /api/v1/voice/voices`.

---

## 3. Hindi Voice Installation (Optional for Windows)

To enable native Hindi text-to-speech on Windows:
1. Open Windows **Settings** > **Time & Language** > **Language & Region**.
2. Add **Hindi** (हिंदी) language pack.
3. Under Language options, install the **Speech** package.
4. LifeOS automatically discovers Microsoft Kalpana or Hemant Hindi voices.
