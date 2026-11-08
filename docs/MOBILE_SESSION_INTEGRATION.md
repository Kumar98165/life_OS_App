# LifeOS – Secure Mobile Session Integration Guide

## 1. Storage Architecture
| Secret | Storage Medium | Rationale |
| :--- | :--- | :--- |
| **Passwords** | **NEVER STORED** | Passwords are only held in transient form state during login/registration. |
| **Refresh Token** | **Expo SecureStore** | Hardware-backed keystore on Android (KeyStore) and iOS (Keychain). Never store in unencrypted `AsyncStorage`. |
| **Access Token** | **In-Memory (Zustand)** | Ephemeral runtime store. Destroyed automatically on app termination. |

---

## 2. Centralized Axios Interceptor Pattern

To ensure seamless, single-flight token rotation without race conditions or infinite loops, the React Native client uses a queued refresh interceptor:

```typescript
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import * as SecureStore from 'expo-secure-store';

let accessToken: string | null = null;
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else if (token) {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

export const apiClient = axios.create({
  baseURL: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:5000/api/v1',
  timeout: 15000,
});

// 1. Inbound Request Interceptor (Injects Memory Access Token)
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (accessToken && config.headers) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// 2. Outbound Response Interceptor (Handles 401 with Single-Flight Refresh)
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest: any = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (originalRequest.url?.includes('/auth/refresh')) {
        // Refresh token itself failed or expired -> force logout
        await handleForceLogout();
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // Queue concurrent requests behind single refresh flight
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const storedRefreshToken = await SecureStore.getItemAsync('lifeos_refresh_token');
        if (!storedRefreshToken) {
          throw new Error('No refresh token available');
        }

        const res = await axios.post(
          `${apiClient.defaults.baseURL}/auth/refresh`,
          {},
          { headers: { Authorization: `Bearer ${storedRefreshToken}` } }
        );

        const newAccessToken = res.data.data.access_token;
        const newRefreshToken = res.data.data.refresh_token;

        accessToken = newAccessToken;
        await SecureStore.setItemAsync('lifeos_refresh_token', newRefreshToken);

        processQueue(null, newAccessToken);
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return apiClient(originalRequest);
      } catch (refreshErr) {
        processQueue(refreshErr, null);
        await handleForceLogout();
        return Promise.reject(refreshErr);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

async function handleForceLogout() {
  accessToken = null;
  await SecureStore.deleteItemAsync('lifeos_refresh_token');
  // Trigger navigation redirect to Auth screen via Zustand store
}
```

---

## 3. Session Safeguards
1. **Single-Flight Execution**: The `isRefreshing` lock ensures that five parallel requests receiving `401` only trigger **one** rotation request to `/auth/refresh`. The four subsequent requests pause and retry once the single flight completes.
2. **Infinite Loop Prevention**: The `_retry` flag and `/auth/refresh` URL check ensure that if `/auth/refresh` returns `401`, the client terminates the session immediately rather than retrying in an endless loop.
3. **Session Revocation**: Upon explicit logout, the client calls `POST /api/v1/auth/logout`, purges `SecureStore`, and clears the in-memory token.

