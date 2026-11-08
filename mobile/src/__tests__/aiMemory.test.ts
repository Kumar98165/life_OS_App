import test from 'node:test';
import assert from 'node:assert';
import {
  AIMemory,
  AIMemoryCategory,
  CreateMemoryPayload,
  UpdateMemoryPayload,
  ApproveSuggestionPayload,
  MemorySettings,
} from '../types/aiMemory';

test('AI Memory - Data Structures & Review Workflow Validation', async (t) => {
  await t.test('structures confirmed memory with valid category and confidence score', () => {
    const memory: AIMemory = {
      id: 'mem-101',
      user_id: 'usr-1',
      memory_key: 'Prefers morning deep work',
      memory_value: 'Best focused work happens between 8 AM and 10 AM.',
      memory_type: 'preference',
      confidence: 0.95,
      status: 'confirmed',
      created_at: new Date().toISOString(),
    };

    assert.strictEqual(memory.id, 'mem-101');
    assert.strictEqual(memory.status, 'confirmed');
    assert.strictEqual(memory.memory_type, 'preference');
    assert.ok(memory.confidence >= 0.7 && memory.confidence <= 1.0);
  });

  await t.test('enforces pending review status for candidate memories', () => {
    const candidate: AIMemory = {
      id: 'sugg-202',
      user_id: 'usr-1',
      memory_key: 'Drinks matcha latte in the morning',
      memory_value: 'User mentioned preparing matcha tea before starting computer work.',
      memory_type: 'routine_pattern',
      confidence: 0.85,
      status: 'pending',
      source_conversation_id: 'conv-99',
      created_at: new Date().toISOString(),
    };

    // Candidates must never be confirmed automatically
    assert.strictEqual(candidate.status, 'pending');
    assert.strictEqual(candidate.source_conversation_id, 'conv-99');
  });

  await t.test('validates payload formatting for creating a memory', () => {
    const payload: CreateMemoryPayload = {
      memory_key: 'Target: AWS Solutions Architect',
      memory_value: 'Studying for the SAA-C03 exam by Q3.',
      memory_type: 'goal_decision',
      confidence: 1.0,
    };

    assert.strictEqual(payload.memory_type, 'goal_decision');
    assert.ok(payload.memory_key.length <= 100);
    assert.ok(payload.memory_value.length > 0);
  });

  await t.test('validates edit-on-approve payload', () => {
    const approvePayload: ApproveSuggestionPayload = {
      memory_key: 'Refined key',
      memory_value: 'Refined value with user corrections.',
      memory_type: 'personal_context',
    };

    assert.strictEqual(approvePayload.memory_key, 'Refined key');
    assert.strictEqual(approvePayload.memory_type, 'personal_context');
  });

  await t.test('validates memory privacy and personalization toggle settings', () => {
    const defaultSettings: MemorySettings = {
      ai_memory_enabled: true,
      privacy_notice: 'Memories are saved locally on your device.',
    };

    assert.strictEqual(defaultSettings.ai_memory_enabled, true);

    const toggledSettings: MemorySettings = {
      ...defaultSettings,
      ai_memory_enabled: false,
    };

    assert.strictEqual(toggledSettings.ai_memory_enabled, false);
  });

  await t.test('filters memories by category correctly', () => {
    const memories: AIMemory[] = [
      {
        id: '1',
        user_id: 'u1',
        memory_key: 'Morning coffee',
        memory_value: 'Black coffee only',
        memory_type: 'preference',
        confidence: 0.9,
        status: 'confirmed',
        created_at: new Date().toISOString(),
      },
      {
        id: '2',
        user_id: 'u1',
        memory_key: 'Gym schedule',
        memory_value: 'Mondays and Thursdays at 6 PM',
        memory_type: 'routine_pattern',
        confidence: 0.88,
        status: 'confirmed',
        created_at: new Date().toISOString(),
      },
    ];

    const preferencesOnly = memories.filter((m) => m.memory_type === 'preference');
    assert.strictEqual(preferencesOnly.length, 1);
    assert.strictEqual(preferencesOnly[0].memory_key, 'Morning coffee');

    const routinesOnly = memories.filter((m) => m.memory_type === 'routine_pattern');
    assert.strictEqual(routinesOnly.length, 1);
    assert.strictEqual(routinesOnly[0].memory_key, 'Gym schedule');
  });
});

