export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  message: string;
  data: T;
  meta?: Record<string, any>;
  code?: number;
  errors?: Array<{ field?: string; message: string }>;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string | null;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

export * from './task';
export * from './auth';
export * from './dashboard';
export * from './planner';
export * from './goal';
export * from './habit';
export * from './extensions';
export * from './people';
export * from './focus';

export interface Note {
  id: string;
  user_id: string;
  title: string;
  content: string;
  tags: string[];
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

export * from './auth';
export * from './dashboard';
export * from './task';




