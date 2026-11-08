import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { z } from 'zod';
import { pushNotificationService } from '../services/pushNotificationService';

// Relative time formatting utility
export function formatRelativeTime(isoString?: string, now: Date = new Date()): string {
  if (!isoString) return '';
  const dt = new Date(isoString);
  const diffMs = now.getTime() - dt.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHrs = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHrs / 24);
  if (diffMin < 1) return 'Just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHrs < 24) return `${diffHrs}h ago`;
  if (diffDays === 1) return 'Yesterday';
  return dt.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

// Client validation schemas
const reminderFormSchema = z.object({
  title: z.string().trim().min(1, 'Title is required').max(255),
  description: z.string().optional(),
  reminder_time: z.string().datetime(),
  is_recurring: z.boolean().default(false),
  recurrence_rule: z.enum(['daily', 'weekdays', 'weekly', 'monthly']).optional(),
});


const quietHoursSchema = z.object({
  start: z.string().regex(/^([01]\d|2[0-3]):[0-5]\d$/, 'Invalid 24h format HH:MM'),
  end: z.string().regex(/^([01]\d|2[0-3]):[0-5]\d$/, 'Invalid 24h format HH:MM'),
});

describe('Notification Domain - Relative Time Formatting', () => {
  test('formats recent notifications as "Just now" or minutes ago', () => {
    const fixedNow = new Date('2026-11-08T14:30:00Z');

    const justNow = new Date('2026-11-08T14:29:45Z').toISOString();
    assert.strictEqual(formatRelativeTime(justNow, fixedNow), 'Just now');

    const tenMinAgo = new Date('2026-11-08T14:20:00Z').toISOString();
    assert.strictEqual(formatRelativeTime(tenMinAgo, fixedNow), '10m ago');

    const twoHoursAgo = new Date('2026-11-08T12:30:00Z').toISOString();
    assert.strictEqual(formatRelativeTime(twoHoursAgo, fixedNow), '2h ago');

    const yesterday = new Date('2026-11-07T14:30:00Z').toISOString();
    assert.strictEqual(formatRelativeTime(yesterday, fixedNow), 'Yesterday');
  });

  test('handles null or empty dates safely without exceptions', () => {
    assert.strictEqual(formatRelativeTime(undefined), '');
    assert.strictEqual(formatRelativeTime(''), '');
  });
});

describe('Notification Domain - Deep Link Parsing', () => {
  test('parses JSON route and params correctly', () => {
    const payload = JSON.stringify({ route: 'TasksTab', taskId: '123-abc' });
    const parsed = pushNotificationService.parseNotificationDeepLink(payload);
    assert.notStrictEqual(parsed, null);
    assert.strictEqual(parsed?.route, 'TasksTab');
    assert.strictEqual(parsed?.params?.taskId, '123-abc');
  });

  test('returns null for empty, invalid or non-route payloads', () => {
    assert.strictEqual(pushNotificationService.parseNotificationDeepLink(null), null);
    assert.strictEqual(pushNotificationService.parseNotificationDeepLink(''), null);
    assert.strictEqual(pushNotificationService.parseNotificationDeepLink('not-json'), null);
    assert.strictEqual(pushNotificationService.parseNotificationDeepLink('{}'), null);
  });
});

describe('Notification Domain - Form Validation Schemas', () => {
  test('reminder schema succeeds on valid data', () => {
    const res = reminderFormSchema.safeParse({
      title: 'Review Financial Budgets',
      description: 'Check month-end savings rate.',
      reminder_time: new Date('2026-11-08T18:00:00Z').toISOString(),
      is_recurring: true,
      recurrence_rule: 'weekly',
    });
    assert.strictEqual(res.success, true);
  });

  test('reminder schema rejects blank title', () => {
    const res = reminderFormSchema.safeParse({
      title: '   ',
      reminder_time: new Date().toISOString(),
    });
    assert.strictEqual(res.success, false);
  });

  test('reminder schema rejects invalid recurrence rule', () => {
    const res = reminderFormSchema.safeParse({
      title: 'Daily Meeting',
      reminder_time: new Date().toISOString(),
      is_recurring: true,
      recurrence_rule: 'yearly', // Not in allowed enum
    });
    assert.strictEqual(res.success, false);
  });
  test('quiet hours validation accepts valid 24h format and rejects invalid formats', () => {
    const valid = quietHoursSchema.safeParse({ start: '22:00', end: '08:00' });
    assert.strictEqual(valid.success, true);

    const invalidHours = quietHoursSchema.safeParse({ start: '25:00', end: '08:00' });
    assert.strictEqual(invalidHours.success, false);

    const invalidMinutes = quietHoursSchema.safeParse({ start: '22:65', end: '08:00' });
    assert.strictEqual(invalidMinutes.success, false);

    const non24h = quietHoursSchema.safeParse({ start: '10:00 PM', end: '8:00 AM' });
    assert.strictEqual(non24h.success, false);
  });
});

