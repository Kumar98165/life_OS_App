import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { automationService } from '../services/automationService';
import { AutomationDefinition } from '../types/automation';

export const AUTOMATION_KEYS = {
  all: ['automations'] as const,
  templates: ['automations', 'templates'] as const,
  detail: (id: string) => ['automations', 'detail', id] as const,
  executions: (defId?: string, status?: string) => ['automations', 'executions', { defId, status }] as const,
  executionDetail: (id: string) => ['automations', 'execution', id] as const,
};

export const useAutomations = () => {
  return useQuery({
    queryKey: AUTOMATION_KEYS.all,
    queryFn: automationService.getAutomations,
  });
};

export const useAutomationTemplates = () => {
  return useQuery({
    queryKey: AUTOMATION_KEYS.templates,
    queryFn: automationService.getTemplates,
  });
};

export const useAutomationDetail = (id: string) => {
  return useQuery({
    queryKey: AUTOMATION_KEYS.detail(id),
    queryFn: () => automationService.getAutomation(id),
    enabled: !!id,
  });
};

export const useAutomationExecutions = (definitionId?: string, status?: string) => {
  return useQuery({
    queryKey: AUTOMATION_KEYS.executions(definitionId, status),
    queryFn: () => automationService.getExecutions(definitionId, status),
  });
};

export const useExecutionDetail = (id: string) => {
  return useQuery({
    queryKey: AUTOMATION_KEYS.executionDetail(id),
    queryFn: () => automationService.getExecution(id),
    enabled: !!id,
  });
};

export const useExecuteAutomation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, userRequest }: { id: string; userRequest?: string }) =>
      automationService.executeAutomation(id, userRequest),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automations'] });
    },
  });
};

export const usePauseAutomation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => automationService.pauseAutomation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: AUTOMATION_KEYS.all });
    },
  });
};

export const useResumeAutomation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => automationService.resumeAutomation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: AUTOMATION_KEYS.all });
    },
  });
};

export const useCancelExecution = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => automationService.cancelExecution(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automations'] });
    },
  });
};

export const useApproveAction = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (approvalId: string) => automationService.approveAction(approvalId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automations'] });
    },
  });
};

export const useRejectAction = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ approvalId, reason }: { approvalId: string; reason?: string }) =>
      automationService.rejectAction(approvalId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automations'] });
    },
  });
};
