# LifeOS - AI Continuous Learning & Feedback Database Architecture

## 1. Overview
This document specifies the database foundation for **STEP 13.5: AI Continuous Learning & Feedback Engine**. It introduces immutable prompt versioning, structured user feedback tracking, multidimensional response evaluation benchmarking, and privacy-preserving training sample curation.

All schemas follow 3NF normalization, utilize UUID primary keys (`VARCHAR(36)`), enforce transaction-safe constraints, and preserve local privacy boundaries.

---

## 2. Entity-Relationship Overview

```
                          +------------------------+
                          |         users          |
                          | (role: 'user'|'admin') |
                          +-----------+------------+
                                      |
         +----------------------------+----------------------------+
         | 1:1                        | 1:N                        | 1:N
         v                            v                            v
+------------------+         +------------------+        +----------------------+
| user_preferences |         | ai_conversations |        |  ai_prompt_versions  |
| (training_consent|         +--------+---------+        | (unique active index)|
+------------------+                  | 1:N              +----------+-----------+
                                      v                             | 0..1:N
                             +------------------+                   |
                             |   ai_messages    |<------------------+
                             +--------+---------+
                                      | 1:1
              +-----------------------+-----------------------+
              | 1:1                                           | 1:N
              v                                               v
     +-----------------+                             +--------------------+
     |   ai_feedback   |                             | ai_evaluation_runs |
     +--------+--------+                             +---------+----------+
              | 0..1:N                                         | 1:N
              v                                                v
+---------------------+                             +-----------------------+
| ai_training_samples |                             | ai_evaluation_metrics |
+---------------------+                             +-----------------------+
```

---

## 3. Table Definitions & Schemas

### 3.1 `ai_prompt_versions`
Registry of versioned system prompts. Historical prompt versions are immutable.

| Column | Type | Nullable | Description / Constraint |
|---|---|---|---|
| `id` | VARCHAR(36) | No | Primary Key (UUID) |
| `version_tag` | VARCHAR(50) | No | Unique version tag (e.g. `'v1.0.0-baseline'`) |
| `prompt_template` | TEXT | No | Parameterized system prompt string |
| `change_summary` | VARCHAR(255) | No | Changelog description for this version |
| `created_by` | VARCHAR(36) | Yes | FK to `users.id` (`ON DELETE SET NULL`) |
| `is_active` | BOOLEAN | No | Default `False`. Only one active prompt allowed |
| `created_at` | TIMESTAMP WITH TIME ZONE | No | UTC creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | No | UTC last update timestamp |

**Indexes & Constraints**:
- `ix_ai_prompt_versions_version_tag` on `version_tag` (UNIQUE)
- `uq_ai_prompt_versions_active` on `is_active` (UNIQUE, `WHERE is_active = true`): Enforces that at most one prompt version can be active simultaneously.

---

### 3.2 `ai_feedback`
Explicit user feedback, ratings, and corrections for specific assistant turns.

| Column | Type | Nullable | Description / Constraint |
|---|---|---|---|
| `id` | VARCHAR(36) | No | Primary Key (UUID) |
| `user_id` | VARCHAR(36) | No | FK to `users.id` (`ON DELETE CASCADE`) |
| `message_id` | VARCHAR(36) | No | FK to `ai_messages.id` (`ON DELETE CASCADE`, UNIQUE) |
| `rating` | INTEGER | No | `+1` (positive) or `-1` (negative) |
| `feedback_type` | VARCHAR(30) | No | Default `'thumbs'`. Types: `'thumbs_up'`, `'thumbs_down'`, `'correction'`, `'issue_report'` |
| `category` | VARCHAR(50) | Yes | Category tag (e.g. `'hallucination'`, `'inaccurate_schedule'`, `'unhelpful'`) |
| `comment` | TEXT | Yes | User explanation or feedback comment |
| `suggested_response`| TEXT | Yes | User-provided ideal response for fine-tuning |
| `created_at` | TIMESTAMP WITH TIME ZONE | No | UTC timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | No | UTC timestamp |

**Indexes & Constraints**:
- `ix_ai_feedback_message_id` on `message_id` (UNIQUE): Enforces exactly one feedback per message.
- `ix_ai_feedback_user_created` on `(user_id, created_at)`: Optimizes user history queries.

---

### 3.3 `ai_evaluation_runs`
Parent container for an automated benchmark evaluation run against an assistant response.

| Column | Type | Nullable | Description / Constraint |
|---|---|---|---|
| `id` | VARCHAR(36) | No | Primary Key (UUID) |
| `message_id` | VARCHAR(36) | No | FK to `ai_messages.id` (`ON DELETE CASCADE`) |
| `prompt_version_id` | VARCHAR(36) | Yes | FK to `ai_prompt_versions.id` (`ON DELETE SET NULL`) |
| `model_name` | VARCHAR(50) | No | Default `'qwen2.5:3b'` |
| `passed` | BOOLEAN | No | Overall binary benchmark pass/fail |
| `overall_score` | FLOAT | Yes | Aggregate score normalized 0.0 to 1.0 |
| `notes` | TEXT | Yes | High-level evaluation summary notes |
| `created_at` | TIMESTAMP WITH TIME ZONE | No | UTC timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | No | UTC timestamp |

**Indexes & Constraints**:
- `ix_ai_eval_runs_msg_created` on `(message_id, created_at)`
- `ix_ai_evaluation_runs_prompt_version_id` on `prompt_version_id`

---

### 3.4 `ai_evaluation_metrics`
Detailed multidimensional quality metrics belonging to an evaluation run.

| Column | Type | Nullable | Description / Constraint |
|---|---|---|---|
| `id` | VARCHAR(36) | No | Primary Key (UUID) |
| `run_id` | VARCHAR(36) | No | FK to `ai_evaluation_runs.id` (`ON DELETE CASCADE`) |
| `metric_name` | VARCHAR(50) | No | Dimension evaluated: `'relevance'`, `'factual_consistency'`, `'instruction_following'`, `'completeness'`, `'clarity'`, `'hallucination_risk'`, `'personalization_quality'` |
| `score` | FLOAT | No | Score 0.0 to 1.0 |
| `passed` | BOOLEAN | No | Pass flag for this individual dimension |
| `reasoning` | TEXT | Yes | Detailed explanation from the local evaluator |
| `created_at` | TIMESTAMP WITH TIME ZONE | No | UTC timestamp |

**Indexes & Constraints**:
- `ix_ai_eval_metrics_run_name` on `(run_id, metric_name)`

---

### 3.5 `ai_training_samples`
Curated instruction-tuning and preference dataset pairs (SFT & DPO).

| Column | Type | Nullable | Description / Constraint |
|---|---|---|---|
| `id` | VARCHAR(36) | No | Primary Key (UUID) |
| `user_id` | VARCHAR(36) | No | FK to `users.id` (`ON DELETE CASCADE`) |
| `source_feedback_id`| VARCHAR(36) | Yes | FK to `ai_feedback.id` (`ON DELETE SET NULL`) |
| `source_message_id` | VARCHAR(36) | Yes | FK to `ai_messages.id` (`ON DELETE SET NULL`) |
| `prompt_input` | TEXT | No | Sanitized user instruction |
| `chosen_response` | TEXT | No | High-quality or corrected response |
| `rejected_response` | TEXT | Yes | Flawed response for DPO preference pairing |
| `dataset_type` | VARCHAR(20) | No | Default `'sft'`. Values: `'sft'`, `'dpo'` |
| `consent_status` | VARCHAR(20) | No | Default `'pending'`. Values: `'pending'`, `'granted'`, `'revoked'` |
| `review_status` | VARCHAR(20) | No | Default `'pending'`. Values: `'pending'`, `'approved'`, `'rejected'` |
| `quality_score` | FLOAT | No | Default `1.0` |
| `created_at` | TIMESTAMP WITH TIME ZONE | No | UTC timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | No | UTC timestamp |

**Indexes & Constraints**:
- `ix_ai_training_samples_user_review` on `(user_id, review_status)`
- `ix_ai_training_samples_consent_review` on `(consent_status, review_status)`

---

### 3.6 Schema Extensions to Existing Tables

#### `users` Table
- Added `role`: `VARCHAR(20)`, NOT NULL, `server_default='user'`. Values: `'user'`, `'admin'`.
- All pre-existing users defaulted to `'user'`.

#### `user_preferences` Table
- Added `ai_training_consent`: `BOOLEAN`, NOT NULL, `server_default=sa.false()`.
- Default is strictly `False` (Opt-in required). Existing `ai_memory_enabled` is unchanged.

#### `ai_messages` Table
- Added `prompt_version_id`: `VARCHAR(36)`, NULLABLE, FK to `ai_prompt_versions.id` (`ON DELETE SET NULL`).
- Added `latency_ms`: `INTEGER`, NULLABLE.
- Existing `tokens_used` column is preserved and reused.

---

## 4. Foreign Key & Deletion Policies

1. **Cascade Deletion (`ON DELETE CASCADE`)**:
   - `ai_feedback.message_id -> ai_messages.id`: If a message is deleted, its feedback is removed immediately.
   - `ai_evaluation_runs.message_id -> ai_messages.id`: If a message is deleted, its evaluation run and child metrics are pruned.
   - `ai_evaluation_metrics.run_id -> ai_evaluation_runs.id`: Deleting a run deletes all associated metric breakdowns.
   - `ai_feedback.user_id -> users.id` & `ai_training_samples.user_id -> users.id`: User account deletion deletes all personal learning data.
2. **Set Null Preservation (`ON DELETE SET NULL`)**:
   - `ai_messages.prompt_version_id -> ai_prompt_versions.id`: Messages retain their text even if an experimental prompt version is deleted.
   - `ai_training_samples.source_feedback_id -> ai_feedback.id`: Training sample pairs remain historically valid if a user deletes their feedback, provided consent remains granted.

---

## 5. Migration History & Revision Chain

- **Migration Script**: `backend/migrations/versions/05e04b80ec43_add_ai_learning_feedback_and_evaluations.py`
- **Revision ID**: `05e04b80ec43`
- **Parent Revision**: `87ec6f9980ac`
- **Database Status**: Applied to PostgreSQL `lifeos_db` on `localhost:5432`. Head verified at `05e04b80ec43`.

---

## 6. Known Database Limitations

1. **Pre-Exported Dataset Files**:
   Deleting records from `ai_training_samples` or withdrawing consent removes rows from PostgreSQL. However, if an administrator has previously exported a JSONL file to local disk or external storage, database deletion cannot retroactively remove offline files. File export pipelines must verify live consent status at runtime.
2. **PostgreSQL vs SQLite Partial Index Syntax**:
   The partial unique index `uq_ai_prompt_versions_active` uses SQLAlchemy dialect arguments (`postgresql_where` and `sqlite_where`). While supported in SQLite 3.8+ for tests, complex boolean expressions in partial indexes should always be verified across database engines.
3. **Admin Provisioning**:
   The `users.role` field defaults to `'user'`. Public registration APIs must never expose `role` in request payloads. Admin accounts must be provisioned via explicit server-side scripts or migrations.

