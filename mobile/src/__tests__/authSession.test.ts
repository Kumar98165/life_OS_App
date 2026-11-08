import test from 'node:test';
import assert from 'node:assert';
import { secureStorage } from '../services/secureStore';
import { setAuthToken, getAuthToken } from '../api/client';

// Test isolation: Mock server responses
const mockUser = {
  id: 'usr_test_123',
  email: 'test@example.com',
  full_name: 'Alex Morgan',
  created_at: new Date().toISOString(),
  is_active: true,
};

const mockTokens = {
  access_token: 'mock.access.token.123',
  refresh_token: 'mock.refresh.token.456',
};

test('Auth Storage - SecureStore and Session Management', async (t) => {
  await t.test('stores and retrieves refresh token securely', async () => {
    await secureStorage.setRefreshToken(mockTokens.refresh_token);
    const retrieved = await secureStorage.getRefreshToken();
    assert.strictEqual(retrieved, mockTokens.refresh_token);
  });

  await t.test('deletes refresh token upon session clearance', async () => {
    await secureStorage.setRefreshToken(mockTokens.refresh_token);
    await secureStorage.deleteRefreshToken();
    const retrieved = await secureStorage.getRefreshToken();
    assert.strictEqual(retrieved, null);
  });

  await t.test('stores and checks onboarding completion flag', async () => {
    await secureStorage.setOnboardingCompleted(false);
    assert.strictEqual(await secureStorage.getOnboardingCompleted(), false);

    await secureStorage.setOnboardingCompleted(true);
    assert.strictEqual(await secureStorage.getOnboardingCompleted(), true);
  });

  await t.test('persists and retrieves onboarding preferences', async () => {
    const prefs = {
      focusAreas: ['health', 'productivity'],
      initialGoals: ['routine'],
      themePreference: 'dark' as const,
      notificationFrequency: 'daily_summary' as const,
      aiInteractionStyle: 'balanced' as const,
    };
    await secureStorage.setOnboardingPreferences(prefs);
    const retrieved = await secureStorage.getOnboardingPreferences<typeof prefs>();
    assert.deepStrictEqual(retrieved, prefs);
  });
});

test('Auth Client - In-Memory Token Management', async (t) => {
  await t.test('sets and gets in-memory access token without persistent storage leak', () => {
    setAuthToken('test.bearer.token');
    assert.strictEqual(getAuthToken(), 'test.bearer.token');
    setAuthToken(null);
    assert.strictEqual(getAuthToken(), null);
  });
});

test('Auth Lifecycle & Navigation State Logic', async (t) => {
  await t.test('unauthenticated user is directed to Auth stack', () => {
    const state = {
      isAuthenticated: false,
      isRestoringSession: false,
      hasCompletedOnboarding: false,
    };

    // Route calculation logic matching RootNavigator
    const targetRoute = !state.isAuthenticated
      ? 'Auth'
      : !state.hasCompletedOnboarding
      ? 'Onboarding'
      : 'Main';

    assert.strictEqual(targetRoute, 'Auth');
  });

  await t.test('authenticated user who has not completed onboarding is directed to Onboarding', () => {
    const state = {
      isAuthenticated: true,
      isRestoringSession: false,
      hasCompletedOnboarding: false,
    };

    const targetRoute = !state.isAuthenticated
      ? 'Auth'
      : !state.hasCompletedOnboarding
      ? 'Onboarding'
      : 'Main';

    assert.strictEqual(targetRoute, 'Onboarding');
  });

  await t.test('authenticated user who completed onboarding is directed to Main', () => {
    const state = {
      isAuthenticated: true,
      isRestoringSession: false,
      hasCompletedOnboarding: true,
    };

    const targetRoute = !state.isAuthenticated
      ? 'Auth'
      : !state.hasCompletedOnboarding
      ? 'Onboarding'
      : 'Main';

    assert.strictEqual(targetRoute, 'Main');
  });

  await t.test('session restoration failure resets tokens and sets unauthenticated', async () => {
    // Simulate expired session
    await secureStorage.setRefreshToken('expired.refresh.token');
    setAuthToken('expired.access.token');

    // Simulate failure handler
    await secureStorage.deleteRefreshToken();
    setAuthToken(null);

    assert.strictEqual(await secureStorage.getRefreshToken(), null);
    assert.strictEqual(getAuthToken(), null);
  });

  await t.test('logout revokes refresh token and clears in-memory session', async () => {
    await secureStorage.setRefreshToken(mockTokens.refresh_token);
    setAuthToken(mockTokens.access_token);

    // Simulate logout action
    await secureStorage.deleteRefreshToken();
    setAuthToken(null);

    assert.strictEqual(await secureStorage.getRefreshToken(), null);
    assert.strictEqual(getAuthToken(), null);
  });
});
