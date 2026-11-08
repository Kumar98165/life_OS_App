# LifeOS Dashboard API Integration Reference

## 1. Current Verified Endpoints

The dashboard integrates with verified backend REST endpoints under `/api/v1`:

| Method | Endpoint | Authorization | Integrated Data | Status |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/auth/me` | `Bearer <access_token>` | Authenticated user profile (`id`, `full_name`, `email`, `avatar_url`) | **Live & Verified** |
| `GET` | `/api/v1/users/me` | `Bearer <access_token>` | User account record from User Service | **Live & Verified** |

---

## 2. Domain Milestones & Empty State Strategy

The database models for `tasks`, `goals`, `habits`, and `planner_blocks` are fully defined in PostgreSQL (from STEP 02). However, backend API endpoints for these modules are scheduled for upcoming development milestones:

| Domain | Target Endpoint | Scheduled Phase | Fallback Behavior in STEP 07 |
| :--- | :--- | :--- | :--- |
| **Tasks** | `GET /api/v1/tasks/today` | STEP 08 (Tasks Engine) | Returns `[]`, computes 0% progress, displays `EmptyState` ("No tasks scheduled for today") with "Add Task" button |
| **Goals** | `GET /api/v1/goals/active` | Milestone: Goals & OKRs | Returns `[]`, displays `EmptyState` ("No active goals yet") with "Create Goal" button |
| **Habits** | `GET /api/v1/habits/summary` | STEP 08 (Habits Engine) | Returns `{ activeCount: 0, completedTodayCount: 0, completionRate: 0 }`, displays informative habits card |
| **AI Assistant** | `POST /api/v1/ai/chat` | Milestone: Local AI / LangGraph | Shows dialog explaining local Ollama readiness on `localhost:11434` without fabricating AI responses |

> [!IMPORTANT]
> **No Fake Data Guarantee**:
> In accordance with Senior Engineering guidelines, the dashboard strictly avoids hardcoding dummy tasks or generating fabricated statistics in production code. Empty states accurately inform the user while maintaining full layout integrity.

---

## 3. Query Caching & Pull-to-Refresh

- **Query Key**: `['dashboardOverview']`
- **Stale Time**: 120,000ms (2 minutes)
- **Retry Policy**: 2 retries with exponential backoff on transient network faults
- **Pull-to-Refresh**: Native `RefreshControl` bound to TanStack Query's `refetch()` function.

