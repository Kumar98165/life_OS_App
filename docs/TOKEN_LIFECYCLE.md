# LifeOS – Token Lifecycle & Rotation (RTR)

## 1. Token Specifications
| Property | Access Token | Refresh Token |
| :--- | :--- | :--- |
| **Duration** | 1 Hour (3600s) | 30 Days (2,592,000s) |
| **Storage (Mobile)** | Memory / Fast State | Expo `SecureStore` (Keychain / Keystore) |
| **Storage (Backend)** | Stateless JWT verification | Stateful `refresh_tokens` table with cryptographic `JTI` |
| **Scope** | Authorizes API requests (`/api/v1/*`) | Rotates tokens (`/api/v1/auth/refresh`) & terminates sessions |

---

## 2. Refresh Token Rotation (RTR) Flow

```mermaid
sequenceDiagram
    autonumber
    participant Client as Mobile Client
    participant API as Flask Backend API
    participant DB as PostgreSQL (refresh_tokens)

    Client->>API: POST /api/v1/auth/refresh (Bearer RefreshToken_A)
    API->>API: Verify signature & expiration
    API->>DB: Query RefreshToken by JTI_A
    alt JTI_A is Revoked (Token Reuse Detected!)
        Note over API,DB: Security Alert: Potential Compromise!
        API->>DB: UPDATE refresh_tokens SET is_revoked = true WHERE user_id = user.id
        API-->>Client: 401 Unauthorized ("Revoked token reuse detected. All sessions terminated.")
    else JTI_A is Valid & Active
        API->>DB: UPDATE refresh_tokens SET is_revoked = true WHERE token_jti = JTI_A
        API->>API: Generate AccessToken_2 & RefreshToken_B (JTI_B)
        API->>DB: INSERT INTO refresh_tokens (JTI_B, expires_at, is_revoked=false)
        API-->>Client: 200 OK (AccessToken_2, RefreshToken_B)
        Client->>Client: Overwrite SecureStore with RefreshToken_B
    end
```

---

## 3. Token Invalidation on Logout
1. Client calls `POST /api/v1/auth/logout` supplying the current refresh token in the `Authorization: Bearer <refresh_token>` header.
2. The endpoint extracts the token claim `jti` and sets `is_revoked = True` in PostgreSQL.
3. Once marked revoked, any subsequent refresh attempt presenting this token is immediately rejected.
4. Short-lived access tokens expire naturally within their 1-hour window without requiring stateful database queries on every HTTP request.

