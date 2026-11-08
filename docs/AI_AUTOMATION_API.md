# LifeOS AI Automation API Reference

> **Version**: 1.0.0  
> **Base URL**: `/api/v1/automations`  
> **Auth**: Bearer JWT Required on all routes

---

## 1. Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/automations` | List user automations and system templates |
| `GET` | `/api/v1/automations/templates` | List all predefined automation templates |
| `POST` | `/api/v1/automations` | Create a new custom automation definition |
| `GET` | `/api/v1/automations/<id>` | Retrieve automation definition details |
| `PATCH` | `/api/v1/automations/<id>` | Update user automation definition |
| `DELETE` | `/api/v1/automations/<id>` | Delete user automation definition |
| `POST` | `/api/v1/automations/<id>/execute` | Trigger execution of an automation |
| `GET` | `/api/v1/automations/executions` | List execution history with filters |
| `GET` | `/api/v1/automations/executions/<id>` | Retrieve full execution details, actions, approvals, and logs |
| `POST` | `/api/v1/automations/approvals/<id>/approve` | Approve and execute pending action |
| `POST` | `/api/v1/automations/approvals/<id>/reject` | Reject pending action |
| `POST` | `/api/v1/automations/executions/<id>/cancel` | Cancel in-flight execution |
| `POST` | `/api/v1/automations/<id>/pause` | Pause scheduled automation |
| `POST` | `/api/v1/automations/<id>/resume` | Resume paused automation |

---

## 2. Example Payloads

### Trigger Execution
```json
POST /api/v1/automations/6b552cc5-d74d-4a4a-a300-7cf99d9d7b20/execute
{
  "user_request": "Plan my morning schedule with high-priority tasks",
  "idempotency_key": "custom-uuid-key-12345"
}
```

### Approve Action
```json
POST /api/v1/automations/approvals/9c1a5b82-e30d-4567-8910-abcdef012345/approve
```

### Reject Action
```json
POST /api/v1/automations/approvals/9c1a5b82-e30d-4567-8910-abcdef012345/reject
{
  "reason": "I prefer to tackle this tomorrow instead."
}
```
