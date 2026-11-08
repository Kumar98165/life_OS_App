# LifeOS - AI Memory Architecture: Personal Digital Brain

## 1. Overview
The LifeOS AI Memory System serves as a private, persistent, user-controlled digital brain. It enables the local Ollama LLM (`qwen2.5:3b`) to recall personalized context across conversations without relying on cloud APIs, vector databases, or external embedding services.

---

## 2. Core Design Principles
1. **Local-First & Offline**: All memory extraction, ranking, storage, and retrieval run entirely on the user's device via PostgreSQL and local Ollama.
2. **Explicit User Approval Lifecycle**:
   - The AI Assistant never directly saves confirmed memories.
   - Dialogue turns generate candidate suggestions in `pending` status.
   - The user must explicitly approve, edit, or reject candidates.
   - Only `confirmed` memories are ever retrieved into system prompts.
3. **Deterministic Retrieval**:
   - PostgreSQL queries filtered by authenticated `user_id` and `status = 'confirmed'`.
   - Keyword overlap matching, category matching, and confidence weighting.
   - Hard budget cap (max 5 memories, ~300 tokens) prevents context flooding.
4. **Complete User Sovereignty (Right to be Forgotten)**:
   - Users can inspect, edit, archive, or permanently delete any memory.
   - Archiving immediately excludes a memory from retrieval.
   - Global toggle allows users to completely disable memory retrieval.

---

## 3. Approval Workflow Diagram

```
+--------------------------------------------------------------------------+
|                              Chat Turn                                   |
|   User asks a question or shares personal context in AIAssistantScreen   |
+------------------------------------+-------------------------------------+
                                     |
                                     v
+------------------------------------+-------------------------------------+
|                     Memory Extraction Engine                             |
|   - Strips sensitive tokens (passwords, tokens, cards, api keys)         |
|   - Skips trivial greetings                                              |
|   - Parses 5 categories (preference, context, goal, routine, fact)       |
+------------------------------------+-------------------------------------+
                                     |
                                     v
+------------------------------------+-------------------------------------+
|                  Candidate Memory (status: "pending")                    |
|   - Persisted in ai_memories table                                       |
|   - Linked to source conversation & message                              |
|   - INVISIBLE to future AI retrieval nodes                               |
+------------------------------------+-------------------------------------+
                                     |
                                     v
+------------------------------------+-------------------------------------+
|                  User Review (AIMemoryScreen)                            |
|   - User views pending candidates in "Pending Review" tab                |
|   - Actions: Approve | Edit & Approve | Reject                           |
+--------------------+---------------------+-------------------------------+
                     |                     |
            Approve / Edit          Reject / Dismiss
                     |                     |
                     v                     v
+--------------------+---------+  +--------+-------------------------------+
| Confirmed Memory             |  | Deleted from Database                  |
| (status: "confirmed")        |  | Zero residual trace                    |
| Active in AI Retrieval       |  +----------------------------------------+
+------------------------------+
```

---

## 4. LangGraph Agent Workflow Integration

In `backend/app/ai/workflow.py`, the state graph was extended with the `node_retrieve_memories` step:

```
[START]
   │
   ▼
[node_retrieve_context]       --> Gathers Tasks, Planner blocks, Goals, Habits
   │
   ▼
[node_retrieve_memories]      --> Queries confirmed memories, scores relevance, budgets prompt
   │
   ▼
[node_classify_intent]        --> Diagnoses user intent (tasks, habits, planner, overview, etc.)
   │
   ▼
[node_generate_response]      --> Injects context + memory blocks into local Ollama prompt
   │
   ▼
[node_validate_response]      --> Sanitizes output and strips prompt artifacts
   │
   ▼
 [END]
```

---

## 5. Database Schema & Alembic Migration

The PostgreSQL `ai_memories` table was upgraded in Alembic revision `87ec6f9980ac`:
- `status`: VARCHAR(20) (`pending`, `confirmed`, `archived`, `rejected`), NOT NULL, default `'confirmed'`.
- `source_conversation_id`: UUID, foreign key to `ai_conversations.id` (ON DELETE SET NULL).
- `source_message_id`: UUID, foreign key to `ai_messages.id` (ON DELETE SET NULL).
- `expires_at`: TIMESTAMP WITH TIME ZONE (nullable for temporary memories).
- Compound Index: `ix_ai_memories_user_status` on `(user_id, status)`.
- `user_preferences.ai_memory_enabled`: BOOLEAN, NOT NULL, default `True`.

