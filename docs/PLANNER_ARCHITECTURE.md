# LifeOS – Daily Planner & Calendar Architecture

## 1. Architectural Overview

The Daily Planner and Calendar Management system orchestrates time-based scheduling for LifeOS. It operationalizes high-level user intentions by converting work items and daily routines into reserved calendar blocks with conflict prevention, timezone normalization, and task integration.

```
+-------------------------------------------------------------+
|                     Mobile UI Layer                         |
|  - PlannerScreen (Day, Week, Month calendar views)          |
|  - CreateEditPlannerBlockModal (Pill selector, color picker)|
|  - PlannerBlockDetailsModal (Details, status transitions)   |
|  - UpcomingScheduleSection (Home Dashboard Widget)          |
+-------------------------------------------------------------+
                              |
                              v  (TanStack Query Cache)
+-------------------------------------------------------------+
|                    Client Service Layer                     |
|  - plannerService.ts (Axios REST client)                    |
|  - Zod plannerBlockFormSchema (Validation & Date Math)      |
|  - usePlanner (Hooks: blocks, daily summary, mutations)     |
+-------------------------------------------------------------+
                              |
                              v  (HTTPS / JWT Bearer)
+-------------------------------------------------------------+
|                    Backend API Layer                        |
|  - Flask Blueprint (/api/v1/planner)                        |
|  - Pydantic Schemas (CreatePlannerBlockRequest, etc.)       |
|  - JWT Authentication & RBAC boundaries                     |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                   Business Service Layer                    |
|  - PlannerService (Conflict detection, task ownership)      |
|  - Strict UTC boundary conversions                          |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                    Persistence Layer                        |
|  - PlannerRepository (SQLAlchemy 2.x, range queries)        |
|  - PostgreSQL planner_blocks Table                          |
|  - Foreign keys: users (CASCADE), tasks (SET NULL)          |
+-------------------------------------------------------------+
```

---

## 2. Core Domain Distinction

| Concept | Definition | Lifecycle | Persistence Target |
| :--- | :--- | :--- | :--- |
| **Task** | Work unit that needs completion (deliverable, goal action). | Pending $\rightarrow$ Completed $\rightarrow$ Archived | `tasks` table |
| **Planner Block** | Reserved time slot on a calendar (e.g. 09:00 - 10:30). | Scheduled $\rightarrow$ Completed / Skipped / Cancelled | `planner_blocks` table |

- **Decoupled Lifecycle**: Completing a planner block does NOT automatically mark a linked task as completed unless explicitly requested.
- **Standalone Blocks**: Blocks can exist independently of tasks (e.g., "Personal Workout", "Client Sync", "Lunch Break").
- **Referential Integrity**: Deleting a planner block preserves the underlying task. Deleting a task safely clears `planner_blocks.task_id` (`ON DELETE SET NULL`).

---

## 3. Conflict Detection Engine

Conflict detection ensures users cannot double-book their active calendar.

### Overlap Invariant
Two time intervals $A = [A_{start}, A_{end}]$ and $B = [B_{start}, B_{end}]$ overlap if and only if:
$$A_{start} < B_{end} \quad \text{AND} \quad A_{end} > B_{start}$$

### Rules
1. **Adjacent Allowed**: Non-overlapping contiguous blocks ($10:00 - 11:00$ followed by $11:00 - 12:00$) are allowed because $A_{end} == B_{start}$.
2. **Cancelled Excluded**: Blocks with `status = 'cancelled'` do not reserve calendar capacity and are excluded from conflict evaluations.
3. **Self-Exclusion on Update**: Modifying a block's details excludes its own ID (`id != exclude_block_id`) to avoid false self-conflicts.
4. **Strict Concurrency**: Enforced at the service layer prior to transaction commit, returning HTTP 409 `CONFLICT`.

