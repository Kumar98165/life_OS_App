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

  await t.test('validates thumbs-down quick action and optional details submission payload', () => {
    // 1. Quick downvote payload without extra details
    const quickDownvote = {
      message_id: 'msg-2',
      rating: -1,
      feedback_type: 'thumbs_down',
      category: 'other',
    };
    assert.strictEqual(quickDownvote.rating, -1);
    assert.strictEqual(quickDownvote.category, 'other');

    // 2. Enhanced negative feedback with category and written comment
    const detailedFeedback = {
      message_id: 'msg-2',
      rating: -1,
      feedback_type: 'thumbs_down',
      category: 'incorrect_answer',
      comment: 'The summary omitted my third task.',
    };
    assert.strictEqual(detailedFeedback.category, 'incorrect_answer');
    assert.strictEqual(detailedFeedback.comment, 'The summary omitted my third task.');

    // 3. Repeated feedback updating same message in place
    const updatedFeedback = {
      ...detailedFeedback,
      category: 'incomplete_answer',
      comment: 'Updated: Actually it missed 2 tasks.',
    };
    assert.strictEqual(updatedFeedback.message_id, detailedFeedback.message_id);
    assert.strictEqual(updatedFeedback.category, 'incomplete_answer');
  });

  await t.test('validates feedback analytics response data structure with empty and populated states', () => {
    // Empty state: total_feedback_count is 0, satisfaction_percentage is null
    const emptyAnalytics: import('../types/ai').FeedbackAnalytics = {
      user_id: 'user-abc',
      window_days: 30,
      total_feedback_count: 0,
      positive_count: 0,
      negative_count: 0,
      satisfaction_percentage: null,
      negative_categories: {},
      feedback_types: {},
      improvement_recommendations: [
        {
          area: 'general',
          recommendation: 'No feedback collected yet.',
          severity: 'info',
        },
      ],
    };
    assert.strictEqual(emptyAnalytics.total_feedback_count, 0);
    assert.strictEqual(emptyAnalytics.satisfaction_percentage, null);
    assert.strictEqual(emptyAnalytics.improvement_recommendations[0].severity, 'info');

    // Populated state: valid satisfaction_percentage computed
    const populatedAnalytics: import('../types/ai').FeedbackAnalytics = {
      user_id: 'user-abc',
      window_days: 30,
      total_feedback_count: 10,
      positive_count: 8,
      negative_count: 2,
      satisfaction_percentage: 80.0,
      negative_categories: { incorrect_answer: 2 },
      feedback_types: { thumbs_up: 8, thumbs_down: 2 },
      improvement_recommendations: [
        {
          area: 'factual_consistency',
          recommendation: 'Prioritize strict grounding in verified context.',
          severity: 'high',
        },
      ],
    };
    assert.strictEqual(populatedAnalytics.total_feedback_count, 10);
    assert.strictEqual(populatedAnalytics.satisfaction_percentage, 80.0);
  });
});

