import { apiClient } from '../api/client';
import {
  AssignedTask, TaskFollowUp,
  MoneyTransaction, MoneyRepayment, MoneyDashboardSummary,
  PersonalItem, ItemLendingRecord,
  PersonLedgerProfile,
} from '../types/people';

export const peopleService = {
  // Module 20: Assigned Tasks
  async getAssignedTasks(params?: { person?: string; status?: string; priority?: string }): Promise<AssignedTask[]> {
    const res = await apiClient.get<{ data: AssignedTask[] }>('/people/tasks', { params });
    return res.data.data;
  },
  async getAssignedTask(taskId: string): Promise<AssignedTask> {
    const res = await apiClient.get<{ data: AssignedTask }>(`/people/tasks/${taskId}`);
    return res.data.data;
  },
  async createAssignedTask(data: Partial<AssignedTask>): Promise<AssignedTask> {
    const res = await apiClient.post<{ data: AssignedTask }>('/people/tasks', data);
    return res.data.data;
  },
  async updateAssignedTask(taskId: string, data: Partial<AssignedTask>): Promise<AssignedTask> {
    const res = await apiClient.patch<{ data: AssignedTask }>(`/people/tasks/${taskId}`, data);
    return res.data.data;
  },
  async deleteAssignedTask(taskId: string): Promise<void> {
    await apiClient.delete(`/people/tasks/${taskId}`);
  },
  async addTaskFollowUp(taskId: string, data: { note: string; follow_up_date?: string; reminder_date?: string }): Promise<TaskFollowUp> {
    const res = await apiClient.post<{ data: TaskFollowUp }>(`/people/tasks/${taskId}/follow-ups`, data);
    return res.data.data;
  },

  // Module 21: Money Lending & Borrowing
  async getMoneyDashboard(): Promise<MoneyDashboardSummary> {
    const res = await apiClient.get<{ data: MoneyDashboardSummary }>('/people/money/dashboard');
    return res.data.data;
  },
  async getMoneyTransactions(params?: { type?: string; status?: string; person?: string }): Promise<MoneyTransaction[]> {
    const res = await apiClient.get<{ data: MoneyTransaction[] }>('/people/money', { params });
    return res.data.data;
  },
  async createMoneyTransaction(data: Partial<MoneyTransaction>): Promise<MoneyTransaction> {
    const res = await apiClient.post<{ data: MoneyTransaction }>('/people/money', data);
    return res.data.data;
  },
  async recordRepayment(txId: string, data: { amount: number; payment_date?: string; payment_method?: string; notes?: string }): Promise<MoneyTransaction> {
    const res = await apiClient.post<{ data: MoneyTransaction }>(`/people/money/${txId}/repayments`, data);
    return res.data.data;
  },
  async deleteMoneyTransaction(txId: string): Promise<void> {
    await apiClient.delete(`/people/money/${txId}`);
  },

  // Module 22: Personal Item Lending
  async getPersonalItems(params?: { status?: string; category?: string }): Promise<PersonalItem[]> {
    const res = await apiClient.get<{ data: PersonalItem[] }>('/people/items', { params });
    return res.data.data;
  },
  async getPersonalItem(itemId: string): Promise<PersonalItem> {
    const res = await apiClient.get<{ data: PersonalItem }>(`/people/items/${itemId}`);
    return res.data.data;
  },
  async createPersonalItem(data: Partial<PersonalItem>): Promise<PersonalItem> {
    const res = await apiClient.post<{ data: PersonalItem }>('/people/items', data);
    return res.data.data;
  },
  async lendItem(itemId: string, data: { person_name: string; person_contact?: string; expected_return_date?: string; notes?: string }): Promise<PersonalItem> {
    const res = await apiClient.post<{ data: PersonalItem }>(`/people/items/${itemId}/lend`, data);
    return res.data.data;
  },
  async returnItem(itemId: string, data?: { actual_return_date?: string; condition_on_return?: string; notes?: string }): Promise<PersonalItem> {
    const res = await apiClient.post<{ data: PersonalItem }>(`/people/items/${itemId}/return`, data || {});
    return res.data.data;
  },
  async deletePersonalItem(itemId: string): Promise<void> {
    await apiClient.delete(`/people/items/${itemId}`);
  },

  // Module 23: People Ledger Profile
  async getPersonLedger(personIdentifier: string): Promise<PersonLedgerProfile> {
    const res = await apiClient.get<{ data: PersonLedgerProfile }>(`/people/ledger/${encodeURIComponent(personIdentifier)}`);
    return res.data.data;
  },
};
