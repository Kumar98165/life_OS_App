/**
 * LifeOS - TanStack Query Hooks for AI Memory Management
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { aiMemoryService } from '../services/aiMemoryService';
import {
  CreateMemoryPayload,
  UpdateMemoryPayload,
  ApproveSuggestionPayload,
} from '../types/aiMemory';

export const AI_MEMORY_QUERY_KEYS = {
  confirmed: (category?: string, search?: string) => ['ai_memories', category || 'all', search || ''] as const,
  suggestions: () => ['ai_memory_suggestions'] as const,
  settings: () => ['ai_memory_settings'] as const,
};

export function useConfirmedMemories(category?: string, search?: string) {
  return useQuery({
    queryKey: AI_MEMORY_QUERY_KEYS.confirmed(category, search),
    queryFn: () => aiMemoryService.getConfirmedMemories({ category: category === 'all' ? undefined : category, search }),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function usePendingSuggestions() {
  return useQuery({
    queryKey: AI_MEMORY_QUERY_KEYS.suggestions(),
    queryFn: () => aiMemoryService.getPendingSuggestions(),
    staleTime: 1000 * 30, // 30 seconds
  });
}

export function useMemorySettings() {
  return useQuery({
    queryKey: AI_MEMORY_QUERY_KEYS.settings(),
    queryFn: () => aiMemoryService.getSettings(),
  });
}

export function useAIMemoryMutations() {
  const queryClient = useQueryClient();

  const invalidateMemories = () => {
    queryClient.invalidateQueries({ queryKey: ['ai_memories'] });
  };

  const invalidateSuggestions = () => {
    queryClient.invalidateQueries({ queryKey: ['ai_memory_suggestions'] });
  };

  const createMemory = useMutation({
    mutationFn: (payload: CreateMemoryPayload) => aiMemoryService.createMemory(payload),
    onSuccess: () => {
      invalidateMemories();
    },
  });

  const updateMemory = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateMemoryPayload }) =>
      aiMemoryService.updateMemory(id, payload),
    onSuccess: () => {
      invalidateMemories();
    },
  });

  const deleteMemory = useMutation({
    mutationFn: (id: string) => aiMemoryService.deleteMemory(id),
    onSuccess: () => {
      invalidateMemories();
    },
  });

  const approveSuggestion = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload?: ApproveSuggestionPayload }) =>
      aiMemoryService.approveSuggestion(id, payload),
    onSuccess: () => {
      invalidateMemories();
      invalidateSuggestions();
    },
  });

  const rejectSuggestion = useMutation({
    mutationFn: (id: string) => aiMemoryService.rejectSuggestion(id),
    onSuccess: () => {
      invalidateSuggestions();
    },
  });

  const archiveMemory = useMutation({
    mutationFn: (id: string) => aiMemoryService.archiveMemory(id),
    onSuccess: () => {
      invalidateMemories();
    },
  });

  const updateSettings = useMutation({
    mutationFn: (enabled: boolean) => aiMemoryService.updateSettings(enabled),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai_memory_settings'] });
    },
  });

  return {
    createMemory,
    updateMemory,
    deleteMemory,
    approveSuggestion,
    rejectSuggestion,
    archiveMemory,
    updateSettings,
  };
}

