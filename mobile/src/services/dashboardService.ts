import { authService } from './authService';
import { taskService } from './taskService';
import { goalService } from './goalService';
import { habitService } from './habitService';
import { DashboardData, Task, Goal, Habit } from '../types';
import { calculateTaskProgress } from '../utils/dashboardUtils';

export const dashboardService = {
  /**
   * Fetches aggregated dashboard overview data for the authenticated user.
   */
  async getDashboardOverview(): Promise<DashboardData> {
    // 1. Fetch live authenticated user profile
    const user = await authService.getProfile();

    // 2. Fetch live today's tasks
    let todayTasks: Task[] = [];
    try {
      const taskResult = await taskService.getTasks({ due_date: 'today', per_page: 50 });
      todayTasks = taskResult.tasks;
    } catch {
      todayTasks = [];
    }

    // 3. Fetch live active goals
    let activeGoals: Goal[] = [];
    try {
      const goalResult = await goalService.getGoals({ status: 'in_progress', per_page: 10 });
      activeGoals = goalResult.goals;
    } catch {
      activeGoals = [];
    }

    // 4. Fetch live active habits
    let habits: Habit[] = [];
    try {
      habits = await habitService.getHabits({ include_archived: false });
    } catch {
      habits = [];
    }

    // 5. Compute accurate statistics from actual dataset
    const taskProgress = calculateTaskProgress(todayTasks);
    const activeCount = habits.length;
    const completedTodayCount = habits.filter((h) => h.completed_today).length;
    const completionRate =
      activeCount > 0 ? Math.round((completedTodayCount / activeCount) * 100) : 0;
    const habitSummary = {
      activeCount,
      completedTodayCount,
      completionRate,
    };

    return {
      user,
      todayTasks,
      activeGoals,
      habitSummary,
      taskProgress,
    };
  },
};

