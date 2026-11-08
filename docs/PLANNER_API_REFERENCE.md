# LifeOS – Daily Planner API Reference

Base Endpoint Prefix: `/api/v1/planner`  
Authentication: `Authorization: Bearer <access_token>`

---

## 1. Create Planner Block
`POST /api/v1/planner/blocks`

### Request Body
```json
{
  "title": "Deep Work - Architecture",
  "description": "Design modular planner and calendar system",
  "start_time": "2026-11-08T09:00:00Z",
  "end_time": "2026-11-08T10:30:00Z",
  "block_type": "work",
  "status": "scheduled",
  "task_id": "optional-uuid-here",
  "color_hex": "#6C63FF"
}
```

### Success Response (`201 Created`)
```json
{
  "status": "success",
  "message": "Planner block scheduled successfully",
  "data": {
    "block": {
      "id": "7b0d5c41-8e9a-41d3-a442-132d0ff12a91",
      "user_id": "c1f7a0b3-90d1-419b-a012-3b028f8d68f1",
      "task_id": "optional-uuid-here",
      "task": null,
      "title": "Deep Work - Architecture",
      "description": "Design modular planner and calendar system",
      "start_time": "2026-11-08T09:00:00+00:00",
      "end_time": "2026-11-08T10:30:00+00:00",
      "block_type": "work",
      "status": "scheduled",
      "color_hex": "#6C63FF",
      "is_completed": false,
      "created_at": "2026-11-08T03:00:00+00:00",
      "updated_at": "2026-11-08T03:00:00+00:00"
    }
  }
}
```

### Error Responses
- `400 Bad Request`: Linked task does not belong to user, or invalid time ordering.
- `409 Conflict`: Overlapping block exists for the same user.
- `422 Unprocessable Entity`: Schema validation errors (title blank, invalid ISO date).

---

## 2. List Planner Blocks
`GET /api/v1/planner/blocks`

### Query Parameters
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `start_date` | ISO 8601 string | Optional | Filter blocks overlapping after this time |
| `end_date` | ISO 8601 string | Optional | Filter blocks overlapping before this time |
| `status` | string | Optional | `scheduled`, `completed`, `cancelled`, `skipped` |
| `block_type` | string | Optional | `work`, `task`, `personal`, `learning`, etc. |
| `task_id` | UUID | Optional | Filter blocks linked to a specific task |
| `page` | integer | Optional | Default `1` |
| `per_page` | integer | Optional | Default `50` |

### Success Response (`200 OK`)
```json
{
  "status": "success",
  "message": "Planner blocks retrieved successfully",
  "data": {
    "blocks": [...]
  },
  "meta": {
    "page": 1,
    "per_page": 50,
    "total": 3,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

---

## 3. Get Planner Block Details
`GET /api/v1/planner/blocks/{block_id}`

### Success Response (`200 OK`)
```json
{
  "status": "success",
  "message": "Planner block retrieved successfully",
  "data": {
    "block": { ... }
  }
}
```

---

## 4. Update Planner Block
`PATCH /api/v1/planner/blocks/{block_id}`

### Request Body (Partial)
```json
{
  "title": "Extended Architecture Review",
  "end_time": "2026-11-08T11:00:00Z"
}
```

---

## 5. Update Block Status
`PATCH /api/v1/planner/blocks/{block_id}/status`

### Request Body
```json
{
  "status": "completed"
}
```

---

## 6. Delete Planner Block
`DELETE /api/v1/planner/blocks/{block_id}`

### Success Response (`200 OK`)
```json
{
  "status": "success",
  "message": "Planner block deleted successfully",
  "data": {}
}
```

---

## 7. Daily Planner Summary
`GET /api/v1/planner/summary/daily?date=YYYY-MM-DD&tz_offset=5.5`

### Success Response (`200 OK`)
```json
{
  "status": "success",
  "message": "Daily planner summary retrieved successfully",
  "data": {
    "date": "2026-11-08",
    "total_blocks": 4,
    "completed_blocks": 2,
    "scheduled_blocks": 2,
    "cancelled_blocks": 0,
    "skipped_blocks": 0,
    "total_scheduled_minutes": 210,
    "completion_rate": 50.0,
    "next_upcoming_block": { ... },
    "blocks": [ ... ]
  }
}
```

