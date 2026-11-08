export type DatePeriod = 'day' | 'week' | 'month' | 'year' | 'custom';

export interface DateRangeParams {
  period?: DatePeriod;
  start_date?: string;
  end_date?: string;
  timezone?: string;
}

export interface DailyTrendItem {
  date: string;
  completed: number;
  created?: number;
  scheduled?: number;
}

export interface ProductivityAnalytics {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  overdue_tasks: number;
  completion_percentage: number;
  total_planner_blocks: number;
  completed_planner_blocks: number;
  planner_completion_percentage: number;
  daily_completion_trend: DailyTrendItem[];
  planner_distribution: { block_type: string; count: number }[];
}

export interface HabitPerformanceItem {
  id: string;
  title: string;
  color_hex: string;
  frequency: string;
  current_streak: number;
  best_streak: number;
  completed_in_period: number;
  scheduled_in_period: number;
  completion_percentage: number;
}

export interface HabitAnalytics {
  total_active_habits: number;
  total_scheduled_checkins: number;
  total_completed_checkins: number;
  consistency_percentage: number;
  average_current_streak: number;
  best_streak_record: number;
  habits_performance: HabitPerformanceItem[];
  daily_trend: DailyTrendItem[];
}

export interface GoalProgressItem {
  id: string;
  title: string;
  category: string | null;
  progress_percentage: number;
  status: string;
  target_date: string | null;
}

export interface GoalDeadlineItem {
  id: string;
  title: string;
  target_date: string;
  days_remaining: number;
  is_overdue: boolean;
}

export interface GoalAnalytics {
  total_goals: number;
  active_goals: number;
  completed_goals: number;
  completion_percentage: number;
  total_milestones: number;
  completed_milestones: number;
  milestone_completion_percentage: number;
  goals_progress: GoalProgressItem[];
  upcoming_deadlines: GoalDeadlineItem[];
}

export interface CategorySpendingItem {
  category_id: string;
  name: string;
  amount: string;
  color_hex: string;
  icon: string | null;
  percentage: number;
}

export interface SavingsGoalProgressItem {
  id: string;
  name: string;
  target_amount: string;
  current_amount: string;
  progress_percentage: number;
  target_date: string | null;
}

export interface FinancialAnalytics {
  period: string;
  total_income: string;
  total_expenses: string;
  net_savings: string;
  savings_rate: number;
  spending_by_category: CategorySpendingItem[];
  budget_adherence_percentage: number;
  savings_goals_progress: SavingsGoalProgressItem[];
}

export interface LifeScoreDimension {
  name: string;
  score: number;
  weight: number;
  weighted_score: number;
  description: string;
  status: 'excellent' | 'good' | 'fair' | 'needs_attention' | 'unpenalized_no_data';
}

export interface LifeScoreResponse {
  overall_score: number;
  score_tier: 'Exceptional' | 'Strong' | 'Balanced' | 'Building Momentum';
  period: string;
  dimensions: LifeScoreDimension[];
  calculation_explanation: string;
  disclaimer: string;
}

export interface CombinedDailyTrend {
  date: string;
  tasks_completed: number;
  habits_completed: number;
  total_activity: number;
}

export interface TrendsAnalyticsResponse {
  period: string;
  start_date: string;
  end_date: string;
  daily_trends: CombinedDailyTrend[];
}

export interface AnalyticsOverviewResponse {
  period: string;
  start_date: string;
  end_date: string;
  life_score: number;
  life_score_tier: string;
  productivity_summary: {
    completed_tasks: number;
    total_tasks: number;
    completion_percentage: number;
    completed_planner_blocks: number;
  };
  habits_summary: {
    active_habits: number;
    consistency_percentage: number;
    best_streak: number;
  };
  goals_summary: {
    active_goals: number;
    completed_goals: number;
    completion_percentage: number;
    upcoming_deadlines_count: number;
  };
  finance_summary: {
    total_income: string;
    total_expenses: string;
    net_savings: string;
    savings_rate: number;
  };
}

export interface AIInsightsResponse {
  generated_at: string;
  period: string;
  life_score: number;
  executive_summary: string;
  productivity_observation: string;
  habit_observation: string;
  financial_observation: string;
  actionable_recommendations: string[];
  is_fallback: boolean;
}

