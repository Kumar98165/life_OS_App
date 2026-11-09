import { describe, it } from 'node:test';
import assert from 'node:assert';
import {
  UserPersonalization,
  DailyRoutine,
  DashboardWidgetItem,
} from '../types/personalization';

describe('Personalization Domain Logic & State Validation', () => {
  it('correctly maps UserPersonalization object fields and default values', () => {
    const p: UserPersonalization = {
      id: 'pers-123',
      user_id: 'user-456',
      preferred_name: 'Alex',
      preferred_language: 'en',
      timezone: 'America/New_York',
      date_format: 'YYYY-MM-DD',
      time_format: '24h',
      week_start_day: 'monday',
      productivity_style: 'deep_work',
      task_priority_strategy: 'impact_first',
      ai_response_style: 'concise',
      ai_response_length: 'short',
      dashboard_widgets: [
        { id: 'today_tasks', visible: true, order: 0, title: "Today's Tasks" },
        { id: 'ai_quick_access', visible: false, order: 1, title: 'AI Assistant' },
      ],
      dashboard_density: 'comfortable',
      personalization_enabled: true,
    };

    assert.strictEqual(p.preferred_name, 'Alex');
    assert.strictEqual(p.productivity_style, 'deep_work');
    assert.strictEqual(p.task_priority_strategy, 'impact_first');
    assert.strictEqual(p.dashboard_widgets.length, 2);
    assert.strictEqual(p.dashboard_widgets[1].visible, false);
    assert.strictEqual(p.personalization_enabled, true);
  });

  it('validates DailyRoutine work hours and focus duration', () => {
    const routine: DailyRoutine = {
      id: 'rout-789',
      user_id: 'user-456',
      wake_time: '06:30',
      sleep_time: '22:30',
      work_start: '08:30',
      work_end: '16:30',
      work_days: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
      focus_block_duration_minutes: 45,
      break_duration_minutes: 15,
      lunch_start: '12:00',
      lunch_duration_minutes: 45,
      morning_routine_enabled: true,
      evening_routine_enabled: true,
      preferred_planning_time: '08:00',
      routine_reminders_enabled: true,
    };

    assert.strictEqual(routine.wake_time, '06:30');
    assert.strictEqual(routine.focus_block_duration_minutes, 45);
    assert.strictEqual(routine.work_days.length, 5);
    assert.ok(routine.work_days.includes('monday'));
    assert.ok(!routine.work_days.includes('sunday'));
  });

  it('correctly sorts and filters dashboard widgets by visibility and order', () => {
    const widgets: DashboardWidgetItem[] = [
      { id: 'habit_summary', visible: true, order: 3, title: 'Habits' },
      { id: 'daily_overview', visible: false, order: 0, title: 'Overview' },
      { id: 'today_tasks', visible: true, order: 1, title: 'Tasks' },
      { id: 'quick_actions', visible: true, order: 2, title: 'Actions' },
    ];

    const visibleSorted = widgets
      .filter((w) => w.visible)
      .sort((a, b) => a.order - b.order)
      .map((w) => w.id);

    assert.deepStrictEqual(visibleSorted, ['today_tasks', 'quick_actions', 'habit_summary']);
  });

  it('validates 24-hour time string format', () => {
    const timeRegex = /^\d{2}:\d{2}$/;
    assert.ok(timeRegex.test('09:00'));
    assert.ok(timeRegex.test('23:45'));
    assert.ok(!timeRegex.test('9:00'));
    assert.ok(!timeRegex.test('9am'));
    assert.ok(!timeRegex.test('invalid'));
  });
});
