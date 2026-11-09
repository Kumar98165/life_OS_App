import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { extensionService } from '../services/extensionService';
import {
  NoteItem,
  ContactItem,
  SubscriptionItem,
  LearningGoalItem,
  TripItem,
  WorkoutItem,
  PersonalAssetItem,
  BillItem,
} from '../types/extensions';

// 12. Notes & Folders
export function useNotes(params?: { search?: string; folder_id?: string; is_pinned?: boolean }) {
  const qc = useQueryClient();
  const query = useQuery({
    queryKey: ['notes', params],
    queryFn: () => extensionService.getNotes(params),
  });

  const createNote = useMutation({
    mutationFn: (data: Partial<NoteItem> & { tag_names?: string[] }) => extensionService.createNote(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notes'] }),
  });

  const deleteNote = useMutation({
    mutationFn: (id: string) => extensionService.deleteNote(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notes'] }),
  });

  return { ...query, createNote, deleteNote };
}

export function useNoteFolders() {
  const qc = useQueryClient();
  const query = useQuery({
    queryKey: ['noteFolders'],
    queryFn: () => extensionService.getFolders(),
  });

  const createFolder = useMutation({
    mutationFn: (data: { name: string; color_hex?: string; icon?: string }) => extensionService.createFolder(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['noteFolders'] }),
  });

  return { ...query, createFolder };
}

// 13. Contacts
export function useContacts(params?: { search?: string; relationship_type?: string }) {
  const qc = useQueryClient();
  const query = useQuery({
    queryKey: ['contacts', params],
    queryFn: () => extensionService.getContacts(params),
  });

  const createContact = useMutation({
    mutationFn: (data: Partial<ContactItem>) => extensionService.createContact(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['contacts'] }),
  });

  const deleteContact = useMutation({
    mutationFn: (id: string) => extensionService.deleteContact(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['contacts'] }),
  });

  return { ...query, createContact, deleteContact };
}

// 14. Subscriptions
export function useSubscriptions(params?: { status?: string }) {
  const qc = useQueryClient();
  const query = useQuery({
    queryKey: ['subscriptions', params],
    queryFn: () => extensionService.getSubscriptions(params),
  });

  const summary = useQuery({
    queryKey: ['subscriptionsSummary'],
    queryFn: () => extensionService.getSubscriptionSummary(),
  });

  const createSubscription = useMutation({
    mutationFn: (data: Partial<SubscriptionItem>) => extensionService.createSubscription(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['subscriptions'] });
      qc.invalidateQueries({ queryKey: ['subscriptionsSummary'] });
    },
  });

  const deleteSubscription = useMutation({
    mutationFn: (id: string) => extensionService.deleteSubscription(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['subscriptions'] });
      qc.invalidateQueries({ queryKey: ['subscriptionsSummary'] });
    },
  });

  return { ...query, summary, createSubscription, deleteSubscription };
}

// 15. Learning & Skill Tracker
export function useLearningGoals(params?: { status?: string }) {
  const qc = useQueryClient();
  const query = useQuery({
    queryKey: ['learningGoals', params],
    queryFn: () => extensionService.getLearningGoals(params),
  });

  const createGoal = useMutation({
    mutationFn: (data: Partial<LearningGoalItem>) => extensionService.createLearningGoal(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['learningGoals'] }),
  });

  const addSession = useMutation({
    mutationFn: ({ goalId, data }: { goalId: string; data: { duration_minutes: number; topics_covered: string; notes?: string } }) =>
      extensionService.addStudySession(goalId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['learningGoals'] }),
  });

  return { ...query, createGoal, addSession };
}

// 16. Travel Planner
export function useTrips(params?: { status?: string }) {
  const qc = useQueryClient();
  const query = useQuery({
    queryKey: ['trips', params],
    queryFn: () => extensionService.getTrips(params),
  });

  const createTrip = useMutation({
    mutationFn: (data: Partial<TripItem>) => extensionService.createTrip(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['trips'] }),
  });

  return { ...query, createTrip };
}

// 17. Fitness
export function useFitness() {
  const qc = useQueryClient();
  const workouts = useQuery({
    queryKey: ['workouts'],
    queryFn: () => extensionService.getWorkouts(),
  });

  const stats = useQuery({
    queryKey: ['fitnessStats'],
    queryFn: () => extensionService.getFitnessStats(),
  });

  const createWorkout = useMutation({
    mutationFn: (data: Partial<WorkoutItem>) => extensionService.createWorkout(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['workouts'] });
      qc.invalidateQueries({ queryKey: ['fitnessStats'] });
    },
  });

  return { workouts, stats, createWorkout };
}

// 18. Personal Assets
export function useAssets(params?: { category?: string }) {
  const qc = useQueryClient();
  const query = useQuery({
    queryKey: ['assets', params],
    queryFn: () => extensionService.getAssets(params),
  });

  const createAsset = useMutation({
    mutationFn: (data: Partial<PersonalAssetItem>) => extensionService.createAsset(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['assets'] }),
  });

  return { ...query, createAsset };
}

// 19. Bills & Payments
export function useBills(params?: { status?: string }) {
  const qc = useQueryClient();
  const query = useQuery({
    queryKey: ['bills', params],
    queryFn: () => extensionService.getBills(params),
  });

  const createBill = useMutation({
    mutationFn: (data: Partial<BillItem>) => extensionService.createBill(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['bills'] }),
  });

  const recordPayment = useMutation({
    mutationFn: ({ billId, data }: { billId: string; data: any }) => extensionService.recordBillPayment(billId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['bills'] }),
  });

  return { ...query, createBill, recordPayment };
}

