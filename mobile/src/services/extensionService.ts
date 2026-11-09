import { apiClient } from '../api/client';
import {
  NoteItem, NoteFolder,
  ContactItem,
  SubscriptionItem, SubscriptionSummary,
  LearningGoalItem, StudySessionItem,
  TripItem, TripItineraryItem, TripPackingItem,
  WorkoutItem, FitnessStats,
  PersonalAssetItem, AssetMaintenanceItem,
  BillItem, BillPaymentItem,
} from '../types/extensions';

export const extensionService = {
  // 12. Notes & Folders
  async getFolders(): Promise<NoteFolder[]> {
    const res = await apiClient.get<{ data: NoteFolder[] }>('/notes/folders');
    return res.data.data;
  },
  async createFolder(data: { name: string; color_hex?: string; icon?: string }): Promise<NoteFolder> {
    const res = await apiClient.post<{ data: NoteFolder }>('/notes/folders', data);
    return res.data.data;
  },
  async deleteFolder(folderId: string): Promise<void> {
    await apiClient.delete(`/notes/folders/${folderId}`);
  },
  async getNotes(params?: { search?: string; folder_id?: string; is_pinned?: boolean }): Promise<NoteItem[]> {
    const res = await apiClient.get<{ data: NoteItem[] }>('/notes', { params });
    return res.data.data;
  },
  async getNote(noteId: string): Promise<NoteItem> {
    const res = await apiClient.get<{ data: NoteItem }>(`/notes/${noteId}`);
    return res.data.data;
  },
  async createNote(data: Partial<NoteItem> & { tag_names?: string[] }): Promise<NoteItem> {
    const res = await apiClient.post<{ data: NoteItem }>('/notes', data);
    return res.data.data;
  },
  async updateNote(noteId: string, data: Partial<NoteItem> & { tag_names?: string[] }): Promise<NoteItem> {
    const res = await apiClient.patch<{ data: NoteItem }>(`/notes/${noteId}`, data);
    return res.data.data;
  },
  async deleteNote(noteId: string): Promise<void> {
    await apiClient.delete(`/notes/${noteId}`);
  },

  // 13. Contacts
  async getContacts(params?: { search?: string; relationship_type?: string }): Promise<ContactItem[]> {
    const res = await apiClient.get<{ data: ContactItem[] }>('/contacts', { params });
    return res.data.data;
  },
  async getContact(contactId: string): Promise<ContactItem> {
    const res = await apiClient.get<{ data: ContactItem }>(`/contacts/${contactId}`);
    return res.data.data;
  },
  async createContact(data: Partial<ContactItem>): Promise<ContactItem> {
    const res = await apiClient.post<{ data: ContactItem }>('/contacts', data);
    return res.data.data;
  },
  async updateContact(contactId: string, data: Partial<ContactItem>): Promise<ContactItem> {
    const res = await apiClient.patch<{ data: ContactItem }>(`/contacts/${contactId}`, data);
    return res.data.data;
  },
  async deleteContact(contactId: string): Promise<void> {
    await apiClient.delete(`/contacts/${contactId}`);
  },
  async addContactInteraction(contactId: string, data: any): Promise<any> {
    const res = await apiClient.post(`/contacts/${contactId}/interactions`, data);
    return res.data.data;
  },

  // 14. Subscriptions
  async getSubscriptions(params?: { status?: string }): Promise<SubscriptionItem[]> {
    const res = await apiClient.get<{ data: SubscriptionItem[] }>('/subscriptions', { params });
    return res.data.data;
  },
  async getSubscriptionSummary(): Promise<SubscriptionSummary> {
    const res = await apiClient.get<{ data: SubscriptionSummary }>('/subscriptions/summary');
    return res.data.data;
  },
  async createSubscription(data: Partial<SubscriptionItem>): Promise<SubscriptionItem> {
    const res = await apiClient.post<{ data: SubscriptionItem }>('/subscriptions', data);
    return res.data.data;
  },
  async updateSubscription(subId: string, data: Partial<SubscriptionItem>): Promise<SubscriptionItem> {
    const res = await apiClient.patch<{ data: SubscriptionItem }>(`/subscriptions/${subId}`, data);
    return res.data.data;
  },
  async deleteSubscription(subId: string): Promise<void> {
    await apiClient.delete(`/subscriptions/${subId}`);
  },

  // 15. Learning & Skill Tracker
  async getLearningGoals(params?: { status?: string }): Promise<LearningGoalItem[]> {
    const res = await apiClient.get<{ data: LearningGoalItem[] }>('/learning/goals', { params });
    return res.data.data;
  },
  async getLearningGoal(goalId: string): Promise<LearningGoalItem> {
    const res = await apiClient.get<{ data: LearningGoalItem }>(`/learning/goals/${goalId}`);
    return res.data.data;
  },
  async createLearningGoal(data: Partial<LearningGoalItem>): Promise<LearningGoalItem> {
    const res = await apiClient.post<{ data: LearningGoalItem }>('/learning/goals', data);
    return res.data.data;
  },
  async updateLearningGoal(goalId: string, data: Partial<LearningGoalItem>): Promise<LearningGoalItem> {
    const res = await apiClient.patch<{ data: LearningGoalItem }>(`/learning/goals/${goalId}`, data);
    return res.data.data;
  },
  async deleteLearningGoal(goalId: string): Promise<void> {
    await apiClient.delete(`/learning/goals/${goalId}`);
  },
  async addStudySession(goalId: string, data: { duration_minutes: number; topics_covered: string; notes?: string }): Promise<StudySessionItem> {
    const res = await apiClient.post<{ data: StudySessionItem }>(`/learning/goals/${goalId}/sessions`, data);
    return res.data.data;
  },

  // 16. Travel Planner
  async getTrips(params?: { status?: string }): Promise<TripItem[]> {
    const res = await apiClient.get<{ data: TripItem[] }>('/travel/trips', { params });
    return res.data.data;
  },
  async getTrip(tripId: string): Promise<TripItem> {
    const res = await apiClient.get<{ data: TripItem }>(`/travel/trips/${tripId}`);
    return res.data.data;
  },
  async createTrip(data: Partial<TripItem>): Promise<TripItem> {
    const res = await apiClient.post<{ data: TripItem }>('/travel/trips', data);
    return res.data.data;
  },
  async updateTrip(tripId: string, data: Partial<TripItem>): Promise<TripItem> {
    const res = await apiClient.patch<{ data: TripItem }>(`/travel/trips/${tripId}`, data);
    return res.data.data;
  },
  async deleteTrip(tripId: string): Promise<void> {
    await apiClient.delete(`/travel/trips/${tripId}`);
  },
  async addItineraryItem(tripId: string, data: Partial<TripItineraryItem>): Promise<TripItineraryItem> {
    const res = await apiClient.post<{ data: TripItineraryItem }>(`/travel/trips/${tripId}/itinerary`, data);
    return res.data.data;
  },
  async addPackingItem(tripId: string, data: Partial<TripPackingItem>): Promise<TripPackingItem> {
    const res = await apiClient.post<{ data: TripPackingItem }>(`/travel/trips/${tripId}/packing`, data);
    return res.data.data;
  },
  async togglePackingItem(tripId: string, itemId: string): Promise<TripPackingItem> {
    const res = await apiClient.post<{ data: TripPackingItem }>(`/travel/trips/${tripId}/packing/${itemId}/toggle`);
    return res.data.data;
  },

  // 17. Fitness
  async getWorkouts(): Promise<WorkoutItem[]> {
    const res = await apiClient.get<{ data: WorkoutItem[] }>('/fitness/workouts');
    return res.data.data;
  },
  async getFitnessStats(): Promise<FitnessStats> {
    const res = await apiClient.get<{ data: FitnessStats }>('/fitness/stats');
    return res.data.data;
  },
  async createWorkout(data: Partial<WorkoutItem>): Promise<WorkoutItem> {
    const res = await apiClient.post<{ data: WorkoutItem }>('/fitness/workouts', data);
    return res.data.data;
  },
  async deleteWorkout(workoutId: string): Promise<void> {
    await apiClient.delete(`/fitness/workouts/${workoutId}`);
  },

  // 18. Personal Assets
  async getAssets(params?: { category?: string }): Promise<PersonalAssetItem[]> {
    const res = await apiClient.get<{ data: PersonalAssetItem[] }>('/assets', { params });
    return res.data.data;
  },
  async getAsset(assetId: string): Promise<PersonalAssetItem> {
    const res = await apiClient.get<{ data: PersonalAssetItem }>(`/assets/${assetId}`);
    return res.data.data;
  },
  async createAsset(data: Partial<PersonalAssetItem>): Promise<PersonalAssetItem> {
    const res = await apiClient.post<{ data: PersonalAssetItem }>('/assets', data);
    return res.data.data;
  },
  async updateAsset(assetId: string, data: Partial<PersonalAssetItem>): Promise<PersonalAssetItem> {
    const res = await apiClient.patch<{ data: PersonalAssetItem }>(`/assets/${assetId}`, data);
    return res.data.data;
  },
  async deleteAsset(assetId: string): Promise<void> {
    await apiClient.delete(`/assets/${assetId}`);
  },
  async addAssetMaintenance(assetId: string, data: Partial<AssetMaintenanceItem>): Promise<AssetMaintenanceItem> {
    const res = await apiClient.post<{ data: AssetMaintenanceItem }>(`/assets/${assetId}/maintenance`, data);
    return res.data.data;
  },

  // 19. Bills & Payments
  async getBills(params?: { status?: string }): Promise<BillItem[]> {
    const res = await apiClient.get<{ data: BillItem[] }>('/bills', { params });
    return res.data.data;
  },
  async getBill(billId: string): Promise<BillItem> {
    const res = await apiClient.get<{ data: BillItem }>(`/bills/${billId}`);
    return res.data.data;
  },
  async createBill(data: Partial<BillItem>): Promise<BillItem> {
    const res = await apiClient.post<{ data: BillItem }>('/bills', data);
    return res.data.data;
  },
  async updateBill(billId: string, data: Partial<BillItem>): Promise<BillItem> {
    const res = await apiClient.patch<{ data: BillItem }>(`/bills/${billId}`, data);
    return res.data.data;
  },
  async deleteBill(billId: string): Promise<void> {
    await apiClient.delete(`/bills/${billId}`);
  },
  async recordBillPayment(billId: string, data: Partial<BillPaymentItem>): Promise<BillPaymentItem> {
    const res = await apiClient.post<{ data: BillPaymentItem }>(`/bills/${billId}/payments`, data);
    return res.data.data;
  },
};
