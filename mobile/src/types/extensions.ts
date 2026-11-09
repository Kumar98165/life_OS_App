// LifeOS Productivity Extensions Types

// 12. Notes & Folders
export interface NoteFolder {
  id: string;
  user_id: string;
  name: string;
  color_hex: string;
  icon: string;
  created_at: string;
}

export interface NoteAttachment {
  id: string;
  note_id: string;
  file_name: string;
  file_type: string;
  file_size_bytes: number;
  file_url: string;
  created_at: string;
}

export interface NoteTag {
  id: string;
  name: string;
  color_hex: string;
}

export interface NoteItem {
  id: string;
  user_id: string;
  title: string;
  content: string;
  is_pinned: boolean;
  is_archived: boolean;
  folder_id?: string | null;
  folder?: NoteFolder | null;
  attachments?: NoteAttachment[];
  tags?: NoteTag[];
  created_at: string;
  updated_at: string;
}

// 13. Contacts
export interface ContactInteraction {
  id: string;
  contact_id: string;
  interaction_type: 'call' | 'meeting' | 'message' | 'email' | 'social';
  summary: string;
  details?: string | null;
  interaction_date: string;
  follow_up_date?: string | null;
  created_at: string;
}

export interface ContactItem {
  id: string;
  user_id: string;
  name: string;
  relationship_type: 'family' | 'friend' | 'colleague' | 'mentor' | 'other';
  email?: string | null;
  phone?: string | null;
  address?: string | null;
  company?: string | null;
  job_title?: string | null;
  birthday?: string | null;
  anniversary?: string | null;
  notes?: string | null;
  is_favorite: boolean;
  interactions?: ContactInteraction[];
  created_at: string;
  updated_at: string;
}

// 14. Subscriptions
export interface SubscriptionItem {
  id: string;
  user_id: string;
  name: string;
  category: 'entertainment' | 'productivity' | 'utility' | 'education' | 'other';
  amount: number;
  currency: string;
  billing_cycle: 'monthly' | 'yearly' | 'quarterly' | 'weekly';
  status: 'active' | 'cancelled' | 'paused' | 'expired';
  renewal_date: string;
  payment_method?: string | null;
  notes?: string | null;
  auto_renew: boolean;
  created_at: string;
  updated_at: string;
}

export interface SubscriptionSummary {
  active_count: number;
  estimated_monthly_expense: number;
  estimated_yearly_expense: number;
}

// 15. Learning & Skill Tracker
export interface StudySessionItem {
  id: string;
  goal_id: string;
  duration_minutes: number;
  topics_covered: string;
  notes?: string | null;
  session_date: string;
  created_at: string;
}

export interface LearningGoalItem {
  id: string;
  user_id: string;
  title: string;
  category: string;
  description?: string | null;
  target_hours: number;
  current_hours: number;
  status: 'in_progress' | 'completed' | 'paused';
  progress_percent: number;
  start_date?: string | null;
  target_completion_date?: string | null;
  sessions?: StudySessionItem[];
  created_at: string;
}

// 16. Travel Planner
export interface TripItineraryItem {
  id: string;
  trip_id: string;
  activity_date: string;
  activity_time?: string | null;
  title: string;
  location?: string | null;
  booking_reference?: string | null;
  estimated_cost: number;
  is_completed: boolean;
  created_at: string;
}

export interface TripPackingItem {
  id: string;
  trip_id: string;
  item_name: string;
  category: string;
  is_packed: boolean;
  quantity: number;
  created_at: string;
}

export interface TripItem {
  id: string;
  user_id: string;
  destination: string;
  title: string;
  start_date: string;
  end_date: string;
  budget: number;
  currency: string;
  status: 'planned' | 'ongoing' | 'completed' | 'cancelled';
  notes?: string | null;
  itinerary?: TripItineraryItem[];
  packing_items?: TripPackingItem[];
  created_at: string;
}

// 17. Fitness
export interface WorkoutItem {
  id: string;
  user_id: string;
  workout_type: string;
  title: string;
  duration_minutes: number;
  calories_burned?: number | null;
  distance_km?: number | null;
  intensity: 'low' | 'medium' | 'high';
  notes?: string | null;
  workout_date: string;
  created_at: string;
}

export interface FitnessStats {
  total_workouts: number;
  total_minutes: number;
  total_calories: number;
  total_distance_km: number;
}

// 18. Assets
export interface AssetMaintenanceItem {
  id: string;
  asset_id: string;
  service_date: string;
  description: string;
  cost: number;
  service_provider?: string | null;
  notes?: string | null;
  created_at: string;
}

export interface PersonalAssetItem {
  id: string;
  user_id: string;
  name: string;
  category: string;
  purchase_date?: string | null;
  purchase_price?: number | null;
  currency: string;
  serial_number?: string | null;
  warranty_expiry?: string | null;
  location?: string | null;
  status: 'active' | 'sold' | 'disposed' | 'in_repair';
  notes?: string | null;
  maintenance_records?: AssetMaintenanceItem[];
  created_at: string;
  updated_at: string;
}

// 19. Bills & Payments
export interface BillPaymentItem {
  id: string;
  bill_id: string;
  amount_paid: number;
  payment_date: string;
  payment_method: string;
  reference_number?: string | null;
  notes?: string | null;
  created_at: string;
}

export interface BillItem {
  id: string;
  user_id: string;
  title: string;
  category: string;
  amount: number;
  currency: string;
  due_date: string;
  is_recurring: boolean;
  frequency: string;
  status: 'unpaid' | 'paid' | 'overdue';
  auto_pay: boolean;
  notes?: string | null;
  payments?: BillPaymentItem[];
  created_at: string;
  updated_at: string;
}
