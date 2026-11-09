import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { personalizationService } from '../services/personalizationService';
import {
  UpdatePersonalizationPayload,
  UpdateDashboardPayload,
  UpdateDailyRoutinePayload,
} from '../types/personalization';

export const PERSONALIZATION_QUERY_KEYS = {
  all: ['personalization'] as const,
  dashboard: ['personalization', 'dashboard'] as const,
  routine: ['personalization', 'routine'] as const,
};

export function usePersonalization() {
  return useQuery({
    queryKey: PERSONALIZATION_QUERY_KEYS.all,
    queryFn: () => personalizationService.getPersonalization(),
  });
}

export function useDashboardPreferences() {
  return useQuery({
    queryKey: PERSONALIZATION_QUERY_KEYS.dashboard,
    queryFn: () => personalizationService.getDashboardPreferences(),
  });
}

export function useDailyRoutine() {
  return useQuery({
    queryKey: PERSONALIZATION_QUERY_KEYS.routine,
    queryFn: () => personalizationService.getDailyRoutine(),
  });
}

export function useUpdatePersonalization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UpdatePersonalizationPayload) =>
      personalizationService.updatePersonalization(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PERSONALIZATION_QUERY_KEYS.all });
    },
  });
}

export function useUpdateDashboardPreferences() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UpdateDashboardPayload) =>
      personalizationService.updateDashboardPreferences(payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(PERSONALIZATION_QUERY_KEYS.dashboard, updated);
      queryClient.invalidateQueries({ queryKey: PERSONALIZATION_QUERY_KEYS.all });
    },
  });
}

export function useUpdateDailyRoutine() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UpdateDailyRoutinePayload) =>
      personalizationService.updateDailyRoutine(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PERSONALIZATION_QUERY_KEYS.routine });
      queryClient.invalidateQueries({ queryKey: PERSONALIZATION_QUERY_KEYS.all });
    },
  });
}

export function useResetPreferences() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (target: 'all' | 'dashboard' | 'routine' | 'identity' | 'ai_style') =>
      personalizationService.resetPreferences(target),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PERSONALIZATION_QUERY_KEYS.all });
      queryClient.invalidateQueries({ queryKey: PERSONALIZATION_QUERY_KEYS.dashboard });
      queryClient.invalidateQueries({ queryKey: PERSONALIZATION_QUERY_KEYS.routine });
    },
  });
}
