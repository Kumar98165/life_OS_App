# LifeOS – Goals UI & Component Guidelines

## 1. Visual Design Principles

The Goals module is built in accordance with the **White Glassmorphism Design System** defined in STEP 05.

- **Background Canvas**: `#F7F8FC`.
- **Card Surfaces**: Frosted glass `rgba(255, 255, 255, 0.75)` with subtle borders `rgba(233, 234, 242, 0.80)`.
- **Accent Primary**: Lavender `#6C63FF` with deep accent `#554CE0`.
- **Priority Indicators**:
  - `high`: Amber `#F59E0B`
  - `medium`: Brand Lavender `#6C63FF`
  - `low`: Muted Slate `#85859A`
- **Status Indicators**:
  - `in_progress` / `active`: Lavender `#6C63FF`
  - `completed` / `achieved`: Emerald `#22C55E`
  - `paused`: Amber `#F59E0B`
  - `cancelled` / `abandoned`: Crimson `#EF4444`

---

## 2. Screen & Modal Composition

### A. `GoalsScreen.tsx`
- **Header**: "Goals & Milestones" title with quick "+ Add Goal" primary action.
- **Metrics Strip**: 3 cards showing Active Goals count, Completed Goals count, and Average Progress percentage.
- **Search & Filters**: `SearchInput` for instant title/category filtering + status selector pills (`All`, `In Progress`, `Completed`, `Paused`).
- **Goal Cards**: Shows title, category badge, status badge, description preview, target date, priority badge, and progress bar with completed/total checkpoint ratio.
- **Interactions**: Tapping any card opens `GoalDetailsModal`.

### B. `GoalDetailsModal.tsx`
- Glass sheet displaying goal vision, priority badge, status badge, and target date.
- Dynamic progress bar with live percentage and checkpoint metrics.
- Checkpoints Checklist: Each milestone has an interactive checkbox allowing instant completion/reopening, title, due date, edit action, and delete action.
- Actions: "+ Add Milestone", "Edit Goal", and destructive "Delete Goal" confirmation.

### C. `CreateEditGoalModal.tsx`
- Form modal with title, target date picker, priority selector pills (`Low`, `Medium`, `High`), status selector (when editing), category selector pills, and description textarea.

### D. `CreateEditMilestoneModal.tsx`
- Lightweight modal for adding or editing specific goal checkpoints (Title, Target Date, Acceptance details).

### E. `ActiveGoalsSection.tsx` (Dashboard)
- Connected to real user data via `dashboardService` $\rightarrow$ `goalService`.
- Displays up to 3 active goals with live progress bars, target dates, and empty state with a "Create Goal" action.

