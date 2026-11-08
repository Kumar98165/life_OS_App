const REFRESH_TOKEN_KEY = 'lifeos_refresh_token';
const ONBOARDING_COMPLETED_KEY = 'lifeos_onboarding_completed';
const ONBOARDING_PREFS_KEY = 'lifeos_onboarding_prefs';

// In-memory fallback for non-native environments (e.g. web browser, Node test runner)
const memoryStorage: Record<string, string> = {};

type SecureStoreModule = typeof import('expo-secure-store');
let secureStoreModule: SecureStoreModule | null = null;
let checkedAvailability = false;

function getPlatformOS(): string {
  try {
    // Dynamic access so unit test environments without react-native bundler do not fail
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const rn = require('react-native');
    return rn?.Platform?.OS || 'unknown';
  } catch {
    return typeof window !== 'undefined' ? 'web' : 'node';
  }
}

async function getSecureStore(): Promise<SecureStoreModule | null> {
  const os = getPlatformOS();
  if (os === 'web' || os === 'node') {
    return null;
  }
  if (checkedAvailability) {
    return secureStoreModule;
  }
  try {
    const mod = await import('expo-secure-store');
    const available = await mod.isAvailableAsync();
    secureStoreModule = available ? mod : null;
  } catch {
    secureStoreModule = null;
  } finally {
    checkedAvailability = true;
  }
  return secureStoreModule;
}

export const secureStorage = {
  async setItem(key: string, value: string): Promise<void> {
    const store = await getSecureStore();
    if (store) {
      await store.setItemAsync(key, value, {
        keychainAccessible: store.AFTER_FIRST_UNLOCK,
      });
    } else {
      memoryStorage[key] = value;
      if (typeof window !== 'undefined' && window.sessionStorage) {
        try {
          window.sessionStorage.setItem(key, value);
        } catch {
          // Ignore storage restrictions
        }
      }
    }
  },

  async getItem(key: string): Promise<string | null> {
    const store = await getSecureStore();
    if (store) {
      return await store.getItemAsync(key);
    }
    if (memoryStorage[key] !== undefined) {
      return memoryStorage[key];
    }
    if (typeof window !== 'undefined' && window.sessionStorage) {
      try {
        return window.sessionStorage.getItem(key);
      } catch {
        return null;
      }
    }
    return null;
  },

  async deleteItem(key: string): Promise<void> {
    const store = await getSecureStore();
    if (store) {
      await store.deleteItemAsync(key);
    }
    delete memoryStorage[key];
    if (typeof window !== 'undefined' && window.sessionStorage) {
      try {
        window.sessionStorage.removeItem(key);
      } catch {
        // Ignore
      }
    }
  },

  async setRefreshToken(token: string): Promise<void> {
    await this.setItem(REFRESH_TOKEN_KEY, token);
  },

  async getRefreshToken(): Promise<string | null> {
    return await this.getItem(REFRESH_TOKEN_KEY);
  },

  async deleteRefreshToken(): Promise<void> {
    await this.deleteItem(REFRESH_TOKEN_KEY);
  },

  async setOnboardingCompleted(completed: boolean): Promise<void> {
    await this.setItem(ONBOARDING_COMPLETED_KEY, completed ? 'true' : 'false');
  },

  async getOnboardingCompleted(): Promise<boolean> {
    const val = await this.getItem(ONBOARDING_COMPLETED_KEY);
    return val === 'true';
  },

  async setOnboardingPreferences(prefs: object): Promise<void> {
    await this.setItem(ONBOARDING_PREFS_KEY, JSON.stringify(prefs));
  },

  async getOnboardingPreferences<T>(): Promise<T | null> {
    const val = await this.getItem(ONBOARDING_PREFS_KEY);
    if (!val) return null;
    try {
      return JSON.parse(val) as T;
    } catch {
      return null;
    }
  },

  async clearAllAuthStorage(): Promise<void> {
    await this.deleteRefreshToken();
  },
};
