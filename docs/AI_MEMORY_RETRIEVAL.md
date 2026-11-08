# LifeOS - AI Memory Retrieval & Ranking Specification

## 1. Retrieval Strategy
LifeOS achieves high-relevance memory injection without requiring external vector databases or high-overhead embeddings. The `MemoryRetrievalEngine` applies a multi-stage deterministic scoring algorithm optimized for low latency and high precision on local hardware.

---

## 2. Eligibility Criteria
A memory is eligible for retrieval if and only if:
1. `user_preferences.ai_memory_enabled == True`
2. `AIMemory.user_id == authenticated_user_id`
3. `AIMemory.status == 'confirmed'`
4. `AIMemory.expires_at IS NULL OR AIMemory.expires_at > UTC_NOW()`

Pending, rejected, and archived memories are filtered out at the database query level.

---

## 3. Deterministic Scoring Algorithm
For each candidate memory, a composite score is computed:

$$Score = (2.0 \times \text{Matched Keyword Tokens}) + \text{Confidence Score} + \text{Recency Bonus}$$

- **Token Match Bonus (+2.0)**: Each query token of length > 2 appearing in `memory_key`, `memory_value`, or `memory_type`.
- **Confidence Weight (+0.5 to 1.0)**: Preserves higher confidence assigned during extraction or manual entry.
- **Recency Access Bonus**: Tie-breaker prioritizing memories accessed or created most recently.

---

## 4. Context Budgeting & Token Limits
- **Max Memories per Prompt**: Capped at 5 memories.
- **Approximate Token Budget**: ~300 tokens maximum.
- **System Prompt Formatting**:
```markdown
### Confirmed User Memories (Personal Knowledge)
The user has previously approved the following personal facts, preferences, and routines:
- **Prefers morning deep work** (preference): Focus sessions best between 8 AM and 10 AM.
- **Target: AWS Certified DevOps** (goal_decision): Studying for exam by Q3.
```

---

## 5. Access Tracking
Whenever a memory is injected into an LLM prompt, `AIMemory.last_accessed_at` is updated to the current UTC timestamp. This powers the "Last Used" badge in the mobile UI and improves future ranking decisions.

