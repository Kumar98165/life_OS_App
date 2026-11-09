import { Task } from './task';

export type FocusSessionType = 'work' | 'short_break' | 'long_break';
export type FocusSessionStatus = 'active' | 'paused' | 'completed' | 'cancelled';
export type DistractionType = 'internal' | 'external';

export interface FocusGoal {
  id: string;
  user_id: string;
  daily_target_minutes: number;
  weekly_target_minutes: number;
  preferred_technique: string; // '25/5' | '50/10' | 'custom'
  custom_work_minutes: number;
  custom_break_minutes: number;
  custom_long_break_minutes: number;
  long_break_interval: number;
  created_at: string;
  updated_at: string;
}

export interface FocusDistraction {
  id: string;
  focus_session_id: string;
  user_id: string;
  distraction_type: DistractionType;
  description: string;
  logged_at: string;
  created_at: string;
}

export interface FocusSession {
  id: string;
  user_id: string;
  task_id?: string | null;
  task?: Task | null;
  planner_block_id?: string | null;
  title: string;
  session_type: FocusSessionType;
  target_duration_minutes: number;
  actual_duration_seconds: number;
  status: FocusSessionStatus;
  start_time: string;
  end_time?: string | null;
  paused_at?: string | null;
  notes?: string | null;
  distraction_count: number;
  distractions?: FocusDistraction[];
  created_at: string;
  updated_at: string;
}

export interface FocusStats {
  today_minutes: number;
  today_target_minutes: number;
  today_progress_pct: number;
  week_minutes: number;
  week_target_minutes: number;
  week_progress_pct: number;
  total_focused_hours: number;
  completed_sessions_today: number;
  distractions_logged_today: number;
  goal: FocusGoal;
}

export interface FreeTimeSlot {
  start_time: string;
  end_time: string;
  duration_minutes: number;
}
