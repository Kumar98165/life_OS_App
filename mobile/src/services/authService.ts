import { apiClient } from '../api/client';
import { ApiResponse, AuthResponse, AuthTokens, User } from '../types';

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export const authService = {
  /**
   * Register a new user account.
   */
  async register(payload: RegisterPayload): Promise<AuthResponse> {
    const response = await apiClient.post<ApiResponse<AuthResponse>>('/auth/register', payload);
    return response.data.data;
  },

  /**
   * Authenticate user with email and password.
   */
  async login(payload: LoginPayload): Promise<AuthResponse> {
    const response = await apiClient.post<ApiResponse<AuthResponse>>('/auth/login', payload);
    return response.data.data;
  },

  /**
   * Terminate active session and revoke refresh token.
   */
  async logout(refreshToken?: string | null): Promise<void> {
    try {
      if (refreshToken) {
        await apiClient.post(
          '/auth/logout',
          {},
          {
            headers: {
              Authorization: `Bearer ${refreshToken}`,
            },
          }
        );
      }
    } catch {
      // Allow local logout to proceed even if remote revocation fails (e.g. offline)
    }
  },

  /**
   * Fetch current user profile.
   */
  async getProfile(): Promise<User> {
    const response = await apiClient.get<ApiResponse<{ user: User }>>('/auth/me');
    return response.data.data.user;
  },

  /**
   * Retrieve profile from users blueprint.
   */
  async getUserProfile(): Promise<User> {
    const response = await apiClient.get<ApiResponse<{ user: User }>>('/users/me');
    return response.data.data.user;
  },
};

