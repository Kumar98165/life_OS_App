export type HabitFrequency = 'daily' | 'weekdays' | 'weekly';

export interface HabitLog {
  id: string;
  habit_id: string;
  log_date: string; // YYYY-MM-DD
  completed: boolean;
  notes?: string | null;
  created_at: string;
}

export interface Habit {
  id: string;
  user_id: string;
  title: string;
  description?: string | null;
  frequency: HabitFrequency;
  target_days_per_week: number;
  current_streak: number;
  longest_streak: number;
  color_hex: string;
  icon?: string | null;
  is_archived: boolean;
  completed_today?: boolean;
  today_log_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateHabitPayload {
  title: string;
  description?: string | null;
  frequency: HabitFrequency;
  target_days_per_week: number;
  color_hex: string;
  icon?: string | null;
}

export interface UpdateHabitPayload {
  title?: string;
  description?: string | null;
  frequency?: HabitFrequency;
  target_days_per_week?: number;
  color_hex?: string;
  icon?: string | null;
  is_archived?: boolean;
}

export interface HabitLogPayload {
  log_date?: string; // YYYY-MM-DD
  completed?: boolean;
  notes?: string | null;
}

export interface HabitStats {
  current_streak: number;
  longest_streak: number;
  total_completed_days: number;
  completion_rate: number;
  weekly_consistency: number;
  monthly_consistency: number;
}

export interface HabitStatsResponse {
  habit: Habit;
  stats: HabitStats;
  recent_logs: HabitLog[];
}

export interface DailyHabitSummary {
  date: string;
  scheduled_count: number;
  completed_count: number;
  completion_percentage: number;
  habits: Habit[];
}

export interface WeeklyHabitSummary {
  week_start: string;
  week_end: string;
  total_completed: number;
  total_scheduled: number;
  overall_percentage: number;
  days: Array<{
    date: string;
    day_name: string;
    scheduled_count: number;
    completed_count: number;
    completion_percentage: number;
  }>;
}

export interface MonthlyHabitSummary {
  year: number;
  month: number;
  total_habits: number;
  total_completed: number;
  total_scheduled: number;
  overall_percentage: number;
  days: Array<{
    date: string;
    day: number;
    completed_count: number;
    scheduled_count: number;
    completion_percentage: number;
  }>;
}

