import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { secureStorage } from '../services/secureStore';

function getPlatformOS(): string {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const rn = require('react-native');
    return rn?.Platform?.OS || 'unknown';
  } catch {
    return typeof window !== 'undefined' ? 'web' : 'node';
  }
}

function getExpoHostUri(): string | null {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const Constants = require('expo-constants').default;
    return Constants?.expoConfig?.hostUri || null;
  } catch {
    return null;
  }
}

/**
 * Resolves the backend API base URL dynamically:
 * - On Web: uses localhost:5000
 * - In Expo Go on physical device: dynamically extracts your computer's Wi-Fi LAN IP (e.g. 192.168.1.103)
 * - Fallback: computer LAN IP 192.168.1.103:5000
 */
export function resolveApiBaseUrl(): string {
  if (process.env.EXPO_PUBLIC_API_URL) {
    return process.env.EXPO_PUBLIC_API_URL;
  }

  const os = getPlatformOS();
  if (os === 'web') {
    return 'http://localhost:5000/api/v1';
  }

  // When running in Expo Go on Android / iOS, hostUri contains the development server's IP and port (e.g. 192.168.1.103:8081)
  const hostUri = getExpoHostUri();
  if (hostUri) {
    const hostIp = hostUri.split(':')[0];
    return `http://${hostIp}:5000/api/v1`;
  }

  return 'http://192.168.1.103:5000/api/v1';
}

export const API_BASE_URL = resolveApiBaseUrl();

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Dedicated raw client for token refresh to avoid interceptor recursion
const refreshClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

let authToken: string | null = null;
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: any) => void;
}> = [];

let sessionExpiredCallback: (() => void) | null = null;

export const setAuthToken = (token: string | null) => {
  authToken = token;
};

export const getAuthToken = () => authToken;

export const setSessionExpiredCallback = (cb: () => void) => {
  sessionExpiredCallback = cb;
};

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

// Request Interceptor: Attach in-memory access token if Authorization header not explicitly set
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (authToken && config.headers && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${authToken}`;
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Response Interceptor: Single-flight token refresh with queue
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Do not attempt refresh on auth endpoints or if already retried
    const isAuthRoute =
      originalRequest?.url?.includes('/auth/login') ||
      originalRequest?.url?.includes('/auth/register') ||
      originalRequest?.url?.includes('/auth/refresh') ||
      originalRequest?.url?.includes('/auth/logout');

    if (error.response?.status === 401 && !originalRequest?._retry && !isAuthRoute) {
      if (isRefreshing) {
        // Enqueue request while another refresh is in flight
        return new Promise<string>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((newToken) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
            }
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const storedRefreshToken = await secureStorage.getRefreshToken();
        if (!storedRefreshToken) {
          throw new Error('No refresh token available');
        }

        // Call backend refresh endpoint with Bearer refresh token
        const refreshResponse = await refreshClient.post(
          '/auth/refresh',
          {},
          {
            headers: {
              Authorization: `Bearer ${storedRefreshToken}`,
            },
          }
        );

        const newTokens = refreshResponse.data?.data;
        if (!newTokens?.access_token || !newTokens?.refresh_token) {
          throw new Error('Invalid token response from refresh endpoint');
        }

        // Update in-memory access token and secure storage refresh token
        setAuthToken(newTokens.access_token);
        await secureStorage.setRefreshToken(newTokens.refresh_token);

        processQueue(null, newTokens.access_token);

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`;
        }
        return apiClient(originalRequest);
      } catch (refreshErr) {
        processQueue(refreshErr, null);
        setAuthToken(null);
        await secureStorage.deleteRefreshToken();
        if (sessionExpiredCallback) {
          sessionExpiredCallback();
        }
        return Promise.reject(refreshErr);
      } finally {
        isRefreshing = false;
      }
    }

    // Extract standardized message from backend error response
    const data = error.response?.data as any;
    const customMessage = data?.message || error.message || 'An unexpected error occurred';
    const enhancedError = new Error(customMessage) as any;
    enhancedError.status = error.response?.status;
    enhancedError.code = data?.code;
    enhancedError.errors = data?.errors;
    return Promise.reject(enhancedError);
  }
);
