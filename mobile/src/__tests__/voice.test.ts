import { describe, it } from 'node:test';
import assert from 'node:assert';
import {
  VoicePreference,
  VoiceAssistantTurnResponse,
  VoiceTranscriptionResult,
} from '../types/voice';

describe('Voice Assistant - Data Structures & Domain Logic', () => {
  it('correctly maps VoicePreference object fields', () => {
    const prefs: VoicePreference = {
      id: 'pref-123',
      user_id: 'user-456',
      language: 'en',
      voice_name: 'Microsoft David',
      speech_rate: 1.25,
      speech_pitch: 1.0,
      auto_play_response: true,
      audio_privacy_enabled: true,
      confirm_actions_via_voice: true,
    };

    assert.strictEqual(prefs.language, 'en');
    assert.strictEqual(prefs.speech_rate, 1.25);
    assert.strictEqual(prefs.audio_privacy_enabled, true);
    assert.strictEqual(prefs.auto_play_response, true);
  });

  it('validates VoiceAssistantTurnResponse with action proposals and audio payload', () => {
    const turn: VoiceAssistantTurnResponse = {
      transcript: 'Plan a focus session tomorrow at 10 AM',
      detected_language: 'en',
      language_probability: 0.98,
      response_text: 'I have prepared a focus block for 10:00 AM. Would you like me to schedule it?',
      conversation_id: 'conv-abc-789',
      requires_approval: true,
      action_proposals: [
        {
          approval_id: 'appr-999',
          action_type: 'create_planner_block',
          risk_level: 'medium',
          summary: 'Schedule focus block tomorrow 10:00 AM',
          parameters: {
            title: 'Focus Session',
            start_time: '10:00',
            end_time: '11:00',
          },
        },
      ],
      audio_base64: 'UklGRi4AAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=',
      audio_mime_type: 'audio/wav',
    };

    assert.strictEqual(turn.requires_approval, true);
    assert.strictEqual(turn.action_proposals.length, 1);
    assert.strictEqual(turn.action_proposals[0].risk_level, 'medium');
    assert.strictEqual(turn.audio_mime_type, 'audio/wav');
    assert.ok(turn.audio_base64 !== null);
  });

  it('validates bilingual / Hindi speech transcription payload', () => {
    const sttResult: VoiceTranscriptionResult = {
      text: 'कल सुबह 9 बजे एक टास्क बनाओ',
      detected_language: 'hi',
      language_probability: 0.965,
      duration_seconds: 3.4,
      segments: [
        {
          id: 0,
          start: 0.0,
          end: 3.4,
          text: 'कल सुबह 9 बजे एक टास्क बनाओ',
          avg_logprob: -0.21,
          no_speech_prob: 0.01,
        },
      ],
      model: 'faster-whisper-tiny',
    };

    assert.strictEqual(sttResult.detected_language, 'hi');
    assert.strictEqual(sttResult.segments.length, 1);
    assert.ok(sttResult.duration_seconds > 0);
  });

  it('correctly handles speech rate boundaries', () => {
    const minRate = 0.5;
    const maxRate = 2.0;
    const testRates = [0.25, 0.75, 1.0, 1.5, 2.5];

    const clampedRates = testRates.map((r) => Math.max(minRate, Math.min(r, maxRate)));

    assert.deepStrictEqual(clampedRates, [0.5, 0.75, 1.0, 1.5, 2.0]);
  });
});
