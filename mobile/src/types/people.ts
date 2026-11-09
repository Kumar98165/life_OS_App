// LifeOS People & Personal Tracking Types

export interface TaskFollowUp {
  id: string;
  task_id: string;
  note: string;
  follow_up_date: string;
  reminder_date?: string | null;
  created_at: string;
}

export interface AssignedTask {
  id: string;
  user_id: string;
  contact_id?: string | null;
  person_name: string;
  person_contact?: string | null;
  title: string;
  description?: string | null;
  assignment_date: string;
  expected_completion_date?: string | null;
  actual_completion_date?: string | null;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'assigned' | 'accepted' | 'in_progress' | 'on_hold' | 'completed' | 'cancelled';
  attachment_url?: string | null;
  follow_ups?: TaskFollowUp[];
  created_at: string;
  updated_at: string;
}

export interface MoneyRepayment {
  id: string;
  transaction_id: string;
  amount: number;
  payment_date: string;
  payment_method: string;
  notes?: string | null;
  proof_url?: string | null;
  created_at: string;
}

export interface MoneyTransaction {
  id: string;
  user_id: string;
  contact_id?: string | null;
  person_name: string;
  person_contact?: string | null;
  transaction_type: 'lent' | 'borrowed';
  amount: number;
  amount_repaid: number;
  remaining_amount: number;
  currency: string;
  transaction_date: string;
  expected_return_date?: string | null;
  payment_method: string;
  description?: string | null;
  proof_url?: string | null;
  status: 'pending' | 'partially_paid' | 'fully_paid' | 'overdue';
  repayments?: MoneyRepayment[];
  created_at: string;
  updated_at: string;
}

export interface MoneyDashboardSummary {
  total_money_lent: number;
  total_money_borrowed: number;
  total_money_received_back: number;
  total_money_repaid: number;
  outstanding_receivables: number;
  outstanding_payables: number;
  overdue_amount: number;
}

export interface ItemLendingRecord {
  id: string;
  item_id: string;
  contact_id?: string | null;
  person_name: string;
  person_contact?: string | null;
  given_date: string;
  expected_return_date?: string | null;
  actual_return_date?: string | null;
  condition_on_return?: string | null;
  notes?: string | null;
  created_at: string;
}

export interface PersonalItem {
  id: string;
  user_id: string;
  name: string;
  category: string;
  description?: string | null;
  initial_condition: string;
  photo_url?: string | null;
  status: 'available' | 'lent' | 'overdue' | 'lost';
  currently_with?: string | null;
  expected_return_date?: string | null;
  active_lending_record?: ItemLendingRecord | null;
  lending_records?: ItemLendingRecord[];
  created_at: string;
  updated_at: string;
}

export interface PersonActivity {
  id: string;
  user_id: string;
  contact_id?: string | null;
  person_name: string;
  activity_type: string;
  summary: string;
  details?: string | null;
  amount?: number | null;
  reference_id?: string | null;
  activity_date: string;
  created_at: string;
}

export interface PersonLedgerProfile {
  contact: {
    id?: string;
    name: string;
    relationship_type: string;
    phone?: string | null;
    email?: string | null;
    notes?: string | null;
  };
  summary: {
    total_tasks_assigned: number;
    pending_tasks_count: number;
    completed_tasks_count: number;
    money_lent: number;
    money_lent_repaid: number;
    money_borrowed: number;
    money_borrowed_repaid: number;
    net_outstanding: number;
    items_given_count: number;
    items_pending_return_count: number;
  };
  pending_tasks: AssignedTask[];
  unreturned_items: ItemLendingRecord[];
  activity_timeline: PersonActivity[];
}
