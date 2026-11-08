import React, { useState, useMemo } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import {
  useHabits,
  useCreateHabit,
  useUpdateHabit,
  useDeleteHabit,
  useHabitCheckIn,
  useUndoHabitCheckIn,
  useHabitDailySummary,
} from '../../hooks/useHabits';
import { Habit, HabitFrequency } from '../../types/habit';
import { HabitFormData } from '../../schemas/habit';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  SkeletonLoader,
  EmptyState,
  ErrorState,
  Toast,
} from '../../components';
import { CreateEditHabitModal, HabitDetailsModal } from '../../components/habits';

const FREQUENCY_FILTERS: { id: string; label: string }[] = [
  { id: '', label: 'All' },
  { id: 'daily', label: 'Daily' },
  { id: 'weekdays', label: 'Weekdays' },
  { id: 'weekly', label: 'Weekly' },
];

export const HabitsScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation();

  // Filters & State
  const [selectedFreq, setSelectedFreq] = useState<string>('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [habitToEdit, setHabitToEdit] = useState<Habit | null>(null);
  const [selectedHabitDetails, setSelectedHabitDetails] = useState<Habit | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 3000);
  };

  const todayStr = useMemo(() => new Date().toISOString().split('T')[0], []);
  const todayFormatted = useMemo(() => {
    return new Date().toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'short',
      day: 'numeric',
    });
  }, []);

  const queryParams = useMemo(() => {
    return {
      frequency: (selectedFreq as HabitFrequency) || undefined,
      include_archived: false,
    };
  }, [selectedFreq]);

  const { data: habits = [], isLoading, isError, refetch, isRefetching } = useHabits(queryParams);
  const { data: dailySummary, refetch: refetchSummary } = useHabitDailySummary(todayStr);

  const createHabitMutation = useCreateHabit();
  const updateHabitMutation = useUpdateHabit();
  const deleteHabitMutation = useDeleteHabit();
  const checkInMutation = useHabitCheckIn();
  const undoCheckInMutation = useUndoHabitCheckIn();

  // Progress metrics
  const completedTodayCount = habits.filter((h) => h.completed_today).length;
  const totalCount = habits.length;
  const progressPercent = totalCount > 0 ? Math.round((completedTodayCount / totalCount) * 100) : 0;

  const handleRefresh = async () => {
    await Promise.all([refetch(), refetchSummary()]);
  };

  const handleCreateOrUpdate = async (formData: HabitFormData) => {
    try {
      if (habitToEdit) {
        await updateHabitMutation.mutateAsync({
          habitId: habitToEdit.id,
          payload: {
            title: formData.title,
            description: formData.description,
            frequency: formData.frequency,
            target_days_per_week: formData.target_days_per_week,
            color_hex: formData.color_hex,
            icon: formData.icon,
          },
        });
        showToast('Habit updated successfully');
      } else {
        await createHabitMutation.mutateAsync({
          title: formData.title,
          description: formData.description,
          frequency: formData.frequency,
          target_days_per_week: formData.target_days_per_week,
          color_hex: formData.color_hex,
          icon: formData.icon,
        });
        showToast('Habit created successfully');
      }
      setHabitToEdit(null);
    } catch (err: any) {
      showToast(err.message || 'Failed to save habit');
    }
  };

  const handleDelete = async (habitId: string) => {
    try {
      await deleteHabitMutation.mutateAsync(habitId);
      showToast('Habit deleted');
      if (selectedHabitDetails?.id === habitId) {
        setSelectedHabitDetails(null);
      }
    } catch (err: any) {
      showToast(err.message || 'Failed to delete habit');
    }
  };

  const handleQuickCheckIn = async (habit: Habit) => {
    try {
      if (habit.completed_today && habit.today_log_id) {
        await undoCheckInMutation.mutateAsync({
          habitId: habit.id,
          logId: habit.today_log_id,
        });
        showToast(`Check-in undone for ${habit.title}`);
      } else {
        await checkInMutation.mutateAsync({
          habitId: habit.id,
          payload: { log_date: todayStr, completed: true },
        });
        showToast(`Great job! Completed ${habit.title} 🎉`);
      }
    } catch (err: any) {
      showToast(err.message || 'Failed to record check-in');
    }
  };

  return (
    <SafeAreaContainer edges={['top']}>
      {/* Toast Alert */}
      <Toast
        visible={!!toastMessage}
        message={toastMessage || ''}
        type="info"
      />

      {/* Top Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Heading level={1}>Habits</Heading>
          <Caption color="secondary">{todayFormatted}</Caption>
        </View>

        <TouchableOpacity
          onPress={() => {
            setHabitToEdit(null);
            setIsCreateModalOpen(true);
          }}
          activeOpacity={0.8}
          style={[styles.addBtn, { backgroundColor: theme.colors.primary }]}
          accessibilityRole="button"
          accessibilityLabel="Add Habit"
        >
          <Ionicons name="add" size={22} color="#FFFFFF" />
          <Caption weight="600" style={{ color: '#FFFFFF', marginLeft: 4 }}>
            New Habit
          </Caption>
        </TouchableOpacity>
      </View>

      <ScrollContainer
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={handleRefresh}
            tintColor={theme.colors.primary}
            colors={[theme.colors.primary]}
          />
        }
        contentContainerStyle={styles.scrollContent}
      >
        {/* Daily Progress Banner */}
        <GlassCard elevation="subtle" style={styles.progressCard}>
          <View style={styles.progressHeader}>
            <View>
              <BodyText weight="600">Daily Routine Progress</BodyText>
              <Caption color="secondary">
                {completedTodayCount} of {totalCount} completed today
              </Caption>
            </View>
            <Heading level={2} style={{ color: theme.colors.primary }}>
              {progressPercent}%
            </Heading>
          </View>

          {/* Progress Bar Track */}
          <View style={[styles.progressBarTrack, { backgroundColor: theme.colors.surfaceSubtle }]}>
            <View
              style={[
                styles.progressBarFill,
                {
                  width: `${progressPercent}%`,
                  backgroundColor: progressPercent === 100 ? theme.colors.success : theme.colors.primary,
                },
              ]}
            />
          </View>
        </GlassCard>

        {/* Frequency Filters */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.filterRow}
        >
          {FREQUENCY_FILTERS.map((f) => {
            const isSelected = selectedFreq === f.id;
            return (
              <TouchableOpacity
                key={f.id}
                onPress={() => setSelectedFreq(f.id)}
                style={[
                  styles.filterPill,
                  {
                    backgroundColor: isSelected
                      ? theme.colors.primary
                      : theme.colors.glassBackgroundSolid,
                    borderColor: isSelected ? theme.colors.primary : theme.colors.glassBorder,
                  },
                ]}
              >
                <Caption
                  weight="600"
                  style={{
                    color: isSelected ? '#FFFFFF' : theme.colors.textSecondary,
                  }}
                >
                  {f.label}
                </Caption>
              </TouchableOpacity>
            );
          })}
        </ScrollView>

        {/* Habits List */}
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <SkeletonLoader width="100%" height={80} borderRadius={18} style={{ marginBottom: 12 }} />
            <SkeletonLoader width="100%" height={80} borderRadius={18} style={{ marginBottom: 12 }} />
            <SkeletonLoader width="100%" height={80} borderRadius={18} />
          </View>
        ) : isError ? (
          <ErrorState
            title="Failed to Load Habits"
            message="Could not retrieve your habits. Please check your network connection."
            onRetry={refetch}
          />
        ) : habits.length === 0 ? (
          <EmptyState
            icon="flame-outline"
            title="No Habits Found"
            description={
              selectedFreq
                ? 'No habits match the selected frequency filter.'
                : 'Start tracking positive habits to build discipline and maintain streaks!'
            }
            actionLabel="Add a Habit"
            onActionPress={() => {
              setHabitToEdit(null);
              setIsCreateModalOpen(true);
            }}
          />
        ) : (
          <View style={styles.habitList}>
            {habits.map((habit) => {
              const accent = habit.color_hex || theme.colors.primary;
              const isDone = habit.completed_today;

              return (
                <TouchableOpacity
                  key={habit.id}
                  activeOpacity={0.88}
                  onPress={() => setSelectedHabitDetails(habit)}
                  style={[
                    styles.habitCard,
                    {
                      backgroundColor: theme.colors.glassBackgroundSolid,
                      borderColor: isDone ? `${theme.colors.success}50` : theme.colors.glassBorder,
                    },
                    theme.shadows.subtle,
                  ]}
                >
                  {/* Left accent color bar */}
                  <View style={[styles.cardAccentBar, { backgroundColor: accent }]} />

                  <View style={styles.cardContent}>
                    {/* Icon circle */}
                    <View
                      style={[
                        styles.habitIconCircle,
                        { backgroundColor: `${accent}18` },
                      ]}
                    >
                      <Ionicons
                        name={(habit.icon as any) || 'flame'}
                        size={20}
                        color={accent}
                      />
                    </View>

                    <View style={styles.habitTextCol}>
                      <BodyText weight="600" numberOfLines={1}>
                        {habit.title}
                      </BodyText>
                      <View style={styles.metaRow}>
                        <Caption color="secondary">
                          {habit.frequency === 'daily'
                            ? 'Daily'
                            : habit.frequency === 'weekdays'
                            ? 'Mon-Fri'
                            : `${habit.target_days_per_week}x / wk`}
                        </Caption>
                        <Caption color="secondary">•</Caption>
                        <Caption style={{ color: theme.colors.warning }}>
                          {habit.current_streak}d streak 🔥
                        </Caption>
                      </View>
                    </View>

                    {/* Quick Check-in Toggle Button */}
                    <TouchableOpacity
                      onPress={(e) => {
                        e.stopPropagation();
                        handleQuickCheckIn(habit);
                      }}
                      activeOpacity={0.8}
                      style={[
                        styles.checkActionBtn,
                        {
                          backgroundColor: isDone ? theme.colors.success : 'transparent',
                          borderColor: isDone ? theme.colors.success : accent,
                        },
                      ]}
                      accessibilityRole="button"
                      accessibilityLabel={isDone ? 'Mark habit incomplete' : 'Complete habit'}
                    >
                      {isDone && <Ionicons name="checkmark" size={18} color="#FFFFFF" />}
                    </TouchableOpacity>
                  </View>
                </TouchableOpacity>
              );
            })}
          </View>
        )}
      </ScrollContainer>

      {/* Create / Edit Habit Modal */}
      <CreateEditHabitModal
        visible={isCreateModalOpen}
        habitToEdit={habitToEdit}
        onClose={() => {
          setIsCreateModalOpen(false);
          setHabitToEdit(null);
        }}
        onSubmit={handleCreateOrUpdate}
        isLoading={createHabitMutation.isPending || updateHabitMutation.isPending}
      />

      {/* Habit Details Modal */}
      <HabitDetailsModal
        visible={!!selectedHabitDetails}
        habit={selectedHabitDetails}
        onClose={() => setSelectedHabitDetails(null)}
        onEdit={(habit) => {
          setSelectedHabitDetails(null);
          setHabitToEdit(habit);
          setIsCreateModalOpen(true);
        }}
        onDelete={handleDelete}
        onCheckInChange={() => refetch()}
      />
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 8,
    paddingBottom: 12,
  },
  headerLeft: {
    flex: 1,
  },
  addBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 20,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 110,
  },
  progressCard: {
    padding: 16,
    borderRadius: 20,
    marginBottom: 16,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  progressBarTrack: {
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  filterRow: {
    flexDirection: 'row',
    gap: 8,
    paddingBottom: 16,
  },
  filterPill: {
    paddingVertical: 7,
    paddingHorizontal: 16,
    borderRadius: 14,
    borderWidth: 1,
  },
  loadingContainer: {
    marginTop: 8,
  },
  habitList: {
    gap: 12,
  },
  habitCard: {
    borderRadius: 18,
    borderWidth: 1,
    overflow: 'hidden',
    position: 'relative',
  },
  cardAccentBar: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    width: 5,
  },
  cardContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    paddingLeft: 16,
  },
  habitIconCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  habitTextCol: {
    flex: 1,
    marginRight: 10,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 2,
  },
  checkActionBtn: {
    width: 34,
    height: 34,
    borderRadius: 17,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
