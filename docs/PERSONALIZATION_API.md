# LifeOS Personalization API Reference

Base URL: `/api/v1/personalization`  
Authentication: `Authorization: Bearer <JWT_ACCESS_TOKEN>`

---

## 1. GET /api/v1/personalization
Retrieves the full personalization settings and daily routine configuration for the authenticated user.

### Response (200 OK)
```json
{
  "status": "success",
  "data": {
    "personalization": {
      "id": "pers-uuid",
      "user_id": "user-uuid",
      "preferred_name": "Alex",
      "preferred_language": "en",
      "timezone": "UTC",
      "date_format": "YYYY-MM-DD",
      "time_format": "24h",
      "week_start_day": "monday",
      "productivity_style": "structured",
      "task_priority_strategy": "eisenhower",
      "ai_response_style": "concise",
      "ai_response_length": "medium",
      "dashboard_density": "comfortable",
      "personalization_enabled": true
    },
    "daily_routine": {
      "id": "routine-uuid",
      "user_id": "user-uuid",
      "wake_time": "07:00",
      "sleep_time": "23:00",
      "work_start": "09:00",
      "work_end": "17:00",
      "work_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
      "focus_block_duration_minutes": 50,
      "break_duration_minutes": 10,
      "lunch_start": "12:30",
      "lunch_duration_minutes": 60,
      "morning_routine_enabled": true,
      "evening_routine_enabled": true,
      "preferred_planning_time": "08:30",
      "routine_reminders_enabled": true
    }
  }
}
```

---

## 2. PATCH /api/v1/personalization
Updates general personalization settings.

### Request Body
```json
{
  "preferred_name": "Alex Mercer",
  "productivity_style": "deep_work",
  "ai_response_style": "detailed",
  "ai_response_length": "short"
}
```

---

## 3. GET & PATCH /api/v1/personalization/dashboard
Manages dashboard widget visibility, ordering, and density.

### Request Body (PATCH)
```json
{
  "dashboard_density": "compact",
  "dashboard_widgets": [
    {"id": "today_tasks", "visible": true, "order": 0, "title": "Today's Tasks"},
    {"id": "ai_quick_access", "visible": true, "order": 1, "title": "AI Assistant"},
    {"id": "daily_overview", "visible": false, "order": 2, "title": "Daily Overview"}
  ]
}
```

---

## 4. GET & PATCH /api/v1/personalization/routine
Manages daily working hours and rhythm boundaries.

### Request Body (PATCH)
```json
{
  "wake_time": "06:30",
  "sleep_time": "22:30",
  "work_start": "08:30",
  "work_end": "16:30",
  "focus_block_duration_minutes": 45
}
```

---

## 5. POST /api/v1/personalization/reset
Selectively resets targeted settings to system defaults.

### Request Body
```json
{
  "target": "dashboard" // Options: "dashboard", "routine", "identity", "ai_style", "all"
}
```
