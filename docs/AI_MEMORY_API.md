# LifeOS - AI Memory REST API Reference

Base URL: `/api/v1/ai/memories`  
Authentication: Bearer JWT Token (`Authorization: Bearer <access_token>`)

---

## 1. Endpoints

### 1.1 List Confirmed Memories
- **Method**: `GET /api/v1/ai/memories`
- **Query Parameters**:
  - `category` (optional): Filter by `preference`, `personal_context`, `goal_decision`, `routine_pattern`, `fact`
  - `search` (optional): Case-insensitive keyword search
  - `limit` (default: 50, max: 100)
  - `offset` (default: 0)
- **Response `200 OK`**:
```json
{
  "status": "success",
  "message": "Memories retrieved successfully",
  "data": {
    "memories": [
      {
        "id": "uuid",
        "memory_key": "Prefers early morning deep work",
        "memory_value": "Focus sessions best between 8 AM and 10 AM.",
        "memory_type": "preference",
        "confidence": 0.95,
        "status": "confirmed",
        "created_at": "2026-11-08T01:00:00Z"
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
  }
}
```

---

### 1.2 Create Confirmed Memory
- **Method**: `POST /api/v1/ai/memories`
- **Request Body**:
```json
{
  "memory_key": "Favorite programming language",
  "memory_value": "User primarily builds in Python and TypeScript",
  "memory_type": "preference",
  "confidence": 1.0
}
```
- **Response `201 Created`**:
```json
{
  "status": "success",
  "message": "Memory created successfully",
  "data": {
    "memory": { "id": "uuid", "status": "confirmed", ... }
  }
}
```

---

### 1.3 Update Memory
- **Method**: `PATCH /api/v1/ai/memories/<id>`
- **Request Body**:
```json
{
  "memory_value": "User now specializes in Rust and TypeScript",
  "confidence": 0.9
}
```
- **Response `200 OK`**

---

### 1.4 Archive Memory
- **Method**: `POST /api/v1/ai/memories/<id>/archive`
- **Response `200 OK`** (transitions `status` to `archived`)

---

### 1.5 Delete Memory
- **Method**: `DELETE /api/v1/ai/memories/<id>`
- **Response `200 OK`** (permanently removed)

---

### 1.6 List Pending Suggestions
- **Method**: `GET /api/v1/ai/memories/pending`
- **Response `200 OK`**:
```json
{
  "status": "success",
  "message": "Pending memory suggestions retrieved successfully",
  "data": {
    "suggestions": [
      {
        "id": "uuid",
        "memory_key": "Drinks Oat Milk Matcha Latte",
        "memory_value": "Prefers oat milk in morning beverages.",
        "memory_type": "preference",
        "confidence": 0.85,
        "status": "pending",
        "source_conversation_id": "conv-uuid"
      }
    ],
    "total": 1
  }
}
```

---

### 1.7 Approve Pending Suggestion
- **Method**: `POST /api/v1/ai/memories/<id>/approve`
- **Request Body** (optional edits):
```json
{
  "memory_key": "Drinks Matcha Latte Daily",
  "memory_value": "Drinks oat milk iced matcha latte before 9 AM.",
  "memory_type": "routine_pattern"
}
```
- **Response `200 OK`** (transitions `status` to `confirmed`)

---

### 1.8 Reject Pending Suggestion
- **Method**: `POST /api/v1/ai/memories/<id>/reject`
- **Response `200 OK`** (purges candidate memory)

---

### 1.9 Get & Update Personalization Settings
- **Method**: `GET /api/v1/ai/memories/settings`
- **Method**: `PATCH /api/v1/ai/memories/settings`
- **Request Body**:
```json
{
  "ai_memory_enabled": true
}
```
- **Response `200 OK`**

