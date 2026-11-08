# LifeOS – Daily Planner Database Design

## 1. Schema Definition (`planner_blocks`)

The table `planner_blocks` was established in STEP 02 and extended in STEP 09 (migration `daaa4c2c151c`).

```sql
CREATE TABLE planner_blocks (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id VARCHAR(36) REFERENCES tasks(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    block_type VARCHAR(30) NOT NULL DEFAULT 'task',
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    color_hex VARCHAR(10),
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 2. Indexes and Performance Strategy

To ensure queries for daily ranges and status filters run efficiently without full table scans:

1. `ix_planner_blocks_user_id`: Fast lookup of blocks belonging to a user.
2. `ix_planner_blocks_task_id`: Fast lookup of calendar reservations for a specific task.
3. `ix_planner_user_start`: Composite index on `(user_id, start_time)` for range filtering.
4. `ix_planner_user_status`: Composite index on `(user_id, status)` for quick conflict exclusions.
5. `ix_planner_user_completed`: Composite index on `(user_id, is_completed)` for metrics.

---

## 3. Relationships & Foreign Key Constraints

| Relationship | Constraint | On Delete Action | Business Justification |
| :--- | :--- | :--- | :--- |
| `PlannerBlock.user` | `users(id)` | `CASCADE` | When a user account is deleted, all their schedule blocks are removed. |
| `PlannerBlock.task` | `tasks(id)` | `SET NULL` | Deleting a task keeps the calendar reservation as an independent standalone block. |

---

## 4. Alembic Migration History

- Initial schema creation: `fd75471a4d7c_create_initial_lifeos_schema.py`
- Step 09 enhancement: `daaa4c2c151c_add_planner_block_fields.py`
  - Added `description TEXT NULL`
  - Added `status VARCHAR(20) NOT NULL DEFAULT 'scheduled'`
  - Added `color_hex VARCHAR(10) NULL`
  - Added composite indexes `ix_planner_user_status` and `ix_planner_user_completed`

