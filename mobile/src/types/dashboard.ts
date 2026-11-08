import { Task, Habit, User } from './index';
import { Goal } from './goal';

export { Goal };

export interface HabitSummary {
  activeCount: number;
  completedTodayCount: number;
  completionRate: number;
}

export interface DailyTaskProgress {
  completed: number;
  total: number;
  percentage: number;
  motivationalMessage: string;
}

export interface DashboardData {
  user: User | null;
  todayTasks: Task[];
  activeGoals: Goal[];
  habitSummary: HabitSummary;
  taskProgress: DailyTaskProgress;
}

