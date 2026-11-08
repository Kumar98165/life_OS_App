import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { taskService } from '../services/taskService';
import {
  Task,
  TaskFilterParams,
  CreateTaskPayload,
  UpdateTaskPayload,
  TaskCategory,
} from '../types/task';
import { DASHBOARD_QUERY_KEY } from './useDashboard';

export const TASKS_QUERY_KEY = ['tasks'];
export const TASK_CATEGORIES_QUERY_KEY = ['taskCategories'];

export function useTasks(params?: TaskFilterParams) {
  return useQuery({
    queryKey: [...TASKS_QUERY_KEY, params],
    queryFn: () => taskService.getTasks(params),
    staleTime: 1000 * 60 * 1, // 1 minute
  });
}

export function useTodayTasks() {
  return useQuery({
    queryKey: [...TASKS_QUERY_KEY, 'today'],
    queryFn: () => taskService.getTasks({ due_date: 'today', per_page: 50 }),
    staleTime: 1000 * 60 * 1,
  });
}

export function useTaskDetails(taskId: string | null) {
  return useQuery({
    queryKey: ['taskDetails', taskId],
    queryFn: () => taskService.getTaskDetails(taskId!),
    enabled: !!taskId,
  });
}

export function useTaskCategories() {
  return useQuery({
    queryKey: TASK_CATEGORIES_QUERY_KEY,
    queryFn: () => taskService.getCategories(),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateTaskPayload) => taskService.createTask(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateTaskPayload }) =>
      taskService.updateTask(id, payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['taskDetails', data.id] });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useToggleCompleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => taskService.toggleCompleteTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => taskService.deleteTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}

