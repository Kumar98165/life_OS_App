import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationService } from '../services/notificationService';
import {
  NotificationCategory,
  ReminderStatus,
  UpdateNotificationPreferencesPayload,
  CreateReminderPayload,
  UpdateReminderPayload,
  RegisterDeviceTokenPayload,
} from '../types/notification';

export const NOTIFICATION_QUERY_KEYS = {
  all: ['notifications'] as const,
  list: (params?: any) => ['notifications', 'list', params] as const,
  unreadCount: () => ['notifications', 'unreadCount'] as const,
  preferences: () => ['notifications', 'preferences'] as const,
  reminders: (status?: ReminderStatus) => ['notifications', 'reminders', status] as const,
};

// -----------------------------------------------------------------------------
// Queries
// -----------------------------------------------------------------------------

export function useNotifications(params?: {
  unread_only?: boolean;
  notification_type?: NotificationCategory;
  page?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: NOTIFICATION_QUERY_KEYS.list(params),
    queryFn: () => notificationService.getNotifications(params),
    staleTime: 1000 * 30, // 30 seconds
  });
}

export function useUnreadNotificationCount() {
  return useQuery({
    queryKey: NOTIFICATION_QUERY_KEYS.unreadCount(),
    queryFn: () => notificationService.getUnreadCount(),
    staleTime: 1000 * 30,
    refetchInterval: 1000 * 60, // Poll every 60s for live badge updates
  });
}

export function useNotificationPreferences() {
  return useQuery({
    queryKey: NOTIFICATION_QUERY_KEYS.preferences(),
    queryFn: () => notificationService.getPreferences(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function useReminders(status?: ReminderStatus) {
  return useQuery({
    queryKey: NOTIFICATION_QUERY_KEYS.reminders(status),
    queryFn: () => notificationService.getReminders({ status }),
    staleTime: 1000 * 60 * 1, // 1 minute
  });
}

// -----------------------------------------------------------------------------
// Mutations
// -----------------------------------------------------------------------------

export function useMarkAsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => notificationService.markAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: NOTIFICATION_QUERY_KEYS.all });
    },
  });
}

export function useMarkAllAsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => notificationService.markAllAsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: NOTIFICATION_QUERY_KEYS.all });
    },
  });
}

export function useDeleteNotification() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => notificationService.deleteNotification(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: NOTIFICATION_QUERY_KEYS.all });
    },
  });
}

export function useUpdateNotificationPreferences() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UpdateNotificationPreferencesPayload) =>
      notificationService.updatePreferences(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: NOTIFICATION_QUERY_KEYS.preferences() });
    },
  });
}

export function useCreateReminder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateReminderPayload) => notificationService.createReminder(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: NOTIFICATION_QUERY_KEYS.reminders() });
    },
  });
}

export function useUpdateReminder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateReminderPayload }) =>
      notificationService.updateReminder(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: NOTIFICATION_QUERY_KEYS.reminders() });
    },
  });
}

export function useDeleteReminder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => notificationService.deleteReminder(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: NOTIFICATION_QUERY_KEYS.reminders() });
    },
  });
}

export function useRegisterDeviceToken() {
  return useMutation({
    mutationFn: (payload: RegisterDeviceTokenPayload) =>
      notificationService.registerDeviceToken(payload),
  });
}

export function useScanContext() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => notificationService.scanContext(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: NOTIFICATION_QUERY_KEYS.all });
    },
  });
}

