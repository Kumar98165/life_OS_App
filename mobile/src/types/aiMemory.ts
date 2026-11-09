/**
 * LifeOS - AI Memory System Type Definitions
 */

export type AIMemoryCategory =
  | 'preference'
  | 'personal_context'
  | 'goal_decision'
  | 'routine_pattern'
  | 'fact';

export type AIMemoryStatus = 'pending' | 'confirmed' | 'archived' | 'rejected';

export interface AIMemory {
  id: string;
  user_id: string;
  memory_key: string;
  memory_value: string;
  memory_type: AIMemoryCategory;
  confidence: number;
  status: AIMemoryStatus;
  source_conversation_id?: string | null;
  source_message_id?: string | null;
  embedding?: Record<string, any> | null;
  last_accessed_at?: string | null;
  expires_at?: string | null;
  created_at: string;
  updated_at?: string;
}

export interface CreateMemoryPayload {
  memory_key: string;
  memory_value: string;
  memory_type: AIMemoryCategory;
  confidence?: number;
  expires_at?: string | null;
}

export interface UpdateMemoryPayload {
  memory_key?: string;
  memory_value?: string;
  memory_type?: AIMemoryCategory;
  confidence?: number;
  status?: AIMemoryStatus;
  expires_at?: string | null;
}

export interface ApproveSuggestionPayload {
  memory_key?: string;
  memory_value?: string;
  memory_type?: AIMemoryCategory;
  edited_key?: string;
  edited_value?: string;
  edited_type?: AIMemoryCategory;
  supersede_existing_id?: string;
}

export interface MemorySettings {
  ai_memory_enabled: boolean;
  privacy_notice?: string;
}

export interface MemoryListResponse {
  memories: AIMemory[];
  total: number;
  limit: number;
  offset: number;
}

export interface SuggestionListResponse {
  suggestions: AIMemory[];
  total: number;
  limit: number;
  offset: number;
}

