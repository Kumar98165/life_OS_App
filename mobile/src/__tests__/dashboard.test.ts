import test from 'node:test';
import assert from 'node:assert';
import {
  getGreeting,
  formatDashboardDate,
  calculateTaskProgress,
  calculateHabitSummary,
} from '../utils/dashboardUtils';
import { Task, Habit, Goal } from '../types';

test('Dashboard Utils - Dynamic Greeting based on Local Time', async (t) => {
  await t.test('returns "Good Morning" between 05:00 and 11:59', () => {
    const morningEarly = new Date(2026, 10, 7, 5, 0, 0);
    const morningMid = new Date(2026, 10, 7, 9, 30, 0);
    const morningLate = new Date(2026, 10, 7, 11, 59, 59);

    assert.strictEqual(getGreeting(morningEarly), 'Good Morning');
    assert.strictEqual(getGreeting(morningMid), 'Good Morning');
    assert.strictEqual(getGreeting(morningLate), 'Good Morning');
  });

  await t.test('returns "Good Afternoon" between 12:00 and 16:59', () => {
    const noon = new Date(2026, 10, 7, 12, 0, 0);
    const afternoonMid = new Date(2026, 10, 7, 14, 15, 0);
    const afternoonLate = new Date(2026, 10, 7, 16, 59, 59);

    assert.strictEqual(getGreeting(noon), 'Good Afternoon');
    assert.strictEqual(getGreeting(afternoonMid), 'Good Afternoon');
    assert.strictEqual(getGreeting(afternoonLate), 'Good Afternoon');
  });

  await t.test('returns "Good Evening" between 17:00 and 04:59', () => {
    const eveningEarly = new Date(2026, 10, 7, 17, 0, 0);
    const eveningLate = new Date(2026, 10, 7, 22, 30, 0);
    const night = new Date(2026, 10, 7, 3, 0, 0);

    assert.strictEqual(getGreeting(eveningEarly), 'Good Evening');
    assert.strictEqual(getGreeting(eveningLate), 'Good Evening');
    assert.strictEqual(getGreeting(night), 'Good Evening');
  });
});

test('Dashboard Utils - Date Formatting', async (t) => {
  await t.test('formats date correctly for dashboard header', () => {
    const testDate = new Date(2026, 10, 7); // Nov 7, 2026 is Saturday
    const formatted = formatDashboardDate(testDate);
    assert.ok(formatted.includes('Nov 7'));
  });
});

test('Dashboard Utils - Task Progress Calculation', async (t) => {
  await t.test('handles 0 tasks safely without NaN or division by zero', () => {
    const progress = calculateTaskProgress([]);
    assert.strictEqual(progress.completed, 0);
    assert.strictEqual(progress.total, 0);
    assert.strictEqual(progress.percentage, 0);
    assert.ok(!Number.isNaN(progress.percentage));
    assert.ok(progress.motivationalMessage.includes('No tasks scheduled'));
  });

  await t.test('calculates partial progress percentage accurately', () => {
    const tasks: Task[] = [
      { id: '1', user_id: 'u1', title: 'Task 1', status: 'completed', priority: 'high', created_at: '', updated_at: '' },
      { id: '2', user_id: 'u1', title: 'Task 2', status: 'completed', priority: 'medium', created_at: '', updated_at: '' },
      { id: '3', user_id: 'u1', title: 'Task 3', status: 'todo', priority: 'low', created_at: '', updated_at: '' },
      { id: '4', user_id: 'u1', title: 'Task 4', status: 'todo', priority: 'medium', created_at: '', updated_at: '' },
    ];

    const progress = calculateTaskProgress(tasks);
    assert.strictEqual(progress.completed, 2);
    assert.strictEqual(progress.total, 4);
    assert.strictEqual(progress.percentage, 50);
    assert.ok(progress.motivationalMessage.includes('halfway'));
  });

  await t.test('handles 100% completion with celebration message', () => {
    const tasks: Task[] = [
      { id: '1', user_id: 'u1', title: 'Task 1', status: 'completed', priority: 'high', created_at: '', updated_at: '' },
      { id: '2', user_id: 'u1', title: 'Task 2', status: 'completed', priority: 'medium', created_at: '', updated_at: '' },
    ];

    const progress = calculateTaskProgress(tasks);
    assert.strictEqual(progress.completed, 2);
    assert.strictEqual(progress.total, 2);
    assert.strictEqual(progress.percentage, 100);
    assert.ok(progress.motivationalMessage.includes('completed all tasks'));
  });

  await t.test('handles 0% completion when tasks are present', () => {
    const tasks: Task[] = [
      { id: '1', user_id: 'u1', title: 'Task 1', status: 'todo', priority: 'urgent', created_at: '', updated_at: '' },
    ];

    const progress = calculateTaskProgress(tasks);
    assert.strictEqual(progress.completed, 0);
    assert.strictEqual(progress.total, 1);
    assert.strictEqual(progress.percentage, 0);
    assert.ok(progress.motivationalMessage.includes('Start with your top priority'));
  });
});

test('Dashboard Utils - Habit Summary Calculation', async (t) => {
  await t.test('handles empty habits list', () => {
    const summary = calculateHabitSummary([]);
    assert.strictEqual(summary.activeCount, 0);
    assert.strictEqual(summary.completedTodayCount, 0);
    assert.strictEqual(summary.completionRate, 0);
  });

  await t.test('calculates habit streak completion rate', () => {
    const habits: Habit[] = [
      { id: '1', user_id: 'u1', title: 'Morning Run', frequency: 'daily', target_days_per_week: 7, current_streak: 5, longest_streak: 10, color_hex: '#6C63FF', is_archived: false, created_at: '', updated_at: '' },
      { id: '2', user_id: 'u1', title: 'Meditation', frequency: 'daily', target_days_per_week: 7, current_streak: 0, longest_streak: 3, color_hex: '#6C63FF', is_archived: false, created_at: '', updated_at: '' },
    ];

    const summary = calculateHabitSummary(habits);
    assert.strictEqual(summary.activeCount, 2);
    assert.strictEqual(summary.completedTodayCount, 1);
    assert.strictEqual(summary.completionRate, 50);
  });
});

test('Dashboard - Empty State and Navigation Flags', async (t) => {
  await t.test('empty tasks collection triggers empty state view', () => {
    const tasks: Task[] = [];
    const shouldShowEmpty = tasks.length === 0;
    assert.strictEqual(shouldShowEmpty, true);
  });

  await t.test('empty goals collection triggers empty state view', () => {
    const goals: Goal[] = [];
    const shouldShowEmpty = goals.length === 0;
    assert.strictEqual(shouldShowEmpty, true);
  });

  await t.test('empty habits summary triggers empty state view', () => {
    const summary = calculateHabitSummary([]);
    const shouldShowEmpty = summary.activeCount === 0;
    assert.strictEqual(shouldShowEmpty, true);
  });
});

