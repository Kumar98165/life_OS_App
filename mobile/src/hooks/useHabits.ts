import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { habitService } from '../services/habitService';
import {
  CreateHabitPayload,
  UpdateHabitPayload,
  HabitLogPayload,
  HabitFrequency,
} from '../types/habit';
import { DASHBOARD_QUERY_KEY } from './useDashboard';

export const HABITS_QUERY_KEY = ['habits'];
export const HABIT_SUMMARY_QUERY_KEY = ['habitSummary'];

export function useHabits(params?: {
  include_archived?: boolean;
  frequency?: HabitFrequency;
}) {
  return useQuery({
    queryKey: [...HABITS_QUERY_KEY, params],
    queryFn: () => habitService.getHabits(params),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

export function useHabitDetails(habitId: string | null) {
  return useQuery({
    queryKey: ['habitDetails', habitId],
    queryFn: () => habitService.getHabitDetails(habitId!),
    enabled: !!habitId,
  });
}

export function useHabitStats(habitId: string | null) {
  return useQuery({
    queryKey: ['habitStats', habitId],
    queryFn: () => habitService.getHabitStats(habitId!),
    enabled: !!habitId,
  });
}

export function useHabitDailySummary(date?: string) {
  return useQuery({
    queryKey: [...HABIT_SUMMARY_QUERY_KEY, 'daily', date],
    queryFn: () => habitService.getDailySummary(date),
    staleTime: 1000 * 60 * 1, // 1 minute
  });
}

export function useHabitWeeklySummary(weekStart?: string) {
  return useQuery({
    queryKey: [...HABIT_SUMMARY_QUERY_KEY, 'weekly', weekStart],
    queryFn: () => habitService.getWeeklySummary(weekStart),
  });
}

export function useHabitMonthlySummary(year?: number, month?: number) {
  return useQuery({
    queryKey: [...HABIT_SUMMARY_QUERY_KEY, 'monthly', year, month],
    queryFn: () => habitService.getMonthlySummary(year, month),
  });
}

export function useCreateHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateHabitPayload) => habitService.createHabit(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: HABITS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: HABIT_SUMMARY_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useUpdateHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      habitId,
      payload,
    }: {
      habitId: string;
      payload: UpdateHabitPayload;
    }) => habitService.updateHabit(habitId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: HABITS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['habitDetails', variables.habitId] });
      queryClient.invalidateQueries({ queryKey: ['habitStats', variables.habitId] });
      queryClient.invalidateQueries({ queryKey: HABIT_SUMMARY_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useDeleteHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (habitId: string) => habitService.deleteHabit(habitId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: HABITS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: HABIT_SUMMARY_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useHabitCheckIn() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      habitId,
      payload,
    }: {
      habitId: string;
      payload?: HabitLogPayload;
    }) => habitService.logCheckIn(habitId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: HABITS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['habitDetails', variables.habitId] });
      queryClient.invalidateQueries({ queryKey: ['habitStats', variables.habitId] });
      queryClient.invalidateQueries({ queryKey: HABIT_SUMMARY_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useUndoHabitCheckIn() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      habitId,
      logId,
    }: {
      habitId: string;
      logId: string;
    }) => habitService.undoCheckIn(habitId, logId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: HABITS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['habitDetails', variables.habitId] });
      queryClient.invalidateQueries({ queryKey: ['habitStats', variables.habitId] });
      queryClient.invalidateQueries({ queryKey: HABIT_SUMMARY_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

