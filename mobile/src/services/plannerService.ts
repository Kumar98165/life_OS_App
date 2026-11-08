import { apiClient } from '../api/client';
import { ApiResponse } from '../types';
import {
  PlannerBlock,
  CreatePlannerBlockPayload,
  UpdatePlannerBlockPayload,
  PlannerFilterParams,
  PlannerBlockStatus,
  PlannerDailySummary,
} from '../types/planner';
import { PaginationMeta } from '../types/task';

export const plannerService = {
  /**
   * Retrieve paginated and filtered planner blocks for the authenticated user.
   */
  async getBlocks(
    params?: PlannerFilterParams
  ): Promise<{ blocks: PlannerBlock[]; meta: PaginationMeta }> {
    const response = await apiClient.get<ApiResponse<{ blocks: PlannerBlock[] }>>('/planner/blocks', {
      params,
    });
    return {
      blocks: response.data.data.blocks,
      meta: (response.data.meta as PaginationMeta) || {
        page: 1,
        per_page: 50,
        total: response.data.data.blocks.length,
        total_pages: 1,
        has_next: false,
        has_prev: false,
      },
    };
  },

  /**
   * Retrieve single planner block details by ID.
   */
  async getBlockDetails(blockId: string): Promise<PlannerBlock> {
    const response = await apiClient.get<ApiResponse<{ block: PlannerBlock }>>(
      `/planner/blocks/${blockId}`
    );
    return response.data.data.block;
  },

  /**
   * Create a new planner block.
   */
  async createBlock(payload: CreatePlannerBlockPayload): Promise<PlannerBlock> {
    const response = await apiClient.post<ApiResponse<{ block: PlannerBlock }>>(
      '/planner/blocks',
      payload
    );
    return response.data.data.block;
  },

  /**
   * Update planner block fields.
   */
  async updateBlock(blockId: string, payload: UpdatePlannerBlockPayload): Promise<PlannerBlock> {
    const response = await apiClient.patch<ApiResponse<{ block: PlannerBlock }>>(
      `/planner/blocks/${blockId}`,
      payload
    );
    return response.data.data.block;
  },

  /**
   * Update status of a planner block (scheduled, completed, cancelled, skipped).
   */
  async updateBlockStatus(blockId: string, status: PlannerBlockStatus): Promise<PlannerBlock> {
    const response = await apiClient.patch<ApiResponse<{ block: PlannerBlock }>>(
      `/planner/blocks/${blockId}/status`,
      { status }
    );
    return response.data.data.block;
  },

  /**
   * Delete a planner block.
   */
  async deleteBlock(blockId: string): Promise<void> {
    await apiClient.delete(`/planner/blocks/${blockId}`);
  },

  /**
   * Retrieve daily summary for a date.
   */
  async getDailySummary(date?: string, tzOffset?: number): Promise<PlannerDailySummary> {
    const params: Record<string, any> = {};
    if (date) params.date = date;
    if (tzOffset !== undefined) {
      params.tz_offset = tzOffset;
    } else {
      // Default to device local timezone offset in hours
      params.tz_offset = -(new Date().getTimezoneOffset() / 60);
    }

    const response = await apiClient.get<ApiResponse<PlannerDailySummary>>(
      '/planner/summary/daily',
      { params }
    );
    return response.data.data;
  },
};

