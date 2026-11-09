# LIFEOS — STEP 5: AI MEMORY QUALITY & CONTEXT OPTIMIZATION

## 1. Existing Memory Architecture Analysis
LifeOS implements a privacy-first, local Digital Brain memory pipeline:
- **Candidate Extraction**: Local LLM (`qwen2.5:3b` via Ollama) extracts structured facts (`preference`, `personal_context`, `goal_decision`, `routine_pattern`, `fact`).
- **Strict Pending Gate**: Every extracted candidate is initially stored with `status="pending"`. The AI never accesses unapproved memories.
- **Explicit User Control**: Memories require explicit approval through `POST /api/v1/ai/memories/{id}/approve` or can be edited, rejected, archived, or deleted.

Prior to STEP 5, three key areas required optimization:
1. **Duplicate & Near-Duplicate Accumulation**: Repeated conversation turns with slight phrasing differences created multiple pending candidates.
2. **Contradiction Resolution**: When a user's habits or preferences shifted (e.g. from concise to detailed responses), conflicting candidate memories were queued without flagging the discrepancy or providing a clean update path.
3. **Retrieval Scoring & Freshness**: Semantic retrieval did not factor in recency decay or recent confirmation bonuses, treating old and newly updated memories identically.

---

## 2. Memory Quality Classification
- **Domain Categories**:
  - `preference`: Long-term communication styles, focus hours, work preferences.
  - `personal_context`: Career background, tools, skills, long-term personal facts.
  - `goal_decision`: Confirmed OKRs, milestones, strategic choices.
  - `routine_pattern`: Daily rhythms, recurring schedules, sleep/wake cycles.
  - `fact`: Important factual background items.
- **Trivial & Transient Filtering**: One-off greetings ("hello", "good morning"), conversational confirmations ("yes", "ok", "great"), and questions are automatically filtered out by `_is_trivial_message`.
- **Sensitive Guardrails**: Passwords, API tokens, JWTs, credit card numbers, and banking details are caught and filtered by `_is_sensitive_content`.

---

## 3. Duplicate Memory Detection
In [`backend/app/ai/memory/comparison.py`](file:///c:/Users/NexviTech/Desktop/LifePs/backend/app/ai/memory/comparison.py):
- **Deterministic Text Normalization**: Punctuation stripping, case flattening, and stop-word filtering (`normalize_memory_text`, `extract_keywords`).
- **Exact & Near Duplicates**: Evaluates identical keys/values and checks keyword Jaccard overlap (threshold >= 0.75).
- **Auto-Suppression**: Duplicates of existing confirmed or pending memories are automatically suppressed during candidate extraction, preventing database bloat.

---

## 4. Contradiction Detection & Safe Updates
- **Polarity Antonym Pairs**: Deterministically tracks opposing concepts (`short` vs `detailed`, `concise` vs `comprehensive`, `morning` vs `evening`, `dark` vs `light`, etc.).
- **Flagging for Review**: When a candidate contradicts an existing approved memory, it is annotated with:
  ```json
  "embedding": {
    "contradiction": {
      "contradicting_memory_id": "<existing_id>",
      "reason": "Conflict detected between 'User now prefers detailed responses' and existing 'User prefers short responses' (detailed vs short)",
      "is_update_candidate": true
    }
  }
  ```
- **Never Silently Overwrites**: The existing approved memory remains active and confirmed until the user explicitly approves the candidate.
- **Safe Archival upon Approval**: When approving an update candidate, the user can pass `supersede_existing_id`. The old memory is transitioned to `archived` (preserving history) while the new candidate becomes `confirmed`.

---

## 5. Expiration, Freshness & Retrieval Optimization
In [`backend/app/ai/memory/retriever.py`](file:///c:/Users/NexviTech/Desktop/LifePs/backend/app/ai/memory/retriever.py):
- **Active Validity**: Base SQL query strictly excludes rejected, pending, archived, and expired memories (`expires_at < now`).
- **Recency & Freshness Boost**:
  - Items confirmed or accessed within the last 7 days receive a +1.0 scoring boost.
  - Items accessed within the last 30 days receive a +0.5 boost.
- **Offset-Aware Timezone Arithmetic**: Ensures UTC timestamps compare safely without Python offset-naive runtime errors.
- **Touch on Access**: Updates `last_accessed_at` in the database whenever a memory is injected into prompt context.
- **Bounded Budget**: Restricts context injection to top `limit=5` memories, formatted as clean markdown bullets.

---

## 6. Provenance and Traceability
Every memory record tracks:
- `user_id`: Authenticated user scope (indexed, with foreign key cascade).
- `source_conversation_id`: Originating chat thread.
- `source_message_id`: Exact user message turn that gave rise to the memory.
- `created_at` / `updated_at`: Complete lifecycle history.
- `last_accessed_at`: AI access timestamps.
- `expires_at`: Optional expiration policy.

---

## 7. Mobile UI Integration
In [`mobile/src/screens/ai/memory/AIMemoryScreen.tsx`](file:///c:/Users/NexviTech/Desktop/LifePs/mobile/src/screens/ai/memory/AIMemoryScreen.tsx):
- **Conflict Warning Banner**: Pending candidate cards inspect `suggestion.embedding.contradiction`. If a conflict exists, a dedicated warning pill (`swap-horizontal`) renders the explanation directly to the user.
- **One-Click Approval**: Users can approve with one tap or choose "Edit & Approve" to refine phrasing before confirming.
- **Privacy Notice**: Informs the user that all memories are locally stored and only confirmed memories enter the AI prompt.

---

## 8. Verification Results

- **Memory System Pytest Suite**: **11/11 PASSED** ([`backend/tests/test_ai_memory.py`](file:///c:/Users/NexviTech/Desktop/LifePs/backend/tests/test_ai_memory.py))
- **Personal Intelligence Suite**: **10/10 PASSED** ([`backend/tests/test_personal_intelligence.py`](file:///c:/Users/NexviTech/Desktop/LifePs/backend/tests/test_personal_intelligence.py))
- **Personalization Suite**: **10/10 PASSED** ([`backend/tests/test_personalization.py`](file:///c:/Users/NexviTech/Desktop/LifePs/backend/tests/test_personalization.py))
- **Streaming Regression Suite**: **6/6 PASSED** ([`backend/tests/test_ai_streaming.py`](file:///c:/Users/NexviTech/Desktop/LifePs/backend/tests/test_ai_streaming.py))
- **Mobile Unit Test Suite**: **156/156 PASSED**, 11 suites.
- **Mobile TypeScript Verification**: **0 errors** (`npm run typecheck`).

---

## 9. Remaining Limitations
1. **Local CPU Inference for Extraction**: Candidate extraction takes ~2-4s after a conversation turn; it runs asynchronously in the background so the user's chat response is never delayed.
2. **Complex Semantic Nuances**: Semantic comparisons utilize token and polarity analysis rather than heavy embedding vectors, keeping memory consumption minimal for low-end device hosts.
