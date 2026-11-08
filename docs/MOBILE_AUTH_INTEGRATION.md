# Mobile Authentication Integration Reference

## 1. Integrated Endpoints Contract

The mobile frontend integrates exclusively with verified backend REST endpoints under `/api/v1`:

| Method | Endpoint | Auth Header | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | None | Registers new user account, returns User entity and token pair. |
| `POST` | `/api/v1/auth/login` | None | Authenticates email & password, returns User entity and token pair. |
| `POST` | `/api/v1/auth/refresh` | `Bearer <refresh_token>` | Rotates refresh token, invalidates old JTI, issues new token pair. |
| `POST` | `/api/v1/auth/logout` | `Bearer <refresh_token>` | Revokes active refresh token by JTI in database. |
| `GET` | `/api/v1/auth/me` | `Bearer <access_token>` | Returns current authenticated user record. |
| `GET` | `/api/v1/users/me` | `Bearer <access_token>` | Returns user profile record from users service. |

---

## 2. Token Storage & Lifecycle

### In-Memory Access Tokens
- Access tokens expire after 15 minutes (`JWT_ACCESS_TOKEN_EXPIRES`).
- Kept strictly in module-scoped memory via `setAuthToken` / `getAuthToken` inside `mobile/src/api/client.ts`.
- Never written to persistent unencrypted flash storage, SQLite, or `AsyncStorage`.

### Hardware-Protected Refresh Tokens
- Refresh tokens expire after 30 days (`JWT_REFRESH_TOKEN_EXPIRES`).
- Persisted on device via `expo-secure-store` with `keychainAccessible: SecureStore.AFTER_FIRST_UNLOCK`.
  - **iOS**: Apple Keychain Services.
  - **Android**: Android Keystore Provider with hardware AES-GCM encryption.
  - **Web Preview**: Graceful session fallback for browser development without native keychain access.

---

## 3. Single-Flight Token Refresh Interceptor

When access tokens expire, background HTTP requests will receive HTTP 401. To prevent concurrency races:

```typescript
// mobile/src/api/client.ts
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: any) => void;
}> = [];

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    // 1. Skip refresh for auth endpoints to prevent recursion
    if (isAuthRoute(originalRequest?.url)) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      // 2. If a refresh is already underway, enqueue this request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((newToken) => {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return apiClient(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const storedRefreshToken = await secureStorage.getRefreshToken();
        // 3. Execute single-flight refresh via dedicated refreshClient
        const refreshResponse = await refreshClient.post('/auth/refresh', {}, {
          headers: { Authorization: `Bearer ${storedRefreshToken}` },
        });

        const newTokens = refreshResponse.data.data;
        setAuthToken(newTokens.access_token);
        await secureStorage.setRefreshToken(newTokens.refresh_token);

        // 4. Resolve all queued requests with the new access token
        processQueue(null, newTokens.access_token);
        return apiClient(originalRequest);
      } catch (refreshErr) {
        // 5. If refresh fails (compromise/expiration), terminate session
        processQueue(refreshErr, null);
        setAuthToken(null);
        await secureStorage.deleteRefreshToken();
        sessionExpiredCallback?.();
        return Promise.reject(refreshErr);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);
```

---

## 4. Session Restoration & Offline Handling

1. **App Startup**:
   - `RootNavigator` invokes `restoreSession()` on startup while displaying `SplashScreen`.
   - `restoreSession()` queries `SecureStore` for the persisted refresh token.
   - If present, invokes `POST /auth/refresh` to obtain a fresh access token and rotate the refresh token.
   - If network is unreachable or refresh token has expired/been revoked, storage is cleared and user is smoothly transitioned to `WelcomeScreen`.
2. **Logout Action**:
   - User confirms logout via `ConfirmationModal`.
   - A best-effort `POST /auth/logout` is dispatched to revoke the JTI on the server.
   - Irrespective of network connectivity, local storage and in-memory tokens are purged immediately.

