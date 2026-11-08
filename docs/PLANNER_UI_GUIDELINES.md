# LifeOS – Planner UI & Component Guidelines

## 1. Visual Design Principles

The Daily Planner follows the **Premium White Glassmorphism Design System** defined in STEP 05.

- **Background**: Soft clean canvas `#F7F8FC`.
- **Card Surfaces**: Frosted glass `rgba(255, 255, 255, 0.75)` with subtle borders `rgba(233, 234, 242, 0.80)`.
- **Brand Primary**: Electric Lavender `#6C63FF` with deep accent `#554CE0`.
- **Status Indicators**:
  - `scheduled`: Lavender `#6C63FF`
  - `completed`: Fresh Emerald `#22C55E`
  - `skipped`: Amber `#F59E0B`
  - `cancelled`: Crimson `#EF4444`

---

## 2. Screen & Modal Composition

### A. `PlannerScreen.tsx`
- **Top Bar**: "Daily Planner" title, "Today" quick shortcut pill, floating primary add button.
- **View Mode Switcher**: Segmented glass tabs for `Day`, `Week`, and `Month`.
- **Date Strip**: 7-day horizontal carousel centered around the selected date.
- **Daily Summary Card**: Real-time counter of total reservations, total scheduled minutes, and completion rate pill.
- **Timeline List**: Chronological cards with left accent color bar matching activity type or user selection, start/end badges, linked task chips, and completion strikethrough.

### B. `CreateEditPlannerBlockModal.tsx`
- Bottom sheet glass card with keyboard avoidance.
- Form fields: Title, Date, Start Time, End Time, Activity Type selector (9 activity presets), Linked Task selector, and 8 color accent presets.
- Inline conflict/error banner displaying human-readable scheduling overlap reasons.

### C. `PlannerBlockDetailsModal.tsx`
- Full-screen glass modal showing scheduled block duration, task metadata, status changer buttons, and delete button with destructive confirmation.

### D. `UpcomingScheduleSection.tsx` (Dashboard Integration)
- Embedded widget inside `DashboardScreen.tsx` between Quick Actions and Today's Tasks.
- Displays upcoming scheduled blocks for the day.
- Honest empty state when no blocks are reserved with an active "Plan Your Day" button.

