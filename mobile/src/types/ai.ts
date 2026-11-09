export type AIMessageRole = 'user' | 'assistant' | 'system';

export interface AIMessage {
  id: string;
  conversation_id: string;
  role: AIMessageRole;
  content: string;
  tool_calls?: Record<string, any> | null;
  tokens_used?: number | null;
  latency_ms?: number | null;
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

export interface ProactiveInsight {
  id: string;
  type: string;
  category: 'schedule' | 'tasks' | 'habits' | 'goals' | 'planner';
  severity: 'warning' | 'info' | 'nudge' | 'celebration' | 'suggestion';
  title: string;
  message: string;
  actionable: boolean;
  target_screen?: string;
}

export interface DailyBriefing {
  user_id: string;
  date: string;
  timezone: string;
  greeting: string;
  schedule_summary: {
    total_blocks: number;
    has_conflicts: boolean;
    conflicts: Array<{ block_1: string; block_2: string; time_overlap: string }>;
    blocks: any[];
  };
  task_summary: {
    total_today: number;
    completed_today: number;
    pending_priority_count: number;
    approaching_deadlines_count: number;
    today_tasks: any[];
    top_pending: any[];
    approaching_deadlines: any[];
  };
  habit_summary: {
    total_habits: number;
    completed_today: number;
    habits: any[];
  };
  goal_summary: {
    active_goals_count: number;
    goals: any[];
  };
  priority_suggestions: string[];
}

export interface FeedbackImprovementRecommendation {
  area: string;
  recommendation: string;
  severity: 'high' | 'medium' | 'low' | 'info';
}

export interface FeedbackAnalytics {
  user_id: string;
  window_days: number;
  total_feedback_count: number;
  positive_count: number;
  negative_count: number;
  satisfaction_percentage: number | null;
  negative_categories: Record<string, number>;
  feedback_types: Record<string, number>;
  improvement_recommendations: FeedbackImprovementRecommendation[];
}



