/**
 * LifeOS - AI Memory Service Client
 * Handles memory inspection, approval workflows, edits, and privacy toggles.
 */
import { apiClient } from '../api/client';
import { ApiResponse } from '../types';
import {
  AIMemory,
  CreateMemoryPayload,
  UpdateMemoryPayload,
  ApproveSuggestionPayload,
  MemorySettings,
  MemoryListResponse,
  SuggestionListResponse,
} from '../types/aiMemory';

export const aiMemoryService = {
  /**
   * List confirmed active memories.
   */
  async getConfirmedMemories(params?: {
    category?: string;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<MemoryListResponse> {
    const response = await apiClient.get<ApiResponse<MemoryListResponse>>('/ai/memories', {
      params,
    });
    return response.data.data;
  },

  /**
   * List pending AI candidate memory suggestions awaiting user review.
   */
  async getPendingSuggestions(limit = 50, offset = 0): Promise<SuggestionListResponse> {
    const response = await apiClient.get<ApiResponse<SuggestionListResponse>>(
      '/ai/memories/pending',
      { params: { limit, offset } }
    );
    return response.data.data;
  },

  /**
   * Get single memory by ID.
   */
  async getMemoryById(id: string): Promise<AIMemory> {
    const response = await apiClient.get<ApiResponse<{ memory: AIMemory }>>(`/ai/memories/${id}`);
    return response.data.data.memory;
  },

  /**
   * Manually create a confirmed memory.
   */
  async createMemory(payload: CreateMemoryPayload): Promise<AIMemory> {
    const response = await apiClient.post<ApiResponse<{ memory: AIMemory }>>(
      '/ai/memories',
      payload
    );
    return response.data.data.memory;
  },

  /**
   * Update an existing memory.
   */
  async updateMemory(id: string, payload: UpdateMemoryPayload): Promise<AIMemory> {
    const response = await apiClient.patch<ApiResponse<{ memory: AIMemory }>>(
      `/ai/memories/${id}`,
      payload
    );
    return response.data.data.memory;
  },

  /**
   * Permanently delete a memory record.
   */
  async deleteMemory(id: string): Promise<void> {
    await apiClient.delete<ApiResponse<null>>(`/ai/memories/${id}`);
  },

  /**
   * Approve a pending suggestion (with optional edits).
   */
  async approveSuggestion(id: string, payload?: ApproveSuggestionPayload): Promise<AIMemory> {
    const response = await apiClient.post<ApiResponse<{ memory: AIMemory }>>(
      `/ai/memories/${id}/approve`,
      payload || {}
    );
    return response.data.data.memory;
  },

  /**
   * Reject and delete a pending suggestion.
   */
  async rejectSuggestion(id: string): Promise<void> {
    await apiClient.post<ApiResponse<null>>(`/ai/memories/${id}/reject`);
  },

  /**
   * Archive a confirmed memory so it is excluded from future prompts.
   */
  async archiveMemory(id: string): Promise<AIMemory> {
    const response = await apiClient.post<ApiResponse<{ memory: AIMemory }>>(
      `/ai/memories/${id}/archive`
    );
    return response.data.data.memory;
  },

  /**
   * Get memory privacy and personalization toggle settings.
   */
  async getSettings(): Promise<MemorySettings> {
    const response = await apiClient.get<ApiResponse<MemorySettings>>('/ai/memories/settings');
    return response.data.data;
  },

  /**
   * Update memory personalization toggle.
   */
  async updateSettings(aiMemoryEnabled: boolean): Promise<MemorySettings> {
    const response = await apiClient.patch<ApiResponse<MemorySettings>>('/ai/memories/settings', {
      ai_memory_enabled: aiMemoryEnabled,
    });
    return response.data.data;
  },
};

