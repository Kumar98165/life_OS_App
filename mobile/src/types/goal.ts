export type GoalPriority = 'low' | 'medium' | 'high';

export type GoalStatus =
  | 'not_started'
  | 'in_progress'
  | 'completed'
  | 'paused'
  | 'cancelled'
  | 'active'
  | 'achieved'
  | 'abandoned';

export interface GoalMilestone {
  id: string;
  goal_id: string;
  title: string;
  description?: string | null;
  target_date?: string | null;
  is_completed: boolean;
  completed_at?: string | null;
  sort_order: number;
  created_at: string;
  updated_at?: string | null;
}

export interface Goal {
  id: string;
  user_id: string;
  title: string;
  description?: string | null;
  target_date?: string | null;
  status: GoalStatus;
  priority: GoalPriority;
  progress_percent: number;
  category?: string | null;
  milestones?: GoalMilestone[];
  total_milestones?: number;
  completed_milestones?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateGoalPayload {
  title: string;
  description?: string | null;
  target_date?: string | null;
  priority?: GoalPriority;
  status?: GoalStatus;
  category?: string | null;
}

export interface UpdateGoalPayload {
  title?: string;
  description?: string | null;
  target_date?: string | null;
  priority?: GoalPriority;
  status?: GoalStatus;
  category?: string | null;
}

export interface CreateMilestonePayload {
  title: string;
  description?: string | null;
  target_date?: string | null;
  is_completed?: boolean;
  sort_order?: number;
}

export interface UpdateMilestonePayload {
  title?: string;
  description?: string | null;
  target_date?: string | null;
  is_completed?: boolean;
  sort_order?: number;
}

export interface GoalFilterParams {
  status?: string;
  priority?: string;
  category?: string;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  per_page?: number;
}

