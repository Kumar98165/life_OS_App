import { notificationService } from './notificationService';

function getPlatformOS(): string {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const rn = require('react-native');
    return rn?.Platform?.OS || 'unknown';
  } catch {
    return typeof window !== 'undefined' ? 'web' : 'node';
  }
}

export interface PushNotificationRegistrationResult {
  token: string | null;
  status: 'granted' | 'denied' | 'unsupported';
  error?: string;
}

export const pushNotificationService = {
  /**
   * Request push notification permissions and register token with backend.
   * Handles web, simulator, permission denial, and unsupported environments gracefully.
   */
  async registerForPushNotifications(): Promise<PushNotificationRegistrationResult> {
    const os = getPlatformOS();
    if (os === 'web' || os === 'node') {
      return { token: null, status: 'unsupported' };
    }

    try {
      // Dynamic import of expo-notifications to ensure safe execution in all runtimes
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      const Notifications = require('expo-notifications');
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      const Device = require('expo-device');

      if (!Device.isDevice) {
        return {
          token: null,
          status: 'unsupported',
          error: 'Push notifications are not supported on virtual simulators.',
        };
      }

      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        return { token: null, status: 'denied' };
      }

      const tokenResponse = await Notifications.getExpoPushTokenAsync();
      const token = tokenResponse.data;

      // Register device push token with backend
      await notificationService.registerDeviceToken({
        token,
        device_type: os,
        device_name: Device.modelName || `${os} Device`,
      });

      return { token, status: 'granted' };
    } catch (err: any) {
      return {
        token: null,
        status: 'unsupported',
        error: err?.message || 'Failed to initialize push notifications.',
      };
    }
  },

  /**
   * Parse deep-link payload and resolve navigation target.
   */
  parseNotificationDeepLink(dataPayload?: string | null): {
    route: string;
    params?: Record<string, any>;
  } | null {
    if (!dataPayload) return null;

    try {
      const parsed = typeof dataPayload === 'string' ? JSON.parse(dataPayload) : dataPayload;
      if (parsed && parsed.route) {
        return {
          route: parsed.route,
          params: parsed,
        };
      }
    } catch {
      // Non-JSON payload
    }
    return null;
  },
};

