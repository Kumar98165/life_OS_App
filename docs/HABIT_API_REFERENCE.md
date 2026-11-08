# LifeOS Habit API Reference

Base URL prefix: `/api/v1/habits`
All endpoints require HTTP header `Authorization: Bearer <access_token>`.

---

## 1. Summary Endpoints

### `GET /api/v1/habits/summary/daily`
Returns daily completion overview for all active user habits.
- **Query Parameters**:
  - `date` (optional, string YYYY-MM-DD): Target calendar date. Defaults to current local date.
- **Response `200 OK`**:
```json
{
  "status": "success",
  "data": {
    "date": "2026-11-08",
    "scheduled_count": 5,
    "completed_count": 3,
    "completion_percentage": 60.0,
    "habits": [...]
  }
}
```

### `GET /api/v1/habits/summary/weekly`
Returns 7-day completion breakdown starting on Monday.
- **Query Parameters**:
  - `week_start` (optional, string YYYY-MM-DD): Monday start date.
- **Response `200 OK`**:
```json
{
  "status": "success",
  "data": {
    "week_start": "2026-11-02",
    "week_end": "2026-11-08",
    "total_completed": 18,
    "total_scheduled": 25,
    "overall_percentage": 72.0,
    "days": [...]
  }
}
```

### `GET /api/v1/habits/summary/monthly`
Returns monthly calendar day completion counts and consistency rates.
- **Query Parameters**:
  - `year` (optional, int)
  - `month` (optional, int)

---

## 2. Habit CRUD Endpoints

### `POST /api/v1/habits`
Creates a new habit.
- **Request Body**:
```json
{
  "title": "Morning Meditation",
  "description": "15 minutes mindfulness breathing",
  "frequency": "daily",
  "target_days_per_week": 7,
  "color_hex": "#10B981",
  "icon": "leaf"
}
```
- **Response `201 Created`**: Returns created habit object.

### `GET /api/v1/habits`
List user's habits decorated with today's completion status.
- **Query Parameters**:
  - `include_archived` (boolean, default: false)
  - `frequency` (string: daily, weekdays, weekly)
- **Response `200 OK`**:
```json
{
  "status": "success",
  "data": {
    "habits": [
      {
        "id": "habit-uuid",
        "title": "Morning Meditation",
        "frequency": "daily",
        "current_streak": 5,
        "longest_streak": 12,
        "color_hex": "#10B981",
        "completed_today": true,
        "today_log_id": "log-uuid"
      }
    ]
  }
}
```

### `GET /api/v1/habits/<habit_id>`
Retrieve single habit details.

### `PATCH /api/v1/habits/<habit_id>`
Update habit attributes (`title`, `description`, `frequency`, `target_days_per_week`, `color_hex`, `icon`, `is_archived`).

### `DELETE /api/v1/habits/<habit_id>`
Permanently deletes habit and cascade-deletes all associated logs.

---

## 3. Check-In & Statistics Endpoints

### `POST /api/v1/habits/<habit_id>/logs`
Records a daily check-in.
- **Request Body**:
```json
{
  "log_date": "2026-11-08",
  "completed": true,
  "notes": "Optional notes on performance"
}
```
- **Response `201 Created`**: Returns created or updated log and newly computed streak counts.

### `GET /api/v1/habits/<habit_id>/logs`
Retrieve historical check-in logs.
- **Query Parameters**: `start_date`, `end_date`, `limit`.

### `DELETE /api/v1/habits/<habit_id>/logs/<log_id>`
Undoes a completion log and recalculates streaks downward.

### `GET /api/v1/habits/<habit_id>/stats`
Calculates comprehensive metrics for the habit (`current_streak`, `longest_streak`, `total_completed_days`, `completion_rate`, `weekly_consistency`, `monthly_consistency`, `recent_logs`).

