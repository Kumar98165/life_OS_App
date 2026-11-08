import { apiClient } from '../api/client';
import { ApiResponse } from '../types';
import {
  AIConversation,
  AIMessage,
  ChatResponse,
  AIHealthStatus,
  AIFeedback,
  SubmitFeedbackPayload,
  PrivacyConsentStatus,
} from '../types/ai';

export const aiService = {
  /**
   * Submit a chat prompt to local LifeOS AI Assistant.
   */
  async sendMessage(message: string, conversationId?: string): Promise<ChatResponse> {
    const response = await apiClient.post<ApiResponse<ChatResponse>>('/ai/chat', {
      message,
      conversation_id: conversationId || undefined,
    });
    return response.data.data;
  },

  /**
   * List all user conversation threads.
   */
  async getConversations(limit = 20, offset = 0): Promise<AIConversation[]> {
    const response = await apiClient.get<ApiResponse<{ conversations: AIConversation[] }>>(
      '/ai/conversations',
      { params: { limit, offset } }
    );
    return response.data.data.conversations;
  },

  /**
   * Fetch full message history for a conversation.
   */
  async getConversationHistory(
    conversationId: string,
    limit = 50
  ): Promise<{ conversation: AIConversation; messages: AIMessage[] }> {
    const response = await apiClient.get<
      ApiResponse<{ conversation: AIConversation; messages: AIMessage[] }>
    >(`/ai/conversations/${conversationId}`, {
      params: { limit },
    });
    return response.data.data;
  },

  /**
   * Explicitly start a new named conversation thread.
   */
  async createConversation(title?: string): Promise<AIConversation> {
    const response = await apiClient.post<ApiResponse<{ conversation: AIConversation }>>(
      '/ai/conversations',
      { title }
    );
    return response.data.data.conversation;
  },

  /**
   * Delete a conversation thread.
   */
  async deleteConversation(conversationId: string): Promise<void> {
    await apiClient.delete<ApiResponse<null>>(`/ai/conversations/${conversationId}`);
  },

  /**
   * Check Ollama connection and model health.
   */
  async checkHealth(): Promise<AIHealthStatus> {
    const response = await apiClient.get<ApiResponse<AIHealthStatus>>('/ai/health');
    return response.data.data;
  },

  /**
   * Submit rating or feedback for an assistant response.
   */
  async submitFeedback(payload: SubmitFeedbackPayload): Promise<AIFeedback> {
    const response = await apiClient.post<ApiResponse<{ feedback: AIFeedback }>>(
      '/ai/feedback',
      payload
    );
    return response.data.data.feedback;
  },

  /**
   * Retrieve existing feedback for a specific message.
   */
  async getMessageFeedback(messageId: string): Promise<AIFeedback | null> {
    try {
      const response = await apiClient.get<ApiResponse<{ feedback: AIFeedback }>>(
        `/ai/messages/${messageId}/feedback`
      );
      return response.data.data?.feedback || null;
    } catch {
      return null;
    }
  },

  /**
   * Fetch user AI training privacy consent status.
   */
  async getPrivacyConsent(): Promise<PrivacyConsentStatus> {
    const response = await apiClient.get<ApiResponse<PrivacyConsentStatus>>('/ai/privacy/consent');
    return response.data.data;
  },

  /**
   * Update user AI training privacy consent status.
   */
  async updatePrivacyConsent(allowTraining: boolean): Promise<PrivacyConsentStatus> {
    const response = await apiClient.put<ApiResponse<PrivacyConsentStatus>>('/ai/privacy/consent', {
      allow_training: allowTraining,
    });
    return response.data.data;
  },

  /**
   * Purge all feedback and derived training data.
   */
  async purgePrivacyData(): Promise<{ purged_feedback_count: number; purged_samples_count: number }> {
    const response = await apiClient.post<
      ApiResponse<{ purged_feedback_count: number; purged_samples_count: number }>
    >('/ai/privacy/purge');
    return response.data.data;
  },
};


