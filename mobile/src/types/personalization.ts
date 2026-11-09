export interface DashboardWidgetItem {
  id: string;
  visible: boolean;
  order: number;
  title: string;
}

export interface UserPersonalization {
  id: string;
  user_id: string;
  preferred_name: string | null;
  preferred_language: 'en' | 'hi' | 'hinglish' | 'es' | 'fr' | 'de';
  timezone: string;
  date_format: 'YYYY-MM-DD' | 'DD/MM/YYYY' | 'MM/DD/YYYY';
  time_format: '12h' | '24h';
  week_start_day: 'monday' | 'sunday';
  productivity_style: 'structured' | 'flexible' | 'pomodoro' | 'deep_work';
  task_priority_strategy: 'eisenhower' | 'deadline_first' | 'impact_first' | 'quick_wins';
  ai_response_style: 'concise' | 'detailed' | 'motivational' | 'formal';
  ai_response_length: 'short' | 'medium' | 'comprehensive';
  dashboard_widgets: DashboardWidgetItem[];
  dashboard_density: 'compact' | 'comfortable';
  personalization_enabled: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface DailyRoutine {
  id: string;
  user_id: string;
  wake_time: string;
  sleep_time: string;
  work_start: string;
  work_end: string;
  work_days: string[];
  focus_block_duration_minutes: number;
  break_duration_minutes: number;
  lunch_start: string;
  lunch_duration_minutes: number;
  morning_routine_enabled: boolean;
  evening_routine_enabled: boolean;
  preferred_planning_time: string;
  routine_reminders_enabled: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface UpdatePersonalizationPayload {
  preferred_name?: string | null;
  preferred_language?: string;
  timezone?: string;
  date_format?: string;
  time_format?: string;
  week_start_day?: string;
  productivity_style?: string;
  task_priority_strategy?: string;
  ai_response_style?: string;
  ai_response_length?: string;
  personalization_enabled?: boolean;
}

export interface UpdateDashboardPayload {
  dashboard_widgets?: DashboardWidgetItem[];
  dashboard_density?: 'compact' | 'comfortable';
}

export interface UpdateDailyRoutinePayload {
  wake_time?: string;
  sleep_time?: string;
  work_start?: string;
  work_end?: string;
  work_days?: string[];
  focus_block_duration_minutes?: number;
  break_duration_minutes?: number;
  lunch_start?: string;
  lunch_duration_minutes?: number;
  morning_routine_enabled?: boolean;
  evening_routine_enabled?: boolean;
  preferred_planning_time?: string;
  routine_reminders_enabled?: boolean;
}
