# LifeOS Voice Assistant Privacy & Security Standards

## 1. Zero Cloud Audio Transmission

LifeOS enforces strict offline audio processing:
- **No Third-Party Speech APIs**: Raw audio is never uploaded to OpenAI Whisper Cloud, ElevenLabs, Google Cloud Speech, AWS Transcribe, or Azure Cognitive Services.
- **Local Engine Execution**: Both speech recognition and speech synthesis occur entirely on the user's host hardware.

---

## 2. Zero Audio Retention Policy

Temporary audio files generated during voice interactions:
1. Are stored exclusively in ephemeral operating system temporary directories (`tempfile`).
2. Are processed into text or memory streams.
3. Are immediately unlinked from the filesystem inside `finally` blocks, regardless of whether processing succeeded or encountered an exception.
4. No audio recordings are permanently indexed or stored in the database.

---

## 3. Human Approval Gate for Voice Actions

- **Voice Command Boundaries**: Spoken instructions cannot directly execute mutating operations without adherence to the Step 19 Risk Assessment Gate.
- **Confirmation Prompts**: If a voice query maps to creating a high-risk action or updating sensitive data, the assistant provides a verbal summary and waits for the user's explicit confirmation.
- **Financial Safety**: Autonomous monetary transfers and account modifications are completely blocked from automated execution.
