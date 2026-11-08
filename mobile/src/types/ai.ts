export type AIMessageRole = 'user' | 'assistant' | 'system';

export interface AIMessage {
  id: string;
  conversation_id: string;
  role: AIMessageRole;
  content: string;
  tool_calls?: Record<string, any> | null;
  tokens_used?: number | null;
  created_at: string;
}

export interface AIConversation {
  id: string;
  user_id: string;
  title: string;
  model_used: string;
  messages_count?: number;
  created_at: string;
  updated_at: string;
}

export interface ChatResponse {
  conversation_id: string;
  conversation_title: string;
  user_message: AIMessage;
  assistant_message: AIMessage;
  response: string;
  intent: string;
}

export interface AIHealthStatus {
  healthy: boolean;
  model_available: boolean;
  status: 'operational' | 'model_missing' | 'degraded' | 'unreachable';
  model: string;
  available_models?: string[];
  base_url?: string;
  error?: string | null;
}

export interface AIFeedback {
  id: string;
  user_id: string;
  message_id: string;
  rating: number; // 1 or -1
  feedback_type?: string;
  category?: string;
  comment?: string;
  suggested_response?: string;
  created_at: string;
  updated_at: string;
}

export interface SubmitFeedbackPayload {
  message_id: string;
  rating: number; // 1 or -1
  feedback_type?: string;
  category?: string;
  comment?: string;
  suggested_response?: string;
}

export interface PrivacyConsentStatus {
  allow_training: boolean;
  user_id: string;
  updated_at?: string;
}


