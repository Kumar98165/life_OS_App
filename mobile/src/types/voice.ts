export interface VoiceTranscriptionSegment {
  id: number;
  start: number;
  end: number;
  text: string;
  avg_logprob?: number;
  no_speech_prob?: number;
}

export interface VoiceTranscriptionResult {
  text: string;
  detected_language: string;
  language_probability: number;
  duration_seconds: number;
  segments: VoiceTranscriptionSegment[];
  model: string;
}

export interface ActionProposal {
  approval_id?: string;
  action_type: string;
  risk_level: 'low' | 'medium' | 'high';
  summary: string;
  parameters: Record<string, any>;
}

export interface VoiceAssistantTurnResponse {
  transcript: string;
  detected_language: string;
  language_probability?: number;
  response_text: string;
  conversation_id?: string;
  requires_approval: boolean;
  action_proposals: ActionProposal[];
  audio_base64?: string | null;
  audio_mime_type?: string | null;
}

export interface VoicePreference {
  id: string;
  user_id: string;
  language: 'en' | 'hi' | 'hinglish';
  voice_name: string;
  speech_rate: number;
  speech_pitch: number;
  auto_play_response: boolean;
  audio_privacy_enabled: boolean;
  confirm_actions_via_voice: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface UpdateVoicePreferencePayload {
  language?: 'en' | 'hi' | 'hinglish';
  voice_name?: string;
  speech_rate?: number;
  speech_pitch?: number;
  auto_play_response?: boolean;
  audio_privacy_enabled?: boolean;
  confirm_actions_via_voice?: boolean;
}

export interface VoiceInfo {
  id: string;
  name: string;
  languages: string[];
  gender?: string;
}

export interface VoiceConversationTurn {
  id: string;
  timestamp: string;
  user_transcript: string;
  assistant_reply: string;
  detected_language?: string;
  action_proposals?: ActionProposal[];
  audio_base64?: string | null;
}
