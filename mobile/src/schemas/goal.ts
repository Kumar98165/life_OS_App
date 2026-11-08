import { z } from 'zod';

export const goalFormSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(255, 'Title must not exceed 255 characters')
    .refine((val) => val.trim().length > 0, 'Title cannot be blank'),
  description: z.string().max(5000, 'Description too long').optional().nullable(),
  target_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Target date must be formatted as YYYY-MM-DD')
    .optional()
    .nullable()
    .or(z.literal('')),
  priority: z.enum(['low', 'medium', 'high']),
  status: z.enum([
    'not_started',
    'in_progress',
    'completed',
    'paused',
    'cancelled',
    'active',
    'achieved',
    'abandoned',
  ]),
  category: z.string().max(50, 'Category too long').optional().nullable().or(z.literal('')),
});

export type GoalFormData = z.infer<typeof goalFormSchema>;

export const milestoneFormSchema = z.object({
  title: z
    .string()
    .min(1, 'Milestone title is required')
    .max(255, 'Milestone title must not exceed 255 characters')
    .refine((val) => val.trim().length > 0, 'Title cannot be blank'),
  description: z.string().max(5000, 'Description too long').optional().nullable(),
  target_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Target date must be formatted as YYYY-MM-DD')
    .optional()
    .nullable()
    .or(z.literal('')),
  sort_order: z.number().int().min(0).optional(),
});

export type MilestoneFormData = z.infer<typeof milestoneFormSchema>;
