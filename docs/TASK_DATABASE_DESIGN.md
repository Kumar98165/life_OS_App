# LifeOS Task Database Design

## 1. Schema & Relational Structure

The Task Management module uses PostgreSQL 3NF normalized tables defined in STEP 02:

```mermaid
erDiagram
    users ||--o{ task_categories : "defines"
    users ||--o{ tasks : "owns"
    task_categories ||--o{ tasks : "categorizes"

    tasks {
        uuid id PK
        uuid user_id FK "ON DELETE CASCADE"
        uuid category_id FK "ON DELETE SET NULL"
        varchar title "NOT NULL, max 255"
        text description "NULL"
        varchar status "NOT NULL, default 'todo'"
        varchar priority "NOT NULL, default 'medium'"
        timestamptz due_date "NULL, indexed"
        timestamptz completed_at "NULL"
        boolean is_archived "NOT NULL, default false"
        int estimated_minutes "NULL"
        timestamptz created_at "NOT NULL, default now()"
        timestamptz updated_at "NOT NULL, default now()"
    }

    task_categories {
        uuid id PK
        uuid user_id FK "ON DELETE CASCADE"
        varchar name "NOT NULL, max 100"
        varchar color_hex "NOT NULL, default '#6C63FF'"
        varchar icon "NULL"
        timestamptz created_at "NOT NULL, default now()"
        timestamptz updated_at "NOT NULL, default now()"
    }
```

---

## 2. Indexes & Performance Optimization

| Table | Index Name | Columns | Pattern / Purpose |
| :--- | :--- | :--- | :--- |
| `tasks` | `ix_tasks_user_status` | `(user_id, status)` | Fast dashboard & list status filtering |
| `tasks` | `ix_tasks_user_due_date` | `(user_id, due_date)` | Daily overview & "today" filtering queries |
| `tasks` | `ix_tasks_user_priority` | `(user_id, priority)` | Priority matrix sorting |
| `tasks` | `ix_tasks_user_archived` | `(user_id, is_archived)` | Active task segregation |
| `task_categories` | `uq_task_category_user_name` | `(user_id, name)` UNIQUE | Prevents duplicate category names per user |

---

## 3. Foreign Key Deletion Semantics

- **User Deletion**: `ON DELETE CASCADE`. If a user account is deleted, all their tasks and categories are purged automatically.
- **Category Deletion**: `ON DELETE SET NULL`. If a category is deleted, associated tasks retain their data and have their `category_id` set to `NULL`.

