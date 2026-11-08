# LifeOS – API Standards & Conventions

## 1. Protocol & Versioning
- **Base Protocol**: HTTPS (REST JSON)
- **Base Route**: `/api/v1`
- **Specification**: OpenAPI 3.1.0 (`docs/openapi.yaml`)

## 2. Standardized Response Envelopes

### 2.1 Success Response (`200 OK`, `201 Created`)
```json
{
  "success": true,
  "status": "success",
  "message": "Operation successful",
  "data": {
    "user": {
      "id": "c1f7a0b3-4f93-4a67-b715-99d9804b3419",
      "email": "alex@lifeos.io",
      "full_name": "Alex Mercer"
    }
  },
  "meta": null
}
```

### 2.2 Paginated Success Response
```json
{
  "success": true,
  "status": "success",
  "message": "Tasks retrieved successfully",
  "data": [
    {
      "id": "e4b2d184-7a1a-460d-88b9-53b9a7c390a1",
      "title": "Deep Work Block",
      "status": "todo"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

### 2.3 Error Response (`4xx`, `5xx`)
```json
{
  "success": false,
  "status": "error",
  "message": "Input validation failed",
  "errors": [
    {
      "field": "password",
      "message": "Password must contain at least one letter and one number"
    }
  ],
  "code": "VALIDATION_ERROR"
}
```

## 3. Standard HTTP Status Codes & Error Codes
| HTTP Status | Error Code (`code`) | Meaning |
| :--- | :--- | :--- |
| **200 OK** | - | Successful fetch or update. |
| **201 Created** | - | Successful resource creation. |
| **400 Bad Request** | `BAD_REQUEST` | Malformed JSON or request syntax. |
| **401 Unauthorized**| `AUTHENTICATION_REQUIRED`, `TOKEN_EXPIRED`, `TOKEN_REVOKED` | Missing, invalid, or revoked JWT. |
| **403 Forbidden** | `AUTHORIZATION_ERROR` | Authenticated user does not own the target resource. |
| **404 Not Found** | `NOT_FOUND` | Resource or route does not exist. |
| **405 Method Not Allowed** | `METHOD_NOT_ALLOWED` | Disallowed HTTP verb on endpoint. |
| **409 Conflict** | `CONFLICT`, `INTEGRITY_ERROR` | Duplicate email or unique constraint violation. |
| **413 Payload Too Large** | `PAYLOAD_TOO_LARGE` | Body exceeds 10MB limit. |
| **422 Unprocessable**| `VALIDATION_ERROR` | Pydantic schema validation failed. |
| **429 Too Many Req** | `RATE_LIMIT_EXCEEDED` | Exceeded rate limit bucket. |
| **500 Server Error**| `INTERNAL_ERROR`, `DATABASE_ERROR` | Internal server fault (sanitized, stack trace hidden). |
| **503 Unavailable** | `SERVICE_UNAVAILABLE` | Database readiness check failed. |

## 4. Header Conventions
- **`Authorization`**: `Bearer <access_token>`
- **`Content-Type`**: `application/json`
- **`X-Request-ID`**: Unique UUID assigned or forwarded for request tracing across client and server logs.

