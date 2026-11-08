# LifeOS – Database Schema Reference

## 1. Core Architecture Conventions
- **RDBMS**: PostgreSQL 18
- **Primary Keys**: UUID v4 36-character alphanumeric strings (`VARCHAR(36)`).
- **Timestamps**: All timestamps stored with timezone (`TIMESTAMP WITH TIME ZONE`), default to `timezone.utc`.
- **Tenant / User Isolation**: Every root entity enforces `user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE`.
- **Monetary Storage**: Fixed-point decimal `NUMERIC(14, 2)` to eliminate floating-point drift.

---

## 2. Table Specifications

### 2.1 `users`
Root entity representing user identity, credentials, and ownership.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | Unique UUID identifier |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | Normalized user email |
| `password_hash` | VARCHAR(255) | NOT NULL | 12-round salted bcrypt hash |
| `full_name` | VARCHAR(100) | NOT NULL | Display name |
| `avatar_url` | VARCHAR(500) | NULLABLE | Profile picture URL |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Account state |
| `created_at` | TIMESTAMPTZ | NOT NULL, INDEX | Record creation UTC timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Last modification UTC timestamp |
- **Indexes**: `ix_users_email`, `ix_users_email_lower`, `ix_users_created_at`.

### 2.2 `user_preferences`
User interface settings, AI behavior adjustments, and regional localization.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | Unique UUID identifier |
| `user_id` | VARCHAR(36) | NOT NULL, UNIQUE, FK -> users.id (CASCADE) | Owner foreign key |
| `theme` | VARCHAR(20) | NOT NULL, DEFAULT 'light' | Glassmorphism UI theme |
| `timezone` | VARCHAR(50) | NOT NULL, DEFAULT 'UTC' | IANA timezone string |
| `notifications_enabled` | BOOLEAN | NOT NULL, DEFAULT TRUE | Global alert toggle |
| `ai_daily_summary` | BOOLEAN | NOT NULL, DEFAULT TRUE | Morning AI briefing toggle |
| `ai_tone` | VARCHAR(30) | NOT NULL, DEFAULT 'balanced' | Conversational persona tone |
| `currency` | VARCHAR(10) | NOT NULL, DEFAULT 'USD' | ISO currency code |
| `created_at`, `updated_at` | TIMESTAMPTZ | NOT NULL | Audit timestamps |

### 2.3 `refresh_tokens`
Long-lived JWT refresh tokens with JTI for immediate cryptographic revocation.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | Unique UUID identifier |
| `user_id` | VARCHAR(36) | NOT NULL, FK -> users.id (CASCADE) | Owner foreign key |
| `token_jti` | VARCHAR(36) | NOT NULL, UNIQUE | JWT ID claim |
| `token_hash` | VARCHAR(255) | NULLABLE | Hash of raw token string |
| `expires_at` | TIMESTAMPTZ | NOT NULL, INDEX | Expiration timestamp |
| `is_revoked` | BOOLEAN | NOT NULL, DEFAULT FALSE | Token revocation flag |
| `created_at`, `updated_at` | TIMESTAMPTZ | NOT NULL | Audit timestamps |
- **Indexes**: `ix_refresh_tokens_token_jti`, `ix_refresh_tokens_expires_at`, `ix_refresh_tokens_user_revoked`.

### 2.4 `task_categories` & `tasks`
Hierarchical task management with Eisenhower priority matrix and calendar deadlines.
#### `task_categories`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | Unique UUID identifier |
| `user_id` | VARCHAR(36) | NOT NULL, FK -> users.id (CASCADE) | Owner foreign key |
| `name` | VARCHAR(100) | NOT NULL | Category title (e.g. Work, Health) |
| `color_hex` | VARCHAR(10) | NOT NULL, DEFAULT '#6C63FF' | Category glass color |
| `icon` | VARCHAR(50) | NULLABLE | Material/Ionicons symbol |
| `created_at`, `updated_at` | TIMESTAMPTZ | NOT NULL | Audit timestamps |
- **Constraints**: UNIQUE(`user_id`, `name`).

#### `tasks`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | Unique UUID identifier |
| `user_id` | VARCHAR(36) | NOT NULL, FK -> users.id (CASCADE) | Owner foreign key |
| `category_id` | VARCHAR(36) | NULLABLE, FK -> task_categories.id (SET NULL) | Associated category |
| `title` | VARCHAR(255) | NOT NULL | Task title |
| `description` | TEXT | NULLABLE | Detailed description / checklist |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'todo' | todo, in_progress, completed, archived |
| `priority` | VARCHAR(20) | NOT NULL, DEFAULT 'medium' | low, medium, high, urgent |
| `due_date` | TIMESTAMPTZ | NULLABLE, INDEX | Target completion deadline |
| `completed_at` | TIMESTAMPTZ | NULLABLE | Actual completion timestamp |
| `is_archived` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft archive flag |
| `estimated_minutes` | INTEGER | NULLABLE | Estimated focus duration |
| `created_at`, `updated_at` | TIMESTAMPTZ | NOT NULL | Audit timestamps |
- **Indexes**: `ix_tasks_user_status`, `ix_tasks_user_due_date`, `ix_tasks_user_priority`, `ix_tasks_user_archived`.

### 2.5 `goals` & `goal_milestones`
High-level strategic objectives with milestone tracking.
- `goals`: `id`, `user_id` (FK), `title`, `description`, `target_date`, `status`, `progress_percent`, `category`.
- `goal_milestones`: `id`, `goal_id` (FK CASCADE), `title`, `target_date`, `is_completed`, `completed_at`, `sort_order`.

### 2.6 `habits` & `habit_logs`
Recurring habit building with streak calculation.
- `habits`: `id`, `user_id` (FK), `title`, `description`, `frequency`, `target_days_per_week`, `current_streak`, `longest_streak`, `color_hex`, `icon`, `is_archived`.
- `habit_logs`: `id`, `habit_id` (FK CASCADE), `log_date`, `completed`, `notes`.
  - **Constraint**: UNIQUE(`habit_id`, `log_date`).

### 2.7 `planner_blocks`
Daily time-blocking schedule.
- `planner_blocks`: `id`, `user_id` (FK), `task_id` (FK SET NULL), `title`, `start_time`, `end_time`, `block_type`, `is_completed`.
  - **Indexes**: `ix_planner_user_start`, `ix_planner_user_completed`.

### 2.8 `notes`, `note_tags` & `note_tag_association`
Personal knowledge base with tag taxonomy.
- `notes`: `id`, `user_id` (FK), `title`, `content`, `is_pinned`, `is_archived`.
- `note_tags`: `id`, `user_id` (FK), `name`, `color_hex`. UNIQUE(`user_id`, `name`).
- `note_tag_association`: Junction table (`note_id` PK, FK CASCADE, `tag_id` PK, FK CASCADE).

### 2.9 `ai_conversations` & `ai_messages`
Local LLM dialogue threads.
- `ai_conversations`: `id`, `user_id` (FK), `title`, `model_used`.
- `ai_messages`: `id`, `conversation_id` (FK CASCADE), `role`, `content`, `tool_calls`, `tokens_used`.

### 2.10 `ai_memories`
Long-term context memory retained by the local AI agent.
- `ai_memories`: `id`, `user_id` (FK), `memory_key`, `memory_value`, `memory_type`, `confidence`, `embedding`, `last_accessed_at`.

### 2.11 `financial_accounts`, `financial_categories` & `financial_transactions`
Personal wealth and expenditure management.
- `financial_accounts`: `id`, `user_id` (FK), `name`, `account_type`, `balance` (NUMERIC), `currency`, `is_active`.
- `financial_categories`: `id`, `user_id` (FK), `name`, `category_type`, `icon`, `color_hex`, `monthly_budget`. UNIQUE(`user_id`, `name`, `category_type`).
- `financial_transactions`: `id`, `user_id` (FK), `account_id` (FK CASCADE), `category_id` (FK SET NULL), `amount` (NUMERIC), `transaction_type`, `description`, `transaction_date`, `is_recurring`.

### 2.12 `notifications`
System reminders and scheduled alerts.
- `notifications`: `id`, `user_id` (FK), `title`, `body`, `notification_type`, `entity_type`, `entity_id`, `is_read`, `read_at`, `scheduled_for`.

### 2.13 `activity_logs`
Immutable audit log.
- `activity_logs`: `id`, `user_id` (FK), `action`, `entity_type`, `entity_id`, `details`, `ip_address`, `created_at`.

