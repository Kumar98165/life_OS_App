import { apiClient } from '../api/client';
import { ApiResponse } from '../types';
import {
  FinancialAccount,
  FinancialCategory,
  FinancialTransaction,
  Budget,
  SavingsGoal,
  SavingsGoalContribution,
  FinanceDashboardData,
  FinanceInsightsData,
  CreateAccountPayload,
  UpdateAccountPayload,
  CreateCategoryPayload,
  UpdateCategoryPayload,
  CreateTransactionPayload,
  UpdateTransactionPayload,
  CreateBudgetPayload,
  UpdateBudgetPayload,
  CreateSavingsGoalPayload,
  UpdateSavingsGoalPayload,
  AddSavingsContributionPayload,
  TransactionFilterParams,
  TransactionType,
  SavingsGoalStatus,
} from '../types/finance';

export const financeService = {
  // -------------------------------------------------------------
  // Dashboard & Local AI Insights
  // -------------------------------------------------------------
  async getDashboard(month?: string): Promise<FinanceDashboardData> {
    const response = await apiClient.get<ApiResponse<FinanceDashboardData>>('/finance/dashboard', {
      params: month ? { month } : undefined,
    });
    return response.data.data;
  },

  async getInsights(month?: string): Promise<FinanceInsightsData> {
    const response = await apiClient.get<ApiResponse<FinanceInsightsData>>('/finance/insights', {
      params: month ? { month } : undefined,
    });
    return response.data.data;
  },

  // -------------------------------------------------------------
  // Accounts
  // -------------------------------------------------------------
  async getAccounts(include_archived: boolean = false): Promise<FinancialAccount[]> {
    const response = await apiClient.get<ApiResponse<{ accounts: FinancialAccount[] }>>(
      '/finance/accounts',
      {
        params: { include_archived },
      }
    );
    return response.data.data.accounts;
  },

  async createAccount(payload: CreateAccountPayload): Promise<FinancialAccount> {
    const response = await apiClient.post<ApiResponse<{ account: FinancialAccount }>>(
      '/finance/accounts',
      payload
    );
    return response.data.data.account;
  },

  async updateAccount(id: string, payload: UpdateAccountPayload): Promise<FinancialAccount> {
    const response = await apiClient.put<ApiResponse<{ account: FinancialAccount }>>(
      `/finance/accounts/${id}`,
      payload
    );
    return response.data.data.account;
  },

  async deleteAccount(id: string): Promise<void> {
    await apiClient.delete(`/finance/accounts/${id}`);
  },

  // -------------------------------------------------------------
  // Categories
  // -------------------------------------------------------------
  async getCategories(category_type?: TransactionType): Promise<FinancialCategory[]> {
    const response = await apiClient.get<ApiResponse<{ categories: FinancialCategory[] }>>(
      '/finance/categories',
      {
        params: category_type ? { category_type } : undefined,
      }
    );
    return response.data.data.categories;
  },

  async createCategory(payload: CreateCategoryPayload): Promise<FinancialCategory> {
    const response = await apiClient.post<ApiResponse<{ category: FinancialCategory }>>(
      '/finance/categories',
      payload
    );
    return response.data.data.category;
  },

  async updateCategory(id: string, payload: UpdateCategoryPayload): Promise<FinancialCategory> {
    const response = await apiClient.put<ApiResponse<{ category: FinancialCategory }>>(
      `/finance/categories/${id}`,
      payload
    );
    return response.data.data.category;
  },

  async deleteCategory(id: string): Promise<void> {
    await apiClient.delete(`/finance/categories/${id}`);
  },

  // -------------------------------------------------------------
  // Transactions
  // -------------------------------------------------------------
  async getTransactions(params?: TransactionFilterParams): Promise<{
    transactions: FinancialTransaction[];
    total: number;
    page: number;
    limit: number;
  }> {
    const response = await apiClient.get<
      ApiResponse<{
        transactions: FinancialTransaction[];
        total: number;
        page: number;
        limit: number;
      }>
    >('/finance/transactions', { params });
    return response.data.data;
  },

  async getTransaction(id: string): Promise<FinancialTransaction> {
    const response = await apiClient.get<ApiResponse<{ transaction: FinancialTransaction }>>(
      `/finance/transactions/${id}`
    );
    return response.data.data.transaction;
  },

  async createTransaction(payload: CreateTransactionPayload): Promise<FinancialTransaction> {
    const response = await apiClient.post<ApiResponse<{ transaction: FinancialTransaction }>>(
      '/finance/transactions',
      payload
    );
    return response.data.data.transaction;
  },

  async updateTransaction(
    id: string,
    payload: UpdateTransactionPayload
  ): Promise<FinancialTransaction> {
    const response = await apiClient.put<ApiResponse<{ transaction: FinancialTransaction }>>(
      `/finance/transactions/${id}`,
      payload
    );
    return response.data.data.transaction;
  },

  async deleteTransaction(id: string): Promise<void> {
    await apiClient.delete(`/finance/transactions/${id}`);
  },

  // -------------------------------------------------------------
  // Budgets
  // -------------------------------------------------------------
  async getBudgets(month?: string): Promise<Budget[]> {
    const response = await apiClient.get<ApiResponse<{ budgets: Budget[] }>>('/finance/budgets', {
      params: month ? { month } : undefined,
    });
    return response.data.data.budgets;
  },

  async createBudget(payload: CreateBudgetPayload): Promise<Budget> {
    const response = await apiClient.post<ApiResponse<{ budget: Budget }>>(
      '/finance/budgets',
      payload
    );
    return response.data.data.budget;
  },

  async updateBudget(id: string, payload: UpdateBudgetPayload): Promise<Budget> {
    const response = await apiClient.put<ApiResponse<{ budget: Budget }>>(
      `/finance/budgets/${id}`,
      payload
    );
    return response.data.data.budget;
  },

  async deleteBudget(id: string): Promise<void> {
    await apiClient.delete(`/finance/budgets/${id}`);
  },

  // -------------------------------------------------------------
  // Savings Goals
  // -------------------------------------------------------------
  async getSavingsGoals(status?: SavingsGoalStatus): Promise<SavingsGoal[]> {
    const response = await apiClient.get<ApiResponse<{ savings_goals: SavingsGoal[] }>>(
      '/finance/savings-goals',
      {
        params: status ? { status } : undefined,
      }
    );
    return response.data.data.savings_goals;
  },

  async getSavingsGoal(id: string): Promise<SavingsGoal> {
    const response = await apiClient.get<ApiResponse<{ savings_goal: SavingsGoal }>>(
      `/finance/savings-goals/${id}`
    );
    return response.data.data.savings_goal;
  },

  async createSavingsGoal(payload: CreateSavingsGoalPayload): Promise<SavingsGoal> {
    const response = await apiClient.post<ApiResponse<{ savings_goal: SavingsGoal }>>(
      '/finance/savings-goals',
      payload
    );
    return response.data.data.savings_goal;
  },

  async updateSavingsGoal(id: string, payload: UpdateSavingsGoalPayload): Promise<SavingsGoal> {
    const response = await apiClient.put<ApiResponse<{ savings_goal: SavingsGoal }>>(
      `/finance/savings-goals/${id}`,
      payload
    );
    return response.data.data.savings_goal;
  },

  async deleteSavingsGoal(id: string): Promise<void> {
    await apiClient.delete(`/finance/savings-goals/${id}`);
  },

  async addSavingsContribution(
    goalId: string,
    payload: AddSavingsContributionPayload
  ): Promise<{
    savings_goal: SavingsGoal;
    contribution: SavingsGoalContribution;
  }> {
    const response = await apiClient.post<
      ApiResponse<{
        savings_goal: SavingsGoal;
        contribution: SavingsGoalContribution;
      }>
    >(`/finance/savings-goals/${goalId}/contributions`, payload);
    return response.data.data;
  },
};

