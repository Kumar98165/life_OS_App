import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { voiceService } from '../services/voiceService';
import {
  UpdateVoicePreferencePayload,
  VoiceAssistantTurnResponse,
} from '../types/voice';

export const VOICE_QUERY_KEYS = {
  settings: ['voice', 'settings'] as const,
  voices: ['voice', 'voices'] as const,
};

export function useVoiceSettings() {
  return useQuery({
    queryKey: VOICE_QUERY_KEYS.settings,
    queryFn: () => voiceService.getSettings(),
  });
}

export function useVoiceList() {
  return useQuery({
    queryKey: VOICE_QUERY_KEYS.voices,
    queryFn: () => voiceService.getVoices(),
  });
}

export function useUpdateVoiceSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UpdateVoicePreferencePayload) => voiceService.updateSettings(payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(VOICE_QUERY_KEYS.settings, updated);
      queryClient.invalidateQueries({ queryKey: VOICE_QUERY_KEYS.settings });
    },
  });
}

export function useVoiceAssistantTurn() {
  return useMutation({
    mutationFn: (
      payload: FormData | { text_input: string; conversation_id?: string; return_audio?: boolean }
    ) => voiceService.sendAssistantTurn(payload),
  });
}

export function useTranscribeAudio() {
  return useMutation({
    mutationFn: (formData: FormData) => voiceService.transcribeAudio(formData),
  });
}
