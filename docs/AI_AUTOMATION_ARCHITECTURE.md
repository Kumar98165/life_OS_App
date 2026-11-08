# LifeOS AI Automation Architecture

> **Version**: 1.0.0  
> **Date**: 2026-11-08  
> **Status**: Implemented & Verified (Step 19)

---

## 1. Architectural Philosophy

The LifeOS AI Automation Engine transforms the local assistant from a reactive conversational tool into a proactive, multi-domain personal operating system.

### Core Principles
1. **Local-First & Zero Paid Cloud APIs**: Powered strictly by local Ollama (`qwen2.5:3b`), ensuring zero user data leaves the device.
2. **Deterministic Boundaries & Sandboxing**: LLMs generate structured proposals; they never execute raw Python, arbitrary SQL, or unverified ledger modifications.
3. **Strict Human-in-the-Loop (HITL) Gate**: Low-risk insights and summaries run autonomously. Medium and high-risk actions (task creation, schedule blocks, reminders) mandate cryptographic approval.
4. **Read-Only Financial Aggregates**: Financial ledgers are strictly read-only. AI is structurally incapable of initiating transfers or editing past financial transactions.
5. **Idempotency & Safe Cancellation**: Re-entrant safe execution runs with hash-bound token signatures to prevent double execution or mutation during flight.

---

## 2. High-Level System Architecture

```
                    ┌─────────────────────────┐
                    │     Mobile Client       │
                    │   React Native / Expo   │
                    └───────────┬─────────────┘
                                │ JWT HTTP REST
                                ▼
                    ┌─────────────────────────┐
                    │     Flask API Layer     │
                    │   /api/v1/automations   │
                    └───────────┬─────────────┘
                                │
             ┌──────────────────┼──────────────────┐
             ▼                  ▼                  ▼
    ┌─────────────────┐┌─────────────────┐┌──────────────────┐
    │ Automation      ││ Automation      ││ Background       │
    │ Service         ││ Tool Registry   ││ Scheduler CLI    │
    │ (Lifecycle, DB) ││ (Schemas, RBAC) ││ (Idempotency)    │
    └────────┬────────┘└────────┬────────┘└────────┬─────────┘
             │                  │                  │
             └──────────────────┼──────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   LangGraph Workflow    │
                    │   10-Phase StateGraph   │
                    └───────────┬─────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
          ┌──────────────────┐    ┌──────────────────┐
          │  Local Ollama    │    │  PostgreSQL DB   │
          │  (qwen2.5:3b)    │    │  (Relational)    │
          └──────────────────┘    └──────────────────┘
```

---

## 3. Database Entity Relationship

1. **`AutomationDefinition`**:
   - Represents a template (`is_template=True`) or a user's customized schedule/trigger (`user_id` FK).
   - Tracks execution statistics (`total_runs`, `successful_runs`, `failed_runs`).
   - Supports `manual`, `scheduled`, and `event` triggers with pause/resume controls.

2. **`AutomationExecution`**:
   - A discrete run instance of an automation workflow.
   - States: `pending`, `planning`, `awaiting_approval`, `executing`, `completed`, `failed`, `cancelled`, `paused`.
   - Stores `idempotency_key` and execution duration metrics.

3. **`AutomationAction`**:
   - Concrete proposed operation (e.g., `tasks.create_task`, `planner.create_block`).
   - Risk scoring: `low`, `medium`, `high`.
   - Tracks parameter validation status and execution output payload.

4. **`AutomationApproval`**:
   - Gated human confirmation record.
   - Contains SHA-256 `parameter_hash` binding approval to the exact proposed parameters.
   - 24-hour expiration (`expires_at`), with auto-rejection on expiry.

5. **`AutomationExecutionLog`**:
   - Append-only diagnostic trail recording step-level progress (`classification`, `planning`, `risk_assessment`, `execution`, `verification`).
