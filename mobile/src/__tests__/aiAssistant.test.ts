import test from 'node:test';
import assert from 'node:assert';
import { AIMessage, AIConversation, AIHealthStatus } from '../types/ai';

test('AI Assistant - Data Structures & State Validation', async (t) => {
  await t.test('formats user and assistant message structures correctly', () => {
    const userMsg: AIMessage = {
      id: 'msg-1',
      conversation_id: 'conv-100',
      role: 'user',
      content: 'What tasks do I have scheduled today?',
      created_at: new Date().toISOString(),
    };

    const assistantMsg: AIMessage = {
      id: 'msg-2',
      conversation_id: 'conv-100',
      role: 'assistant',
      content: 'You have 3 tasks due today: Gym, Coding, and Grocery shopping.',
      created_at: new Date().toISOString(),
    };

    assert.strictEqual(userMsg.role, 'user');
    assert.strictEqual(assistantMsg.role, 'assistant');
    assert.strictEqual(userMsg.conversation_id, assistantMsg.conversation_id);
    assert.ok(assistantMsg.content.includes('tasks due today'));
  });

  await t.test('parses local AI health status correctly', () => {
    const operationalStatus: AIHealthStatus = {
      healthy: true,
      model_available: true,
      status: 'operational',
      model: 'qwen2.5:3b',
      available_models: ['qwen2.5:3b', 'llama3.2:latest'],
      base_url: 'http://localhost:11434',
      error: null,
    };

    assert.strictEqual(operationalStatus.healthy, true);
    assert.strictEqual(operationalStatus.model_available, true);
    assert.strictEqual(operationalStatus.model, 'qwen2.5:3b');
    assert.strictEqual(operationalStatus.status, 'operational');

    const degradedStatus: AIHealthStatus = {
      healthy: false,
      model_available: false,
      status: 'unreachable',
      model: 'qwen2.5:3b',
      error: 'Cannot connect to Ollama runtime',
    };

    assert.strictEqual(degradedStatus.healthy, false);
    assert.strictEqual(degradedStatus.status, 'unreachable');
  });

  await t.test('validates conversation thread metadata', () => {
    const conv: AIConversation = {
      id: 'conv-1',
      user_id: 'user-abc',
      title: 'Morning Productivity Plan',
      model_used: 'qwen2.5:3b',
      messages_count: 4,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    assert.strictEqual(conv.title, 'Morning Productivity Plan');
    assert.strictEqual(conv.model_used, 'qwen2.5:3b');
    assert.strictEqual(conv.messages_count, 4);
  });
});

