import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { goalService } from '../services/goalService';
import {
  Goal,
  GoalMilestone,
  CreateGoalPayload,
  UpdateGoalPayload,
  CreateMilestonePayload,
  UpdateMilestonePayload,
  GoalFilterParams,
} from '../types/goal';
import { DASHBOARD_QUERY_KEY } from './useDashboard';

export const GOALS_QUERY_KEY = ['goals'];

export function useGoals(params?: GoalFilterParams) {
  return useQuery({
    queryKey: [...GOALS_QUERY_KEY, params],
    queryFn: () => goalService.getGoals(params),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

export function useGoalDetails(goalId: string | null) {
  return useQuery({
    queryKey: ['goalDetails', goalId],
    queryFn: () => goalService.getGoalDetails(goalId!),
    enabled: !!goalId,
  });
}

export function useCreateGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateGoalPayload) => goalService.createGoal(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GOALS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useUpdateGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      goalId,
      payload,
    }: {
      goalId: string;
      payload: UpdateGoalPayload;
    }) => goalService.updateGoal(goalId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: GOALS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['goalDetails', variables.goalId] });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useDeleteGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (goalId: string) => goalService.deleteGoal(goalId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GOALS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useCreateMilestone() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      goalId,
      payload,
    }: {
      goalId: string;
      payload: CreateMilestonePayload;
    }) => goalService.createMilestone(goalId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: GOALS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['goalDetails', variables.goalId] });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useUpdateMilestone() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      goalId,
      milestoneId,
      payload,
    }: {
      goalId: string;
      milestoneId: string;
      payload: UpdateMilestonePayload;
    }) => goalService.updateMilestone(goalId, milestoneId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: GOALS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['goalDetails', variables.goalId] });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useCompleteMilestone() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      goalId,
      milestoneId,
      isCompleted,
    }: {
      goalId: string;
      milestoneId: string;
      isCompleted: boolean;
    }) => goalService.completeMilestone(goalId, milestoneId, isCompleted),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: GOALS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['goalDetails', variables.goalId] });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useDeleteMilestone() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      goalId,
      milestoneId,
    }: {
      goalId: string;
      milestoneId: string;
    }) => goalService.deleteMilestone(goalId, milestoneId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: GOALS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['goalDetails', variables.goalId] });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

