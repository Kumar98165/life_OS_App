# LifeOS Task UI Guidelines

## 1. Design Tokens & Visual Hierarchy

The Task Management UI strictly adheres to **White Glassmorphism** guidelines:

| Visual Element | Specification | Semantic Purpose |
| :--- | :--- | :--- |
| **Card Surface** | `theme.colors.glassBackgroundSolid` (`rgba(255,255,255,0.75)`) | Task row background |
| **Borders** | `theme.colors.glassBorder` (`#E9EAF2`) | Subtle structural containment |
| **Urgent Priority Strip** | `#EF4444` (`theme.colors.error`) | Critical / urgent tasks |
| **High Priority Strip** | `#F59E0B` (`theme.colors.warning`) | High-priority deadlines |
| **Medium Priority Strip** | `#6C63FF` (`theme.colors.primary`) | Standard priorities |
| **Low Priority Strip** | `#85859A` (`theme.colors.textMuted`) | Low priority backlog items |
| **Completed Task** | Line-through on title, `#85859A` text, green check | Clear visual feedback of accomplishment |

---

## 2. Interaction Specifications

- **Single-Tap Completion**: Tapping the circular icon button on the left edge toggles completion immediately. Completed tasks visually strike through.
- **Card Tap**: Tapping anywhere on the task content opens the `TaskDetailsModal`.
- **Search Bar**: Debounced input prevents network thrashing while typing.
- **Delete Confirmation**: Deleting a task invokes `ConfirmationModal` with destructive styling, preventing accidental data loss.
- **Pull-to-Refresh**: Available on both the Tasks screen and Dashboard to synchronize live data.

