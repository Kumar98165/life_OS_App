import { create } from 'zustand';
import { AuthState, LoginFormData, RegisterFormData, OnboardingPreferences, User } from '../types';
import { authService } from '../services/authService';
import { secureStorage } from '../services/secureStore';
import { setAuthToken, setSessionExpiredCallback, API_BASE_URL } from '../api/client';
import { queryClient } from '../api/queryClient';

interface AuthActions {
  login: (data: LoginFormData) => Promise<void>;
  register: (data: RegisterFormData) => Promise<void>;
  logout: () => Promise<void>;
  restoreSession: () => Promise<void>;
  completeOnboarding: (preferences: OnboardingPreferences) => Promise<void>;
  setUser: (user: User) => void;
  clearError: () => void;
}

export type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>((set, get) => {
  // Register session expiration callback to reset store on unauthorized refresh failure
  setSessionExpiredCallback(() => {
    setAuthToken(null);
    queryClient.clear();
    set({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  return {
    user: null,
    accessToken: null,
    isAuthenticated: false,
    isLoading: false,
    isRestoringSession: true,
    hasCompletedOnboarding: false,
    onboardingPreferences: null,

    login: async (data: LoginFormData) => {
      set({ isLoading: true });
      try {
        const response = await authService.login({
          email: data.email,
          password: data.password,
        });

        // Store tokens securely
        setAuthToken(response.tokens.access_token);
        await secureStorage.setRefreshToken(response.tokens.refresh_token);

        // Check onboarding completion status
        const completedOnboarding = await secureStorage.getOnboardingCompleted();
        const savedPreferences = await secureStorage.getOnboardingPreferences<OnboardingPreferences>();

        set({
          user: response.user,
          accessToken: response.tokens.access_token,
          isAuthenticated: true,
          hasCompletedOnboarding: completedOnboarding,
          onboardingPreferences: savedPreferences,
          isLoading: false,
        });
      } catch (err: any) {
        set({ isLoading: false });
        throw err;
      }
    },

    register: async (data: RegisterFormData) => {
      set({ isLoading: true });
      try {
        const response = await authService.register({
          email: data.email,
          password: data.password,
          full_name: data.full_name,
        });

        // Store tokens securely
        setAuthToken(response.tokens.access_token);
        await secureStorage.setRefreshToken(response.tokens.refresh_token);

        // Fresh registration starts with onboarding pending
        const completedOnboarding = await secureStorage.getOnboardingCompleted();

        set({
          user: response.user,
          accessToken: response.tokens.access_token,
          isAuthenticated: true,
          hasCompletedOnboarding: completedOnboarding,
          isLoading: false,
        });
      } catch (err: any) {
        set({ isLoading: false });
        throw err;
      }
    },

    logout: async () => {
      set({ isLoading: true });
      try {
        const refreshToken = await secureStorage.getRefreshToken();
        await authService.logout(refreshToken);
      } catch {
        // Proceed with local logout regardless of network status
      } finally {
        await secureStorage.deleteRefreshToken();
        setAuthToken(null);
        queryClient.clear();
        set({
          user: null,
          accessToken: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    },

    restoreSession: async () => {
      set({ isRestoringSession: true });
      try {
        const storedRefreshToken = await secureStorage.getRefreshToken();
        if (!storedRefreshToken) {
          set({
            user: null,
            accessToken: null,
            isAuthenticated: false,
            isRestoringSession: false,
          });
          return;
        }

        // Check onboarding completion status
        const completedOnboarding = await secureStorage.getOnboardingCompleted();
        const savedPreferences = await secureStorage.getOnboardingPreferences<OnboardingPreferences>();

        // Attempt to fetch profile using client which auto-refreshes if needed
        // For fresh session restore, we use refresh endpoint directly
        const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${storedRefreshToken}`,
          },
        });

        if (!refreshRes.ok) {
          throw new Error('Refresh token invalid or expired');
        }

        const refreshData = await refreshRes.json();
        const newTokens = refreshData.data;

        setAuthToken(newTokens.access_token);
        await secureStorage.setRefreshToken(newTokens.refresh_token);

        // Fetch user profile with new access token
        const profile = await authService.getProfile();

        set({
          user: profile,
          accessToken: newTokens.access_token,
          isAuthenticated: true,
          hasCompletedOnboarding: completedOnboarding,
          onboardingPreferences: savedPreferences,
          isRestoringSession: false,
        });
      } catch {
        // On session restore failure, clear stale storage
        await secureStorage.deleteRefreshToken();
        setAuthToken(null);
        set({
          user: null,
          accessToken: null,
          isAuthenticated: false,
          isRestoringSession: false,
        });
      }
    },

    completeOnboarding: async (preferences: OnboardingPreferences) => {
      await secureStorage.setOnboardingCompleted(true);
      await secureStorage.setOnboardingPreferences(preferences);
      set({
        hasCompletedOnboarding: true,
        onboardingPreferences: preferences,
      });
    },

    setUser: (user: User) => set({ user }),
    clearError: () => set({ isLoading: false }),
  };
});

