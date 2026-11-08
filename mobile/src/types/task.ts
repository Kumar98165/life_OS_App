export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';
export type TaskStatus = 'pending' | 'todo' | 'in_progress' | 'completed' | 'cancelled' | 'archived';

export interface TaskCategory {
  id: string;
  user_id: string;
  name: string;
  color_hex: string;
  icon?: string | null;
  created_at?: string | null;
}

export interface Task {
  id: string;
  user_id: string;
  category_id?: string | null;
  category?: TaskCategory | null;
  title: string;
  description?: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string | null;
  completed_at?: string | null;
  is_archived?: boolean;
  estimated_minutes?: number | null;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskPayload {
  title: string;
  description?: string | null;
  category_id?: string | null;
  priority?: TaskPriority;
  status?: TaskStatus;
  due_date?: string | null;
  estimated_minutes?: number | null;
}

export interface UpdateTaskPayload {
  title?: string;
  description?: string | null;
  category_id?: string | null;
  priority?: TaskPriority;
  status?: TaskStatus;
  due_date?: string | null;
  estimated_minutes?: number | null;
  is_archived?: boolean;
}

export interface TaskFilterParams {
  status?: string;
  priority?: string;
  category_id?: string;
  search?: string;
  due_date?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  per_page?: number;
}

export interface PaginationMeta {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

