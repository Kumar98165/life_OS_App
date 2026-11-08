# LifeOS - AI Memory Privacy & Safety Boundaries

## 1. Zero Cloud Transmission
- **No Third-Party APIs**: Unlike cloud assistants that transmit conversation histories to OpenAI, Anthropic, or external embedding providers, LifeOS executes all memory extraction, indexing, and synthesis on the user's host machine using Ollama and PostgreSQL.
- **Local Database Isolation**: All records reside inside the local `lifeos_db` instance with row-level ownership enforcement on `user_id`.

---

## 2. Strict Human-in-the-Loop Memory Lifecycle
1. **Never Auto-Confirm**: Candidate memories extracted from user messages are assigned `status = 'pending'`. The AI cannot promote a suggestion to confirmed memory on its own.
2. **Review & Editing Interface**: The user inspects pending candidates in `AIMemoryScreen`, corrects any inaccuracies in key/value statements or categorization, and explicitly confirms them.
3. **Instant Rejection**: Rejecting a suggestion permanently purges the record from the database to eliminate noise and bloat.

---

## 3. Sensitive Data Filtering & Redaction
The `MemoryExtractionEngine` applies strict regex pattern guards before passing text to the extractor prompt. Any message containing or mentioning:
- Passwords (`password`, `passwd`, `secret`)
- API keys, JWTs, and bearer tokens (`api_key`, `access_token`, `bearer`)
- Credit card numbers, CVVs, bank routing numbers, or SSNs
- Private keys or authentication codes

is immediately rejected for candidate extraction. In addition, the extraction system prompt explicitly instructs the LLM never to remember credentials or financial data.

---

## 4. Right to be Forgotten
- **Single-Click Deletion**: Users can delete any memory from the "Confirmed" tab.
- **Archival**: Archiving a memory sets `status = 'archived'`. Archived memories remain readable in user exports but are instantly excluded from all future assistant prompts.
- **Master Privacy Killswitch**: Users can disable AI memory personalization at any time in the "Privacy & Settings" tab (`PATCH /api/v1/ai/memories/settings` -> `ai_memory_enabled = false`). When disabled, `MemoryRetrievalEngine` bypasses all database lookups and injects zero memory context into system prompts.

