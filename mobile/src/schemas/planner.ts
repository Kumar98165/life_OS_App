import { z } from 'zod';

export const plannerBlockFormSchema = z
  .object({
    title: z
      .string()
      .min(1, 'Title is required')
      .max(255, 'Title must not exceed 255 characters')
      .refine((val) => val.trim().length > 0, 'Title cannot be blank'),
    description: z.string().max(5000, 'Description too long').optional().nullable(),
    block_type: z.enum([
      'task',
      'personal',
      'work',
      'break',
      'learning',
      'meeting',
      'other',
      'focus',
      'routine',
    ]),
    status: z.enum(['scheduled', 'completed', 'cancelled', 'skipped']),
    date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be formatted as YYYY-MM-DD'),
    start_time: z.string().regex(/^([01]\d|2[0-3]):([0-5]\d)$/, 'Start time must be HH:MM'),
    end_time: z.string().regex(/^([01]\d|2[0-3]):([0-5]\d)$/, 'End time must be HH:MM'),
    task_id: z.string().optional().nullable(),
    color_hex: z
      .string()
      .regex(/^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/, 'Must be a valid hex color')
      .optional()
      .nullable(),
    recurrence_rule: z.enum(['daily', 'weekly', 'monthly', 'weekdays']).optional().nullable(),
    reminder_minutes_before: z.number().min(0).max(10080).optional().nullable(),
    timezone: z.string().optional().nullable(),
  })
  .refine(
    (data) => {
      const [startH, startM] = data.start_time.split(':').map(Number);
      const [endH, endM] = data.end_time.split(':').map(Number);
      const startMinutes = startH * 60 + startM;
      const endMinutes = endH * 60 + endM;
      return endMinutes > startMinutes;
    },
    {
      message: 'End time must be after start time',
      path: ['end_time'],
    }
  );

export type PlannerBlockFormData = z.infer<typeof plannerBlockFormSchema>;

