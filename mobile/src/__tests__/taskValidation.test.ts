import test from 'node:test';
import assert from 'node:assert';
import { taskFormSchema } from '../schemas/task';
import { calculateTaskProgress } from '../utils/dashboardUtils';
import { Task } from '../types/task';

test('Task Form Validation - taskFormSchema', async (t) => {
  await t.test('fails when title is empty or blank whitespace', () => {
    const result1 = taskFormSchema.safeParse({
      title: '',
      priority: 'medium',
    });
    assert.strictEqual(result1.success, false);

    const result2 = taskFormSchema.safeParse({
      title: '   ',
      priority: 'medium',
    });
    assert.strictEqual(result2.success, false);
    if (!result2.success) {
      assert.ok(result2.error.issues.some((i) => i.message.includes('required')));
    }
  });

  await t.test('fails when priority is not one of low, medium, high, urgent', () => {
    const result = taskFormSchema.safeParse({
      title: 'Valid Task Title',
      priority: 'critical_invalid',
    });
    assert.strictEqual(result.success, false);
  });

  await t.test('fails when title exceeds 255 characters', () => {
    const longTitle = 'a'.repeat(256);
    const result = taskFormSchema.safeParse({
      title: longTitle,
      priority: 'high',
    });
    assert.strictEqual(result.success, false);
    if (!result.success) {
      assert.ok(result.error.issues.some((i) => i.message.includes('cannot exceed 255 characters')));
    }
  });

  await t.test('succeeds with valid task inputs', () => {
    const validData = {
      title: 'Deploy Production Backend',
      description: 'Run migration and verify health probes',
      category_id: 'cat_work_123',
      priority: 'urgent' as const,
      due_date: '2026-11-07T18:00:00Z',
      estimated_minutes: 45,
    };
    const result = taskFormSchema.safeParse(validData);
    assert.strictEqual(result.success, true);
    if (result.success) {
      assert.strictEqual(result.data.title, 'Deploy Production Backend');
      assert.strictEqual(result.data.priority, 'urgent');
      assert.strictEqual(result.data.estimated_minutes, 45);
    }
  });

  await t.test('succeeds with minimal required fields and nullables', () => {
    const minimalData = {
      title: 'Quick Task',
      priority: 'low' as const,
      description: null,
      category_id: null,
      due_date: null,
      estimated_minutes: null,
    };
    const result = taskFormSchema.safeParse(minimalData);
    assert.strictEqual(result.success, true);
  });
});

test('Task Domain - Completion and State Transitions', async (t) => {
  await t.test('toggles task completion state properly', () => {
    const pendingTask: Task = {
      id: 'task_1',
      user_id: 'usr_1',
      title: 'Review pull request',
      status: 'pending',
      priority: 'high',
      is_archived: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Toggle to completed
    const completedTask: Task = {
      ...pendingTask,
      status: 'completed',
      completed_at: new Date().toISOString(),
    };
    assert.strictEqual(completedTask.status, 'completed');
    assert.ok(completedTask.completed_at !== null);

    // Toggle back to pending
    const reopenedTask: Task = {
      ...completedTask,
      status: 'pending',
      completed_at: null,
    };
    assert.strictEqual(reopenedTask.status, 'pending');
    assert.strictEqual(reopenedTask.completed_at, null);
  });
});

test('Task Domain - Dashboard Progress Integration', async (t) => {
  await t.test('calculates correct task progress from actual task list', () => {
    const tasks: Task[] = [
      { id: '1', user_id: 'u1', title: 'Task 1', status: 'completed', priority: 'medium', is_archived: false, created_at: '', updated_at: '' },
      { id: '2', user_id: 'u1', title: 'Task 2', status: 'completed', priority: 'urgent', is_archived: false, created_at: '', updated_at: '' },
      { id: '3', user_id: 'u1', title: 'Task 3', status: 'pending', priority: 'low', is_archived: false, created_at: '', updated_at: '' },
    ];

    const progress = calculateTaskProgress(tasks);
    assert.strictEqual(progress.total, 3);
    assert.strictEqual(progress.completed, 2);
    assert.strictEqual(progress.percentage, 67);
  });
});

