import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services/dashboardService';
import { DashboardData } from '../types';

export const DASHBOARD_QUERY_KEY = ['dashboardOverview'];

export function useDashboard() {
  const query = useQuery<DashboardData, Error>({
    queryKey: DASHBOARD_QUERY_KEY,
    queryFn: () => dashboardService.getDashboardOverview(),
    staleTime: 1000 * 60 * 2, // 2 minutes
    retry: 2,
  });

  return {
    dashboardData: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
    isRefetching: query.isRefetching,
  };
}

