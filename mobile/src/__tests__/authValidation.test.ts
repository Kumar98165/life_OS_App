import test from 'node:test';
import assert from 'node:assert';
import { loginSchema, registerSchema } from '../schemas/auth';

test('Auth Validation - Login Schema', async (t) => {
  await t.test('fails when email is empty', () => {
    const result = loginSchema.safeParse({ email: '', password: 'Password123' });
    assert.strictEqual(result.success, false);
    if (!result.success) {
      assert.ok(result.error.issues.some((i) => i.path.includes('email')));
    }
  });

  await t.test('fails when email format is invalid', () => {
    const result = loginSchema.safeParse({ email: 'not-an-email', password: 'Password123' });
    assert.strictEqual(result.success, false);
    if (!result.success) {
      assert.ok(result.error.issues.some((i) => i.message.includes('valid email')));
    }
  });

  await t.test('fails when password is empty', () => {
    const result = loginSchema.safeParse({ email: 'test@example.com', password: '' });
    assert.strictEqual(result.success, false);
    if (!result.success) {
      assert.ok(result.error.issues.some((i) => i.path.includes('password')));
    }
  });

  await t.test('succeeds with valid email and password', () => {
    const result = loginSchema.safeParse({ email: 'user@example.com', password: 'MyPassword1' });
    assert.strictEqual(result.success, true);
    if (result.success) {
      assert.strictEqual(result.data.email, 'user@example.com');
      assert.strictEqual(result.data.password, 'MyPassword1');
    }
  });
});

test('Auth Validation - Registration Schema', async (t) => {
  await t.test('fails when full name is shorter than 2 characters', () => {
    const result = registerSchema.safeParse({
      full_name: 'A',
      email: 'alex@example.com',
      password: 'SecurePassword1',
      confirmPassword: 'SecurePassword1',
    });
    assert.strictEqual(result.success, false);
    if (!result.success) {
      assert.ok(result.error.issues.some((i) => i.message.includes('at least 2 characters')));
    }
  });

  await t.test('fails when password is shorter than 8 characters', () => {
    const result = registerSchema.safeParse({
      full_name: 'Alex Morgan',
      email: 'alex@example.com',
      password: 'Pass1',
      confirmPassword: 'Pass1',
    });
    assert.strictEqual(result.success, false);
    if (!result.success) {
      assert.ok(result.error.issues.some((i) => i.message.includes('at least 8 characters')));
    }
  });

  await t.test('fails when password contains no digit', () => {
    const result = registerSchema.safeParse({
      full_name: 'Alex Morgan',
      email: 'alex@example.com',
      password: 'PasswordOnly',
      confirmPassword: 'PasswordOnly',
    });
    assert.strictEqual(result.success, false);
    if (!result.success) {
      assert.ok(result.error.issues.some((i) => i.message.includes('one letter and one number')));
    }
  });

  await t.test('fails when password contains no letter', () => {
    const result = registerSchema.safeParse({
      full_name: 'Alex Morgan',
      email: 'alex@example.com',
      password: '1234567890',
      confirmPassword: '1234567890',
    });
    assert.strictEqual(result.success, false);
    if (!result.success) {
      assert.ok(result.error.issues.some((i) => i.message.includes('one letter and one number')));
    }
  });

  await t.test('fails when confirmPassword does not match password', () => {
    const result = registerSchema.safeParse({
      full_name: 'Alex Morgan',
      email: 'alex@example.com',
      password: 'SecurePassword1',
      confirmPassword: 'DifferentPassword2',
    });
    assert.strictEqual(result.success, false);
    if (!result.success) {
      assert.ok(result.error.issues.some((i) => i.message.includes('do not match')));
    }
  });

  await t.test('succeeds and normalizes email with valid registration data', () => {
    const result = registerSchema.safeParse({
      full_name: '  Alex Morgan  ',
      email: '  ALEX@Example.Com  ',
      password: 'ValidPassword1',
      confirmPassword: 'ValidPassword1',
    });
    assert.strictEqual(result.success, true);
    if (result.success) {
      assert.strictEqual(result.data.full_name, 'Alex Morgan');
      assert.strictEqual(result.data.email, 'alex@example.com');
      assert.strictEqual(result.data.password, 'ValidPassword1');
    }
  });
});
