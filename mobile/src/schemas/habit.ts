import { z } from 'zod';

export const habitFormSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(255, 'Title must not exceed 255 characters')
    .refine((val) => val.trim().length > 0, 'Title cannot be blank'),
  description: z.string().max(2000, 'Description too long').optional().nullable().or(z.literal('')),
  frequency: z.enum(['daily', 'weekdays', 'weekly']),
  target_days_per_week: z.number().int().min(1).max(7),
  color_hex: z
    .string()
    .regex(/^#[0-9a-fA-F]{6}$/, 'Must be a valid hex color code (#RRGGBB)'),
  icon: z.string().max(50).optional().nullable().or(z.literal('')),
});

export type HabitFormData = z.infer<typeof habitFormSchema>;

export const habitLogSchema = z.object({
  log_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be formatted as YYYY-MM-DD')
    .optional(),
  completed: z.boolean().default(true),
  notes: z.string().max(1000, 'Notes too long').optional().nullable(),
});

export type HabitLogFormData = z.infer<typeof habitLogSchema>;
