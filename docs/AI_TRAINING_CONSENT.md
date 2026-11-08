# LifeOS – AI Training Data Privacy & Consent Policy (Step 13.5: Phase 3)

## 1. Privacy First Architecture

LifeOS is an AI personal operating system built with local-first, privacy-by-design foundations.

User interactions with the AI assistant belong exclusively to the user. No conversations or feedback entries are ever transmitted to third-party commercial LLM providers (e.g. OpenAI, Anthropic, Google Gemini cloud endpoints).

---

## 2. Consent Policy & Default State

- **Default State**: AI training data contribution defaults strictly to **`FALSE`** (`server_default=sa.false()`).
- **Independent Feedback**: Users are encouraged to submit thumbs-up (+1) and thumbs-down (-1) feedback to track interaction quality regardless of whether training consent is granted. A user may provide feedback without ever contributing to local model fine-tuning sets.
- **Opt-in Requirement**: An explicit opt-in action (`PATCH /api/v1/ai/learning/consent` with `{"ai_training_consent": true}`) is required before any feedback or anonymized dialogue turn can be designated for training dataset curation.

---

## 3. Consent Management API

### Retrieve Current Consent
- **Endpoint**: `GET /api/v1/ai/learning/consent`
- **Authentication**: Required (`Bearer <access_token>`)
- **Response**:
```json
{
  "success": true,
  "message": "AI training consent preferences retrieved successfully",
  "data": {
    "user_id": "b18b671c-fb57-4029-9468-c91860cbe1b3",
    "ai_training_consent": false,
    "policy_version": "v1.0",
    "privacy_notice": "When enabled, your feedback and anonymized corrections may be used to fine-tune local LifeOS models. Consent defaults to false, is completely optional, and can be withdrawn at any time."
  }
}
```

### Update / Revoke Consent
- **Endpoint**: `PATCH /api/v1/ai/learning/consent`
- **Request Body**:
```json
{
  "ai_training_consent": false
}
```
- **Response**:
```json
{
  "success": true,
  "message": "AI training consent preference updated successfully",
  "data": {
    "user_id": "b18b671c-fb57-4029-9468-c91860cbe1b3",
    "ai_training_consent": false,
    "samples_revoked": 4
  }
}
```

---

## 4. Withdrawal Mechanics & Invalidation Workflow

When a user sets `ai_training_consent = false`:
1. **Atomic Transaction**: In the same database transaction that updates `user_preferences.ai_training_consent`, all rows in `ai_training_samples` where `user_id == current_user_id` are updated to `consent_status = 'revoked'`.
2. **Export Filtering**: Any subsequent offline dataset compilation filters strictly by `consent_status == 'granted'` and `user_preferences.ai_training_consent == true`. Revoked samples are excluded from future training builds.
3. **Preservation of User Feedback**: Feedback records (`ai_feedback`) are *not* deleted upon consent withdrawal. The user's ratings and notes remain visible in their personal UI until the user chooses to delete them individually.

---

## 5. Technical Limitations & Air-Gapped Considerations

- **Pre-Exported Offline Datasets**:
  If an administrator or user generated and downloaded an offline JSONL dataset file to disk prior to consent revocation, the database trigger cannot retrospectively modify air-gapped or copied local files. System operators must re-export datasets following any revocation events.
- **Regex Redaction Notice**:
  Regex filtering applied to anonymize training samples removes common sensitive patterns (emails, telephone numbers, credit cards). However, regex cannot mathematically guarantee complete removal of novel PII or subtle linguistic identifiers. Consent revocation provides the primary legal and technical guarantee against dataset inclusion.

