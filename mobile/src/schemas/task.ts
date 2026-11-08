import { z } from 'zod';

export const taskFormSchema = z.object({
  title: z
    .string()
    .trim()
    .min(1, 'Task title is required')
    .max(255, 'Title cannot exceed 255 characters'),
  description: z
    .string()
    .max(5000, 'Description cannot exceed 5000 characters')
    .optional()
    .nullable(),
  category_id: z.string().optional().nullable(),
  priority: z.enum(['low', 'medium', 'high', 'urgent']),
  due_date: z.string().optional().nullable(),
  estimated_minutes: z.number().min(1).max(1440).optional().nullable(),
});

export type TaskFormValues = z.infer<typeof taskFormSchema>;
