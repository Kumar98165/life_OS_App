import { apiClient } from '../api/client';
import {
  VoiceTranscriptionResult,
  VoiceAssistantTurnResponse,
  VoicePreference,
  UpdateVoicePreferencePayload,
  VoiceInfo,
} from '../types/voice';

export const voiceService = {
  /**
   * Upload audio recording for speech-to-text transcription.
   */
  async transcribeAudio(formData: FormData): Promise<VoiceTranscriptionResult> {
    const res = await apiClient.post<{ data: VoiceTranscriptionResult }>(
      '/voice/transcribe',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return res.data.data;
  },

  /**
   * Send audio or text turn to Voice Assistant pipeline.
   */
  async sendAssistantTurn(
    payload: FormData | { text_input: string; conversation_id?: string; return_audio?: boolean }
  ): Promise<VoiceAssistantTurnResponse> {
    const isFormData = payload instanceof FormData;
    const res = await apiClient.post<{ data: VoiceAssistantTurnResponse }>(
      '/voice/assistant',
      payload,
      isFormData
        ? {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          }
        : undefined
    );
    return res.data.data;
  },

  /**
   * Request direct audio synthesis for text string.
   */
  async synthesizeSpeech(params: {
    text: string;
    language?: string;
    speech_rate?: number;
    voice_name?: string;
  }): Promise<ArrayBuffer> {
    const res = await apiClient.post('/voice/synthesize', params, {
      responseType: 'arraybuffer',
    });
    return res.data;
  },

  /**
   * List available system voices.
   */
  async getVoices(): Promise<VoiceInfo[]> {
    const res = await apiClient.get<{ data: { voices: VoiceInfo[] } }>('/voice/voices');
    return res.data.data.voices;
  },

  /**
   * Fetch authenticated user's voice preferences.
   */
  async getSettings(): Promise<VoicePreference> {
    const res = await apiClient.get<{ data: VoicePreference }>('/voice/settings');
    return res.data.data;
  },

  /**
   * Update authenticated user's voice preferences.
   */
  async updateSettings(payload: UpdateVoicePreferencePayload): Promise<VoicePreference> {
    const res = await apiClient.patch<{ data: VoicePreference }>('/voice/settings', payload);
    return res.data.data;
  },
};
