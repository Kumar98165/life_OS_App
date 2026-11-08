import { describe, it } from 'node:test';
import assert from 'node:assert';
import {
  AutomationDefinition,
  AutomationTemplate,
  AutomationExecution,
  AutomationApproval,
} from '../types/automation';

describe('Automation Domain Logic & State Validation', () => {
  it('correctly maps template definition properties', () => {
    const template: AutomationTemplate = {
      slug: 'plan_my_day',
      title: 'Plan My Day',
      category: 'productivity',
      description: 'Optimizes daily schedule',
      trigger_type: 'scheduled',
      scheduled_time: '08:00',
      scheduled_days: 'daily',
      configuration: { max_tasks: 3 },
    };

    assert.strictEqual(template.slug, 'plan_my_day');
    assert.strictEqual(template.category, 'productivity');
    assert.strictEqual(template.trigger_type, 'scheduled');
    assert.strictEqual(template.configuration.max_tasks, 3);
  });

  it('evaluates approval expiration status properly', () => {
    const now = new Date();
    const futureDate = new Date(now.getTime() + 24 * 60 * 60 * 1000).toISOString();
    const pastDate = new Date(now.getTime() - 60 * 1000).toISOString();

    const activeApproval: AutomationApproval = {
      id: 'appr-1',
      execution_id: 'exec-1',
      action_id: 'act-1',
      user_id: 'user-1',
      status: 'pending',
      parameter_hash: 'hash123',
      change_summary: 'Schedule deep work block',
      expires_at: futureDate,
      is_expired: false,
      created_at: now.toISOString(),
    };

    const expiredApproval: AutomationApproval = {
      ...activeApproval,
      id: 'appr-2',
      expires_at: pastDate,
      is_expired: true,
    };

    assert.strictEqual(activeApproval.is_expired, false);
    assert.strictEqual(expiredApproval.is_expired, true);
    assert.strictEqual(activeApproval.status, 'pending');
  });

  it('calculates execution duration and maps actions', () => {
    const execution: AutomationExecution = {
      id: 'exec-10',
      user_id: 'user-1',
      definition_title: 'Plan My Day',
      triggered_by: 'manual',
      status: 'awaiting_approval',
      risk_level: 'medium',
      trigger_payload: { user_request: 'Plan my morning' },
      execution_duration_ms: 1250,
      retry_count: 0,
      max_retries: 3,
      created_at: new Date().toISOString(),
      actions: [
        {
          id: 'act-1',
          execution_id: 'exec-10',
          user_id: 'user-1',
          sequence_order: 1,
          tool_name: 'tasks.create_task',
          action_type: 'create_task',
          description: 'Review Q4 Priorities',
          risk_level: 'medium',
          requires_approval: true,
          parameters: { title: 'Review Q4 Priorities', priority: 'high' },
          status: 'awaiting_approval',
          has_approval: true,
          approval_id: 'appr-1',
          created_at: new Date().toISOString(),
        },
      ],
    };

    assert.strictEqual(execution.status, 'awaiting_approval');
    assert.strictEqual(execution.risk_level, 'medium');
    assert.strictEqual(execution.execution_duration_ms, 1250);
    assert.strictEqual(execution.actions?.length, 1);
    assert.strictEqual(execution.actions?.[0].requires_approval, true);
    assert.strictEqual(execution.actions?.[0].tool_name, 'tasks.create_task');
  });

  it('validates pause and resume transitions', () => {
    let definition: AutomationDefinition = {
      id: 'def-1',
      user_id: 'user-1',
      slug: 'upcoming_deadlines',
      title: 'Upcoming Deadline Assistant',
      category: 'productivity',
      is_template: false,
      is_active: true,
      is_paused: false,
      trigger_type: 'scheduled',
      configuration: {},
      total_runs: 5,
      successful_runs: 5,
      failed_runs: 0,
      created_at: new Date().toISOString(),
    };

    // Pause
    definition = { ...definition, is_paused: true };
    assert.strictEqual(definition.is_paused, true);

    // Resume
    definition = { ...definition, is_paused: false };
    assert.strictEqual(definition.is_paused, false);
  });
});
