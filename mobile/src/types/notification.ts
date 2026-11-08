export type NotificationCategory =
  | 'task'
  | 'planner'
  | 'habit'
  | 'goal'
  | 'finance'
  | 'reminder'
  | 'system'
  | 'general';

export type ReminderStatus = 'pending' | 'triggered' | 'cancelled' | 'snoozed' | 'expired';
export type RecurrenceRule = 'daily' | 'weekdays' | 'weekly' | 'monthly';

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  body: string;
  notification_type: NotificationCategory;
  entity_type?: string | null;
  entity_id?: string | null;
  is_read: boolean;
  read_at?: string | null;
  scheduled_for?: string | null;
  data_payload?: string | null; // JSON string
  is_delivered: boolean;
  delivered_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface NotificationPreference {
  id: string;
  user_id: string;
  tasks_enabled: boolean;
  planner_enabled: boolean;
  habits_enabled: boolean;
  goals_enabled: boolean;
  finance_enabled: boolean;
  push_enabled: boolean;
  in_app_enabled: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start: string; // "HH:MM"
  quiet_hours_end: string; // "HH:MM"
  timezone: string;
  created_at?: string;
  updated_at?: string;
}

export interface Reminder {
  id: string;
  user_id: string;
  title: string;
  description?: string | null;
  reminder_time: string; // ISO string
  entity_type?: string | null;
  entity_id?: string | null;
  is_recurring: boolean;
  recurrence_rule?: RecurrenceRule | null;
  status: ReminderStatus;
  triggered_at?: string | null;
  notification_id?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface PushDeviceToken {
  id: string;
  user_id: string;
  token: string;
  device_type: string;
  device_name?: string | null;
  is_active: boolean;
  last_used_at?: string | null;
  created_at?: string;
}

// Request Payloads
export interface UpdateNotificationPreferencesPayload {
  tasks_enabled?: boolean;
  planner_enabled?: boolean;
  habits_enabled?: boolean;
  goals_enabled?: boolean;
  finance_enabled?: boolean;
  push_enabled?: boolean;
  in_app_enabled?: boolean;
  quiet_hours_enabled?: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  timezone?: string;
}

export interface CreateReminderPayload {
  title: string;
  description?: string;
  reminder_time: string;
  entity_type?: string;
  entity_id?: string;
  is_recurring?: boolean;
  recurrence_rule?: RecurrenceRule;
}

export interface UpdateReminderPayload {
  title?: string;
  description?: string;
  reminder_time?: string;
  status?: ReminderStatus;
  is_recurring?: boolean;
  recurrence_rule?: RecurrenceRule;
}

export interface RegisterDeviceTokenPayload {
  token: string;
  device_type?: string;
  device_name?: string;
}

