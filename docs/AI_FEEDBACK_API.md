# LifeOS – AI Feedback REST API Reference (Step 13.5: Phase 3)

All endpoints require standard Bearer JWT authorization in the `Authorization` HTTP header (`Bearer <access_token>`).

All API responses follow the standard LifeOS envelope:
```json
{
  "success": true,
  "data": { ... },
  "message": "Human-readable status summary"
}
```

---

## 1. Submit or Update Feedback

Submits a rating, defect category, qualitative comment, or suggested correction for an assistant message. If feedback already exists for the given message, it updates the record idempotently.

- **Endpoint**: `POST /api/v1/ai/feedback`
- **Authentication**: Required (`Bearer <access_token>`)
- **Status Codes**: 
  - `201 Created` (if initial feedback for this message)
  - `200 OK` (if updating previous feedback on this message)
  - `400 Bad Request` (invalid rating, category, or role != assistant)
  - `403 Forbidden` (message belongs to another user)
  - `404 Not Found` (message does not exist)
  - `422 Unprocessable Entity` (Pydantic validation failure)

### Request Body
```json
{
  "message_id": "b18b671c-fb57-4029-9468-c91860cbe1b3",
  "rating": -1,
  "feedback_type": "correction",
  "category": "incorrect_answer",
  "comment": "The schedule was off by two hours.",
  "suggested_response": "You have a deep work block from 8 AM to 10 AM, then standup at 10 AM."
}
```

#### Field Specifications:
- `message_id` (*required*, UUID string, 36 chars): ID of the target assistant turn.
- `rating` (*required*, integer): `1` (thumbs up) or `-1` (thumbs down).
- `feedback_type` (*optional*, string): `thumbs_up`, `thumbs_down`, `correction`, `issue_report`. (Automatically derived if omitted).
- `category` (*optional*, string): One of:
  - `incorrect_answer`
  - `incomplete_answer`
  - `irrelevant_answer`
  - `poor_explanation`
  - `wrong_tone`
  - `outdated_context`
  - `other`
- `comment` (*optional*, string, max 2000 chars): User explanation or note.
- `suggested_response` (*optional*, string, max 5000 chars): Ground-truth correction.

### Response `201 Created` / `200 OK`
```json
{
  "success": true,
  "message": "Feedback submitted successfully",
  "data": {
    "feedback": {
      "id": "e458e3a5-9bf8-4bec-9474-88697c0cb084",
      "user_id": "b18b671c-fb57-4029-9468-c91860cbe1b3",
      "message_id": "c94e6949-ca39-4392-bd72-c7ef08fc891c",
      "rating": -1,
      "feedback_type": "correction",
      "category": "incorrect_answer",
      "comment": "The schedule was off by two hours.",
      "suggested_response": "You have a deep work block from 8 AM to 10 AM, then standup at 10 AM.",
      "created_at": "2026-11-08T13:15:00.000000Z",
      "updated_at": "2026-11-08T13:15:00.000000Z"
    }
  }
}
```

---

## 2. List User Feedback

Retrieves paginated feedback records authored by the authenticated user.

- **Endpoint**: `GET /api/v1/ai/feedback`
- **Query Parameters**:
  - `rating` (*optional*, integer): Filter by `1` or `-1`.
  - `limit` (*optional*, integer, default `20`, max `100`): Page size.
  - `offset` (*optional*, integer, default `0`): Pagination offset.
- **Status Codes**: `200 OK`

### Response `200 OK`
```json
{
  "success": true,
  "message": "Feedback list retrieved successfully",
  "data": {
    "feedback": [
      {
        "id": "e458e3a5-9bf8-4bec-9474-88697c0cb084",
        "user_id": "b18b671c-fb57-4029-9468-c91860cbe1b3",
        "message_id": "c94e6949-ca39-4392-bd72-c7ef08fc891c",
        "rating": 1,
        "feedback_type": "thumbs_up",
        "category": null,
        "comment": null,
        "suggested_response": null,
        "created_at": "2026-11-08T13:15:00.000000Z",
        "updated_at": "2026-11-08T13:15:00.000000Z"
      }
    ],
    "total": 14,
    "limit": 20,
    "offset": 0
  }
}
```

---

## 3. Get Feedback by ID

Retrieves a single feedback record by its primary key ID.

- **Endpoint**: `GET /api/v1/ai/feedback/<feedback_id>`
- **Status Codes**: `200 OK`, `403 Forbidden`, `404 Not Found`

---

## 4. Update Feedback by ID

Selectively modifies fields on an existing feedback submission.

- **Endpoint**: `PATCH /api/v1/ai/feedback/<feedback_id>`
- **Request Body**:
```json
{
  "rating": -1,
  "category": "wrong_tone",
  "comment": "Too informal for a morning brief."
}
```
- **Status Codes**: `200 OK`, `400 Bad Request`, `403 Forbidden`, `404 Not Found`

---

## 5. Delete Feedback by ID

Permanently removes a feedback submission.

- **Endpoint**: `DELETE /api/v1/ai/feedback/<feedback_id>`
- **Status Codes**: `200 OK`, `403 Forbidden`, `404 Not Found`

---

## 6. Get Feedback for Specific Message

Retrieves the feedback record linked to an assistant message.

- **Endpoint**: `GET /api/v1/ai/messages/<message_id>/feedback`
- **Status Codes**: `200 OK`, `403 Forbidden`, `404 Not Found`

