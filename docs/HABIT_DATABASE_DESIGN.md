# LifeOS Habit Database Design

The habit tracking subsystem is modeled in Third Normal Form (3NF) within PostgreSQL, ensuring referential integrity, performant streak queries, and idempotent daily logging.

---

## 1. Relational Entities

### `habits` Table
Stores high-level recurring habit definitions.
- `id` (VARCHAR(36), PK): UUID primary key.
- `user_id` (VARCHAR(36), FK -> `users.id` ON DELETE CASCADE, NOT NULL): Owner.
- `title` (VARCHAR(255), NOT NULL): Habit name.
- `description` (TEXT, NULL): Optional notes.
- `frequency` (VARCHAR(20), NOT NULL, DEFAULT 'daily'): 'daily', 'weekdays', or 'weekly'.
- `target_days_per_week` (INTEGER, NOT NULL, DEFAULT 7): Target completions per calendar week.
- `current_streak` (INTEGER, NOT NULL, DEFAULT 0): Cached current consecutive streak length.
- `longest_streak` (INTEGER, NOT NULL, DEFAULT 0): All-time longest streak recorded.
- `color_hex` (VARCHAR(10), NOT NULL, DEFAULT '#6C63FF'): Hex color code for UI cards.
- `icon` (VARCHAR(50), NULL): Ionicons glyph name.
- `is_archived` (BOOLEAN, NOT NULL, DEFAULT FALSE): Soft-archive toggle.
- `created_at` (TIMESTAMPTZ, NOT NULL): Creation timestamp.
- `updated_at` (TIMESTAMPTZ, NOT NULL): Last modification timestamp.

### `habit_logs` Table
Stores discrete completion records.
- `id` (VARCHAR(36), PK): UUID primary key.
- `habit_id` (VARCHAR(36), FK -> `habits.id` ON DELETE CASCADE, NOT NULL): Target habit.
- `log_date` (DATE, NOT NULL): Calendar date (YYYY-MM-DD) of the log.
- `completed` (BOOLEAN, NOT NULL, DEFAULT TRUE): Completion status flag.
- `notes` (TEXT, NULL): Optional reflection or execution note.
- `created_at` (TIMESTAMPTZ, NOT NULL): Record timestamp.

---

## 2. Constraints & Indexes
1. **Unique Date Constraint**:
   ```sql
   CONSTRAINT uq_habit_log_date UNIQUE (habit_id, log_date)
   ```
   Ensures no duplicate records exist for the same habit on a single day.
2. **Performance Indexes**:
   - `ix_habits_user_archived` ON `habits (user_id, is_archived)`: Rapid filtered habit listing.
   - `ix_habit_logs_habit_date` ON `habit_logs (habit_id, log_date)`: Fast streak and date-range lookups.
   - `ix_habit_logs_log_date` ON `habit_logs (log_date)`: Fast daily summary aggregation.

