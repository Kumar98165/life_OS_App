# LifeOS — STEP 10: AI Model Version Management & Rollback Architecture

## 1. Executive Summary

STEP 10 establishes a secure, robust model version management registry and rollback system for LifeOS.

Key features:
- **Comprehensive Registry**: Tracks base models, version tags, training runs (STEP 8), evaluation scores (STEP 9), artifact SHA-256 checksums, and active runtime flags.
- **Strict Lifecycle Progression**: Validates transitions across `registered` $\to$ `candidate` $\to$ `evaluated` $\to$ `approved` $\to$ `active` $\to$ `archived` / `rejected`.
- **Safe Activation**: Only models with verified benchmark scores ($\ge 0.65$) and verified Ollama runtime availability can be activated. Previous active model states are preserved atomically.
- **Instant Rollback**: Enables rapid restoration of previously approved model versions with mandatory audit logging and rollback reasons.
- **Dynamic Runtime Provider**: Centralized `AIRuntimeConfig` dynamically resolves the active model from PostgreSQL while preserving fallback to `qwen2.5:3b`.
- **Administrative Security**: Role-based access control enforces `admin` authorization for registration, approval, activation, and rollback actions.

---

## 2. Database Models & Schema Migration

Implemented in `backend/app/models/ai.py` and Alembic migration `0eda9830f2db`:

### 2.1 `AIModelVersion` (`ai_model_versions`)
- `id`: UUID primary key.
- `model_tag`: Unique Ollama identifier (e.g. `qwen2.5:3b`, `qwen2.5:3b-lifeos:v1`).
- `base_model`: Base Hugging Face model (`Qwen/Qwen2.5-3B-Instruct`).
- `version_tag`: Semantic version tag (`v1.0.0`).
- `training_run_id`: Provenance linking to STEP 8 run artifacts.
- `dataset_version`: Provenance linking to STEP 7 dataset version snapshot.
- `artifact_checksum`: 64-character SHA-256 hexadecimal string of adapter or GGUF weights.
- `status`: Lifecycle status (`registered`, `candidate`, `evaluated`, `approved`, `active`, `rejected`, `archived`).
- `is_active`: Boolean flag indicating active runtime model.
- `evaluation_score`: Overall benchmark score from STEP 9.
- `evaluation_report_path`: Path to detailed JSON benchmark report.
- `approved_by` / `approved_at`: Audit timestamps and user foreign keys.
- `activated_by` / `activated_at`: Activation audit metadata.

### 2.2 `AIModelRollbackLog` (`ai_model_rollback_logs`)
- `from_model_id`: Previous active model foreign key.
- `to_model_id`: Newly activated / restored model foreign key.
- `action`: `activation` or `rollback`.
- `reason`: Detailed mandatory rationale text.
- `executed_by`: Administrator user ID.
- `created_at`: UTC timestamp.

---

## 3. Model Lifecycle & State Machine

```
                   +------------+
                   | registered |
                   +-----+------+
                         |
           +-------------+-------------+
           |                           |
           v                           v
     +-----------+               +-----------+
     | candidate |               | evaluated |
     +-----+-----+               +-----+-----+
           |                           |
           v                           v
     +-----------+               +-----------+
     | evaluated |               | approved  | (score >= 0.65)
     +-----+-----+               +-----+-----+
           |                           |
           v                           v
     +-----------+               +-----------+
     | approved  |               |  active   | (verified in Ollama)
     +-----+-----+               +-----+-----+
           |                           |
           |                           v
           |                     +-----------+
           +-------------------->|  rollback | (restores previous approved)
                                 +-----------+
```

---

## 4. REST API Reference (`/api/v1/ai/models`)

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/ai/models` | Authenticated | List registered models with pagination and status filtering. |
| `GET` | `/api/v1/ai/models/active` | Authenticated | Get currently active runtime model. |
| `POST` | `/api/v1/ai/models` | Admin only | Register a new AI model version. |
| `POST` | `/api/v1/ai/models/<id>/evaluate` | Admin only | Attach STEP 9 benchmark evaluation report and score. |
| `POST` | `/api/v1/ai/models/<id>/approve` | Admin only | Approve an evaluated model for activation. |
| `POST` | `/api/v1/ai/models/<id>/activate` | Admin only | Atomically activate an approved model version. |
| `POST` | `/api/v1/ai/models/rollback` | Admin only | Roll back to a previous approved model version. |
| `GET` | `/api/v1/ai/models/audit-logs` | Authenticated | View activation and rollback audit history. |

---

## 5. Security & Safety Invariants

1. **Active Model Safety**: The current production model `qwen2.5:3b` remains active until an administrator explicitly approves and activates a replacement.
2. **Availability Pre-Check**: Activation requires verification via Ollama's `/api/tags` API. Unavailable or missing models cannot be activated.
3. **Immutability of History**: Models are never automatically deleted upon deactivation; their state transitions to `approved` and rollback logs are preserved indefinitely.
4. **Zero Weight Mutation**: Model management operates purely on metadata, configuration, and Ollama tags. Model weights are never modified.

---

## 6. Verification & Test Evidence

- **New Test Suite**: `backend/tests/test_ai_model_version.py` (10 tests, **100% pass rate**).
  - Model initialization, semantic version validation, checksum validation, duplicate suppression.
  - Evaluation threshold enforcement (rejection if score $< 0.65$).
  - Approval workflow and role-based access control.
  - Activation, atomic transition, and rollback lifecycle.
  - Missing Ollama model rejection.
  - Full REST API endpoint testing with JWT authentication.
- **Combined Backend AI Tests**: 46 passed in 20.06s across all 4 AI modules (Model Version, Evaluation, Training, Dataset).
- **Mobile Regression**: `npm --prefix mobile test` (158 passed in 6.64s).
- **TypeScript Verification**: `npm --prefix mobile run typecheck` (0 errors).
