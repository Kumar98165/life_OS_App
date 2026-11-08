# LifeOS – AI Feedback Architecture (Step 13.5: Phase 3)

## 1. Overview & Architectural Vision

The **AI Feedback & Continuous Learning Subsystem** provides a secure, privacy-preserving feedback loop for LifeOS interactions with local large language models (Ollama / Qwen 2.5 3B). 

While Step 12 introduced the LangGraph assistant orchestration and Step 13 created the local digital brain memory system, Step 13.5 establishes explicit human-in-the-loop signal collection. Users can express qualitative judgments on assistant answers (+1 / -1), classify answer defects, and provide corrective reference answers.

```
       +-------------------------------------------------------------+
       |                     React Native Mobile UI                  |
       +-------------------------------------------------------------+
                                      |
                     REST HTTP (Bearer JWT Authorization)
                                      v
       +-------------------------------------------------------------+
       |               Flask API Layer (ai_feedback_bp)              |
       |  - POST /api/v1/ai/feedback                                 |
       |  - GET  /api/v1/ai/feedback                                 |
       |  - GET  /api/v1/ai/feedback/<id>                            |
       |  - PATCH/api/v1/ai/feedback/<id>                            |
       |  - DELETE /api/v1/ai/feedback/<id>                          |
       |  - GET  /api/v1/ai/messages/<message_id>/feedback           |
       |  - GET  /api/v1/ai/learning/consent                         |
       |  - PATCH /api/v1/ai/learning/consent                        |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                    AIFeedbackService                        |
       |  - Anti-IDOR Resource Ownership Verification                |
       |  - Message Role Validation (assistant only)                 |
       |  - Pydantic v2 Input Normalization & Length Bounds          |
       |  - Transactional Consent Revocation Cascade                 |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                  AIFeedbackRepository                       |
       |  - Idempotent upsert by message_id (zero duplicate rows)    |
       |  - Paginated user list queries                              |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                 PostgreSQL 18 Storage Engine                |
       |  - ai_feedback (unique constraint on message_id)            |
       |  - user_preferences (ai_training_consent boolean default F) |
       |  - ai_training_samples (revoked on consent withdrawal)      |
       +-------------------------------------------------------------+
```

---

## 2. Core Architectural Principles

1. **Local-First & Zero Paid Cloud Dependencies**:
   - Everything runs on the user's infrastructure with local Ollama runtimes.
   - No feedback, prompts, or conversation contents are ever forwarded to external cloud APIs or third-party telemetries.
2. **Assistant Turn Constraint**:
   - Feedback can strictly be submitted only for dialogue turns where `role = 'assistant'`.
   - Submissions attempting to rate user inputs or system instructions are rejected with HTTP 400 Bad Request.
3. **Idempotent Single Feedback per Message**:
   - Each assistant message can have at most one feedback record (`UNIQUE` constraint on `ai_feedback.message_id`).
   - If a user changes their rating or submits an updated correction, the service updates the existing record without duplicate row creation or unique key collisions.
4. **Strict Anti-IDOR Authorization**:
   - A user cannot rate, inspect, modify, or delete feedback for an assistant turn that occurred in another user's conversation.
   - Verification evaluates `conversation.user_id == current_user_id` and `feedback.user_id == current_user_id` on all endpoints.
5. **Decoupled Training Consent & Invalidation**:
   - Collecting user ratings (+1 / -1) and feedback is completely separate from AI training consent.
   - Feedback collection operates whether `ai_training_consent` is true or false.
   - When a user withdraws consent, all candidate training samples belonging to that user are transactionally marked as `'revoked'`, while existing feedback records remain intact.

---

## 3. Data Schema & Relationships

```mermaid
erDiagram
    users ||--o{ ai_conversations : "owns"
    users ||--o{ ai_feedback : "submits"
    users ||--o1 user_preferences : "configures"
    users ||--o{ ai_training_samples : "contributes"
    
    ai_conversations ||--o{ ai_messages : "contains"
    ai_prompt_versions ||--o{ ai_messages : "attributed to"
    
    ai_messages ||--o1 ai_feedback : "evaluated by"
    ai_messages ||--o{ ai_training_samples : "source message"
    ai_feedback ||--o{ ai_training_samples : "source feedback"

    ai_feedback {
        uuid id PK
        uuid user_id FK
        uuid message_id FK "UNIQUE"
        int rating "+1 or -1"
        string feedback_type "thumbs_up | thumbs_down | correction | issue_report"
        string category "supported defect category"
        text comment "max 2000 chars"
        text suggested_response "max 5000 chars"
        timestamp created_at
        timestamp updated_at
    }
```

---

## 4. Privacy & Redaction Boundaries

- **Input Size Hard Bounds**: Comments are capped at 2,000 characters and corrections at 5,000 characters to prevent buffer exhaustion and payload abuse.
- **Regex Redaction Limitation**: Pattern scrubbing (e.g., regex matching credit cards, phone numbers, email addresses) provides a valuable defense-in-depth mitigation against accidental leakage. However, regex is *not* a mathematically guaranteed defense against adversarial prompt reconstruction or novel PII formats. LifeOS enforces strict database-level consent checks (`consent_status == 'granted'`) before any sample enters training preparation.
- **Stable Message Identifiers**: Assistant responses returned from `/api/v1/ai/chat` contain both root `"message_id"` and `"assistant_message": {"id": "..."}` to enable immediate, deterministic client feedback submissions.

