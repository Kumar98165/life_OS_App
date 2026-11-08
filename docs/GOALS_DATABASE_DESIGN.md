# LifeOS – Goals & Milestones Database Design

## 1. Relational Schema Architecture

The database architecture employs two normalized tables with strict foreign key referential integrity:

```sql
-- Goals Table
CREATE TABLE goals (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    progress_percent FLOAT NOT NULL DEFAULT 0.0,
    category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Goal Milestones Table
CREATE TABLE goal_milestones (
    id VARCHAR(36) PRIMARY KEY,
    goal_id VARCHAR(36) NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_date TIMESTAMP WITH TIME ZONE,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 2. Performance Indexes

1. `ix_goals_user_id`: Fast lookup for user-scoped queries.
2. `ix_goals_user_status`: Composite index on `(user_id, status)` for fast dashboard queries and tab filtering.
3. `ix_goals_user_priority`: Composite index on `(user_id, priority)` for priority-based triage.
4. `ix_goal_milestones_goal_id`: Fast lookup and joins for goal checkpoint lists.
5. `ix_goal_milestones_created_at`: Chronological ordering.

---

## 3. Migration Records

- Initial Creation: `fd75471a4d7c_add_complete_database_architecture_.py` (STEP 02)
- Step 10 Enhancement: `e3bb8a0112fa_add_goal_priority_and_milestone_description.py`
  - Added `goals.priority` (`VARCHAR(20) NOT NULL DEFAULT 'medium'`)
  - Added index `ix_goals_user_priority`
  - Added `goal_milestones.description` (`TEXT NULL`)
- Applied and verified on PostgreSQL at head `e3bb8a0112fa (head)`.

