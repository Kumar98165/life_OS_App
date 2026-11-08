import { apiClient } from '../api/client';
import { ApiResponse } from '../types';
import {
  Task,
  TaskCategory,
  CreateTaskPayload,
  UpdateTaskPayload,
  TaskFilterParams,
  PaginationMeta,
} from '../types/task';

export const taskService = {
  /**
   * Retrieve paginated and filtered tasks for the authenticated user.
   */
  async getTasks(params?: TaskFilterParams): Promise<{ tasks: Task[]; meta: PaginationMeta }> {
    const response = await apiClient.get<ApiResponse<{ tasks: Task[] }>>('/tasks', {
      params,
    });
    return {
      tasks: response.data.data.tasks,
      meta: (response.data.meta as PaginationMeta) || {
        page: 1,
        per_page: 20,
        total: response.data.data.tasks.length,
        total_pages: 1,
        has_next: false,
        has_prev: false,
      },
    };
  },

  /**
   * Retrieve single task details by ID.
   */
  async getTaskDetails(taskId: string): Promise<Task> {
    const response = await apiClient.get<ApiResponse<{ task: Task }>>(`/tasks/${taskId}`);
    return response.data.data.task;
  },

  /**
   * Create a new task.
   */
  async createTask(payload: CreateTaskPayload): Promise<Task> {
    const response = await apiClient.post<ApiResponse<{ task: Task }>>('/tasks', payload);
    return response.data.data.task;
  },

  /**
   * Update task attributes.
   */
  async updateTask(taskId: string, payload: UpdateTaskPayload): Promise<Task> {
    const response = await apiClient.patch<ApiResponse<{ task: Task }>>(`/tasks/${taskId}`, payload);
    return response.data.data.task;
  },

  /**
   * Toggle task completion state.
   */
  async toggleCompleteTask(taskId: string): Promise<Task> {
    const response = await apiClient.patch<ApiResponse<{ task: Task }>>(`/tasks/${taskId}/complete`);
    return response.data.data.task;
  },

  /**
   * Delete a task.
   */
  async deleteTask(taskId: string): Promise<void> {
    await apiClient.delete(`/tasks/${taskId}`);
  },

  /**
   * Retrieve all categories for the authenticated user.
   */
  async getCategories(): Promise<TaskCategory[]> {
    const response = await apiClient.get<ApiResponse<{ categories: TaskCategory[] }>>('/tasks/categories');
    return response.data.data.categories;
  },

  /**
   * Create a new custom category.
   */
  async createCategory(payload: { name: string; color_hex?: string; icon?: string }): Promise<TaskCategory> {
    const response = await apiClient.post<ApiResponse<{ category: TaskCategory }>>('/tasks/categories', payload);
    return response.data.data.category;
  },
};

