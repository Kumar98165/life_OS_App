# LifeOS – Immutable AI Prompt Version Management (Step 13.5: Phase 4)

## 1. Architectural Philosophy

In production-grade AI systems, prompt templates are treated as immutable executable code artifacts rather than mutable configuration strings. 

When users chat with the LifeOS Assistant, every generated assistant turn must be deterministically reproducible and auditable. If an administrator alters system prompt directives to tune tone, accuracy, or formatting, past interactions must retain exact historical attribution to the specific prompt version that governed their generation.

```
+---------------------------------------------------------------------------------------+
|                                    Administrator                                      |
+---------------------------------------------------------------------------------------+
        |                                                       |
        v (POST /ai/prompts)                                    v (POST /ai/prompts/<id>/activate)
+---------------------------------------+       +-----------------------------------------------+
|         AIPromptVersion (New)         |       |              AIPromptRepository               |
|  - version_tag (unique, immutable)    |       |  - SELECT ... FOR UPDATE (Row Locking)        |
|  - prompt_template (immutable)        | ----> |  - UPDATE prior active -> is_active = False   |
|  - is_active = False                  |       |  - UPDATE target version -> is_active = True  |
+---------------------------------------+       |  - updated activated_at = NOW()               |
                                                +-----------------------------------------------+
                                                                        |
                                                                        v
+---------------------------------------------------------------------------------------+
|                              LifeOS Chat Generation Turn                              |
+---------------------------------------------------------------------------------------+
        |
        v
+---------------------------------------+       +-----------------------------------------------+
|           AIPromptService             | ----> |            LangGraph Workflow State           |
|  - get_active_prompt_or_initialize()  |       |  - prompt_version_id frozen in State          |
|  - Active prompt resolved once        |       |  - prompt_template injected into Node         |
+---------------------------------------+       +-----------------------------------------------+
                                                                        |
                                                                        v
                                                +-----------------------------------------------+
                                                |                   AIMessage                   |
                                                |  - prompt_version_id = frozen_id              |
                                                |  - latency_ms = measured_ms                   |
                                                |  - Immutable historical record                |
                                                +-----------------------------------------------+
```

---

## 2. Immutability & Safety Rules

1. **Write-Once Immutability**:
   Once an `AIPromptVersion` is persisted, its `prompt_template` and `version_tag` can never be edited or overwritten. Any refinement or adjustment requires publishing a new version tag (e.g. `v1.2.0-structured`).
2. **Deterministic Attribution Preservation**:
   Every `AIMessage` persisted with `role = 'assistant'` stores the exact foreign key `prompt_version_id` corresponding to the active prompt at the moment generation began.
3. **No Cascading Deletion of Historical Versions**:
   Any attempt to delete a prompt version that is referenced by existing rows in `ai_messages` is blocked at both the service and database levels (`BadRequestException`). Deletion is restricted to unreferenced, inactive drafts.
4. **Concurrency-Safe Single-Active Invariant**:
   Enforced at the PostgreSQL engine level via a partial unique index:
   ```sql
   CREATE UNIQUE INDEX uq_ai_prompt_versions_active 
   ON ai_prompt_versions (is_active) 
   WHERE is_active = TRUE;
   ```
   During activation or rollback, the transaction locks active rows (`with_for_update()`), deactivates predecessors, and promotes the target version atomically.
5. **Safe Baseline Fallback**:
   If a new deployment has zero prompt versions registered in the database, `get_active_prompt_or_initialize()` automatically creates and activates `v1.0.0-baseline` containing the validated default system prompt.

---

## 3. Database Schema Specification

### `ai_prompt_versions`
| Column | Type | Nullable | Description |
| :--- | :--- | :---: | :--- |
| `id` | `VARCHAR(36)` | No | Primary Key UUID |
| `version_tag` | `VARCHAR(50)` | No | Unique semantic tag (e.g., `v1.0.0-baseline`, `v1.1.0`) |
| `prompt_template` | `TEXT` | No | System prompt template containing `{context_block}` and `{memory_block}` |
| `change_summary` | `VARCHAR(255)` | No | Documented reason and rationale for prompt adjustments |
| `created_by` | `VARCHAR(36)` | Yes | Foreign Key $\rightarrow$ `users.id` (ON DELETE SET NULL) |
| `is_active` | `BOOLEAN` | No | Active deployment flag (Default: `False`) |
| `activated_at` | `TIMESTAMP WITH TIME ZONE` | Yes | Timestamp of most recent promotion to active |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | No | Record creation timestamp |
| `updated_at` | `TIMESTAMP WITH TIME ZONE` | No | Record update timestamp |

### Indexes
- `uq_ai_prompt_versions_active` (`is_active`) `UNIQUE WHERE is_active = TRUE`
- `ix_ai_prompt_versions_version_tag` (`version_tag`) `UNIQUE`
- `ix_ai_prompt_versions_created_at` (`created_at`)

---

## 4. Administrative Role & Provisioning

Prompt version management is strictly restricted to administrative accounts.

- **Endpoint Protection**: Decorated with `@admin_required()` in [`app.core.security`](file:///C:/Users/NexviTech/Desktop/LifePs/backend/app/core/security.py).
- **Normal User Restriction**: Non-admin users (`role = 'user'`) receive HTTP 403 Forbidden on all prompt management endpoints.
- **Zero Public Self-Promotion**: No public API allows modifying `users.role`.
- **Out-of-Band Admin Provisioning**: Administrators are provisioned via secure server CLI:
  ```bash
  flask auth make-admin user@example.com
  flask auth revoke-admin user@example.com
  ```

