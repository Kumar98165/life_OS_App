import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { aiService } from '../services/aiService';

export const AI_CONVERSATIONS_KEY = ['ai_conversations'];

export function useAIConversations() {
  return useQuery({
    queryKey: AI_CONVERSATIONS_KEY,
    queryFn: () => aiService.getConversations(),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

export function useAIConversationHistory(conversationId: string | null) {
  return useQuery({
    queryKey: ['ai_conversation_history', conversationId],
    queryFn: () => aiService.getConversationHistory(conversationId!),
    enabled: !!conversationId,
  });
}

export function useAIHealth() {
  return useQuery({
    queryKey: ['ai_health'],
    queryFn: () => aiService.checkHealth(),
    staleTime: 1000 * 30, // 30 seconds
  });
}

export function useAISendMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      message,
      conversationId,
    }: {
      message: string;
      conversationId?: string;
    }) => aiService.sendMessage(message, conversationId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: AI_CONVERSATIONS_KEY });
      if (data.conversation_id) {
        queryClient.invalidateQueries({
          queryKey: ['ai_conversation_history', data.conversation_id],
        });
      }
    },
  });
}

export function useAICreateConversation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (title?: string) => aiService.createConversation(title),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: AI_CONVERSATIONS_KEY });
    },
  });
}

export function useAIDeleteConversation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (conversationId: string) => aiService.deleteConversation(conversationId),
    onSuccess: (_, conversationId) => {
      queryClient.invalidateQueries({ queryKey: AI_CONVERSATIONS_KEY });
      queryClient.removeQueries({ queryKey: ['ai_conversation_history', conversationId] });
    },
  });
}

export function useAISubmitFeedback() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: {
      message_id: string;
      rating: number;
      feedback_type?: string;
      category?: string;
      comment?: string;
      suggested_response?: string;
    }) => aiService.submitFeedback(payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['ai_message_feedback', variables.message_id],
      });
    },
  });
}

export function useAIMessageFeedback(messageId: string | null) {
  return useQuery({
    queryKey: ['ai_message_feedback', messageId],
    queryFn: () => aiService.getMessageFeedback(messageId!),
    enabled: !!messageId,
  });
}

export function useAIPrivacyConsent() {
  return useQuery({
    queryKey: ['ai_privacy_consent'],
    queryFn: () => aiService.getPrivacyConsent(),
  });
}

export function useAIUpdatePrivacyConsent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (allowTraining: boolean) => aiService.updatePrivacyConsent(allowTraining),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai_privacy_consent'] });
    },
  });
}

export function useAIDailyBriefing() {
  return useQuery({
    queryKey: ['ai_daily_briefing'],
    queryFn: () => aiService.getDailyBriefing(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function useAIProactiveInsights() {
  return useQuery({
    queryKey: ['ai_proactive_insights'],
    queryFn: () => aiService.getProactiveInsights(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}



