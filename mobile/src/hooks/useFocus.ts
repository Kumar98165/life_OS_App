import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { focusService } from '../services/focusService';
import { FocusGoal } from '../types/focus';

export const FOCUS_KEYS = {
  goal: ['focus', 'goal'] as const,
  active: ['focus', 'active'] as const,
  stats: ['focus', 'stats'] as const,
  sessions: (page: number) => ['focus', 'sessions', page] as const,
  freeTime: (date: string) => ['planner', 'freeTime', date] as const,
};

export function useFocusGoal() {
  const queryClient = useQueryClient();
  const query = useQuery({
    queryKey: FOCUS_KEYS.goal,
    queryFn: focusService.getGoal,
  });

  const updateMutation = useMutation({
    mutationFn: (payload: Partial<FocusGoal>) => focusService.updateGoal(payload),
    onSuccess: (data) => {
      queryClient.setQueryData(FOCUS_KEYS.goal, data);
      queryClient.invalidateQueries({ queryKey: FOCUS_KEYS.stats });
    },
  });

  return { ...query, updateGoal: updateMutation.mutateAsync };
}

export function useActiveFocusSession() {
  const queryClient = useQueryClient();
  const query = useQuery({
    queryKey: FOCUS_KEYS.active,
    queryFn: focusService.getActiveSession,
    refetchInterval: 30000,
  });

  const startMutation = useMutation({
    mutationFn: focusService.startSession,
    onSuccess: (data) => {
      queryClient.setQueryData(FOCUS_KEYS.active, data);
      queryClient.invalidateQueries({ queryKey: ['focus'] });
    },
  });

  const pauseMutation = useMutation({
    mutationFn: (sessionId: string) => focusService.pauseSession(sessionId),
    onSuccess: (data) => {
      queryClient.setQueryData(FOCUS_KEYS.active, data);
    },
  });

  const resumeMutation = useMutation({
    mutationFn: (sessionId: string) => focusService.resumeSession(sessionId),
    onSuccess: (data) => {
      queryClient.setQueryData(FOCUS_KEYS.active, data);
    },
  });

  const stopMutation = useMutation({
    mutationFn: ({
      sessionId,
      actual_duration_seconds,
      notes,
    }: {
      sessionId: string;
      actual_duration_seconds: number;
      notes?: string;
    }) => focusService.stopSession(sessionId, { actual_duration_seconds, notes }),
    onSuccess: () => {
      queryClient.setQueryData(FOCUS_KEYS.active, null);
      queryClient.invalidateQueries({ queryKey: ['focus'] });
    },
  });

  const logDistractionMutation = useMutation({
    mutationFn: ({
      sessionId,
      distraction_type,
      description,
    }: {
      sessionId: string;
      distraction_type: string;
      description: string;
    }) => focusService.logDistraction(sessionId, { distraction_type, description }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FOCUS_KEYS.active });
      queryClient.invalidateQueries({ queryKey: FOCUS_KEYS.stats });
    },
  });

  return {
    ...query,
    startSession: startMutation.mutateAsync,
    pauseSession: pauseMutation.mutateAsync,
    resumeSession: resumeMutation.mutateAsync,
    stopSession: stopMutation.mutateAsync,
    logDistraction: logDistractionMutation.mutateAsync,
    isStarting: startMutation.isPending,
    isStopping: stopMutation.isPending,
  };
}

export function useFocusStats() {
  return useQuery({
    queryKey: FOCUS_KEYS.stats,
    queryFn: focusService.getStats,
  });
}

export function useFocusSessions(page = 1) {
  return useQuery({
    queryKey: FOCUS_KEYS.sessions(page),
    queryFn: () => focusService.listSessions({ page }),
  });
}

export function useFreeTimeSlots(dateStr: string) {
  return useQuery({
    queryKey: FOCUS_KEYS.freeTime(dateStr),
    queryFn: () => focusService.getFreeTime({ date: dateStr }),
    enabled: !!dateStr,
  });
}
