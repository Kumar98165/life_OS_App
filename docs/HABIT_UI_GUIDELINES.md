# LifeOS Habit Tracker UI & Design Guidelines

## 1. Visual Token Alignment
The Habit Tracker interface follows the White Glassmorphism design system defined in `DESIGN_SYSTEM.md`:
- **Canvas Background**: `#F7F8FC`
- **Glass Surface Solid**: `#FFFFFF` with `rgba(255, 255, 255, 0.85)` transparency where supported
- **Borders**: Hairline `rgba(226, 232, 240, 0.8)`
- **Completed Accent**: `#10B981` (Emerald Success)
- **Active Streak Indicator**: `#F59E0B` (Amber Flame 🔥)
- **Brand Accent**: `#6C63FF` (LifeOS Indigo)

---

## 2. Component Guidelines

### A. Habit Card
- Shows vertical accent bar on left border matching chosen color.
- Card title rendered in `BodyText` semi-bold (`weight="600"`).
- Metadata row displaying frequency chip (`Daily`, `Mon-Fri`, `3x/wk`) alongside current streak (`🔥 5d streak`).
- Quick-check action button:
  - If unchecked: crisp circular outline in habit accent color.
  - If checked: animated solid emerald background with white checkmark icon.

### B. Habit Details Modal & Calendar Heatmap
- Current & Longest Streak metric tiles.
- Interactive month grid supporting previous month navigation (`<` / `>`).
- Grid cells:
  - **Completed**: `#10B981` soft background with emerald text and check dot.
  - **Unscheduled**: Muted neutral gray (opacity 0.5) for weekend days on weekday-only habits.
  - **Missed**: Neutral cell with dark gray number.
  - **Future**: Muted text preventing misleading historical completion indicators.
- One-tap check-in toggle with immediate rollback on mutation failure.
- Destructive actions guarded by `ConfirmationModal`.

### C. Dashboard Integration
- The `HabitSummarySection` on the Home Dashboard surfaces:
  - `activeCount`: Total non-archived habits.
  - `completedTodayCount`: Habits marked complete for today's date.
  - `completionRate`: Progress percentage completed today.
- Direct navigation links to the dedicated `Habits` screen.

