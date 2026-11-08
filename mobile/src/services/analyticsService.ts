import { apiClient } from '../api/client';
import { ApiResponse } from '../types';
import {
  DateRangeParams,
  AnalyticsOverviewResponse,
  ProductivityAnalytics,
  HabitAnalytics,
  GoalAnalytics,
  FinancialAnalytics,
  TrendsAnalyticsResponse,
  LifeScoreResponse,
  AIInsightsResponse,
} from '../types/analytics';

export const analyticsService = {
  /**
   * Fetch high-level multi-domain dashboard summary.
   */
  async getOverview(params?: DateRangeParams): Promise<AnalyticsOverviewResponse> {
    const response = await apiClient.get<ApiResponse<AnalyticsOverviewResponse>>(
      '/analytics/overview',
      { params }
    );
    return response.data.data;
  },

  /**
   * Fetch productivity analytics (Tasks & Planner).
   */
  async getProductivity(params?: DateRangeParams): Promise<ProductivityAnalytics> {
    const response = await apiClient.get<ApiResponse<ProductivityAnalytics>>(
      '/analytics/productivity',
      { params }
    );
    return response.data.data;
  },

  /**
   * Fetch habit consistency, adherence, and streak metrics.
   */
  async getHabits(params?: DateRangeParams): Promise<HabitAnalytics> {
    const response = await apiClient.get<ApiResponse<HabitAnalytics>>(
      '/analytics/habits',
      { params }
    );
    return response.data.data;
  },

  /**
   * Fetch goals progress, milestones velocity, and deadlines.
   */
  async getGoals(): Promise<GoalAnalytics> {
    const response = await apiClient.get<ApiResponse<GoalAnalytics>>('/analytics/goals');
    return response.data.data;
  },

  /**
   * Fetch personal finance cash flow, category spending, and savings rate.
   */
  async getFinance(params?: DateRangeParams): Promise<FinancialAnalytics> {
    const response = await apiClient.get<ApiResponse<FinancialAnalytics>>(
      '/analytics/finance',
      { params }
    );
    return response.data.data;
  },

  /**
   * Fetch multi-domain daily completion trends.
   */
  async getTrends(params?: DateRangeParams): Promise<TrendsAnalyticsResponse> {
    const response = await apiClient.get<ApiResponse<TrendsAnalyticsResponse>>(
      '/analytics/trends',
      { params }
    );
    return response.data.data;
  },

  /**
   * Calculate transparent 4-pillar Life Score.
   */
  async getLifeScore(params?: DateRangeParams): Promise<LifeScoreResponse> {
    const response = await apiClient.get<ApiResponse<LifeScoreResponse>>(
      '/analytics/life-score',
      { params }
    );
    return response.data.data;
  },

  /**
   * Synthesize narrative personal insights and actionable tips via local Ollama.
   */
  async getAIInsights(params?: DateRangeParams): Promise<AIInsightsResponse> {
    const response = await apiClient.get<ApiResponse<AIInsightsResponse>>(
      '/analytics/insights',
      { params }
    );
    return response.data.data;
  },
};

