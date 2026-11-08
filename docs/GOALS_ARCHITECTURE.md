# LifeOS – Goals & Milestones Architecture

## 1. Architectural Overview

The Goals & Milestones module empowers users to establish long-term objectives (OKRs, personal growth targets, fitness aspirations, career achievements) and decompose them into actionable, measurable checkpoints.

```
+-------------------------------------------------------------+
|                      Mobile UI Layer                        |
|  - GoalsScreen (Active/Completed counts, Progress, Filters) |
|  - CreateEditGoalModal (Priority, Target Date, Category)    |
|  - CreateEditMilestoneModal (Title, Due Date, Sort Order)   |
|  - GoalDetailsModal (Milestone Checklist, Direct Toggles)   |
|  - ActiveGoalsSection (Home Dashboard Live Integration)     |
+-------------------------------------------------------------+
                              |
                              v  (TanStack Query Cache)
+-------------------------------------------------------------+
|                    Client Service Layer                     |
|  - goalService.ts (REST client with JWT Authorization)      |
|  - Zod goalFormSchema & milestoneFormSchema                 |
|  - useGoals (Query & Mutation hooks with cache invalidation)|
+-------------------------------------------------------------+
                              |
                              v  (HTTPS / JWT Bearer)
+-------------------------------------------------------------+
|                    Backend API Layer                        |
|  - Flask Blueprint (/api/v1/goals)                          |
|  - Pydantic Schemas (CreateGoalRequest, UpdateGoalRequest)  |
|  - JWT Authentication & RBAC boundaries                     |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                   Business Service Layer                    |
|  - GoalService (IDOR enforcement, Milestone parent check)   |
|  - Automatic mathematical progress percentage sync          |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                    Persistence Layer                        |
|  - GoalRepository (SQLAlchemy 2.x, selectinload)            |
|  - PostgreSQL goals & goal_milestones Tables                |
|  - Foreign keys: users (CASCADE), goals (CASCADE)           |
+-------------------------------------------------------------+
```

---

## 2. Domain Separation: Goals, Tasks, Planner

| Domain | Entity | Core Question | Resolution |
| :--- | :--- | :--- | :--- |
| **Goals** | `Goal`, `GoalMilestone` | *"What long-term outcome am I trying to achieve?"* | High-level measurable achievement decomposed into sequential checkpoints. |
| **Tasks** | `Task` | *"What specific work deliverable must be completed?"* | Discrete actionable item with priority and due date. |
| **Planner**| `PlannerBlock` | *"When will I reserve time on my calendar today?"* | Concrete time reservation with conflict detection. |

Milestones represent checkpoints within a goal. They remain decoupled from tasks and calendar blocks to prevent rigid cascade side-effects.

---

## 3. Progress Calculation Architecture
The backend strictly computes and stores `progress_percent` on the `Goal` entity:
$$\text{progress\_percent} = \begin{cases} 0.0 & \text{if total\_milestones} = 0 \\ \text{round}\left(\frac{\text{completed\_milestones}}{\text{total\_milestones}} \times 100, 1\right) & \text{if total\_milestones} > 0 \end{cases}$$

Client applications display real progress calculated by the server and never submit raw client-calculated progress percentages.

