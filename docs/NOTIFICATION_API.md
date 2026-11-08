# LifeOS Notifications & Reminders REST API Reference

Base URL: `/api/v1/notifications`  
Authentication: `Authorization: Bearer <access_token>`

## 1. Notification Center Endpoints

### GET `/api/v1/notifications`
Retrieve paginated notifications for the authenticated user.
- **Query Parameters**:
  - `unread_only`: boolean (`true` | `false`, default: `false`)
  - `notification_type`: string (`task`, `planner`, `habit`, `goal`, `finance`, `reminder`, `system`)
  - `page`: integer (default: 1)
  - `limit`: integer (default: 50, max: 100)
- **Response**: `200 OK`
```json
{
  "success": true,
  "message": "Notifications retrieved successfully.",
  "data": {
    "notifications": [
      {
        "id": "uuid-123",
        "user_id": "user-uuid",
        "title": "Task Due Today: Tax Filings",
        "body": "Scheduled for today. Stay focused on your priority goals.",
        "notification_type": "task",
        "entity_type": "task",
        "entity_id": "task-uuid",
        "is_read": false,
        "read_at": null,
        "scheduled_for": null,
        "data_payload": "{\"route\": \"TasksTab\", \"taskId\": \"task-uuid\"}",
        "is_delivered": true,
        "delivered_at": "2026-11-08T14:00:00Z",
        "created_at": "2026-11-08T14:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 50
  }
}
```

### GET `/api/v1/notifications/unread-count`
Retrieve total count of unread notifications for badge indicators.
- **Response**: `200 OK`
```json
{
  "success": true,
  "message": "Unread notification count retrieved.",
  "data": {
    "unread_count": 3
  }
}
```

### GET `/api/v1/notifications/{id}`
Retrieve a single notification with IDOR check.
- **Response**: `200 OK` (or `404 Not Found`)

### PATCH `/api/v1/notifications/{id}/read`
Mark a single notification as read.
- **Response**: `200 OK`

### PATCH `/api/v1/notifications/read-all`
Mark all unread notifications for user as read.
- **Response**: `200 OK`
```json
{
  "success": true,
  "message": "Marked 3 notifications as read.",
  "data": {
    "marked_count": 3
  }
}
```

### DELETE `/api/v1/notifications/{id}`
Delete a notification record with ownership validation.
- **Response**: `200 OK`

---

## 2. Notification Preferences Endpoints

### GET `/api/v1/notifications/preferences`
Retrieve user category toggles, channel preferences, and quiet hours settings.
- **Response**: `200 OK`
```json
{
  "success": true,
  "message": "Notification preferences retrieved.",
  "data": {
    "preferences": {
      "id": "pref-uuid",
      "user_id": "user-uuid",
      "tasks_enabled": true,
      "planner_enabled": true,
      "habits_enabled": true,
      "goals_enabled": true,
      "finance_enabled": true,
      "push_enabled": true,
      "in_app_enabled": true,
      "quiet_hours_enabled": false,
      "quiet_hours_start": "22:00",
      "quiet_hours_end": "08:00",
      "timezone": "America/New_York"
    }
  }
}
```

### PATCH `/api/v1/notifications/preferences`
Update user category toggles, channel preferences, or quiet hours.
- **Request Body**:
```json
{
  "quiet_hours_enabled": true,
  "quiet_hours_start": "23:00",
  "quiet_hours_end": "07:30",
  "timezone": "America/New_York"
}
```
- **Response**: `200 OK`

---

## 3. Scheduled Reminders Endpoints

### GET `/api/v1/notifications/reminders`
- **Query Parameters**: `status` (`pending`, `triggered`, `cancelled`, `snoozed`, `expired`), `page`, `limit`
- **Response**: `200 OK` with `{ "reminders": [...], "total": 4 }`

### POST `/api/v1/notifications/reminders`
- **Request Body**:
```json
{
  "title": "Review Weekly Budget",
  "description": "Examine spending categories and savings rate.",
  "reminder_time": "2026-11-08T18:00:00Z",
  "entity_type": "finance",
  "is_recurring": true,
  "recurrence_rule": "weekly"
}
```
- **Response**: `201 Created`

### PATCH `/api/v1/notifications/reminders/{id}`
- **Request Body**: Partial update (`title`, `description`, `reminder_time`, `status`, `is_recurring`, `recurrence_rule`)
- **Response**: `200 OK`

### DELETE `/api/v1/notifications/reminders/{id}`
- Cancel and delete reminder.
- **Response**: `200 OK`

---

## 4. Device Push Tokens Endpoints

### POST `/api/v1/notifications/devices`
Register or update an Expo device push token.
- **Request Body**:
```json
{
  "token": "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]",
  "device_type": "ios",
  "device_name": "iPhone 15 Pro"
}
```
- **Response**: `201 Created`

### DELETE `/api/v1/notifications/devices/{id}`
- Unregister/deactivate push token.
- **Response**: `200 OK`

---

## 5. Operations & Context Scanners

### POST `/api/v1/notifications/process-due`
Scheduler worker or cron webhook to trigger due reminders.
- **Response**: `200 OK` with `{"processed_count": N}`

### POST `/api/v1/notifications/scan`
Scan current user tasks, habits, and budgets to synthesize contextual notifications.
- **Response**: `200 OK` with counts of generated notifications.

