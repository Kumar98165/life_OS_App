import { apiClient } from '../api/client';
import {
  FocusGoal,
  FocusSession,
  FocusDistraction,
  FocusStats,
  FreeTimeSlot,
} from '../types/focus';

export const focusService = {
  getGoal: async (): Promise<FocusGoal> => {
    const res = await apiClient.get('/focus/goal');
    return res.data.data.goal;
  },

  updateGoal: async (payload: Partial<FocusGoal>): Promise<FocusGoal> => {
    const res = await apiClient.patch('/focus/goal', payload);
    return res.data.data.goal;
  },

  getActiveSession: async (): Promise<FocusSession | null> => {
    const res = await apiClient.get('/focus/sessions/active');
    return res.data.data.session;
  },

  startSession: async (payload: {
    title?: string;
    session_type: string;
    target_duration_minutes: number;
    task_id?: string | null;
    planner_block_id?: string | null;
    notes?: string;
  }): Promise<FocusSession> => {
    const res = await apiClient.post('/focus/sessions', payload);
    return res.data.data.session;
  },

  pauseSession: async (sessionId: string): Promise<FocusSession> => {
    const res = await apiClient.post(`/focus/sessions/${sessionId}/pause`);
    return res.data.data.session;
  },

  resumeSession: async (sessionId: string): Promise<FocusSession> => {
    const res = await apiClient.post(`/focus/sessions/${sessionId}/resume`);
    return res.data.data.session;
  },

  stopSession: async (
    sessionId: string,
    payload: { actual_duration_seconds: number; notes?: string }
  ): Promise<FocusSession> => {
    const res = await apiClient.post(`/focus/sessions/${sessionId}/stop`, payload);
    return res.data.data.session;
  },

  logDistraction: async (
    sessionId: string,
    payload: { distraction_type: string; description: string }
  ): Promise<FocusDistraction> => {
    const res = await apiClient.post(
      `/focus/sessions/${sessionId}/distractions`,
      payload
    );
    return res.data.data.distraction;
  },

  listSessions: async (params?: { page?: number; per_page?: number; session_type?: string }): Promise<{
    sessions: FocusSession[];
    meta: any;
  }> => {
    const res = await apiClient.get('/focus/sessions', { params });
    return {
      sessions: res.data.data.sessions,
      meta: res.data.meta,
    };
  },

  getStats: async (): Promise<FocusStats> => {
    const res = await apiClient.get('/focus/stats');
    return res.data.data.stats;
  },

  getFreeTime: async (params?: {
    date?: string;
    start_hour?: number;
    end_hour?: number;
    tz_offset?: number;
  }): Promise<FreeTimeSlot[]> => {
    const res = await apiClient.get('/planner/free-time', { params });
    return res.data.data.free_slots;
  },

  getCalendarExportUrl: (): string => {
    return `${apiClient.defaults.baseURL}/planner/export.ics`;
  },
};
