import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '../services/analyticsService';
import { DateRangeParams } from '../types/analytics';

export const ANALYTICS_QUERY_KEYS = {
  all: ['analytics'] as const,
  overview: (params?: DateRangeParams) => ['analytics', 'overview', params] as const,
  productivity: (params?: DateRangeParams) => ['analytics', 'productivity', params] as const,
  habits: (params?: DateRangeParams) => ['analytics', 'habits', params] as const,
  goals: () => ['analytics', 'goals'] as const,
  finance: (params?: DateRangeParams) => ['analytics', 'finance', params] as const,
  trends: (params?: DateRangeParams) => ['analytics', 'trends', params] as const,
  lifeScore: (params?: DateRangeParams) => ['analytics', 'lifeScore', params] as const,
  insights: (params?: DateRangeParams) => ['analytics', 'insights', params] as const,
};

export function useAnalyticsOverview(params?: DateRangeParams) {
  return useQuery({
    queryKey: ANALYTICS_QUERY_KEYS.overview(params),
    queryFn: () => analyticsService.getOverview(params),
    staleTime: 1000 * 60, // 1 minute
  });
}

export function useProductivityAnalytics(params?: DateRangeParams) {
  return useQuery({
    queryKey: ANALYTICS_QUERY_KEYS.productivity(params),
    queryFn: () => analyticsService.getProductivity(params),
    staleTime: 1000 * 60,
  });
}

export function useHabitAnalytics(params?: DateRangeParams) {
  return useQuery({
    queryKey: ANALYTICS_QUERY_KEYS.habits(params),
    queryFn: () => analyticsService.getHabits(params),
    staleTime: 1000 * 60,
  });
}

export function useGoalAnalytics() {
  return useQuery({
    queryKey: ANALYTICS_QUERY_KEYS.goals(),
    queryFn: () => analyticsService.getGoals(),
    staleTime: 1000 * 60,
  });
}

export function useFinancialAnalytics(params?: DateRangeParams) {
  return useQuery({
    queryKey: ANALYTICS_QUERY_KEYS.finance(params),
    queryFn: () => analyticsService.getFinance(params),
    staleTime: 1000 * 60,
  });
}

export function useTrendsAnalytics(params?: DateRangeParams) {
  return useQuery({
    queryKey: ANALYTICS_QUERY_KEYS.trends(params),
    queryFn: () => analyticsService.getTrends(params),
    staleTime: 1000 * 60,
  });
}

export function useLifeScore(params?: DateRangeParams) {
  return useQuery({
    queryKey: ANALYTICS_QUERY_KEYS.lifeScore(params),
    queryFn: () => analyticsService.getLifeScore(params),
    staleTime: 1000 * 60,
  });
}

export function useAIInsights(params?: DateRangeParams) {
  return useQuery({
    queryKey: ANALYTICS_QUERY_KEYS.insights(params),
    queryFn: () => analyticsService.getAIInsights(params),
    staleTime: 1000 * 60 * 5, // 5 minutes (LLM heavy)
  });
}

