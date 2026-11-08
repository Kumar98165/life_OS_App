import { Task } from './task';

export type PlannerBlockType =
  | 'task'
  | 'personal'
  | 'work'
  | 'break'
  | 'learning'
  | 'meeting'
  | 'other'
  | 'focus'
  | 'routine';

export type PlannerBlockStatus = 'scheduled' | 'completed' | 'cancelled' | 'skipped';

export interface PlannerBlock {
  id: string;
  user_id: string;
  task_id?: string | null;
  task?: Task | null;
  title: string;
  description?: string | null;
  start_time: string;
  end_time: string;
  block_type: PlannerBlockType;
  status: PlannerBlockStatus;
  color_hex?: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreatePlannerBlockPayload {
  title: string;
  description?: string | null;
  start_time: string;
  end_time: string;
  block_type?: PlannerBlockType;
  status?: PlannerBlockStatus;
  task_id?: string | null;
  color_hex?: string | null;
}

export interface UpdatePlannerBlockPayload {
  title?: string;
  description?: string | null;
  start_time?: string;
  end_time?: string;
  block_type?: PlannerBlockType;
  status?: PlannerBlockStatus;
  task_id?: string | null;
  color_hex?: string | null;
}

export interface PlannerFilterParams {
  start_date?: string;
  end_date?: string;
  status?: string;
  block_type?: string;
  task_id?: string;
  page?: number;
  per_page?: number;
}

export interface PlannerDailySummary {
  date: string;
  total_blocks: number;
  completed_blocks: number;
  scheduled_blocks: number;
  cancelled_blocks: number;
  skipped_blocks: number;
  total_scheduled_minutes: number;
  completion_rate: number;
  next_upcoming_block?: PlannerBlock | null;
  blocks: PlannerBlock[];
}

