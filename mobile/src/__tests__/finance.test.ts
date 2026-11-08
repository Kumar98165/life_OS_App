import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { z } from 'zod';

// Financial calculation helper functions
export function calculateNetSavings(income: string, expense: string): string {
  const inc = parseFloat(income) || 0;
  const exp = parseFloat(expense) || 0;
  return (inc - exp).toFixed(2);
}

export function calculateSavingsRate(income: string, expense: string): number {
  const inc = parseFloat(income) || 0;
  const exp = parseFloat(expense) || 0;
  if (inc <= 0) return 0;
  const net = inc - exp;
  if (net <= 0) return 0;
  return Math.round((net / inc) * 1000) / 10;
}

export function calculateBudgetUtilization(spent: string, budget: string): {
  percentage: number;
  remaining: string;
  isOverBudget: boolean;
} {
  const sp = parseFloat(spent) || 0;
  const bg = parseFloat(budget) || 0;
  if (bg <= 0) {
    return { percentage: 0, remaining: '0.00', isOverBudget: sp > 0 };
  }
  const pct = Math.round((sp / bg) * 1000) / 10;
  const rem = (bg - sp).toFixed(2);
  return {
    percentage: pct,
    remaining: rem,
    isOverBudget: sp > bg,
  };
}

export function calculateGoalProgress(current: string, target: string): number {
  const cur = parseFloat(current) || 0;
  const tgt = parseFloat(target) || 0;
  if (tgt <= 0) return 0;
  return Math.min(100, Math.round((cur / tgt) * 1000) / 10);
}

// Zod schemas for client-side forms
const transactionFormSchema = z.object({
  account_id: z.string().min(1, 'Account is required'),
  amount: z.string().refine((val) => {
    const num = parseFloat(val);
    return !isNaN(num) && num > 0;
  }, 'Amount must be a positive number'),
  transaction_type: z.enum(['income', 'expense', 'transfer']),
  description: z.string().trim().min(1, 'Description is required').max(255),
  category_id: z.string().optional(),
  is_recurring: z.boolean().default(false),
});

const budgetFormSchema = z.object({
  month: z.string().regex(/^\d{4}-(0[1-9]|1[0-2])$/, 'Month must be in YYYY-MM format'),
  amount: z.string().refine((val) => {
    const num = parseFloat(val);
    return !isNaN(num) && num > 0;
  }, 'Budget amount must be greater than 0'),
  category_id: z.string().nullable().optional(),
});

const savingsGoalFormSchema = z.object({
  title: z.string().trim().min(1, 'Goal title is required').max(150),
  target_amount: z.string().refine((val) => {
    const num = parseFloat(val);
    return !isNaN(num) && num > 0;
  }, 'Target amount must be greater than 0'),
  initial_deposit: z.string().optional(),
  target_date: z.string().nullable().optional(),
});

describe('Finance Domain - Decimal Arithmetic & Metrics', () => {
  test('calculates net savings accurately', () => {
    assert.strictEqual(calculateNetSavings('5000.00', '3200.50'), '1799.50');
    assert.strictEqual(calculateNetSavings('1500.00', '2000.00'), '-500.00');
    assert.strictEqual(calculateNetSavings('0.00', '0.00'), '0.00');
  });

  test('calculates savings rate percentage correctly', () => {
    assert.strictEqual(calculateSavingsRate('5000.00', '3500.00'), 30);
    assert.strictEqual(calculateSavingsRate('4000.00', '1000.00'), 75);
    // If expenses exceed income, rate is 0%
    assert.strictEqual(calculateSavingsRate('2000.00', '2500.00'), 0);
    // If income is 0, rate is 0%
    assert.strictEqual(calculateSavingsRate('0.00', '100.00'), 0);
  });

  test('calculates budget utilization, remaining amount, and over-budget flag', () => {
    const under = calculateBudgetUtilization('400.00', '500.00');
    assert.strictEqual(under.percentage, 80);
    assert.strictEqual(under.remaining, '100.00');
    assert.strictEqual(under.isOverBudget, false);

    const exact = calculateBudgetUtilization('500.00', '500.00');
    assert.strictEqual(exact.percentage, 100);
    assert.strictEqual(exact.remaining, '0.00');
    assert.strictEqual(exact.isOverBudget, false);

    const over = calculateBudgetUtilization('650.00', '500.00');
    assert.strictEqual(over.percentage, 130);
    assert.strictEqual(over.remaining, '-150.00');
    assert.strictEqual(over.isOverBudget, true);
  });

  test('calculates savings goal progress percentage safely', () => {
    assert.strictEqual(calculateGoalProgress('500.00', '2000.00'), 25);
    assert.strictEqual(calculateGoalProgress('2000.00', '2000.00'), 100);
    assert.strictEqual(calculateGoalProgress('2500.00', '2000.00'), 100); // capped at 100
    assert.strictEqual(calculateGoalProgress('0.00', '1000.00'), 0);
    assert.strictEqual(calculateGoalProgress('100.00', '0.00'), 0); // division by zero safety
  });
});

describe('Finance Domain - Form Validation Schemas', () => {
  test('transaction validation succeeds on valid data', () => {
    const result = transactionFormSchema.safeParse({
      account_id: 'acc-uuid-1',
      amount: '45.50',
      transaction_type: 'expense',
      description: 'Coffee and groceries',
      category_id: 'cat-uuid-1',
      is_recurring: false,
    });
    assert.strictEqual(result.success, true);
  });

  test('transaction validation rejects negative or zero amount', () => {
    const resZero = transactionFormSchema.safeParse({
      account_id: 'acc-uuid-1',
      amount: '0.00',
      transaction_type: 'expense',
      description: 'Zero test',
    });
    assert.strictEqual(resZero.success, false);

    const resNeg = transactionFormSchema.safeParse({
      account_id: 'acc-uuid-1',
      amount: '-15.00',
      transaction_type: 'expense',
      description: 'Negative test',
    });
    assert.strictEqual(resNeg.success, false);
  });

  test('transaction validation rejects empty description or missing account', () => {
    const resEmptyDesc = transactionFormSchema.safeParse({
      account_id: 'acc-uuid-1',
      amount: '20.00',
      transaction_type: 'income',
      description: '   ',
    });
    assert.strictEqual(resEmptyDesc.success, false);

    const resNoAcc = transactionFormSchema.safeParse({
      account_id: '',
      amount: '20.00',
      transaction_type: 'income',
      description: 'Valid description',
    });
    assert.strictEqual(resNoAcc.success, false);
  });

  test('budget validation enforces YYYY-MM format and positive amount', () => {
    const valid = budgetFormSchema.safeParse({
      month: '2026-11',
      amount: '400.00',
      category_id: null,
    });
    assert.strictEqual(valid.success, true);

    const invalidMonth = budgetFormSchema.safeParse({
      month: '11-2026',
      amount: '400.00',
    });
    assert.strictEqual(invalidMonth.success, false);

    const invalidMonthNum = budgetFormSchema.safeParse({
      month: '2026-13',
      amount: '400.00',
    });
    assert.strictEqual(invalidMonthNum.success, false);
  });

  test('savings goal validation requires title and positive target', () => {
    const valid = savingsGoalFormSchema.safeParse({
      title: 'Emergency Reserve',
      target_amount: '5000.00',
    });
    assert.strictEqual(valid.success, true);

    const emptyTitle = savingsGoalFormSchema.safeParse({
      title: '   ',
      target_amount: '5000.00',
    });
    assert.strictEqual(emptyTitle.success, false);

    const zeroTarget = savingsGoalFormSchema.safeParse({
      title: 'Valid Goal',
      target_amount: '0.00',
    });
    assert.strictEqual(zeroTarget.success, false);
  });
});

