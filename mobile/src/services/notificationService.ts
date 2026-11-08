import { apiClient } from '../api/client';
import { ApiResponse } from '../types';
import {
  Notification,
  NotificationPreference,
  Reminder,
  PushDeviceToken,
  UpdateNotificationPreferencesPayload,
  CreateReminderPayload,
  UpdateReminderPayload,
  RegisterDeviceTokenPayload,
  NotificationCategory,
  ReminderStatus,
} from '../types/notification';

export const notificationService = {
  // -------------------------------------------------------------
  // Notification Center
  // -------------------------------------------------------------
  async getNotifications(params?: {
    unread_only?: boolean;
    notification_type?: NotificationCategory;
    page?: number;
    limit?: number;
  }): Promise<{
    notifications: Notification[];
    total: number;
    page: number;
    limit: number;
  }> {
    const response = await apiClient.get<
      ApiResponse<{
        notifications: Notification[];
        total: number;
        page: number;
        limit: number;
      }>
    >('/notifications', { params });
    return response.data.data;
  },

  async getUnreadCount(): Promise<number> {
    const response = await apiClient.get<ApiResponse<{ unread_count: number }>>(
      '/notifications/unread-count'
    );
    return response.data.data.unread_count;
  },

  async getNotification(id: string): Promise<Notification> {
    const response = await apiClient.get<ApiResponse<{ notification: Notification }>>(
      `/notifications/${id}`
    );
    return response.data.data.notification;
  },

  async markAsRead(id: string): Promise<Notification> {
    const response = await apiClient.patch<ApiResponse<{ notification: Notification }>>(
      `/notifications/${id}/read`
    );
    return response.data.data.notification;
  },

  async markAllAsRead(): Promise<number> {
    const response = await apiClient.patch<ApiResponse<{ marked_count: number }>>(
      '/notifications/read-all'
    );
    return response.data.data.marked_count;
  },

  async deleteNotification(id: string): Promise<void> {
    await apiClient.delete(`/notifications/${id}`);
  },

  // -------------------------------------------------------------
  // Preferences
  // -------------------------------------------------------------
  async getPreferences(): Promise<NotificationPreference> {
    const response = await apiClient.get<ApiResponse<{ preferences: NotificationPreference }>>(
      '/notifications/preferences'
    );
    return response.data.data.preferences;
  },

  async updatePreferences(
    payload: UpdateNotificationPreferencesPayload
  ): Promise<NotificationPreference> {
    const response = await apiClient.patch<ApiResponse<{ preferences: NotificationPreference }>>(
      '/notifications/preferences',
      payload
    );
    return response.data.data.preferences;
  },

  // -------------------------------------------------------------
  // Reminders
  // -------------------------------------------------------------
  async getReminders(params?: {
    status?: ReminderStatus;
    page?: number;
    limit?: number;
  }): Promise<{
    reminders: Reminder[];
    total: number;
    page: number;
    limit: number;
  }> {
    const response = await apiClient.get<
      ApiResponse<{
        reminders: Reminder[];
        total: number;
        page: number;
        limit: number;
      }>
    >('/notifications/reminders', { params });
    return response.data.data;
  },

  async createReminder(payload: CreateReminderPayload): Promise<Reminder> {
    const response = await apiClient.post<ApiResponse<{ reminder: Reminder }>>(
      '/notifications/reminders',
      payload
    );
    return response.data.data.reminder;
  },

  async updateReminder(id: string, payload: UpdateReminderPayload): Promise<Reminder> {
    const response = await apiClient.patch<ApiResponse<{ reminder: Reminder }>>(
      `/notifications/reminders/${id}`,
      payload
    );
    return response.data.data.reminder;
  },

  async deleteReminder(id: string): Promise<void> {
    await apiClient.delete(`/notifications/reminders/${id}`);
  },

  // -------------------------------------------------------------
  // Device Push Tokens
  // -------------------------------------------------------------
  async registerDeviceToken(payload: RegisterDeviceTokenPayload): Promise<PushDeviceToken> {
    const response = await apiClient.post<ApiResponse<{ device: PushDeviceToken }>>(
      '/notifications/devices',
      payload
    );
    return response.data.data.device;
  },

  async deleteDeviceToken(deviceId: string): Promise<void> {
    await apiClient.delete(`/notifications/devices/${deviceId}`);
  },

  // -------------------------------------------------------------
  // Context Scanner Trigger
  // -------------------------------------------------------------
  async scanContext(): Promise<{
    task_notifications: number;
    habit_notifications: number;
    finance_notifications: number;
    total_generated: number;
  }> {
    const response = await apiClient.post<
      ApiResponse<{
        task_notifications: number;
        habit_notifications: number;
        finance_notifications: number;
        total_generated: number;
      }>
    >('/notifications/scan');
    return response.data.data;
  },
};

