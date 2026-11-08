# LifeOS AI Automation Workflow

> **Version**: 1.0.0  
> **Date**: 2026-11-08  
> **Status**: Verified

---

## 1. 10-Phase LangGraph StateGraph

The LifeOS automation engine runs on an orchestrated 10-node StateGraph:

```
[START]
   │
   ▼
1. Intent Classification
   │
   ▼
2. Context Retrieval (Tasks, Habits, Goals, Schedule, Finance)
   │
   ▼
3. Automation Planning (Local Ollama Qwen)
   │
   ▼
4. Action Validation (Pydantic Schema Check)
   │
   ▼
5. Risk Assessment (Low vs. Medium vs. High)
   │
   ▼
6. Approval Gate (Persists HITL records)
   │
   ▼
7. Action Execution (Low-risk immediate run)
   │
   ▼
8. Result Verification
   │
   ▼
9. Response Generation (Narrative + Action Addendum)
   │
   ▼
[END]
```

---

## 2. Node Responsibilities

| # | Node Name | Description |
|---|-----------|-------------|
| 1 | `classify_intent` | Maps user trigger or template slug to one of the 7 predefined operational intents. |
| 2 | `retrieve_context` | Pulls verified tasks, schedule, habits, and read-only financial totals from PostgreSQL. |
| 3 | `plan_automation` | Prompts local Qwen model to synthesize a structured narrative and a JSON action array. |
| 4 | `validate_actions` | Validates every proposed action against predefined Pydantic schemas in the tool registry. |
| 5 | `assess_risk` | Computes maximum risk level across all proposed actions. |
| 6 | `approval_gate` | Creates database approval records for medium/high risk actions, pausing workflow if required. |
| 7 | `execute_actions` | Executes permitted low-risk tools autonomously while holding approved actions in pending state. |
| 8 | `verify_results` | Verifies execution output integrity and logs errors. |
| 9 | `generate_response` | Synthesizes user-facing markdown summary detailing proposed or executed actions. |

---

## 3. Predefined Automation Templates

1. **Plan My Day**: Reviews pending tasks, habits, and calendar blocks to propose an optimal daily schedule.
2. **Prepare My Weekly Review**: Sunday reflection analyzing 7-day task velocity, streaks, milestones, and cash flow.
3. **Upcoming Deadline Assistant**: Triage assistant scanning tasks and milestones due within 48-72 hours.
4. **Habit Recovery Assistant**: Empathic recovery assistant detecting missed habits and broken streaks.
5. **Goal Progress Review**: Evaluates active goals and flags lagging milestone progress.
6. **Budget Awareness Assistant**: Read-only monthly budget audit highlighting categories exceeding 80% utilization.
7. **Daily Productivity Summary**: End-of-day digest detailing completed tasks, concluded time blocks, and check-ins.
