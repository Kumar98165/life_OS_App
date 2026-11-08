import { apiClient } from '../api/client';
import {
  AutomationDefinition,
  AutomationTemplate,
  AutomationExecution,
  AutomationApproval,
} from '../types/automation';

export const automationService = {
  // Definition & Templates
  getAutomations: async (): Promise<AutomationDefinition[]> => {
    const res = await apiClient.get('/automations');
    return res.data?.data?.automations || [];
  },

  getTemplates: async (): Promise<AutomationTemplate[]> => {
    const res = await apiClient.get('/automations/templates');
    return res.data?.data?.templates || [];
  },

  getAutomation: async (id: string): Promise<AutomationDefinition> => {
    const res = await apiClient.get(`/automations/${id}`);
    return res.data?.data?.automation;
  },

  createAutomation: async (data: Partial<AutomationDefinition>): Promise<AutomationDefinition> => {
    const res = await apiClient.post('/automations', data);
    return res.data?.data?.automation;
  },

  updateAutomation: async (id: string, data: Partial<AutomationDefinition>): Promise<AutomationDefinition> => {
    const res = await apiClient.patch(`/automations/${id}`, data);
    return res.data?.data?.automation;
  },

  deleteAutomation: async (id: string): Promise<void> => {
    await apiClient.delete(`/automations/${id}`);
  },

  pauseAutomation: async (id: string): Promise<void> => {
    await apiClient.post(`/automations/${id}/pause`);
  },

  resumeAutomation: async (id: string): Promise<void> => {
    await apiClient.post(`/automations/${id}/resume`);
  },

  // Executions
  executeAutomation: async (id: string, userRequest?: string): Promise<AutomationExecution> => {
    const res = await apiClient.post(`/automations/${id}/execute`, {
      user_request: userRequest,
    });
    return res.data?.data?.execution;
  },

  getExecutions: async (definitionId?: string, status?: string): Promise<AutomationExecution[]> => {
    const params: Record<string, string> = {};
    if (definitionId) params.definition_id = definitionId;
    if (status) params.status = status;
    const res = await apiClient.get('/automations/executions', { params });
    return res.data?.data?.executions || [];
  },

  getExecution: async (id: string): Promise<AutomationExecution> => {
    const res = await apiClient.get(`/automations/executions/${id}`);
    return res.data?.data?.execution;
  },

  cancelExecution: async (id: string): Promise<void> => {
    await apiClient.post(`/automations/executions/${id}/cancel`);
  },

  // Approvals
  approveAction: async (approvalId: string): Promise<any> => {
    const res = await apiClient.post(`/automations/approvals/${approvalId}/approve`);
    return res.data?.data;
  },

  rejectAction: async (approvalId: string, reason?: string): Promise<any> => {
    const res = await apiClient.post(`/automations/approvals/${approvalId}/reject`, { reason });
    return res.data?.data;
  },
};
