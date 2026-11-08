import { apiClient } from '../api/client';
import { ApiResponse } from '../types';
import {
  Goal,
  GoalMilestone,
  CreateGoalPayload,
  UpdateGoalPayload,
  CreateMilestonePayload,
  UpdateMilestonePayload,
  GoalFilterParams,
} from '../types/goal';
import { PaginationMeta } from '../types/task';

export const goalService = {
  /**
   * Retrieve filtered and paginated goals for the authenticated user.
   */
  async getGoals(params?: GoalFilterParams): Promise<{ goals: Goal[]; meta: PaginationMeta }> {
    const response = await apiClient.get<ApiResponse<{ goals: Goal[] }>>('/goals', {
      params,
    });
    return {
      goals: response.data.data.goals,
      meta: (response.data.meta as PaginationMeta) || {
        page: 1,
        per_page: 20,
        total: response.data.data.goals.length,
        total_pages: 1,
        has_next: false,
        has_prev: false,
      },
    };
  },

  /**
   * Retrieve goal details including its milestones.
   */
  async getGoalDetails(goalId: string): Promise<Goal> {
    const response = await apiClient.get<ApiResponse<{ goal: Goal }>>(`/goals/${goalId}`);
    return response.data.data.goal;
  },

  /**
   * Create a new goal.
   */
  async createGoal(payload: CreateGoalPayload): Promise<Goal> {
    const response = await apiClient.post<ApiResponse<{ goal: Goal }>>('/goals', payload);
    return response.data.data.goal;
  },

  /**
   * Update an existing goal.
   */
  async updateGoal(goalId: string, payload: UpdateGoalPayload): Promise<Goal> {
    const response = await apiClient.patch<ApiResponse<{ goal: Goal }>>(`/goals/${goalId}`, payload);
    return response.data.data.goal;
  },

  /**
   * Delete a goal.
   */
  async deleteGoal(goalId: string): Promise<void> {
    await apiClient.delete(`/goals/${goalId}`);
  },

  /**
   * List milestones for a goal.
   */
  async getMilestones(goalId: string): Promise<GoalMilestone[]> {
    const response = await apiClient.get<ApiResponse<{ milestones: GoalMilestone[] }>>(
      `/goals/${goalId}/milestones`
    );
    return response.data.data.milestones;
  },

  /**
   * Create a milestone under a goal.
   */
  async createMilestone(
    goalId: string,
    payload: CreateMilestonePayload
  ): Promise<{ milestone: GoalMilestone; goal: Goal }> {
    const response = await apiClient.post<
      ApiResponse<{ milestone: GoalMilestone; goal: Goal }>
    >(`/goals/${goalId}/milestones`, payload);
    return response.data.data;
  },

  /**
   * Update milestone details.
   */
  async updateMilestone(
    goalId: string,
    milestoneId: string,
    payload: UpdateMilestonePayload
  ): Promise<{ milestone: GoalMilestone; goal: Goal }> {
    const response = await apiClient.patch<
      ApiResponse<{ milestone: GoalMilestone; goal: Goal }>
    >(`/goals/${goalId}/milestones/${milestoneId}`, payload);
    return response.data.data;
  },

  /**
   * Complete or reopen a milestone.
   */
  async completeMilestone(
    goalId: string,
    milestoneId: string,
    isCompleted: boolean
  ): Promise<{ milestone: GoalMilestone; goal: Goal }> {
    const response = await apiClient.patch<
      ApiResponse<{ milestone: GoalMilestone; goal: Goal }>
    >(`/goals/${goalId}/milestones/${milestoneId}/complete`, {
      is_completed: isCompleted,
    });
    return response.data.data;
  },

  /**
   * Delete a milestone.
   */
  async deleteMilestone(goalId: string, milestoneId: string): Promise<{ goal: Goal }> {
    const response = await apiClient.delete<ApiResponse<{ goal: Goal }>>(
      `/goals/${goalId}/milestones/${milestoneId}`
    );
    return response.data.data;
  },
};

