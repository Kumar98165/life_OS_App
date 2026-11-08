import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { financeService } from '../services/financeService';
import {
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

export const FINANCE_QUERY_KEYS = {
  all: ['finance'] as const,
  dashboard: (month?: string) => ['finance', 'dashboard', month] as const,
  insights: (month?: string) => ['finance', 'insights', month] as const,
  accounts: (include_archived?: boolean) => ['finance', 'accounts', include_archived] as const,
  categories: (type?: TransactionType) => ['finance', 'categories', type] as const,
  transactions: (params?: TransactionFilterParams) => ['finance', 'transactions', params] as const,
  transaction: (id: string) => ['finance', 'transaction', id] as const,
  budgets: (month?: string) => ['finance', 'budgets', month] as const,
  savingsGoals: (status?: SavingsGoalStatus) => ['finance', 'savings_goals', status] as const,
  savingsGoal: (id: string) => ['finance', 'savings_goal', id] as const,
};

// -------------------------------------------------------------
// Queries
// -------------------------------------------------------------

export function useFinanceDashboard(month?: string) {
  return useQuery({
    queryKey: FINANCE_QUERY_KEYS.dashboard(month),
    queryFn: () => financeService.getDashboard(month),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

export function useFinanceInsights(month?: string) {
  return useQuery({
    queryKey: FINANCE_QUERY_KEYS.insights(month),
    queryFn: () => financeService.getInsights(month),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function useFinanceAccounts(include_archived: boolean = false) {
  return useQuery({
    queryKey: FINANCE_QUERY_KEYS.accounts(include_archived),
    queryFn: () => financeService.getAccounts(include_archived),
    staleTime: 1000 * 60 * 3,
  });
}

export function useFinanceCategories(type?: TransactionType) {
  return useQuery({
    queryKey: FINANCE_QUERY_KEYS.categories(type),
    queryFn: () => financeService.getCategories(type),
    staleTime: 1000 * 60 * 10,
  });
}

export function useFinanceTransactions(params?: TransactionFilterParams) {
  return useQuery({
    queryKey: FINANCE_QUERY_KEYS.transactions(params),
    queryFn: () => financeService.getTransactions(params),
    staleTime: 1000 * 60 * 1,
  });
}

export function useFinanceTransaction(id: string | null) {
  return useQuery({
    queryKey: FINANCE_QUERY_KEYS.transaction(id || ''),
    queryFn: () => financeService.getTransaction(id!),
    enabled: !!id,
  });
}

export function useFinanceBudgets(month?: string) {
  return useQuery({
    queryKey: FINANCE_QUERY_KEYS.budgets(month),
    queryFn: () => financeService.getBudgets(month),
    staleTime: 1000 * 60 * 2,
  });
}

export function useSavingsGoals(status?: SavingsGoalStatus) {
  return useQuery({
    queryKey: FINANCE_QUERY_KEYS.savingsGoals(status),
    queryFn: () => financeService.getSavingsGoals(status),
    staleTime: 1000 * 60 * 2,
  });
}

export function useSavingsGoal(id: string | null) {
  return useQuery({
    queryKey: FINANCE_QUERY_KEYS.savingsGoal(id || ''),
    queryFn: () => financeService.getSavingsGoal(id!),
    enabled: !!id,
  });
}

// -------------------------------------------------------------
// Mutations
// -------------------------------------------------------------

export function useCreateAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateAccountPayload) => financeService.createAccount(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useUpdateAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateAccountPayload }) =>
      financeService.updateAccount(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useDeleteAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => financeService.deleteAccount(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useCreateCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateCategoryPayload) => financeService.createCategory(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useUpdateCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateCategoryPayload }) =>
      financeService.updateCategory(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useDeleteCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => financeService.deleteCategory(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useCreateTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateTransactionPayload) => financeService.createTransaction(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useUpdateTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateTransactionPayload }) =>
      financeService.updateTransaction(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useDeleteTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => financeService.deleteTransaction(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useCreateBudget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateBudgetPayload) => financeService.createBudget(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useUpdateBudget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateBudgetPayload }) =>
      financeService.updateBudget(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useDeleteBudget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => financeService.deleteBudget(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useCreateSavingsGoal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateSavingsGoalPayload) => financeService.createSavingsGoal(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useUpdateSavingsGoal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateSavingsGoalPayload }) =>
      financeService.updateSavingsGoal(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useDeleteSavingsGoal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => financeService.deleteSavingsGoal(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

export function useAddSavingsContribution() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      goalId,
      payload,
    }: {
      goalId: string;
      payload: AddSavingsContributionPayload;
    }) => financeService.addSavingsContribution(goalId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FINANCE_QUERY_KEYS.all });
    },
  });
}

