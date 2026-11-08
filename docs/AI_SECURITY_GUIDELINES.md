# LifeOS AI Security & Privacy Guidelines

## 1. Local-First Privacy Standards
LifeOS strictly adheres to privacy-by-design standards:
- **No Third-Party AI Transmission**: User task titles, private habit notes, daily schedules, and goals are processed locally on the user's host machine via Ollama.
- **No Telemetry / Prompt Logging to External Clouds**: No user data is sent to external API vendors.

---

## 2. Authorization & Invariant Enforcement
1. **JWT Verification**:
   - Every `/api/v1/ai/*` endpoint (except the generic `/health` probe) requires an active JWT bearer token.
   - The user's identity is derived strictly from the verified JWT payload.
2. **Conversation & Message Ownership**:
   - Conversations are isolated by `user_id`.
   - Access to `GET /api/v1/ai/conversations/<id>` or `DELETE /api/v1/ai/conversations/<id>` checks `check_resource_ownership(conversation.user_id, current_user_id)`.
   - Submitting prompts to an existing `conversation_id` validates ownership before the turn executes.
3. **Read-Only Agent Permissions**:
   - The agent tools (`get_pending_tasks`, `get_active_goals`, etc.) are strictly read-only queries.
   - The LLM cannot execute arbitrary SQL queries, run Python code, or directly delete user records.
   - Destructive actions (such as deleting tasks or resetting streaks) must always be executed directly by the user in the mobile UI.

---

## 3. Defense Against Hallucination & Prompt Injection
- **Input Sanitization**: User prompt length is limited to 4000 characters to prevent buffer and memory exhaustion.
- **System Prompt Integrity**: System instructions enforce that the model strictly relies on the provided context and refrains from fabricating items.
- **Output Sanitization**: The validation node strips internal prompt instructions before delivering messages to the client.

