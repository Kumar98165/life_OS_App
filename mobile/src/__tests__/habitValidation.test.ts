import test from 'node:test';
import assert from 'node:assert';
import { habitFormSchema, habitLogSchema } from '../schemas/habit';

test('Habit Form Validation - habitFormSchema', async (t) => {
  await t.test('fails when title is empty or blank whitespace', () => {
    const res1 = habitFormSchema.safeParse({
      title: '',
      frequency: 'daily',
      target_days_per_week: 7,
      color_hex: '#6C63FF',
    });
    assert.strictEqual(res1.success, false);

    const res2 = habitFormSchema.safeParse({
      title: '    ',
      frequency: 'daily',
      target_days_per_week: 7,
      color_hex: '#6C63FF',
    });
    assert.strictEqual(res2.success, false);
  });

  await t.test('fails on invalid frequency', () => {
    const res = habitFormSchema.safeParse({
      title: 'Valid Habit Title',
      frequency: 'monthly_invalid',
      target_days_per_week: 7,
      color_hex: '#6C63FF',
    });
    assert.strictEqual(res.success, false);
  });

  await t.test('fails when target_days_per_week is out of range', () => {
    const resLow = habitFormSchema.safeParse({
      title: 'Valid Habit',
      frequency: 'weekly',
      target_days_per_week: 0,
      color_hex: '#6C63FF',
    });
    assert.strictEqual(resLow.success, false);

    const resHigh = habitFormSchema.safeParse({
      title: 'Valid Habit',
      frequency: 'weekly',
      target_days_per_week: 8,
      color_hex: '#6C63FF',
    });
    assert.strictEqual(resHigh.success, false);
  });

  await t.test('fails on invalid hex color code', () => {
    const res = habitFormSchema.safeParse({
      title: 'Morning Yoga',
      frequency: 'daily',
      target_days_per_week: 7,
      color_hex: 'invalid-hex-color',
    });
    assert.strictEqual(res.success, false);
  });

  await t.test('succeeds with valid daily habit configuration', () => {
    const res = habitFormSchema.safeParse({
      title: 'Morning Meditation',
      description: '15 mins mindfulness',
      frequency: 'daily',
      target_days_per_week: 7,
      color_hex: '#10B981',
      icon: 'leaf',
    });
    assert.strictEqual(res.success, true);
    if (res.success) {
      assert.strictEqual(res.data.title, 'Morning Meditation');
      assert.strictEqual(res.data.frequency, 'daily');
      assert.strictEqual(res.data.color_hex, '#10B981');
    }
  });

  await t.test('succeeds with valid weekday habit configuration', () => {
    const res = habitFormSchema.safeParse({
      title: 'Standup & Planning',
      frequency: 'weekdays',
      target_days_per_week: 5,
      color_hex: '#3B82F6',
      icon: 'fitness',
    });
    assert.strictEqual(res.success, true);
    if (res.success) {
      assert.strictEqual(res.data.frequency, 'weekdays');
    }
  });

  await t.test('succeeds with valid weekly target habit configuration', () => {
    const res = habitFormSchema.safeParse({
      title: 'Gym Workout',
      frequency: 'weekly',
      target_days_per_week: 4,
      color_hex: '#EF4444',
      icon: 'fitness',
    });
    assert.strictEqual(res.success, true);
    if (res.success) {
      assert.strictEqual(res.data.target_days_per_week, 4);
    }
  });
});

test('Habit Log Validation - habitLogSchema', async (t) => {
  await t.test('succeeds on valid check-in date format YYYY-MM-DD', () => {
    const res = habitLogSchema.safeParse({
      log_date: '2026-11-08',
      completed: true,
      notes: 'Completed ahead of schedule',
    });
    assert.strictEqual(res.success, true);
    if (res.success) {
      assert.strictEqual(res.data.completed, true);
      assert.strictEqual(res.data.log_date, '2026-11-08');
    }
  });

  await t.test('fails on malformed date format', () => {
    const res = habitLogSchema.safeParse({
      log_date: '11/08/2026',
      completed: true,
    });
    assert.strictEqual(res.success, false);
  });
});

