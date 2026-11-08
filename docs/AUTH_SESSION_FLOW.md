# LifeOS – Authentication & Session Lifecycle Architecture

This document details the complete client-server authentication flow, session restoration lifecycle, token rotation mechanics, single-flight concurrent request deduplication, and cache isolation standards implemented in LifeOS.

---

## 1. Authentication Architecture & Storage Security

LifeOS adheres to strict mobile security best practices to protect user sessions while preventing persistent token theft:

| Storage Tier | Target Token / Data | Implementation | Security Properties |
|---|---|---|---|
| **In-Memory Storage** | Short-Lived Access Token (15m expiry) | `mobile/src/api/client.ts` (`authToken` variable) | Never written to disk or device file system. Immune to unencrypted device backup attacks or extraction from physical storage. |
| **Encrypted Persistent Storage** | Long-Lived Refresh Token (30d expiry) | `expo-secure-store` (Keychain on iOS, Keystore/AES-GCM on Android) | Encrypted hardware-backed storage with cryptographic isolation. |
| **Persistent User Metadata** | User Profile, Onboarding Completed Flag | `zustand/middleware` (`persist`) | Non-sensitive UI preferences and flags stored in client storage. |
| **Server State Cache** | Private User Domain Entities | `queryClient` (TanStack Query) | Completely purged in-memory via `queryClient.clear()` on session termination. |

---

## 2. Authentication Lifecycle Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant MobileUI as Mobile Screen / Store
    participant ApiClient as Axios Client Interceptor
    participant SecureStore as Hardware SecureStore
    participant Backend as Flask JWT Auth API

    %% Registration / Login
    Note over User,Backend: 1. Initial Authentication (Login / Register)
    User->>MobileUI: Submits email & password
    MobileUI->>Backend: POST /api/v1/auth/login
    Backend-->>MobileUI: Returns { access_token, refresh_token, user }
    MobileUI->>ApiClient: setAuthToken(access_token) (In-Memory)
    MobileUI->>SecureStore: setRefreshToken(refresh_token) (Hardware Encrypted)
    MobileUI->>MobileUI: Transition to Main Dashboard

    %% App Launch / Session Restoration
    Note over User,Backend: 2. Cold App Launch & Session Restoration
    MobileUI->>SecureStore: getRefreshToken()
    alt No Refresh Token Exists
        MobileUI->>MobileUI: Set state to unauthenticated -> Show Auth Stack
    else Valid Refresh Token Present
        MobileUI->>Backend: POST /api/v1/auth/refresh (Bearer refresh_token)
        alt Refresh Token Valid
            Backend-->>MobileUI: Returns { access_token, refresh_token }
            MobileUI->>ApiClient: setAuthToken(new_access_token)
            MobileUI->>SecureStore: setRefreshToken(new_refresh_token)
            MobileUI->>Backend: GET /api/v1/auth/me
            Backend-->>MobileUI: Returns authenticated user
            MobileUI->>MobileUI: Set isAuthenticated=true -> Show Main Stack
        else Refresh Token Expired / Revoked
            Backend-->>MobileUI: 401 Unauthorized
            MobileUI->>SecureStore: deleteRefreshToken()
            MobileUI->>ApiClient: setAuthToken(null)
            MobileUI->>MobileUI: Redirect to Login Screen
        end
    end

    %% Concurrent Requests & Single-Flight Refresh Queue
    Note over User,Backend: 3. Token Expiry & Single-Flight Auto-Refresh
    MobileUI->>ApiClient: Request A (Tasks) & Request B (Habits)
    ApiClient->>Backend: GET /api/v1/tasks (Expired Token)
    Backend-->>ApiClient: 401 UNAUTHORIZED
    Note over ApiClient: isRefreshing lock acquired
    Note over ApiClient: Request B queued in failedQueue[]
    ApiClient->>Backend: POST /api/v1/auth/refresh (Bearer refresh_token)
    Backend-->>ApiClient: Returns new access_token & refresh_token
    Note over ApiClient: In-memory token updated & failedQueue replayed
    ApiClient->>Backend: Retry Request A & Retry Request B with new token
    Backend-->>ApiClient: 200 OK (Both requests succeed transparently)

    %% Explicit Logout
    Note over User,Backend: 4. Secure Session Termination (Logout)
    User->>MobileUI: Presses Logout
    MobileUI->>SecureStore: deleteRefreshToken()
    MobileUI->>ApiClient: setAuthToken(null)
    MobileUI->>MobileUI: queryClient.clear() (Purges all cached tasks, habits, finances)
    MobileUI->>MobileUI: Reset auth store state -> Show Login
```

---

## 3. Key Reliability & Security Mechanisms

### 3.1 Single-Flight Refresh Queue (`mobile/src/api/client.ts`)
When multiple concurrent queries fire (such as when the user opens the Dashboard which concurrently fetches Tasks, Habits, Goals, and Analytics), an expired access token causes multiple simultaneous 401 errors.

The LifeOS HTTP client handles this with an atomic single-flight lock:
1. `isRefreshing` flag: Set to `true` on the very first 401.
2. `failedQueue`: Array of pending promises representing each concurrent failed request.
3. Once the single refresh request resolves:
   - The in-memory access token is updated.
   - All queued requests are resolved and re-dispatched with the new token.
   - `isRefreshing` is reset to `false`.
4. If the refresh fails:
   - All queued requests are rejected.
   - `useAuthStore.getState().logout()` is triggered automatically.

### 3.2 Complete Query Cache Purge on Signout
To prevent cross-account privacy leakage (e.g. if User A logs out and User B logs in on the same shared device):
- `useAuthStore.ts` explicitly imports the centralized `queryClient` from `mobile/src/api/queryClient.ts`.
- In both `logout()` and `restoreSession()` failure branches, `queryClient.clear()` is executed immediately.
- This ensures zero stale financial records, private tasks, or health memories remain in RAM.

