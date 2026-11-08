# LifeOS – Security Guidelines

## 1. Authentication & Token Management
1. **Password Hashing**:
   - Salting and hashing are performed using **bcrypt** with a minimum work factor of 12 rounds.
   - Plaintext passwords are never logged, stored in memory longer than necessary, or serialized in responses.
2. **Token Rotation & Revocation**:
   - Short-lived Access Tokens (default: 1 hour).
   - Long-lived Refresh Tokens (default: 30 days) stored with unique cryptographic JTI claims in the `refresh_tokens` table.
   - Calling `POST /api/v1/auth/logout` explicitly marks the token record `is_revoked = True`.
   - The token blocklist loader intercepts revoked refresh tokens and rejects subsequent refresh attempts (`TOKEN_REVOKED`).

## 2. Resource Ownership & Multi-Tenant Isolation
1. **Never Trust Client-Provided User IDs**:
   - Endpoints never trust a `user_id` passed in request payloads or URL parameters to grant data access.
   - Resource ownership is strictly resolved against the authenticated identity (`get_jwt_identity()`).
2. **Ownership Verification Helper**:
   - All mutation and read operations enforce:
     ```python
     check_resource_ownership(resource_user_id=item.user_id, current_user_id=jwt_identity)
     ```
   - Violations raise `ForbiddenException("AUTHORIZATION_ERROR")`.

## 3. Rate Limiting & Denial of Service Defense
1. **Rate Limiting**:
   - Powered by `Flask-Limiter` with fixed-window counters.
   - Auth endpoints are throttled:
     - `/auth/register`: 10 requests / minute
     - `/auth/login`: 15 requests / minute
2. **Payload Size Guardrails**:
   - `MAX_CONTENT_LENGTH = 10 * 1024 * 1024` (10MB) prevents memory exhaustion attacks.

## 4. Production Secrets Validation
- In `ProductionConfig`, startup routines assert that:
  1. `DATABASE_URL` is set.
  2. `SECRET_KEY` and `JWT_SECRET_KEY` are not default or trivial placeholder strings.
- Startup fails immediately with an explicit fatal log if requirements are not met.

