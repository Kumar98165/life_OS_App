import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { plannerService } from '../services/plannerService';
import {
  PlannerBlock,
  PlannerFilterParams,
  CreatePlannerBlockPayload,
  UpdatePlannerBlockPayload,
  PlannerBlockStatus,
} from '../types/planner';
import { DASHBOARD_QUERY_KEY } from './useDashboard';
import { TASKS_QUERY_KEY } from './useTasks';

export const PLANNER_BLOCKS_KEY = ['planner', 'blocks'];
export const PLANNER_SUMMARY_KEY = ['planner', 'summary'];

export function usePlannerBlocks(params?: PlannerFilterParams) {
  return useQuery({
    queryKey: [...PLANNER_BLOCKS_KEY, params],
    queryFn: () => plannerService.getBlocks(params),
    staleTime: 1000 * 60 * 1, // 1 minute
  });
}

export function usePlannerSummary(date?: string) {
  return useQuery({
    queryKey: [...PLANNER_SUMMARY_KEY, date],
    queryFn: () => plannerService.getDailySummary(date),
    staleTime: 1000 * 60 * 1, // 1 minute
  });
}

export function usePlannerBlockDetails(blockId: string | null) {
  return useQuery({
    queryKey: ['plannerBlockDetails', blockId],
    queryFn: () => plannerService.getBlockDetails(blockId!),
    enabled: !!blockId,
  });
}

export function useCreatePlannerBlock() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreatePlannerBlockPayload) => plannerService.createBlock(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PLANNER_BLOCKS_KEY });
      queryClient.invalidateQueries({ queryKey: PLANNER_SUMMARY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useUpdatePlannerBlock() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      blockId,
      payload,
    }: {
      blockId: string;
      payload: UpdatePlannerBlockPayload;
    }) => plannerService.updateBlock(blockId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PLANNER_BLOCKS_KEY });
      queryClient.invalidateQueries({ queryKey: PLANNER_SUMMARY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useUpdatePlannerStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      blockId,
      status,
    }: {
      blockId: string;
      status: PlannerBlockStatus;
    }) => plannerService.updateBlockStatus(blockId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PLANNER_BLOCKS_KEY });
      queryClient.invalidateQueries({ queryKey: PLANNER_SUMMARY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useDeletePlannerBlock() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (blockId: string) => plannerService.deleteBlock(blockId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PLANNER_BLOCKS_KEY });
      queryClient.invalidateQueries({ queryKey: PLANNER_SUMMARY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

