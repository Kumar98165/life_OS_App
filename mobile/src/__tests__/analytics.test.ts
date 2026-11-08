import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { z } from 'zod';

// -----------------------------------------------------------------------------
// Life Score Client Calculation Helpers (Pure logic mirror)
// -----------------------------------------------------------------------------

export interface PillarInput {
  hasData: boolean;
  score: number;
  baseWeight: number;
}

export function computeNormalizedLifeScore(pillars: {
  productivity: PillarInput;
  habits: PillarInput;
  goals: PillarInput;
  finance: PillarInput;
}): { overallScore: number; tier: string; weights: Record<string, number> } {
  const activeWeights: Record<string, number> = {};
  let totalActive = 0;

  for (const [key, p] of Object.entries(pillars)) {
    if (p.hasData) {
      activeWeights[key] = p.baseWeight;
      totalActive += p.baseWeight;
    } else {
      activeWeights[key] = 0;
    }
  }

  const normalizedWeights: Record<string, number> = {};
  if (totalActive > 0) {
    for (const [key, w] of Object.entries(activeWeights)) {
      normalizedWeights[key] = w / totalActive;
    }
  } else {
    normalizedWeights.productivity = 0.25;
    normalizedWeights.habits = 0.25;
    normalizedWeights.goals = 0.25;
    normalizedWeights.finance = 0.25;
  }

  let composite = 0;
  for (const [key, p] of Object.entries(pillars)) {
    const s = p.hasData ? p.score : 100.0;
    composite += s * normalizedWeights[key];
  }

  const overall = Math.max(0, Math.min(100, Math.round(composite)));

  let tier = 'Building Momentum';
  if (overall >= 85) tier = 'Exceptional';
  else if (overall >= 70) tier = 'Strong';
  else if (overall >= 50) tier = 'Balanced';

  return {
    overallScore: overall,
    tier,
    weights: normalizedWeights,
  };
}

export function computeSavingsRate(income: number, expense: number): number {
  if (income <= 0) return 0.0;
  const net = income - expense;
  if (net <= 0) return 0.0;
  return Math.round((net / income) * 1000) / 10;
}

// -----------------------------------------------------------------------------
// Schema Validation
// -----------------------------------------------------------------------------

const dateRangeParamsSchema = z.object({
  period: z.enum(['day', 'week', 'month', 'year', 'custom']).default('week'),
  start_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Must be YYYY-MM-DD').optional(),
  end_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Must be YYYY-MM-DD').optional(),
  timezone: z.string().default('UTC'),
});

// -----------------------------------------------------------------------------
// Tests
// -----------------------------------------------------------------------------

describe('Life Score Engine - Dynamic Weight Normalization', () => {
  test('calculates 100 when all pillars have zero data (unpenalized)', () => {
    const result = computeNormalizedLifeScore({
      productivity: { hasData: false, score: 0, baseWeight: 0.3 },
      habits: { hasData: false, score: 0, baseWeight: 0.3 },
      goals: { hasData: false, score: 0, baseWeight: 0.2 },
      finance: { hasData: false, score: 0, baseWeight: 0.2 },
    });

    assert.strictEqual(result.overallScore, 100);
    assert.strictEqual(result.tier, 'Exceptional');
  });

  test('fairly re-normalizes weights when only productivity and habits exist', () => {
    const result = computeNormalizedLifeScore({
      productivity: { hasData: true, score: 80, baseWeight: 0.3 },
      habits: { hasData: true, score: 90, baseWeight: 0.3 },
      goals: { hasData: false, score: 0, baseWeight: 0.2 },
      finance: { hasData: false, score: 0, baseWeight: 0.2 },
    });

    // 0.3 + 0.3 = 0.6 active weight. Re-normalized weights: 0.5 each
    assert.strictEqual(result.weights.productivity, 0.5);
    assert.strictEqual(result.weights.habits, 0.5);
    assert.strictEqual(result.weights.goals, 0);
    assert.strictEqual(result.weights.finance, 0);

    // Composite: 80 * 0.5 + 90 * 0.5 = 85
    assert.strictEqual(result.overallScore, 85);
    assert.strictEqual(result.tier, 'Exceptional');
  });

  test('classifies tiers correctly across score intervals', () => {
    const pillarsAllActive = (score: number) => ({
      productivity: { hasData: true, score, baseWeight: 0.3 },
      habits: { hasData: true, score, baseWeight: 0.3 },
      goals: { hasData: true, score, baseWeight: 0.2 },
      finance: { hasData: true, score, baseWeight: 0.2 },
    });

    assert.strictEqual(computeNormalizedLifeScore(pillarsAllActive(92)).tier, 'Exceptional');
    assert.strictEqual(computeNormalizedLifeScore(pillarsAllActive(75)).tier, 'Strong');
    assert.strictEqual(computeNormalizedLifeScore(pillarsAllActive(60)).tier, 'Balanced');
    assert.strictEqual(computeNormalizedLifeScore(pillarsAllActive(42)).tier, 'Building Momentum');
  });
});

describe('Financial Analytics - Savings Rate Calculator', () => {
  test('computes positive savings rate with one decimal precision', () => {
    // $3000 income, $1200 expense => $1800 net => 60.0%
    const rate = computeSavingsRate(3000, 1200);
    assert.strictEqual(rate, 60.0);
  });

  test('returns 0.0 when expenses exceed income', () => {
    const rate = computeSavingsRate(2000, 2500);
    assert.strictEqual(rate, 0.0);
  });

  test('returns 0.0 when income is zero', () => {
    const rate = computeSavingsRate(0, 500);
    assert.strictEqual(rate, 0.0);
  });
});

describe('Analytics DateRangeParams Validation', () => {
  test('accepts valid predefined periods', () => {
    const parsed = dateRangeParamsSchema.parse({ period: 'week' });
    assert.strictEqual(parsed.period, 'week');
    assert.strictEqual(parsed.timezone, 'UTC');
  });

  test('rejects invalid period strings', () => {
    assert.throws(() => {
      dateRangeParamsSchema.parse({ period: 'decade' });
    });
  });

  test('validates YYYY-MM-DD custom dates', () => {
    const valid = dateRangeParamsSchema.parse({
      period: 'custom',
      start_date: '2026-11-01',
      end_date: '2026-11-08',
    });
    assert.strictEqual(valid.start_date, '2026-11-01');

    assert.throws(() => {
      dateRangeParamsSchema.parse({
        period: 'custom',
        start_date: '01-11-2026',
      });
    });
  });
});

