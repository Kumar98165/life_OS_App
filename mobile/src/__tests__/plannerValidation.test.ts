import test from 'node:test';
import assert from 'node:assert';
import { plannerBlockFormSchema } from '../schemas/planner';

test('Planner Form Validation - plannerBlockFormSchema', async (t) => {
  await t.test('fails when title is empty or blank whitespace', () => {
    const res1 = plannerBlockFormSchema.safeParse({
      title: '',
      date: '2026-11-08',
      start_time: '09:00',
      end_time: '10:00',
      block_type: 'work',
      status: 'scheduled',
    });
    assert.strictEqual(res1.success, false);

    const res2 = plannerBlockFormSchema.safeParse({
      title: '   ',
      date: '2026-11-08',
      start_time: '09:00',
      end_time: '10:00',
      block_type: 'work',
      status: 'scheduled',
    });
    assert.strictEqual(res2.success, false);
  });

  await t.test('fails when end_time is earlier than or equal to start_time', () => {
    // Equal times
    const res1 = plannerBlockFormSchema.safeParse({
      title: 'Valid Title',
      date: '2026-11-08',
      start_time: '10:00',
      end_time: '10:00',
      block_type: 'work',
      status: 'scheduled',
    });
    assert.strictEqual(res1.success, false);

    // End before start
    const res2 = plannerBlockFormSchema.safeParse({
      title: 'Valid Title',
      date: '2026-11-08',
      start_time: '11:00',
      end_time: '10:00',
      block_type: 'work',
      status: 'scheduled',
    });
    assert.strictEqual(res2.success, false);
  });

  await t.test('fails on invalid date format', () => {
    const res = plannerBlockFormSchema.safeParse({
      title: 'Valid Title',
      date: '11/08/2026', // wrong format
      start_time: '09:00',
      end_time: '10:00',
      block_type: 'work',
      status: 'scheduled',
    });
    assert.strictEqual(res.success, false);
  });

  await t.test('fails on invalid block_type or status', () => {
    const res = plannerBlockFormSchema.safeParse({
      title: 'Valid Title',
      date: '2026-11-08',
      start_time: '09:00',
      end_time: '10:00',
      block_type: 'invalid_type',
      status: 'scheduled',
    });
    assert.strictEqual(res.success, false);
  });

  await t.test('fails on malformed color_hex', () => {
    const res = plannerBlockFormSchema.safeParse({
      title: 'Valid Title',
      date: '2026-11-08',
      start_time: '09:00',
      end_time: '10:00',
      block_type: 'work',
      status: 'scheduled',
      color_hex: 'not-a-color',
    });
    assert.strictEqual(res.success, false);
  });

  await t.test('succeeds with valid minimal planner block data', () => {
    const res = plannerBlockFormSchema.safeParse({
      title: 'Architecture Review',
      date: '2026-11-08',
      start_time: '09:00',
      end_time: '10:30',
      block_type: 'work',
      status: 'scheduled',
    });
    assert.strictEqual(res.success, true);
    if (res.success) {
      assert.strictEqual(res.data.title, 'Architecture Review');
      assert.strictEqual(res.data.start_time, '09:00');
      assert.strictEqual(res.data.end_time, '10:30');
    }
  });

  await t.test('succeeds with complete optional fields (task_id, description, hex color)', () => {
    const res = plannerBlockFormSchema.safeParse({
      title: 'Coding Session',
      description: 'Implement daily planner and calendar module',
      date: '2026-11-08',
      start_time: '14:00',
      end_time: '16:00',
      block_type: 'learning',
      status: 'scheduled',
      task_id: 'task-uuid-1234',
      color_hex: '#6C63FF',
    });
    assert.strictEqual(res.success, true);
    if (res.success) {
      assert.strictEqual(res.data.task_id, 'task-uuid-1234');
      assert.strictEqual(res.data.color_hex, '#6C63FF');
    }
  });
});

test('Planner Scheduling Logic - Interval Overlap Detection', async (t) => {
  function checkOverlap(
    aStart: string,
    aEnd: string,
    bStart: string,
    bEnd: string
  ): boolean {
    const a1 = new Date(aStart).getTime();
    const a2 = new Date(aEnd).getTime();
    const b1 = new Date(bStart).getTime();
    const b2 = new Date(bEnd).getTime();
    return a1 < b2 && a2 > b1;
  }

  await t.test('detects overlapping time blocks', () => {
    const isOverlapping = checkOverlap(
      '2026-11-08T09:00:00Z',
      '2026-11-08T10:00:00Z',
      '2026-11-08T09:30:00Z',
      '2026-11-08T10:30:00Z'
    );
    assert.strictEqual(isOverlapping, true);
  });

  await t.test('allows strictly adjacent non-overlapping blocks', () => {
    const isOverlapping = checkOverlap(
      '2026-11-08T09:00:00Z',
      '2026-11-08T10:00:00Z',
      '2026-11-08T10:00:00Z',
      '2026-11-08T11:00:00Z'
    );
    assert.strictEqual(isOverlapping, false);
  });

  await t.test('allows disjoint non-overlapping blocks', () => {
    const isOverlapping = checkOverlap(
      '2026-11-08T09:00:00Z',
      '2026-11-08T10:00:00Z',
      '2026-11-08T14:00:00Z',
      '2026-11-08T15:00:00Z'
    );
    assert.strictEqual(isOverlapping, false);
  });
});

test('Planner Summary Metrics - Calculations', async (t) => {
  await t.test('computes total scheduled minutes and completion rate accurately', () => {
    const blocks = [
      { start: '2026-11-08T09:00:00Z', end: '2026-11-08T10:00:00Z', status: 'completed' },
      { start: '2026-11-08T10:00:00Z', end: '2026-11-08T11:30:00Z', status: 'scheduled' },
      { start: '2026-11-08T14:00:00Z', end: '2026-11-08T15:00:00Z', status: 'cancelled' },
    ];

    const activeBlocks = blocks.filter((b) => b.status !== 'cancelled');
    const totalMinutes = activeBlocks.reduce((acc, b) => {
      const dur = (new Date(b.end).getTime() - new Date(b.start).getTime()) / 60000;
      return acc + dur;
    }, 0);

    assert.strictEqual(totalMinutes, 150); // 60 + 90 = 150 mins

    const completedCount = blocks.filter((b) => b.status === 'completed').length;
    const totalCount = blocks.length;
    const rate = Math.round((completedCount / totalCount) * 100);
    assert.strictEqual(rate, 33);
  });
});

