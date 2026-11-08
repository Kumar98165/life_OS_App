# LifeOS – Goals & Milestones API Reference

Base Endpoint Prefix: `/api/v1/goals`  
Authentication: `Authorization: Bearer <access_token>`

---

## 1. Goal Endpoints

### Create Goal
`POST /api/v1/goals`

#### Request Body
```json
{
  "title": "Become a Principal Cloud Architect",
  "description": "Master distributed systems, AWS/GCP architecture, and team leadership",
  "priority": "high",
  "status": "in_progress",
  "category": "Career",
  "target_date": "2026-12-31T00:00:00Z"
}
```

#### Success Response (`201 Created`)
```json
{
  "status": "success",
  "message": "Goal created successfully",
  "data": {
    "goal": {
      "id": "c1f7a0b3-90d1-419b-a012-3b028f8d68f1",
      "user_id": "8e9a-41d3-a442-132d0ff12a91",
      "title": "Become a Principal Cloud Architect",
      "description": "Master distributed systems...",
      "target_date": "2026-12-31T00:00:00+00:00",
      "status": "in_progress",
      "priority": "high",
      "progress_percent": 0.0,
      "category": "Career",
      "total_milestones": 0,
      "completed_milestones": 0,
      "milestones": [],
      "created_at": "2026-11-08T03:00:00+00:00",
      "updated_at": "2026-11-08T03:00:00+00:00"
    }
  }
}
```

---

### List Goals
`GET /api/v1/goals`

#### Query Parameters
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `status` | string | Optional | `in_progress`, `completed`, `paused`, `not_started`, `cancelled` |
| `priority` | string | Optional | `low`, `medium`, `high` |
| `category` | string | Optional | Filter by category name |
| `search` | string | Optional | Substring match in title, description, or category |
| `sort_by` | string | Optional | `target_date`, `created_at`, `priority` (default `target_date`) |
| `sort_order` | string | Optional | `asc` or `desc` (default `asc`) |
| `page` | integer| Optional | Default `1` |
| `per_page` | integer| Optional | Default `20` |

---

### Get Goal Details
`GET /api/v1/goals/{goal_id}`

Returns the full Goal entity including its complete list of checkpoints (`milestones`).

---

### Update Goal
`PATCH /api/v1/goals/{goal_id}`

#### Request Body (Partial)
```json
{
  "title": "Senior Staff Architect Target",
  "status": "completed"
}
```

---

### Delete Goal
`DELETE /api/v1/goals/{goal_id}`

Deletes the goal and cascades to all associated milestones.

---

## 2. Milestone Endpoints

### Create Milestone
`POST /api/v1/goals/{goal_id}/milestones`

#### Request Body
```json
{
  "title": "Pass AWS Solutions Architect Exam",
  "description": "Score at least 850/1000",
  "target_date": "2026-11-30T00:00:00Z",
  "sort_order": 1
}
```

#### Success Response (`201 Created`)
Returns created `milestone` and updated parent `goal` with recalculated `progress_percent`.

---

### List Milestones
`GET /api/v1/goals/{goal_id}/milestones`

Returns all checkpoints for the goal sorted by `sort_order asc, created_at asc`.

---

### Update Milestone
`PATCH /api/v1/goals/{goal_id}/milestones/{milestone_id}`

---

### Complete / Reopen Milestone
`PATCH /api/v1/goals/{goal_id}/milestones/{milestone_id}/complete`

#### Request Body
```json
{
  "is_completed": true
}
```
Setting `is_completed: true` sets `completed_at = now()` and automatically updates goal progress. Setting `false` clears `completed_at` to `null`.

---

### Delete Milestone
`DELETE /api/v1/goals/{goal_id}/milestones/{milestone_id}`

Deletes the milestone and recalculates goal progress.

