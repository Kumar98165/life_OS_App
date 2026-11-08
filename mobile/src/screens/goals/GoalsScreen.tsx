import React, { useState, useMemo } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import {
  useGoals,
  useCreateGoal,
  useUpdateGoal,
  useDeleteGoal,
  useCreateMilestone,
  useUpdateMilestone,
  useCompleteMilestone,
  useDeleteMilestone,
} from '../../hooks/useGoals';
import { Goal, GoalMilestone, GoalPriority, GoalStatus } from '../../types/goal';
import { GoalFormData, MilestoneFormData } from '../../schemas/goal';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  SearchInput,
  Heading,
  BodyText,
  Caption,
  SkeletonLoader,
  EmptyState,
  ErrorState,
  Toast,
} from '../../components';
import {
  CreateEditGoalModal,
  CreateEditMilestoneModal,
  GoalDetailsModal,
} from '../../components/goals';

const STATUS_FILTERS: { id: string; label: string }[] = [
  { id: '', label: 'All' },
  { id: 'in_progress', label: 'In Progress' },
  { id: 'completed', label: 'Completed' },
  { id: 'paused', label: 'Paused' },
];

export const GoalsScreen: React.FC = () => {
  const { theme } = useTheme();

  // Search & Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');

  // Modals state
  const [isCreateGoalOpen, setIsCreateGoalOpen] = useState(false);
  const [goalToEdit, setGoalToEdit] = useState<Goal | null>(null);
  const [selectedGoalDetails, setSelectedGoalDetails] = useState<Goal | null>(null);

  // Milestone modal state
  const [isMilestoneModalOpen, setIsMilestoneModalOpen] = useState(false);
  const [milestoneTargetGoalId, setMilestoneTargetGoalId] = useState<string | null>(null);
  const [milestoneToEdit, setMilestoneToEdit] = useState<GoalMilestone | null>(null);

  // Feedback state
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Query parameters
  const queryParams = useMemo(() => {
    return {
      status: selectedStatus || undefined,
      search: searchQuery.trim() || undefined,
      per_page: 50,
    };
  }, [selectedStatus, searchQuery]);

  const { data, isLoading, isError, refetch, isRefetching } = useGoals(queryParams);

  const createGoalMutation = useCreateGoal();
  const updateGoalMutation = useUpdateGoal();
  const deleteGoalMutation = useDeleteGoal();

  const createMilestoneMutation = useCreateMilestone();
  const updateMilestoneMutation = useUpdateMilestone();
  const completeMilestoneMutation = useCompleteMilestone();
  const deleteMilestoneMutation = useDeleteMilestone();

  const goals = data?.goals || [];

  // Metrics calculation
  const metrics = useMemo(() => {
    const totalGoals = goals.length;
    const activeGoals = goals.filter((g) => g.status === 'in_progress' || g.status === 'active').length;
    const completedGoals = goals.filter((g) => g.status === 'completed' || g.status === 'achieved').length;
    const avgProgress =
      totalGoals > 0
        ? Math.round(goals.reduce((acc, g) => acc + (g.progress_percent || 0), 0) / totalGoals)
        : 0;

    return { totalGoals, activeGoals, completedGoals, avgProgress };
  }, [goals]);

  // Goal Form Submission
  const handleGoalSubmit = async (formData: GoalFormData) => {
    let targetIso: string | null = null;
    if (formData.target_date && formData.target_date.trim()) {
      targetIso = new Date(`${formData.target_date}T00:00:00Z`).toISOString();
    }

    const payload = {
      title: formData.title,
      description: formData.description || null,
      target_date: targetIso,
      priority: formData.priority,
      status: formData.status,
      category: formData.category || null,
    };

    if (goalToEdit) {
      const updated = await updateGoalMutation.mutateAsync({
        goalId: goalToEdit.id,
        payload,
      });
      setToastMessage('Goal updated successfully');
      setGoalToEdit(null);
      if (selectedGoalDetails && selectedGoalDetails.id === goalToEdit.id) {
        setSelectedGoalDetails(updated);
      }
    } else {
      await createGoalMutation.mutateAsync(payload);
      setToastMessage('Goal created successfully');
    }
  };

  // Milestone Form Submission
  const handleMilestoneSubmit = async (formData: MilestoneFormData) => {
    if (!milestoneTargetGoalId) return;

    let targetIso: string | null = null;
    if (formData.target_date && formData.target_date.trim()) {
      targetIso = new Date(`${formData.target_date}T00:00:00Z`).toISOString();
    }

    if (milestoneToEdit) {
      const res = await updateMilestoneMutation.mutateAsync({
        goalId: milestoneTargetGoalId,
        milestoneId: milestoneToEdit.id,
        payload: {
          title: formData.title,
          description: formData.description || null,
          target_date: targetIso,
          sort_order: formData.sort_order,
        },
      });
      setToastMessage('Milestone updated');
      setMilestoneToEdit(null);
      if (selectedGoalDetails && selectedGoalDetails.id === milestoneTargetGoalId) {
        setSelectedGoalDetails(res.goal);
      }
    } else {
      const res = await createMilestoneMutation.mutateAsync({
        goalId: milestoneTargetGoalId,
        payload: {
          title: formData.title,
          description: formData.description || null,
          target_date: targetIso,
          sort_order: formData.sort_order,
        },
      });
      setToastMessage('Milestone added');
      if (selectedGoalDetails && selectedGoalDetails.id === milestoneTargetGoalId) {
        setSelectedGoalDetails(res.goal);
      }
    }
  };

  const handleToggleMilestone = async (
    goalId: string,
    milestoneId: string,
    isCompleted: boolean
  ) => {
    const res = await completeMilestoneMutation.mutateAsync({
      goalId,
      milestoneId,
      isCompleted,
    });
    setToastMessage(isCompleted ? 'Milestone completed!' : 'Milestone reopened');
    if (selectedGoalDetails && selectedGoalDetails.id === goalId) {
      setSelectedGoalDetails(res.goal);
    }
  };

  const handleDeleteMilestone = async (goalId: string, milestoneId: string) => {
    const res = await deleteMilestoneMutation.mutateAsync({ goalId, milestoneId });
    setToastMessage('Milestone deleted');
    if (selectedGoalDetails && selectedGoalDetails.id === goalId) {
      setSelectedGoalDetails(res.goal);
    }
  };

  const handleDeleteGoal = async (goalId: string) => {
    await deleteGoalMutation.mutateAsync(goalId);
    setToastMessage('Goal removed');
    setSelectedGoalDetails(null);
  };

  const getPriorityColor = (priority: GoalPriority) => {
    switch (priority) {
      case 'high':
        return theme.colors.warning;
      case 'low':
        return theme.colors.textSecondary;
      default:
        return theme.colors.primary;
    }
  };

  const getStatusColor = (status: GoalStatus) => {
    switch (status) {
      case 'completed':
      case 'achieved':
        return theme.colors.success;
      case 'paused':
        return theme.colors.warning;
      case 'cancelled':
      case 'abandoned':
        return theme.colors.error;
      default:
        return theme.colors.primary;
    }
  };

  return (
    <SafeAreaContainer>
      {/* Top Header */}
      <View style={styles.header}>
        <View>
          <Caption color="secondary">VISION & TARGETS</Caption>
          <Heading level={2}>Goals & Milestones</Heading>
        </View>
        <TouchableOpacity
          onPress={() => {
            setGoalToEdit(null);
            setIsCreateGoalOpen(true);
          }}
          style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
        >
          <Ionicons name="add" size={24} color="#FFF" />
        </TouchableOpacity>
      </View>

      {/* Metrics Strip */}
      <View style={styles.metricsRow}>
        <GlassCard style={styles.metricCard}>
          <Caption color="secondary">ACTIVE</Caption>
          <Heading level={3} style={{ color: theme.colors.primary }}>
            {metrics.activeGoals}
          </Heading>
        </GlassCard>
        <GlassCard style={styles.metricCard}>
          <Caption color="secondary">COMPLETED</Caption>
          <Heading level={3} style={{ color: theme.colors.success }}>
            {metrics.completedGoals}
          </Heading>
        </GlassCard>
        <GlassCard style={styles.metricCard}>
          <Caption color="secondary">AVG PROGRESS</Caption>
          <Heading level={3} style={{ color: theme.colors.primaryDark }}>
            {metrics.avgProgress}%
          </Heading>
        </GlassCard>
      </View>

      {/* Search Input */}
      <View style={styles.searchContainer}>
        <SearchInput
          placeholder="Search goals by title or category..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          onClear={() => setSearchQuery('')}
        />
      </View>

      {/* Status Filter Tabs */}
      <View style={styles.filterTabsRow}>
        {STATUS_FILTERS.map((f) => {
          const isSelected = selectedStatus === f.id;
          return (
            <TouchableOpacity
              key={f.id}
              onPress={() => setSelectedStatus(f.id)}
              style={[
                styles.filterPill,
                {
                  backgroundColor: isSelected
                    ? theme.colors.primary
                    : theme.colors.glassBackground,
                  borderColor: isSelected ? theme.colors.primary : theme.colors.border,
                },
              ]}
            >
              <BodyText
                style={[
                  styles.filterPillText,
                  {
                    color: isSelected ? '#FFF' : theme.colors.textSecondary,
                    fontWeight: isSelected ? '600' : '400',
                  },
                ]}
              >
                {f.label}
              </BodyText>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Goals Content List */}
      <ScrollContainer
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={() => {
              refetch();
            }}
            tintColor={theme.colors.primary}
          />
        }
      >
        {isLoading && !goals.length ? (
          <View style={styles.loadingContainer}>
            <SkeletonLoader width="100%" height={110} borderRadius={16} />
            <View style={{ height: 12 }} />
            <SkeletonLoader width="100%" height={110} borderRadius={16} />
            <View style={{ height: 12 }} />
            <SkeletonLoader width="100%" height={110} borderRadius={16} />
          </View>
        ) : isError ? (
          <ErrorState
            title="Unable to load goals"
            message="Could not retrieve your goals from the server. Please check your connection."
            onRetry={refetch}
          />
        ) : goals.length === 0 ? (
          <EmptyState
            title="No Goals Found"
            description="Start building towards your milestones by creating your first life target."
            actionLabel="Create First Goal"
            onActionPress={() => {
              setGoalToEdit(null);
              setIsCreateGoalOpen(true);
            }}
          />
        ) : (
          <View style={styles.goalsList}>
            {goals.map((goal) => {
              const progress = Math.round(goal.progress_percent || 0);
              const totalMilestones = goal.total_milestones ?? (goal.milestones?.length || 0);
              const completedMilestones =
                goal.completed_milestones ??
                (goal.milestones ? goal.milestones.filter((m) => m.is_completed).length : 0);

              const formattedTarget = goal.target_date
                ? new Date(goal.target_date).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })
                : null;

              return (
                <TouchableOpacity
                  key={goal.id}
                  activeOpacity={0.8}
                  onPress={() => setSelectedGoalDetails(goal)}
                >
                  <GlassCard style={styles.goalCard}>
                    <View style={styles.cardHeaderRow}>
                      <View style={styles.titleCol}>
                        <BodyText style={styles.goalCardTitle}>{goal.title}</BodyText>
                        {goal.category ? (
                          <Caption color="secondary" style={styles.categoryText}>
                            {goal.category}
                          </Caption>
                        ) : null}
                      </View>
                      <View
                        style={[
                          styles.statusBadge,
                          { backgroundColor: getStatusColor(goal.status) + '20' },
                        ]}
                      >
                        <BodyText
                          style={[
                            styles.statusBadgeText,
                            { color: getStatusColor(goal.status) },
                          ]}
                        >
                          {goal.status.replace('_', ' ')}
                        </BodyText>
                      </View>
                    </View>

                    {goal.description ? (
                      <Caption numberOfLines={2} color="secondary" style={styles.descText}>
                        {goal.description}
                      </Caption>
                    ) : null}

                    {/* Progress Bar */}
                    <View style={styles.progressSection}>
                      <View style={styles.progressBarBg}>
                        <View
                          style={[
                            styles.progressBarFill,
                            {
                              width: `${progress}%`,
                              backgroundColor:
                                progress === 100 ? theme.colors.success : theme.colors.primary,
                            },
                          ]}
                        />
                      </View>
                      <View style={styles.progressStatsRow}>
                        <Caption color="secondary">
                          {completedMilestones} / {totalMilestones} checkpoints
                        </Caption>
                        <Caption style={[styles.progressPercentText, { color: theme.colors.primary }]}>
                          {progress}%
                        </Caption>
                      </View>
                    </View>

                    {/* Footer Info */}
                    <View style={styles.cardFooterRow}>
                      <View
                        style={[
                          styles.priorityPill,
                          { backgroundColor: getPriorityColor(goal.priority) + '18' },
                        ]}
                      >
                        <Caption style={{ color: getPriorityColor(goal.priority), fontWeight: '700' }}>
                          {goal.priority.toUpperCase()}
                        </Caption>
                      </View>

                      {formattedTarget && (
                        <View style={styles.targetDateRow}>
                          <Ionicons name="calendar-outline" size={12} color={theme.colors.textMuted} />
                          <Caption color="secondary" style={{ marginLeft: 4 }}>
                            {formattedTarget}
                          </Caption>
                        </View>
                      )}
                    </View>
                  </GlassCard>
                </TouchableOpacity>
              );
            })}
          </View>
        )}
      </ScrollContainer>

      {/* Create / Edit Goal Modal */}
      <CreateEditGoalModal
        visible={isCreateGoalOpen}
        goalToEdit={goalToEdit}
        isLoading={createGoalMutation.isPending || updateGoalMutation.isPending}
        onClose={() => {
          setIsCreateGoalOpen(false);
          setGoalToEdit(null);
        }}
        onSubmit={handleGoalSubmit}
      />

      {/* Goal Details Modal */}
      <GoalDetailsModal
        visible={!!selectedGoalDetails}
        goal={selectedGoalDetails}
        onClose={() => setSelectedGoalDetails(null)}
        onEditGoal={(g) => {
          setGoalToEdit(g);
          setIsCreateGoalOpen(true);
        }}
        onDeleteGoal={handleDeleteGoal}
        onAddMilestone={(goalId) => {
          setMilestoneTargetGoalId(goalId);
          setMilestoneToEdit(null);
          setIsMilestoneModalOpen(true);
        }}
        onEditMilestone={(goalId, m) => {
          setMilestoneTargetGoalId(goalId);
          setMilestoneToEdit(m);
          setIsMilestoneModalOpen(true);
        }}
        onToggleMilestone={handleToggleMilestone}
        onDeleteMilestone={handleDeleteMilestone}
      />

      {/* Create / Edit Milestone Modal */}
      <CreateEditMilestoneModal
        visible={isMilestoneModalOpen}
        milestoneToEdit={milestoneToEdit}
        isLoading={createMilestoneMutation.isPending || updateMilestoneMutation.isPending}
        onClose={() => {
          setIsMilestoneModalOpen(false);
          setMilestoneToEdit(null);
          setMilestoneTargetGoalId(null);
        }}
        onSubmit={handleMilestoneSubmit}
      />

      {/* Toast Feedback */}
      <Toast
        visible={!!toastMessage}
        message={toastMessage || ''}
        type="success"
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
    paddingTop: 12,
    paddingBottom: 8,
  },
  addButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  metricsRow: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 6,
    gap: 8,
  },
  metricCard: {
    flex: 1,
    padding: 10,
    borderRadius: 14,
    alignItems: 'center',
  },
  searchContainer: {
    paddingHorizontal: 20,
    paddingVertical: 6,
  },
  filterTabsRow: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 6,
    gap: 8,
  },
  filterPill: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    borderWidth: 1,
  },
  filterPillText: {
    fontSize: 12,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  loadingContainer: {
    marginTop: 10,
  },
  goalsList: {
    gap: 12,
    marginTop: 6,
  },
  goalCard: {
    padding: 14,
    borderRadius: 16,
  },
  cardHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  titleCol: {
    flex: 1,
    marginRight: 8,
  },
  goalCardTitle: {
    fontSize: 15,
    fontWeight: '700',
  },
  categoryText: {
    marginTop: 2,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  statusBadgeText: {
    fontSize: 10,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  descText: {
    marginVertical: 8,
  },
  progressSection: {
    marginVertical: 8,
  },
  progressBarBg: {
    height: 6,
    borderRadius: 3,
    backgroundColor: 'rgba(233, 234, 242, 0.7)',
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 3,
  },
  progressStatsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 4,
  },
  progressPercentText: {
    fontSize: 11,
    fontWeight: '700',
  },
  cardFooterRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 4,
  },
  priorityPill: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  targetDateRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
});

