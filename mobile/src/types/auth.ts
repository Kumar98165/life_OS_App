import { User, AuthTokens } from './index';

export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  full_name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface OnboardingPreferences {
  focusAreas: string[];
  initialGoals: string[];
  themePreference: 'light' | 'dark' | 'system';
  notificationFrequency: 'realtime' | 'daily_summary' | 'quiet';
  aiInteractionStyle: 'concise' | 'balanced' | 'comprehensive';
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isRestoringSession: boolean;
  hasCompletedOnboarding: boolean;
  onboardingPreferences: OnboardingPreferences | null;
}

