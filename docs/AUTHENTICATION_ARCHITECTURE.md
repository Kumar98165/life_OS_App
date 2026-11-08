# LifeOS – Authentication Architecture

## 1. Overview
The LifeOS Authentication Architecture provides a zero-compromise, cryptographically secure foundation built on **Flask-JWT-Extended**, **salted bcrypt hashing** (work factor 12), and **persistent Refresh Token Rotation (RTR)** stored in **PostgreSQL 18**.

## 2. Authentication Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as Mobile User (Expo)
    participant Client as Axios Client (Mobile)
    participant API as Flask Backend API
    participant Service as AuthService
    participant DB as PostgreSQL 18

    %% Registration
    rect rgb(245, 247, 255)
    note right of User: User Registration Flow
    User->>Client: Enters Name, Email, Password
    Client->>API: POST /api/v1/auth/register
    API->>Service: register_user(email, password, full_name)
    Service->>DB: Check email uniqueness (normalized lowercase)
    Service->>Service: Salt & hash password (bcrypt 12 rounds)
    Service->>DB: INSERT INTO users & INSERT INTO refresh_tokens (JTI)
    Service-->>API: User object & JWT pair
    API-->>Client: 201 Created (User sanitized, access & refresh tokens)
    Client->>Client: Store refresh_token in SecureStore, access_token in memory
    end

    %% Login
    rect rgb(240, 255, 245)
    note right of User: User Login Flow
    User->>Client: Enters Email & Password
    Client->>API: POST /api/v1/auth/login
    API->>Service: authenticate_user(email, password)
    Service->>DB: Fetch user by normalized email
    Service->>Service: bcrypt.checkpw(password, password_hash)
    alt Invalid Credentials
        Service-->>API: 401 Unauthorized ("Invalid email or password credentials")
        API-->>Client: Uniform error response (prevents account enumeration)
    else Valid Credentials
        Service->>DB: INSERT INTO refresh_tokens (JTI, expires_at)
        Service-->>API: User object & JWT pair
        API-->>Client: 200 OK (User sanitized, access & refresh tokens)
    end
    end
```

## 3. Account Enumeration Defense
- Failed authentication attempts return an identical error message: `"Invalid email or password credentials"`.
- Error codes and HTTP statuses (`401 Unauthorized`) do not vary whether the email is unallocated or the password was incorrect.
- Rate limiting enforces a strict quota (`15 requests / minute` for login, `10 requests / minute` for registration).

## 4. Sensitive Data Sanitization
- Database entity `User.to_dict()` exclusively serializes public identity fields:
  ```json
  {
    "id": "uuid-v4",
    "email": "user@lifeos.io",
    "full_name": "Alex Mercer",
    "avatar_url": null,
    "is_active": true,
    "created_at": "2026-11-07T12:00:00Z",
    "updated_at": "2026-11-07T12:00:00Z"
  }
  ```
- `password_hash` is strictly excluded from all schemas and responses.

