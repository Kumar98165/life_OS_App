import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { peopleService } from '../services/peopleService';
import { AssignedTask, MoneyTransaction, PersonalItem } from '../types/people';

// Module 20: Assigned Tasks
export function useAssignedTasks(params?: { person?: string; status?: string; priority?: string }) {
  const qc = useQueryClient();
  const query = useQuery({
    queryKey: ['assignedTasks', params],
    queryFn: () => peopleService.getAssignedTasks(params),
  });

  const createTask = useMutation({
    mutationFn: (data: Partial<AssignedTask>) => peopleService.createAssignedTask(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['assignedTasks'] });
      qc.invalidateQueries({ queryKey: ['personLedger'] });
    },
  });

  const updateTask = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<AssignedTask> }) => peopleService.updateAssignedTask(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['assignedTasks'] });
      qc.invalidateQueries({ queryKey: ['personLedger'] });
    },
  });

  const deleteTask = useMutation({
    mutationFn: (id: string) => peopleService.deleteAssignedTask(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['assignedTasks'] });
      qc.invalidateQueries({ queryKey: ['personLedger'] });
    },
  });

  const addFollowUp = useMutation({
    mutationFn: ({ id, data }: { id: string; data: { note: string; follow_up_date?: string; reminder_date?: string } }) =>
      peopleService.addTaskFollowUp(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['assignedTasks'] });
      qc.invalidateQueries({ queryKey: ['personLedger'] });
    },
  });

  return { ...query, createTask, updateTask, deleteTask, addFollowUp };
}

// Module 21: Money Lending & Borrowing
export function useMoneyTracker(params?: { type?: string; status?: string; person?: string }) {
  const qc = useQueryClient();
  const query = useQuery({
    queryKey: ['moneyTransactions', params],
    queryFn: () => peopleService.getMoneyTransactions(params),
  });

  const dashboard = useQuery({
    queryKey: ['moneyDashboard'],
    queryFn: () => peopleService.getMoneyDashboard(),
  });

  const createTransaction = useMutation({
    mutationFn: (data: Partial<MoneyTransaction>) => peopleService.createMoneyTransaction(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['moneyTransactions'] });
      qc.invalidateQueries({ queryKey: ['moneyDashboard'] });
      qc.invalidateQueries({ queryKey: ['personLedger'] });
    },
  });

  const recordRepayment = useMutation({
    mutationFn: ({ id, data }: { id: string; data: { amount: number; payment_date?: string; payment_method?: string; notes?: string } }) =>
      peopleService.recordRepayment(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['moneyTransactions'] });
      qc.invalidateQueries({ queryKey: ['moneyDashboard'] });
      qc.invalidateQueries({ queryKey: ['personLedger'] });
    },
  });

  const deleteTransaction = useMutation({
    mutationFn: (id: string) => peopleService.deleteMoneyTransaction(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['moneyTransactions'] });
      qc.invalidateQueries({ queryKey: ['moneyDashboard'] });
      qc.invalidateQueries({ queryKey: ['personLedger'] });
    },
  });

  return { ...query, dashboard, createTransaction, recordRepayment, deleteTransaction };
}

// Module 22: Personal Item Lending
export function usePersonalItems(params?: { status?: string; category?: string }) {
  const qc = useQueryClient();
  const query = useQuery({
    queryKey: ['personalItems', params],
    queryFn: () => peopleService.getPersonalItems(params),
  });

  const createItem = useMutation({
    mutationFn: (data: Partial<PersonalItem>) => peopleService.createPersonalItem(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['personalItems'] }),
  });

  const lendItem = useMutation({
    mutationFn: ({ id, data }: { id: string; data: { person_name: string; person_contact?: string; expected_return_date?: string; notes?: string } }) =>
      peopleService.lendItem(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['personalItems'] });
      qc.invalidateQueries({ queryKey: ['personLedger'] });
    },
  });

  const returnItem = useMutation({
    mutationFn: ({ id, data }: { id: string; data?: { actual_return_date?: string; condition_on_return?: string; notes?: string } }) =>
      peopleService.returnItem(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['personalItems'] });
      qc.invalidateQueries({ queryKey: ['personLedger'] });
    },
  });

  const deleteItem = useMutation({
    mutationFn: (id: string) => peopleService.deletePersonalItem(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['personalItems'] }),
  });

  return { ...query, createItem, lendItem, returnItem, deleteItem };
}

// Module 23: People Ledger Profile
export function usePersonLedger(personIdentifier: string) {
  return useQuery({
    queryKey: ['personLedger', personIdentifier],
    queryFn: () => peopleService.getPersonLedger(personIdentifier),
    enabled: !!personIdentifier,
  });
}
