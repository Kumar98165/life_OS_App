# LifeOS – Database Architecture

## 1. Overview
LifeOS leverages **PostgreSQL 18** as its relational database. The schema is normalized (3NF), enforces strict referential integrity with foreign keys, and indexes frequently queried and filtered columns across all 14 personal productivity domains.

Detailed companion references:
- **[DATABASE_ER_DIAGRAM.md](file:///c:/Users/NexviTech/Desktop/LifePs/docs/DATABASE_ER_DIAGRAM.md)**: Full visual Mermaid ER model.
- **[DATABASE_SCHEMA_REFERENCE.md](file:///c:/Users/NexviTech/Desktop/LifePs/docs/DATABASE_SCHEMA_REFERENCE.md)**: Exhaustive table, column, and constraint specifications.

## 2. Core Design Principles
1. **Primary Keys**: 36-character UUID strings (`uuid.uuid4`) across all tables to avoid sequential ID enumeration attacks and facilitate distributed operations.
2. **Timestamps**: All tables implement `created_at` and `updated_at` storing timezone-aware UTC timestamps (`DateTime(timezone=True)`).
3. **User Isolation**: All domain entities contain a non-nullable `user_id` foreign key with `ON DELETE CASCADE`, ensuring data ownership boundaries are strictly maintained.
4. **Indexing Strategy**: Indexes are created on foreign keys (`user_id`), unique attributes (`email`), status columns (`status`), and date/time ranges (`created_at`, `due_date`, `scheduled_for`).
5. **Precision Arithmetic**: Monetary fields strictly use `NUMERIC(14, 2)` to eliminate IEEE floating-point imprecision.

## 3. Database Modules Summary
1. **User Management**: `users` (credentials, profile, status)
2. **Authentication & Tokens**: `refresh_tokens` (JWT rotation, JTI tracking)
3. **User Preferences**: `user_preferences` (theme, notifications, timezone, AI persona)
4. **Tasks & Categories**: `task_categories`, `tasks` (priorities, due dates, statuses)
5. **Goals & Milestones**: `goals`, `goal_milestones` (OKRs, progress metrics)
6. **Habits & Logs**: `habits`, `habit_logs` (daily/weekly streaks, completion records)
7. **Daily Planner**: `planner_blocks` (time-blocking schedule, focus sessions)
8. **Notes & Knowledge**: `notes`, `note_tags`, `note_tag_association` (markdown notes, tag taxonomy)
9. **AI Dialogue**: `ai_conversations`, `ai_messages` (local Ollama chats, token counts)
10. **AI Memory**: `ai_memories` (context facts, user preferences, embedding vectors)
11. **Finance Accounts & Transactions**: `financial_accounts`, `financial_transactions`
12. **Financial Categories**: `financial_categories` (income/expense classifications, budgets)
13. **Notifications**: `notifications` (reminders, scheduled alerts, read tracking)
14. **Activity Logs**: `activity_logs` (security audit trails, entity mutation logs)

## 4. Migration Protocol (Alembic)
1. Schema changes are never applied directly to PostgreSQL.
2. Changes are introduced into declarative models in `backend/app/models/`.
3. Migrations are generated via:
   ```bash
   flask db migrate -m "Descriptive migration summary"
   ```
4. Migrations are applied via:
   ```bash
   flask db upgrade
   ```
5. Downgrade routines are verified before deployment.
