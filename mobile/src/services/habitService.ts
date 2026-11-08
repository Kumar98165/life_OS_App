import { apiClient } from '../api/client';
import { ApiResponse } from '../types';
import {
  Habit,
  HabitLog,
  CreateHabitPayload,
  UpdateHabitPayload,
  HabitLogPayload,
  HabitStatsResponse,
  DailyHabitSummary,
  WeeklyHabitSummary,
  MonthlyHabitSummary,
  HabitFrequency,
} from '../types/habit';

export const habitService = {
  /**
   * Retrieve habits for authenticated user.
   */
  async getHabits(params?: {
    include_archived?: boolean;
    frequency?: HabitFrequency;
  }): Promise<Habit[]> {
    const response = await apiClient.get<ApiResponse<{ habits: Habit[] }>>('/habits', {
      params,
    });
    return response.data.data.habits;
  },

  /**
   * Retrieve single habit details.
   */
  async getHabitDetails(habitId: string): Promise<Habit> {
    const response = await apiClient.get<ApiResponse<{ habit: Habit }>>(`/habits/${habitId}`);
    return response.data.data.habit;
  },

  /**
   * Create a new habit.
   */
  async createHabit(payload: CreateHabitPayload): Promise<Habit> {
    const response = await apiClient.post<ApiResponse<{ habit: Habit }>>('/habits', payload);
    return response.data.data.habit;
  },

  /**
   * Update an existing habit.
   */
  async updateHabit(habitId: string, payload: UpdateHabitPayload): Promise<Habit> {
    const response = await apiClient.patch<ApiResponse<{ habit: Habit }>>(
      `/habits/${habitId}`,
      payload
    );
    return response.data.data.habit;
  },

  /**
   * Delete a habit.
   */
  async deleteHabit(habitId: string): Promise<void> {
    await apiClient.delete<ApiResponse<null>>(`/habits/${habitId}`);
  },

  /**
   * Check in for a habit on a given date (defaults to today).
   */
  async logCheckIn(
    habitId: string,
    payload?: HabitLogPayload
  ): Promise<{ log: HabitLog; habit: Habit }> {
    const response = await apiClient.post<ApiResponse<{ log: HabitLog; habit: Habit }>>(
      `/habits/${habitId}/logs`,
      payload || {}
    );
    return response.data.data;
  },

  /**
   * Undo a check-in log.
   */
  async undoCheckIn(habitId: string, logId: string): Promise<{ habit: Habit }> {
    const response = await apiClient.delete<ApiResponse<{ habit: Habit }>>(
      `/habits/${habitId}/logs/${logId}`
    );
    return response.data.data;
  },

  /**
   * Retrieve check-in logs for a habit.
   */
  async getHabitLogs(
    habitId: string,
    params?: { start_date?: string; end_date?: string; limit?: number }
  ): Promise<HabitLog[]> {
    const response = await apiClient.get<ApiResponse<{ logs: HabitLog[] }>>(
      `/habits/${habitId}/logs`,
      { params }
    );
    return response.data.data.logs;
  },

  /**
   * Retrieve statistics and streak breakdown for a habit.
   */
  async getHabitStats(habitId: string): Promise<HabitStatsResponse> {
    const response = await apiClient.get<ApiResponse<HabitStatsResponse>>(
      `/habits/${habitId}/stats`
    );
    return response.data.data;
  },

  /**
   * Retrieve daily completion summary across all active habits.
   */
  async getDailySummary(date?: string): Promise<DailyHabitSummary> {
    const response = await apiClient.get<ApiResponse<DailyHabitSummary>>('/habits/summary/daily', {
      params: date ? { date } : undefined,
    });
    return response.data.data;
  },

  /**
   * Retrieve weekly completion summary across 7 days.
   */
  async getWeeklySummary(weekStart?: string): Promise<WeeklyHabitSummary> {
    const response = await apiClient.get<ApiResponse<WeeklyHabitSummary>>(
      '/habits/summary/weekly',
      {
        params: weekStart ? { week_start: weekStart } : undefined,
      }
    );
    return response.data.data;
  },

  /**
   * Retrieve monthly completion breakdown by day.
   */
  async getMonthlySummary(year?: number, month?: number): Promise<MonthlyHabitSummary> {
    const response = await apiClient.get<ApiResponse<MonthlyHabitSummary>>(
      '/habits/summary/monthly',
      {
        params: { year, month },
      }
    );
    return response.data.data;
  },
};

