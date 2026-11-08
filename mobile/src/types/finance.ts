export type AccountType = 'bank' | 'cash' | 'credit' | 'savings' | 'investment' | 'other';
export type TransactionType = 'income' | 'expense' | 'transfer';
export type SavingsGoalStatus = 'in_progress' | 'completed' | 'archived';

export interface FinancialAccount {
  id: string;
  user_id: string;
  name: string;
  account_type: AccountType;
  balance: string;
  currency: string;
  is_active: boolean;
  is_archived: boolean;
  is_default: boolean;
  color_hex: string;
  icon: string;
  created_at?: string;
  updated_at?: string;
}

export interface FinancialCategory {
  id: string;
  user_id?: string;
  name: string;
  category_type: TransactionType;
  color_hex: string;
  icon: string;
  is_system: boolean;
  created_at?: string;
}

export interface FinancialTransaction {
  id: string;
  user_id: string;
  account_id: string;
  account_name?: string | null;
  category_id?: string | null;
  category_name?: string | null;
  category_color?: string;
  category_icon?: string;
  amount: string;
  transaction_type: TransactionType;
  description: string;
  transaction_date: string;
  is_recurring: boolean;
  is_deleted: boolean;
  created_at?: string;
}

export interface Budget {
  id: string;
  user_id: string;
  category_id?: string | null;
  category_name?: string;
  category_color?: string;
  month: string; // YYYY-MM
  amount: string;
  currency: string;
  spent_amount?: string;
  remaining_amount?: string;
  utilization_percentage?: number;
  is_over_budget?: boolean;
  created_at?: string;
}

export interface SavingsGoalContribution {
  id: string;
  savings_goal_id: string;
  user_id: string;
  account_id?: string | null;
  account_name?: string | null;
  amount: string;
  contribution_date: string;
  note?: string | null;
  created_at?: string;
}

export interface SavingsGoal {
  id: string;
  user_id: string;
  title: string;
  target_amount: string;
  current_amount: string;
  progress_percentage: number;
  target_date?: string | null;
  status: SavingsGoalStatus;
  currency: string;
  color_hex: string;
  icon: string;
  notes?: string | null;
  contributions?: SavingsGoalContribution[];
  created_at?: string;
  updated_at?: string;
}

export interface CategoryBreakdownItem {
  category_id: string;
  name: string;
  color_hex: string;
  icon: string;
  total_amount: string;
  percentage: number;
}

export interface FinanceDashboardData {
  month: string;
  total_balance: string;
  monthly_income: string;
  monthly_expenses: string;
  monthly_net_savings: string;
  accounts: FinancialAccount[];
  category_breakdown: CategoryBreakdownItem[];
  recent_transactions: FinancialTransaction[];
  budgets: Budget[];
  savings_goals: SavingsGoal[];
}

export interface FinanceInsightsData {
  month: string;
  total_balance: string;
  monthly_income: string;
  monthly_expenses: string;
  monthly_net_savings: string;
  savings_rate: number;
  top_spending_category: {
    name: string;
    amount: string;
    percentage: number;
  } | null;
  budget_status: {
    total_budgets: number;
    over_budget_count: number;
  };
  savings_status: {
    active_goals_count: number;
    total_target: string;
    total_saved: string;
  };
  ai_observations: string;
  generated_at: string;
}

// Request payloads
export interface CreateAccountPayload {
  name: string;
  account_type: AccountType;
  balance?: string;
  currency?: string;
  color_hex?: string;
  icon?: string;
  is_default?: boolean;
}

export interface UpdateAccountPayload {
  name?: string;
  account_type?: AccountType;
  color_hex?: string;
  icon?: string;
  is_archived?: boolean;
  is_default?: boolean;
}

export interface CreateCategoryPayload {
  name: string;
  category_type: TransactionType;
  color_hex?: string;
  icon?: string;
}

export interface UpdateCategoryPayload {
  name?: string;
  category_type?: TransactionType;
  color_hex?: string;
  icon?: string;
}

export interface CreateTransactionPayload {
  account_id: string;
  amount: string;
  transaction_type: TransactionType;
  description: string;
  category_id?: string;
  transaction_date?: string;
  is_recurring?: boolean;
}

export interface UpdateTransactionPayload {
  account_id?: string;
  amount?: string;
  transaction_type?: TransactionType;
  description?: string;
  category_id?: string;
  transaction_date?: string;
  is_recurring?: boolean;
}

export interface CreateBudgetPayload {
  category_id?: string | null;
  month: string; // YYYY-MM
  amount: string;
  currency?: string;
}

export interface UpdateBudgetPayload {
  amount: string;
  currency?: string;
}

export interface CreateSavingsGoalPayload {
  title: string;
  target_amount: string;
  initial_deposit?: string;
  target_date?: string | null;
  currency?: string;
  color_hex?: string;
  icon?: string;
  notes?: string;
}

export interface UpdateSavingsGoalPayload {
  title?: string;
  target_amount?: string;
  target_date?: string | null;
  status?: SavingsGoalStatus;
  color_hex?: string;
  icon?: string;
  notes?: string;
}

export interface AddSavingsContributionPayload {
  amount: string;
  account_id?: string;
  note?: string;
}

export interface TransactionFilterParams {
  account_id?: string;
  category_id?: string;
  transaction_type?: TransactionType;
  date_from?: string;
  date_to?: string;
  page?: number;
  limit?: number;
}

