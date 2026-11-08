import { Task, Habit, DailyTaskProgress, HabitSummary } from '../types';

/**
 * Returns dynamic greeting based on current local hour.
 * - 05:00 to 11:59: "Good Morning"
 * - 12:00 to 16:59: "Good Afternoon"
 * - 17:00 to 04:59: "Good Evening"
 */
export function getGreeting(date: Date = new Date()): string {
  const hour = date.getHours();
  if (hour >= 5 && hour < 12) {
    return 'Good Morning';
  }
  if (hour >= 12 && hour < 17) {
    return 'Good Afternoon';
  }
  return 'Good Evening';
}

/**
 * Formats date for dashboard display header.
 * Example: "Tuesday, Nov 7"
 */
export function formatDashboardDate(date: Date = new Date()): string {
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Calculates task completion statistics and generates an honest motivational message.
 * Safely handles 0 tasks without NaN or division by zero.
 */
export function calculateTaskProgress(tasks: Task[] = []): DailyTaskProgress {
  const total = tasks.length;
  if (total === 0) {
    return {
      completed: 0,
      total: 0,
      percentage: 0,
      motivationalMessage: 'No tasks scheduled for today. Take time to plan your priorities.',
    };
  }

  const completed = tasks.filter((t) => t.status === 'completed').length;
  const percentage = Math.round((completed / total) * 100);

  let motivationalMessage: string;
  if (percentage === 100) {
    motivationalMessage = "Outstanding! You've completed all tasks for today! 🎯";
  } else if (percentage >= 75) {
    motivationalMessage = 'Almost there! Keep the momentum going strong! ⚡';
  } else if (percentage >= 50) {
    motivationalMessage = 'Great progress! You are past the halfway mark! 🚀';
  } else if (percentage > 0) {
    motivationalMessage = 'Good start! Keep moving through your priorities. 💪';
  } else {
    motivationalMessage = 'Ready to conquer your day? Start with your top priority! ☀️';
  }

  return {
    completed,
    total,
    percentage,
    motivationalMessage,
  };
}

/**
 * Calculates habit summary stats.
 */
export function calculateHabitSummary(habits: Habit[] = []): HabitSummary {
  const activeCount = habits.length;
  if (activeCount === 0) {
    return {
      activeCount: 0,
      completedTodayCount: 0,
      completionRate: 0,
    };
  }

  // Habits with active streaks are considered active
  const completedTodayCount = habits.filter((h) => h.current_streak > 0).length;
  const completionRate = Math.round((completedTodayCount / activeCount) * 100);

  return {
    activeCount,
    completedTodayCount,
    completionRate,
  };
}

