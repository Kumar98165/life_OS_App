# LifeOS Automation Tool Registry

> **Version**: 1.0.0  
> **Date**: 2026-11-08  
> **Status**: Verified

---

## 1. Registry Architecture

The `AutomationToolRegistry` is a singleton container registering all operations callable by automation workflows. Direct database manipulation by the model is impossible; only registered tools with explicit Pydantic schemas can execute.

---

## 2. Permitted Tool List

| Tool Identifier | Category | Risk Level | Requires Approval | Parameters Schema | Description |
|-----------------|----------|------------|-------------------|-------------------|-------------|
| `tasks.create_task` | Tasks | Medium | ✅ Yes | `CreateTaskSchema` | Create task with title, priority, due date, estimated minutes |
| `tasks.update_task` | Tasks | High | ✅ Yes | `UpdateTaskSchema` | Update task priority, status, or deadline |
| `tasks.get_pending_tasks` | Tasks | Low | ❌ No | `GetPendingTasksSchema` | Read-only query of pending and in-progress tasks |
| `planner.create_block` | Planner | Medium | ✅ Yes | `CreatePlannerBlockSchema` | Schedule calendar block with conflict detection |
| `planner.get_upcoming_schedule` | Planner | Low | ❌ No | `GetUpcomingScheduleSchema` | Read-only query of calendar blocks |
| `habits.get_habit_progress` | Habits | Low | ❌ No | None | Read-only summary of active habits and streaks |
| `goals.get_goal_progress` | Goals | Low | ❌ No | None | Read-only summary of active goals and milestone completion |
| `notifications.create_reminder` | Notifications | Medium | ✅ Yes | `CreateReminderSchema` | Schedule in-app reminder notification |
| `notifications.get_upcoming_reminders` | Notifications | Low | ❌ No | None | Read-only query of pending reminders |
| `finance.get_financial_summary` | Finance | Low | ❌ No | `ReadOnlyFinanceSchema` | Read-only monthly income, expenses, and budget utilization |

---

## 3. Tool Invariants

1. **User Scoping**: Every tool handler requires `user_id` injected from the authenticated session context. The LLM cannot specify or override the target `user_id`.
2. **Strict Schema Parsing**: Parameters must conform to Pydantic constraints before execution is attempted.
3. **Financial Read-Only Enforcement**: There are NO financial write tools (no transfers, no balance updates, no transaction creation/deletion).
