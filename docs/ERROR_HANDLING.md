# LifeOS – Centralized Error Handling

## 1. Design Philosophy
Clients must receive structured, predictable error envelopes with semantic machine-readable error codes. Internal tracebacks, database dialect details, and infrastructure credentials must **never** be exposed in client responses.

## 2. Global Exception Interceptor Architecture
The centralized error handling mechanism is initialized via `register_error_handlers(app)` in `app/core/handlers.py`:

```mermaid
flowchart TD
    Req[Inbound HTTP Request] --> Route[Flask Blueprint Route]
    Route --> Exception{Exception Raised?}
    Exception -->|No| SuccessResp[200 / 201 api_response]
    
    Exception -->|LifeOSException| DomainH[handle_lifeos_exception]
    Exception -->|Pydantic ValidationError| PydanticH[handle_pydantic_validation]
    Exception -->|SQLAlchemy IntegrityError| DBMetaH[handle_database_integrity]
    Exception -->|RateLimitExceeded| RateLimitH[handle_rate_limit]
    Exception -->|Werkzeug HTTPException| HttpH[handle_http_exception]
    Exception -->|JWT Errors| JWTH[handle_expired / revoked / invalid_token]
    Exception -->|Unexpected Exception| FatalH[handle_unexpected_exception]

    DomainH --> ErrResp[error_response Envelope]
    PydanticH --> ErrResp
    DBMetaH --> ErrResp
    RateLimitH --> ErrResp
    HttpH --> ErrResp
    JWTH --> ErrResp
    FatalH --> ErrResp
```

## 3. Custom Domain Exception Hierarchy
- `LifeOSException`: Base class with `status_code`, `error_code`, `message`, `payload`.
  - `NotFoundException` (404, `NOT_FOUND`)
  - `ValidationException` (422, `VALIDATION_ERROR`)
  - `UnauthorizedException` (401, `AUTHENTICATION_ERROR`)
  - `ForbiddenException` (403, `AUTHORIZATION_ERROR`)
  - `ConflictException` (409, `CONFLICT`)
  - `IntegrityException` (409, `INTEGRITY_ERROR`)
  - `RateLimitException` (429, `RATE_LIMIT_EXCEEDED`)

