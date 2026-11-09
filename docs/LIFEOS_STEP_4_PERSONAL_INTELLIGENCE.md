# LIFEOS — STEP 4: ADVANCED PERSONAL INTELLIGENCE ENGINE

## 1. Existing Architecture Analysis
Prior to STEP 4, LifeOS possessed core domain tables (Tasks, Goals, Habits, Planner, Finance, AI Memories, and User Personalization preferences) and an SSE-based local AI streaming system. However, context aggregation was basic:
- Context retrieval did not incorporate timezone awareness or local day boundaries.
- Habit consistency, missed streaks, and approaching deadlines were not evaluated proactively.
- Schedule overlaps and conflicts were not detected across planner blocks.
- Communication styles and language preferences (e.g. Hinglish, concise vs. comprehensive) were not translated into actionable prompt directives for Ollama.

STEP 4 transforms this pipeline into a centralized, privacy-first **Personal Intelligence Engine**.

---

## 2. Personal Context Engine Design
The enhanced [`LifeOSContextEngine`](file:///c:/Users/NexviTech/Desktop/LifePs/backend/app/ai/context_engine.py) provides a single unified entry point for aggregating authenticated user context:
- **User-Scoped Queries**: All queries filter strictly by `user_id`. No cross-user data leakage or shared state.
- **Timezone & Local Date Precision**: Resolves user timezone from `UserPersonalization` or `UserPreference` (e.g. `ZoneInfo("Asia/Kolkata")`), ensuring "today" aligns with the user's wall clock rather than UTC server time.
- **Bounded Token Budgeting**: Enforces strict item caps per domain (`limit=5` per section) to keep prompt context well within Qwen2.5:3b's optimal attention span without truncation.
- **Relevance & Financial Privacy**: Aggregated 30-day cash flow and account summaries are only attached if the user explicitly discusses finances or requests them. Individual transaction details remain completely excluded.
- **Privacy Toggle Enforcement**: If `personalization_enabled` is set to `False`, personalization rules and routines are omitted, falling back cleanly to default system guidelines.

---

## 3. Personalized Response Engine
In [`backend/app/ai/workflow.py`](file:///c:/Users/NexviTech/Desktop/LifePs/backend/app/ai/workflow.py), `prepare_llm_messages` dynamically translates user settings into explicit formatting constraints:
- **Language**:
  - `hi`: Instructs the model to respond primarily in Hindi.
  - `hinglish`: Instructs natural Romanized Hindi mixed with English.
  - User-specified language code: Directs response in the chosen tongue unless the user explicitly switches languages in their turn.
- **Length**:
  - `short`: Terse, bulleted output with zero fluff.
  - `comprehensive`: Detailed, deep-dive breakdowns.
- **Style**:
  - `motivational`: Uplifting, encouraging tone.
  - `formal`: Corporate, objective tone.
  - `concise`: Structured markdown bullets.

---

## 4. Daily Intelligence & Schedule Analysis
The [`PersonalIntelligenceService`](file:///c:/Users/NexviTech/Desktop/LifePs/backend/app/services/personal_intelligence_service.py) exposes `GET /api/v1/ai/intelligence/briefing`, computing:
1. **Dynamic Greeting**: Automatically adapts between "Good morning", "Good afternoon", and "Good evening" using the user's preferred name.
2. **Schedule Conflict Detection**: Scans today's planner blocks chronologically; detects overlapping time ranges and flags them with precise conflict intervals.
3. **Prioritized Recommendations**: Employs user strategy (`eisenhower`, `deadline_first`, `impact_first`) to suggest tangible, non-hallucinatory priorities.

---

## 5. Goal and Habit Intelligence
- **Habit Streak & Rebound Detection**: Identifies habits where the user missed yesterday and hasn't logged today, offering encouraging 5-minute micro-habit nudges without punitive labeling. Celebrates multi-day streaks (>= 5 days).
- **Approaching Deadlines**: Evaluates tasks with due dates in the next 3 days, warning the user ahead of crunch time.
- **Goal Finish-Line Awareness**: Highlights goals exceeding 75% progress with their exact milestone counts.

---

## 6. Proactive Insights System
Exposed via `GET /api/v1/ai/intelligence/insights`:
- Purely deterministic rule evaluation (0 extra LLM latency, instantaneous response).
- Generates stable insight IDs (e.g. `insight-conflict-{date}`, `insight-deadline-{taskId}`) for deduplication and client-side dismissal.
- Connects directly to mobile navigation targets (`PlannerTab`, `TasksTab`, `Habits`, `GoalsTab`).

---

## 7. Memory and Feedback Integration
- Strictly confirmed memories with non-expired timestamps are retrieved.
- Rejected or pending memories are excluded from inference.
- Learning consent status is respected; user conversation turns are never silently converted into training samples.

---

## 8. Mobile UI Integration
- **`AIQuickAccessCard` Enhanced**:
  - Automatically loads top proactive insights or daily briefings using TanStack Query.
  - Renders alert banners for schedule conflicts, habit momentum nudges, or upcoming deadlines.
  - Includes direct one-click deep link navigation to the relevant screen or AI chat.
- **Lightweight & Low-End Device Safe**: Zero heavy animations or canvas dependencies; respects low-end Android memory constraints.

---

## 9. Performance & Verification Metrics
- **Context Retrieval Latency**: < 15 ms across 7 domain queries.
- **Briefing API Latency**: ~ 20-30 ms (deterministic database queries).
- **Automated Test Coverage**:
  - `backend/tests/test_personal_intelligence.py`: **7/7 PASSED**.
  - `backend/tests/test_ai_streaming.py`: **6/6 PASSED**.
  - `backend/tests/test_personalization.py`: **10/10 PASSED**.
  - `backend/tests/test_prompt_security.py`: **7/7 PASSED**.
  - `mobile/src/__tests__`: **156/156 PASSED**, 11 suites.
  - Mobile TypeScript: **0 errors** (`tsc --noEmit`).

---

## 10. Remaining Limitations
1. **CPU LLM Generation Latency**: On local 4-thread CPU, Ollama inference requires 3-10s; proactive insights bypass this entirely by using deterministic rule evaluation for immediate rendering.
2. **Offline Mobile Insights**: Proactive insights are currently fetched from the backend API. When disconnected from the local network/server, mobile falls back to cached TanStack Query data.

