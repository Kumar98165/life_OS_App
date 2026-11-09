import { apiClient, API_BASE_URL, getAuthToken } from '../api/client';
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

export interface SSEChatCallbacks {
  onStart?: (data: { conversation_id: string; conversation_title: string }) => void;
  onToken?: (content: string) => void;
  onComplete?: (data: { message_id: string; conversation_id: string; latency_ms: number }) => void;
  onError?: (error: { code: string; message: string }) => void;
}

export const aiService = {
  /**
   * Submit a chat prompt to local LifeOS AI Assistant via progressive Server-Sent Events (SSE).
   * Supports authenticated POST, abort signal cancellation, and incremental token parsing.
   */
  async streamChatMessage(
    message: string,
    conversationId?: string,
    callbacks?: SSEChatCallbacks,
    abortSignal?: AbortSignal
  ): Promise<void> {
    const token = getAuthToken();
    const url = `${API_BASE_URL}/ai/chat/stream`;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          message,
          conversation_id: conversationId || undefined,
        }),
        signal: abortSignal,
      });

      if (!response.ok) {
        let errMessage = `HTTP error ${response.status}`;
        try {
          const errJson = await response.json();
          errMessage = errJson.message || errMessage;
        } catch {
          // Response body was not JSON
        }
        callbacks?.onError?.({ code: `HTTP_${response.status}`, message: errMessage });
        return;
      }

      if (!response.body) {
        // Fallback for runtimes without ReadableStream body
        const fullText = await response.text();
        this._parseSSEStreamText(fullText, callbacks);
        return;
      }

      // Progressive stream consumption
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        buffer = this._processSSEBuffer(buffer, callbacks);
      }

      // Flush remaining buffer
      if (buffer.trim()) {
        this._processSSEBuffer(buffer + '\n\n', callbacks);
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        // User deliberately cancelled stream
        return;
      }
      callbacks?.onError?.({
        code: 'NETWORK_ERROR',
        message: err.message || 'Stream connection failed',
      });
    }
  },

  /**
   * Internal helper to extract and dispatch complete SSE event blocks from buffer.
   */
  _processSSEBuffer(buffer: string, callbacks?: SSEChatCallbacks): string {
    const events = buffer.split('\n\n');
    // Keep incomplete tail in buffer
    const remaining = events.pop() || '';

    for (const rawEvent of events) {
      if (!rawEvent.trim()) continue;
      this._dispatchSingleSSE(rawEvent, callbacks);
    }
    return remaining;
  },

  /**
   * Internal helper for single SSE text chunk dispatch.
   */
  _parseSSEStreamText(text: string, callbacks?: SSEChatCallbacks) {
    const rawEvents = text.split('\n\n');
    for (const raw of rawEvents) {
      if (raw.trim()) {
        this._dispatchSingleSSE(raw, callbacks);
      }
    }
  },

  /**
   * Dispatches typed events: start, token, complete, error.
   */
  _dispatchSingleSSE(rawEvent: string, callbacks?: SSEChatCallbacks) {
    let eventType = 'message';
    let dataStr = '';

    const lines = rawEvent.split('\n');
    for (const line of lines) {
      if (line.startsWith('event:')) {
        eventType = line.replace('event:', '').trim();
      } else if (line.startsWith('data:')) {
        dataStr = line.replace('data:', '').trim();
      }
    }

    if (!dataStr) return;

    try {
      const parsedData = JSON.parse(dataStr);
      switch (eventType) {
        case 'start':
          callbacks?.onStart?.(parsedData);
          break;
        case 'token':
          if (parsedData.content) {
            callbacks?.onToken?.(parsedData.content);
          }
          break;
        case 'complete':
          callbacks?.onComplete?.(parsedData);
          break;
        case 'error':
          callbacks?.onError?.(parsedData);
          break;
        default:
          break;
      }
    } catch {
      // Ignore malformed individual chunks
    }
  },

  /**
   * Submit a chat prompt to local LifeOS AI Assistant (synchronous fallback).
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

  /**
   * Retrieve structured daily intelligence briefing.
   */
  async getDailyBriefing(): Promise<import('../types/ai').DailyBriefing> {
    const response = await apiClient.get<ApiResponse<import('../types/ai').DailyBriefing>>(
      '/ai/intelligence/briefing'
    );
    return response.data.data;
  },

  /**
   * Retrieve context-aware proactive insights and observations.
   */
  async getProactiveInsights(): Promise<import('../types/ai').ProactiveInsight[]> {
    const response = await apiClient.get<ApiResponse<{ insights: import('../types/ai').ProactiveInsight[] }>>(
      '/ai/intelligence/insights'
    );
    return response.data.data.insights;
  },
};



