# LifeOS – AI Prompt Versioning REST API Reference (Step 13.5: Phase 4)

All endpoints require standard Bearer JWT authorization for a user account possessing the `admin` role (`role = 'admin'`). Non-admin requests receive HTTP 403 Forbidden.

All responses use the standard LifeOS envelope (`{"success": true, "data": {...}, "message": "..."}`).

---

## 1. Create Prompt Version

Creates a new immutable prompt version.

- **Endpoint**: `POST /api/v1/ai/prompts`
- **Authorization**: `Bearer <admin_jwt>`
- **Status Codes**: `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `422 Unprocessable Entity`

### Request Body
```json
{
  "version_tag": "v1.1.0-structured",
  "prompt_template": "You are LifeOS, a personal intelligent operating system assistant.\n\nCORE GUIDELINES:\n1. Base answers on provided context.\n2. Keep answers concise and structured.\n\n{context_block}\n\n{memory_block}\n",
  "change_summary": "Enforce concise markdown formatting for morning brief answers",
  "activate_immediately": false
}
```

#### Fields
- `version_tag` (*required*, string, 1–50 chars): Unique semantic version identifier.
- `prompt_template` (*required*, string, 10–20000 chars): Template containing `{context_block}`.
- `change_summary` (*required*, string, 1–255 chars): Rationale for change.
- `activate_immediately` (*optional*, boolean, default `false`): If `true`, promotes to active upon creation.

### Response `201 Created`
```json
{
  "success": true,
  "message": "Prompt version 'v1.1.0-structured' created successfully",
  "data": {
    "prompt": {
      "id": "7fa84b91-12f3-4a81-9b60-c4819df51112",
      "version_tag": "v1.1.0-structured",
      "prompt_template": "You are LifeOS...",
      "change_summary": "Enforce concise markdown formatting for morning brief answers",
      "created_by": "00000000-0000-0000-0000-000000000001",
      "is_active": false,
      "activated_at": null,
      "created_at": "2026-11-08T13:30:00.000000Z",
      "updated_at": "2026-11-08T13:30:00.000000Z"
    }
  }
}
```

---

## 2. List Prompt Versions

Retrieves paginated prompt versions ordered by creation timestamp descending.

- **Endpoint**: `GET /api/v1/ai/prompts`
- **Query Parameters**:
  - `limit` (*optional*, integer, default `20`, max `100`)
  - `offset` (*optional*, integer, default `0`)
- **Status Codes**: `200 OK`, `401 Unauthorized`, `403 Forbidden`

### Response `200 OK`
```json
{
  "success": true,
  "message": "Prompt versions retrieved successfully",
  "data": {
    "prompts": [
      {
        "id": "7fa84b91-12f3-4a81-9b60-c4819df51112",
        "version_tag": "v1.1.0-structured",
        "prompt_template": "You are LifeOS...",
        "change_summary": "Enforce concise markdown formatting",
        "created_by": "00000000-0000-0000-0000-000000000001",
        "is_active": true,
        "activated_at": "2026-11-08T13:35:00.000000Z",
        "created_at": "2026-11-08T13:30:00.000000Z",
        "updated_at": "2026-11-08T13:35:00.000000Z"
      }
    ],
    "total": 2,
    "limit": 20,
    "offset": 0
  }
}
```

---

## 3. Get Active Prompt Version

Retrieves the single currently active prompt version that governs ongoing AI interactions. If no active version exists, automatically initializes the baseline prompt.

- **Endpoint**: `GET /api/v1/ai/prompts/active`
- **Status Codes**: `200 OK`, `401 Unauthorized`, `403 Forbidden`

---

## 4. Get Prompt Version by ID

Retrieves details of a specific prompt version.

- **Endpoint**: `GET /api/v1/ai/prompts/<prompt_id>`
- **Status Codes**: `200 OK`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`

---

## 5. Activate Prompt Version / Rollback

Promotes a prompt version to active and deactivates any predecessor within a single transaction. Can be used to deploy a new version or roll back to an older version.

- **Endpoint**: `POST /api/v1/ai/prompts/<prompt_id>/activate`
- **Status Codes**: `200 OK`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`

### Response `200 OK`
```json
{
  "success": true,
  "message": "Prompt version 'v1.0.0-baseline' activated successfully",
  "data": {
    "prompt": {
      "id": "c138f6d1-419b-4395-8e2b-f4581109a251",
      "version_tag": "v1.0.0-baseline",
      "is_active": true,
      "activated_at": "2026-11-08T13:40:00.000000Z"
    }
  }
}
```

