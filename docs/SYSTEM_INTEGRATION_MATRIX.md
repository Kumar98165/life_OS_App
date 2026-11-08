# LifeOS – Complete System Integration Matrix

Comprehensive audit matrix covering all 14 LifeOS modules, verifying end-to-end integration between Flask/SQLAlchemy backend endpoints and React Native/Expo frontend screens, services, hooks, and stores.

---

## 1. Module Overview Matrix

| # | Module | Backend Blueprint Prefix | Mobile Screen(s) | Service Client | TanStack Query Hook(s) | State Store | Validation Layer | Status |
|---|---|---|---|---|---|---|---|---|
| **1** | **Authentication & Sessions** | `/api/v1/auth`, `/api/v1/users` | `LoginScreen`, `RegisterScreen`, `WelcomeScreen`, `SplashScreen` | `authService.ts` | Mutation hooks | `useAuthStore` (Zustand + SecureStore) | Pydantic (`RegisterRequest`, `LoginRequest`) / Zod (`loginSchema`, `registerSchema`) | **Verified (100%)** |
| **2** | **Unified Dashboard** | Aggregated (`/tasks`, `/goals`, `/habits`, `/analytics`) | `DashboardScreen`, `HomeScreen` | `dashboardService.ts` | `useDashboardOverview` | TanStack Query Cache (`['dashboard_overview']`) | Aggregated response typing | **Verified (100%)** |
| **3** | **Task Management** | `/api/v1/tasks` | `TasksScreen` | `taskService.ts` | `useTasks`, `useTaskDetails`, `useCreateTask`, `useUpdateTask`, `useToggleCompleteTask`, `useDeleteTask` | TanStack Query Cache (`['tasks']`) | Pydantic (`CreateTaskRequest`, `UpdateTaskRequest`) / Zod (`taskFormSchema`) | **Verified (100%)** |
| **4** | **Planner & Time Blocking** | `/api/v1/planner` | `PlannerScreen` | `plannerService.ts` | `usePlannerBlocks`, `usePlannerBlockDetails`, `useCreateBlock`, `useUpdateBlock`, `useUpdateBlockStatus`, `useDailySummary` | TanStack Query Cache (`['planner_blocks']`) | Pydantic (`CreatePlannerBlockRequest`, `UpdatePlannerBlockRequest`) / Zod (`plannerBlockFormSchema`) | **Verified (100%)** |
| **5** | **Goals & Milestones** | `/api/v1/goals` | `GoalsScreen` | `goalService.ts` | `useGoals`, `useGoalDetails`, `useCreateGoal`, `useUpdateGoal`, `useDeleteGoal`, `useMilestones`, `useCreateMilestone`, `useUpdateMilestone` | TanStack Query Cache (`['goals']`) | Pydantic (`CreateGoalRequest`, `MilestoneRequest`) / Zod (`goalFormSchema`, `milestoneFormSchema`) | **Verified (100%)** |
| **6** | **Habits & Streaks** | `/api/v1/habits` | `HabitsScreen` | `habitService.ts` | `useHabits`, `useHabitDetails`, `useCreateHabit`, `useUpdateHabit`, `useDeleteHabit`, `useLogCheckIn`, `useUndoCheckIn`, `useHabitLogs`, `useHabitStats` | TanStack Query Cache (`['habits']`) | Pydantic (`CreateHabitRequest`, `HabitLogRequest`) / Zod (`habitFormSchema`, `habitLogSchema`) | **Verified (100%)** |
| **7** | **AI Assistant (Local LLM)** | `/api/v1/ai` | `AIAssistantScreen` | `aiService.ts` | `useAIConversations`, `useAIConversationHistory`, `useAISendMessage`, `useAICreateConversation`, `useAIDeleteConversation`, `useAIHealth` | TanStack Query + local message buffer | Pydantic (`ChatRequest`, `CreateConversationRequest`) / Client response contracts | **Verified (100%)** |
| **8** | **AI Memory Engine** | `/api/v1/ai/memories` | `AIMemoryScreen` | `aiMemoryService.ts` | `useConfirmedMemories`, `usePendingSuggestions`, `useApproveSuggestion`, `useRejectSuggestion`, `useCreateMemory`, `useDeleteMemory`, `useMemorySettings` | TanStack Query Cache (`['ai_memories']`) | Pydantic (`CreateMemoryRequest`, `ApproveSuggestionRequest`) / Typed client contracts | **Verified (100%)** |
| **9** | **AI Feedback & Training Consent** | `/api/v1/ai/feedback`, `/api/v1/ai/privacy` | `AIAssistantScreen` | `aiService.ts` | `useAISubmitFeedback`, `useAIMessageFeedback`, `useAIPrivacyConsent`, `useAIUpdatePrivacyConsent` | TanStack Query Cache (`['ai_message_feedback']`) | Pydantic (`SubmitFeedbackRequest`, `UpdateConsentRequest`) / Strict TS interfaces | **Verified (100%)** |
| **10** | **AI Prompt Versioning** | `/api/v1/ai/prompts` | Admin & Audit routes | Backend service layer (`AIPromptVersionRepository`) | Orchestrated dynamically in `AIService` LangGraph pipeline | Immutable DB persistence (`ai_prompt_versions`) | Pydantic (`CreatePromptVersionRequest`, `ActivatePromptVersionRequest`) | **Verified (100%)** |
| **11** | **Personal Money Management** | `/api/v1/finance` | `FinanceDashboardScreen`, `AccountsScreen`, `AddTransactionScreen`, `TransactionHistoryScreen`, `TransactionDetailScreen`, `BudgetManagementScreen`, `SavingsGoalsScreen`, `FinanceSettingsScreen` | `financeService.ts` | `useFinanceDashboard`, `useFinanceInsights`, `useAccounts`, `useCategories`, `useTransactions`, `useBudgets`, `useSavingsGoals` | TanStack Query Cache (`['finance']`) | Pydantic (`CreateTransactionRequest`, `CreateAccountRequest`, etc.) / Zod finance schemas | **Verified (100%)** |
| **12** | **Centralized Notifications** | `/api/v1/notifications` | `NotificationCenterScreen`, `NotificationSettingsScreen` | `notificationService.ts`, `pushNotificationService.ts` | `useNotifications`, `useUnreadNotificationsCount`, `useNotificationPreferences`, `useMarkNotificationRead`, `useMarkAllNotificationsRead` | TanStack Query Cache (`['notifications']`) | Pydantic (`NotificationPreferenceRequest`, `PushTokenRequest`) / Zod notification schemas | **Verified (100%)** |
| **13** | **Intelligent Reminders** | `/api/v1/notifications/reminders` | `ReminderManagementScreen`, `CreateEditReminderScreen` | `notificationService.ts` | `useReminders`, `useCreateReminder`, `useUpdateReminder`, `useDeleteReminder` | TanStack Query Cache (`['reminders']`) | Pydantic (`CreateReminderRequest`, `UpdateReminderRequest`) / Zod (`reminderFormSchema`) | **Verified (100%)** |
| **14** | **Life Analytics & Insights** | `/api/v1/analytics` | `LifeAnalyticsScreen`, `ProductivityAnalyticsScreen`, `HabitAnalyticsScreen`, `GoalsAnalyticsScreen`, `FinanceAnalyticsScreen`, `LifeInsightsScreen`, `AnalyticsQuickCard` | `analyticsService.ts` | `useAnalyticsOverview`, `useProductivityAnalytics`, `useHabitAnalytics`, `useGoalAnalytics`, `useFinanceAnalytics`, `useTrendsAnalytics`, `useLifeScore`, `useAIInsights` | TanStack Query Cache (`['analytics']`) | Pydantic query models (`Period`, `DateRangeParams`) / Typed analytics contracts | **Verified (100%)** |

---

## 2. Cross-Module Data Dependencies & Workflow Matrix

### 2.1 Tasks + Planner + Productivity Analytics
- **Interaction**: Creating a task allows immediate scheduling into a time-blocked planner block (`block_type='task'`, `task_id=<uuid>`).
- **Completion Sync**: Completing a task or marking a block finished updates both module entities.
- **Analytics Consumption**: The `/api/v1/analytics/productivity` endpoint aggregates task completion counts, planner scheduled minutes, and adherence ratios into composite productivity metrics.

### 2.2 Habits + Streaks + Habit Analytics
- **Interaction**: Habits track daily/weekday check-in logs with idempotent single-day check-in logic.
- **Streak Calculation**: Continuous daily log chains calculate current and longest streaks.
- **Analytics Consumption**: `/api/v1/analytics/habits` aggregates total check-ins against target schedule, yielding consistency percentages used directly in the 4-pillar Life Score.

### 2.3 Goals + Milestones + Goal Analytics
- **Interaction**: Goals contain hierarchical milestone checkpoints.
- **Progress Sync**: Marking a milestone complete recalculates overall goal completion percentage.
- **Analytics Consumption**: `/api/v1/analytics/goals` calculates active goals, milestone completion velocity, and pending deadlines.

### 2.4 Personal Finance + Ledgers + Financial Analytics
- **Interaction**: Financial accounts maintain running Decimal balances mutated transactionally by income and expense entries.
- **Budget Utilization**: Real-time spending per category calculates budget utilization percentages.
- **Analytics Consumption**: `/api/v1/analytics/finance` computes periodic income, expenses, net savings, and savings rate (`(net_savings / income) * 100`).

### 2.5 Centralized Notifications + Cross-Domain Entities
- **Interaction**: Scheduled events across Tasks, Habits, Goals, and Budgets dispatch deduplicated reminders and notifications.
- **Deep-Link Resolution**: In-app push notifications carry `{ entity_type, entity_id }` payloads that route directly to the source module screen (`Tasks`, `Habits`, `Goals`, `Finance`).

### 2.6 AI Assistant + Dynamic Context + Prompt Attribution
- **Interaction**: The local LangGraph workflow retrieves live user context across tasks, habits, and goals to provide personalized assistance.
- **Auditability**: Every generated assistant turn records the active `prompt_version_id`, model name (`qwen2.5:3b`), and token counts.
- **Feedback Loop**: User ratings (+1 / -1) and correction suggestions attach directly to message IDs with user-controlled training consent.

### 2.7 4-Pillar Transparent Life Score Engine
- **Formula**:
  $$\text{Life Score} = W_p \cdot S_p + W_h \cdot S_h + W_g \cdot S_g + W_f \cdot S_f$$
  Where base weights are: Productivity ($0.30$), Habits ($0.30$), Goals ($0.20$), Financial Discipline ($0.20$).
- **Dynamic Normalization**: If a user has zero activity in one or more pillars (e.g. no financial accounts or goals set up yet), those pillars are flagged as `unpenalized_no_data` and their weights are re-normalized across active pillars, ensuring beginners are not unfairly penalized.
- **Disclaimer**: Every Life Score output includes a mandatory non-clinical disclaimer stating it is a personal productivity metric and not a medical or psychological diagnosis.

