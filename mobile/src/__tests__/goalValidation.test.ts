import test from 'node:test';
import assert from 'node:assert';
import { goalFormSchema, milestoneFormSchema } from '../schemas/goal';

test('Goal Form Validation - goalFormSchema', async (t) => {
  await t.test('fails when title is empty or blank whitespace', () => {
    const res1 = goalFormSchema.safeParse({
      title: '',
      priority: 'medium',
      status: 'in_progress',
    });
    assert.strictEqual(res1.success, false);

    const res2 = goalFormSchema.safeParse({
      title: '   ',
      priority: 'medium',
      status: 'in_progress',
    });
    assert.strictEqual(res2.success, false);
  });

  await t.test('fails on invalid priority', () => {
    const res = goalFormSchema.safeParse({
      title: 'Valid Goal Title',
      priority: 'critical_emergency',
      status: 'in_progress',
    });
    assert.strictEqual(res.success, false);
  });

  await t.test('fails on malformed target_date format', () => {
    const res = goalFormSchema.safeParse({
      title: 'Valid Goal Title',
      target_date: '12/31/2026', // wrong format
      priority: 'medium',
      status: 'in_progress',
    });
    assert.strictEqual(res.success, false);
  });

  await t.test('succeeds with valid minimal goal inputs', () => {
    const res = goalFormSchema.safeParse({
      title: 'Learn Cloud Architecture',
      priority: 'high',
      status: 'in_progress',
    });
    assert.strictEqual(res.success, true);
    if (res.success) {
      assert.strictEqual(res.data.title, 'Learn Cloud Architecture');
      assert.strictEqual(res.data.priority, 'high');
      assert.strictEqual(res.data.status, 'in_progress');
    }
  });

  await t.test('succeeds with complete optional fields', () => {
    const res = goalFormSchema.safeParse({
      title: 'Become AWS Solutions Architect',
      description: 'Complete hands-on projects, study guides, and take the official exam',
      target_date: '2026-12-31',
      priority: 'high',
      status: 'in_progress',
      category: 'Career',
    });
    assert.strictEqual(res.success, true);
    if (res.success) {
      assert.strictEqual(res.data.target_date, '2026-12-31');
      assert.strictEqual(res.data.category, 'Career');
    }
  });
});

test('Milestone Form Validation - milestoneFormSchema', async (t) => {
  await t.test('fails when title is empty or blank', () => {
    const res = milestoneFormSchema.safeParse({
      title: '   ',
      sort_order: 1,
    });
    assert.strictEqual(res.success, false);
  });

  await t.test('fails on negative sort_order', () => {
    const res = milestoneFormSchema.safeParse({
      title: 'Valid Milestone',
      sort_order: -5,
    });
    assert.strictEqual(res.success, false);
  });

  await t.test('succeeds with valid milestone inputs', () => {
    const res = milestoneFormSchema.safeParse({
      title: 'Complete VPC and Networking Module',
      description: 'Set up private/public subnets, NAT Gateways, and Route Tables',
      target_date: '2026-11-20',
      sort_order: 2,
    });
    assert.strictEqual(res.success, true);
    if (res.success) {
      assert.strictEqual(res.data.title, 'Complete VPC and Networking Module');
      assert.strictEqual(res.data.sort_order, 2);
    }
  });
});

test('Goal Progress Calculation Logic', async (t) => {
  function calculateProgress(milestones: { is_completed: boolean }[]): number {
    if (!milestones || milestones.length === 0) {
      return 0.0;
    }
    const completed = milestones.filter((m) => m.is_completed).length;
    return Math.round((completed / milestones.length) * 100);
  }

  await t.test('handles zero milestones without division by zero', () => {
    assert.strictEqual(calculateProgress([]), 0.0);
  });

  await t.test('computes exact milestone completion percentages', () => {
    // 1 of 4 completed = 25%
    const ms1 = [
      { is_completed: true },
      { is_completed: false },
      { is_completed: false },
      { is_completed: false },
    ];
    assert.strictEqual(calculateProgress(ms1), 25);

    // 2 of 4 completed = 50%
    const ms2 = [
      { is_completed: true },
      { is_completed: true },
      { is_completed: false },
      { is_completed: false },
    ];
    assert.strictEqual(calculateProgress(ms2), 50);

    // 3 of 4 completed = 75%
    const ms3 = [
      { is_completed: true },
      { is_completed: true },
      { is_completed: true },
      { is_completed: false },
    ];
    assert.strictEqual(calculateProgress(ms3), 75);

    // 4 of 4 completed = 100%
    const ms4 = [
      { is_completed: true },
      { is_completed: true },
      { is_completed: true },
      { is_completed: true },
    ];
    assert.strictEqual(calculateProgress(ms4), 100);
  });

  await t.test('handles rounded percentages properly', () => {
    // 1 of 3 completed = 33%
    const ms = [
      { is_completed: true },
      { is_completed: false },
      { is_completed: false },
    ];
    assert.strictEqual(calculateProgress(ms), 33);
  });
});

