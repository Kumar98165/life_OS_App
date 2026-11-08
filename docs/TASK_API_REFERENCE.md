# LifeOS Task Management API Reference

All routes require authentication via `Authorization: Bearer <access_token>`.

Base URL prefix: `/api/v1/tasks`

---

## 1. Endpoints Summary

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/tasks` | Create a new task | 201 Created |
| `GET` | `/api/v1/tasks` | List tasks with filters & pagination | 200 OK |
| `GET` | `/api/v1/tasks/categories` | List user task categories (auto-seeded) | 200 OK |
| `POST` | `/api/v1/tasks/categories` | Create custom task category | 201 Created |
| `GET` | `/api/v1/tasks/{id}` | Get task details | 200 OK |
| `PATCH` | `/api/v1/tasks/{id}` | Update task attributes | 200 OK |
| `PATCH` | `/api/v1/tasks/{id}/complete` | Toggle task completion status | 200 OK |
| `DELETE` | `/api/v1/tasks/{id}` | Delete task permanently | 200 OK |

---

## 2. Request / Response Contracts

### `POST /api/v1/tasks`
**Request Body**:
```json
{
  "title": "Complete System Architecture",
  "description": "Design modular layered architecture",
  "category_id": "optional-uuid",
  "priority": "high",
  "status": "pending",
  "due_date": "2026-11-08T18:00:00Z",
  "estimated_minutes": 60
}
```
**Response (201 Created)**:
```json
{
  "success": true,
  "status": "success",
  "message": "Task created successfully",
  "data": {
    "task": {
      "id": "e4b52b57-61c0-4251-912f-2d7c5ee15d9a",
      "user_id": "d0c8d10b-80df-4f05-b040-362a2752179b",
      "category_id": null,
      "category": null,
      "title": "Complete System Architecture",
      "description": "Design modular layered architecture",
      "status": "pending",
      "priority": "high",
      "due_date": "2026-11-08T18:00:00+00:00",
      "completed_at": null,
      "is_archived": false,
      "estimated_minutes": 60,
      "created_at": "2026-11-07T18:40:00+00:00",
      "updated_at": "2026-11-07T18:40:00+00:00"
    }
  }
}
```

---

### `GET /api/v1/tasks`
**Query Parameters**:
- `status`: `'pending'`, `'in_progress'`, `'completed'`, `'archived'`
- `priority`: `'low'`, `'medium'`, `'high'`, `'urgent'`
- `category_id`: category UUID
- `search`: case-insensitive substring search across title and description
- `due_date`: `'today'`, `'overdue'`, `'upcoming'`
- `sort_by`: `'created_at'`, `'due_date'`, `'priority'` (default: `'created_at'`)
- `sort_order`: `'asc'`, `'desc'` (default: `'desc'`)
- `page`: integer (default: 1)
- `per_page`: integer (default: 20, max: 100)

**Response (200 OK)**:
```json
{
  "success": true,
  "status": "success",
  "message": "Tasks retrieved successfully",
  "data": {
    "tasks": [ ... ]
  },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 42,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

---

### `PATCH /api/v1/tasks/{id}/complete`
Toggles status between `'completed'` and `'pending'`, automatically managing `completed_at` timestamps in UTC.

**Response (200 OK)**:
```json
{
  "success": true,
  "status": "success",
  "message": "Task completion state updated successfully",
  "data": {
    "task": {
      "id": "e4b52b57-...",
      "status": "completed",
      "completed_at": "2026-11-07T18:42:00+00:00"
    }
  }
}
```

