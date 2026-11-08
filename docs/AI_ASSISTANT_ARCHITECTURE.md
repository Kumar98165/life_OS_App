# LifeOS AI Personal Assistant Architecture

## 1. Local-First AI Vision
LifeOS features a fully local, privacy-preserving AI assistant. By utilizing an on-device local LLM runtime (Ollama) hosting open-weights models (`qwen2.5:3b`), user tasks, habits, schedules, and goals are never transmitted to external proprietary AI services.

```mermaid
flowchart TD
    RN[React Native AIAssistantScreen] -->|POST /api/v1/ai/chat (JWT Auth)| Flask[Flask AI Blueprint]
    Flask -->|Validate & Check Ownership| Service[AIService]
    Service -->|User / Assistant History| Repo[(PostgreSQL: ai_conversations / ai_messages)]
    Service -->|Execute Graph| LangGraph[LangGraph StateGraph Workflow]
    LangGraph -->|Read User Data| Context[LifeOSContextEngine]
    Context -->|Read-Only Queries| Data[(PostgreSQL: tasks, goals, habits, planner)]
    LangGraph -->|Inject Context & Chat History| LocalLLM[ChatOllama: qwen2.5:3b on localhost:11434]
    LocalLLM -->|Streamed / Structured Output| LangGraph
    LangGraph -->|Sanitize & Validate| Service
    Service -->|Persist Turn & Return Envelope| Flask
    Flask -->|JSON Response| RN
```

---

## 2. Core Architectural Components

### A. Local LLM Runtime (Ollama)
- Direct interface through `langchain_ollama.ChatOllama` communicating over local HTTP (`http://localhost:11434`).
- Primary target model: `qwen2.5:3b` (installed locally with 1.9 GB footprint).
- Zero mandatory cloud API keys; zero reliance on paid external APIs.

### B. Agentic Orchestration (LangGraph)
- Built on `langgraph.graph.StateGraph` using a typed execution state (`LifeOSAgentState`).
- Unidirectional graph progression:
  1. `retrieve_context`: Loads authorized user data from PostgreSQL.
  2. `classify_intent`: Identifies domain focus (tasks, habits, goals, schedule, overview).
  3. `generate_response`: Invokes local LLM with structured system prompt and message history.
  4. `validate_response`: Ensures clean formatting, prevents prompt echoing, and guarantees non-empty responses.

### C. Conversation Persistence
- Multi-turn dialog threads are stored in PostgreSQL 3NF tables:
  - `ai_conversations`: Holds thread metadata (`id`, `user_id`, `title`, `model_used`, `created_at`, `updated_at`).
  - `ai_messages`: Holds individual dialogue turns (`role`, `content`, `tokens_used`, `created_at`).

---

## 3. Privacy & Safety Guarantees
- **Strict Data Ownership**: All tools and context loaders query strictly with `user_id = authenticated_user_id`.
- **Read-Only Context**: The AI assistant cannot perform silent database mutations, cancellations, or deletions.
- **Truthful Prompting**: The system prompt instructs the model to only cite data present in the context payload and to explicitly declare when information is unavailable.

