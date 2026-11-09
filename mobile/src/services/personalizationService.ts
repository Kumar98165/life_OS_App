import { apiClient } from '../api/client';
import {
  UserPersonalization,
  DailyRoutine,
  UpdatePersonalizationPayload,
  UpdateDashboardPayload,
  UpdateDailyRoutinePayload,
  DashboardWidgetItem,
} from '../types/personalization';

export const personalizationService = {
  /**
   * Fetch complete user personalization & daily routine configuration.
   */
  async getPersonalization(): Promise<{
    personalization: UserPersonalization;
    daily_routine: DailyRoutine;
  }> {
    const res = await apiClient.get<{
      data: {
        personalization: UserPersonalization;
        daily_routine: DailyRoutine;
      };
    }>('/personalization');
    return res.data.data;
  },

  /**
   * Update identity, regional, productivity, or AI response styles.
   */
  async updatePersonalization(payload: UpdatePersonalizationPayload): Promise<UserPersonalization> {
    const res = await apiClient.patch<{ data: UserPersonalization }>('/personalization', payload);
    return res.data.data;
  },

  /**
   * Fetch customized dashboard widget configurations.
   */
  async getDashboardPreferences(): Promise<{
    dashboard_widgets: DashboardWidgetItem[];
    dashboard_density: 'compact' | 'comfortable';
  }> {
    const res = await apiClient.get<{
      data: {
        dashboard_widgets: DashboardWidgetItem[];
        dashboard_density: 'compact' | 'comfortable';
      };
    }>('/personalization/dashboard');
    return res.data.data;
  },

  /**
   * Update dashboard widget visibility, order, and layout density.
   */
  async updateDashboardPreferences(payload: UpdateDashboardPayload): Promise<{
    dashboard_widgets: DashboardWidgetItem[];
    dashboard_density: 'compact' | 'comfortable';
  }> {
    const res = await apiClient.patch<{
      data: {
        dashboard_widgets: DashboardWidgetItem[];
        dashboard_density: 'compact' | 'comfortable';
      };
    }>('/personalization/dashboard', payload);
    return res.data.data;
  },

  /**
   * Fetch daily routine schedule.
   */
  async getDailyRoutine(): Promise<DailyRoutine> {
    const res = await apiClient.get<{ data: DailyRoutine }>('/personalization/routine');
    return res.data.data;
  },

  /**
   * Update daily routine work hours, break intervals, or rituals.
   */
  async updateDailyRoutine(payload: UpdateDailyRoutinePayload): Promise<DailyRoutine> {
    const res = await apiClient.patch<{ data: DailyRoutine }>('/personalization/routine', payload);
    return res.data.data;
  },

  /**
   * Reset specific category of preferences to system defaults.
   */
  async resetPreferences(target: 'all' | 'dashboard' | 'routine' | 'identity' | 'ai_style'): Promise<{
    personalization: UserPersonalization;
    daily_routine: DailyRoutine;
    reset_target: string;
  }> {
    const res = await apiClient.post<{
      data: {
        personalization: UserPersonalization;
        daily_routine: DailyRoutine;
        reset_target: string;
      };
    }>('/personalization/reset', { target });
    return res.data.data;
  },
};
