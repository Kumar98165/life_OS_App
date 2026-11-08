# LifeOS Dashboard Component Guidelines

## 1. Design & Typography Tokens

| Element | Light Theme Token | Dark Theme Token | Specifications |
| :--- | :--- | :--- | :--- |
| **Canvas Background** | `#F7F8FC` | `#0F0F18` | `theme.colors.background` |
| **Glass Card Surface** | `rgba(255, 255, 255, 0.75)` | `rgba(26, 26, 38, 0.75)` | High opacity fallback on Android/Web |
| **Card Borders** | `#E9EAF2` | `#2D2D42` | `1px solid` |
| **Primary Brand Accent** | `#6C63FF` | `#6C63FF` | Used for progress fills, highlights, icons |
| **Primary Dark Accent** | `#554CE0` | `#554CE0` | Gradient end-stops |
| **Primary Text** | `#202033` | `#FFFFFF` | Headings and titles |
| **Secondary Text** | `#85859A` | `#A0A0B5` | Captions and descriptions |

---

## 2. Reusable Component Specifications

### `DashboardHeader`
- **Location**: `mobile/src/components/dashboard/DashboardHeader.tsx`
- **Props**:
  - `userName?: string | null`
  - `onProfilePress?: () => void`
  - `onNotificationPress?: () => void`
  - `hasUnreadNotifications?: boolean`
- **Dynamic Greeting**: Time-aware logic partitioned into Morning (05:00–11:59), Afternoon (12:00–16:59), and Evening (17:00–04:59).

### `DailyOverviewCard`
- **Location**: `mobile/src/components/dashboard/DailyOverviewCard.tsx`
- **Props**:
  - `progress: DailyTaskProgress` (`completed`, `total`, `percentage`, `motivationalMessage`)
- **Safe Math**: Avoids division by zero; when `total === 0`, percentage defaults to `0%` and renders rest-day reassurance.

### `QuickActionsSection`
- **Location**: `mobile/src/components/dashboard/QuickActionsSection.tsx`
- **Props**:
  - `onActionPress: (action: QuickActionType) => void`
- **Actions**: `add_task`, `plan_day`, `create_goal`, `talk_ai`. Minimum touch target is $44 \times 44\text{pt}$ with accessible labels.

### `TodayTasksSection`
- **Location**: `mobile/src/components/dashboard/TodayTasksSection.tsx`
- **Props**:
  - `tasks: Task[]`
  - `isLoading?: boolean`
  - `isError?: boolean`
  - `onRetry?: () => void`
  - `onViewAll?: () => void`
  - `onTaskPress?: (task: Task) => void`
  - `onAddTask?: () => void`
- **Visuals**: Displays priority badges (`low`, `medium`, `high`, `urgent`) with strike-through styling on completed items.

### `ActiveGoalsSection`
- **Location**: `mobile/src/components/dashboard/ActiveGoalsSection.tsx`
- **Props**:
  - `goals: Goal[]`
  - `isLoading?: boolean`
  - `onViewAll?: () => void`
  - `onGoalPress?: (goal: Goal) => void`
  - `onCreateGoal?: () => void`

### `HabitSummarySection`
- **Location**: `mobile/src/components/dashboard/HabitSummarySection.tsx`
- **Props**:
  - `summary: HabitSummary` (`activeCount`, `completedTodayCount`, `completionRate`)
  - `onViewAll?: () => void`
  - `onTrackHabit?: () => void`

### `AIQuickAccessCard`
- **Location**: `mobile/src/components/dashboard/AIQuickAccessCard.tsx`
- **Props**:
  - `onTalkToAI: () => void`
- **Behavior**: Direct launcher to upcoming local AI assistant modal.

### `GlassBottomNavigation`
- **Location**: `mobile/src/components/glass/GlassBottomNavigation.tsx`
- **Integrated Tabs**: `Home`, `Planner`, `Tasks`, `Goals`, `Profile`.
- **Active Indicator**: Horizontal active pill below active icon with label text bolding.

