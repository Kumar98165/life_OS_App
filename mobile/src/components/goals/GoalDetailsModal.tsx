import React, { useState } from 'react';
import { View, StyleSheet, Modal, TouchableOpacity, ScrollView, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { Goal, GoalMilestone, GoalPriority, GoalStatus } from '../../types/goal';
import {
  GlassCard,
  PrimaryButton,
  SecondaryButton,
  Heading,
  BodyText,
  Caption,
  ConfirmationModal,
} from '../../components';

export interface GoalDetailsModalProps {
  visible: boolean;
  goal: Goal | null;
  onClose: () => void;
  onEditGoal: (goal: Goal) => void;
  onDeleteGoal: (goalId: string) => Promise<void>;
  onAddMilestone: (goalId: string) => void;
  onEditMilestone: (goalId: string, milestone: GoalMilestone) => void;
  onToggleMilestone: (goalId: string, milestoneId: string, isCompleted: boolean) => Promise<void>;
  onDeleteMilestone: (goalId: string, milestoneId: string) => Promise<void>;
}

export const GoalDetailsModal: React.FC<GoalDetailsModalProps> = ({
  visible,
  goal,
  onClose,
  onEditGoal,
  onDeleteGoal,
  onAddMilestone,
  onEditMilestone,
  onToggleMilestone,
  onDeleteMilestone,
}) => {
  const { theme } = useTheme();
  const [showDeleteGoalConfirm, setShowDeleteGoalConfirm] = useState(false);
  const [milestoneToDelete, setMilestoneToDelete] = useState<string | null>(null);

  if (!goal) return null;

  const milestones = goal.milestones || [];
  const completedCount = milestones.filter((m) => m.is_completed).length;
  const totalCount = milestones.length;
  const progress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : Math.round(goal.progress_percent || 0);

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

  const formatDate = (iso?: string | null) => {
    if (!iso) return null;
    return new Date(iso).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <View style={styles.modalBackdrop}>
        <View style={styles.sheetContainer}>
          <GlassCard style={styles.modalCard}>
            {/* Header Badges & Close */}
            <View style={styles.headerRow}>
              <View style={styles.badgesRow}>
                <View
                  style={[
                    styles.badge,
                    { backgroundColor: getStatusColor(goal.status) + '20' },
                  ]}
                >
                  <BodyText
                    style={[
                      styles.badgeText,
                      { color: getStatusColor(goal.status) },
                    ]}
                  >
                    {goal.status.replace('_', ' ').toUpperCase()}
                  </BodyText>
                </View>

                <View
                  style={[
                    styles.badge,
                    { backgroundColor: getPriorityColor(goal.priority) + '20' },
                  ]}
                >
                  <BodyText
                    style={[
                      styles.badgeText,
                      { color: getPriorityColor(goal.priority) },
                    ]}
                  >
                    {goal.priority.toUpperCase()} PRIORITY
                  </BodyText>
                </View>

                {goal.category && (
                  <View
                    style={[
                      styles.badge,
                      { backgroundColor: theme.colors.surfaceSubtle },
                    ]}
                  >
                    <BodyText style={[styles.badgeText, { color: theme.colors.textSecondary }]}>
                      {goal.category.toUpperCase()}
                    </BodyText>
                  </View>
                )}
              </View>

              <TouchableOpacity
                onPress={onClose}
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                style={styles.closeButton}
              >
                <Ionicons name="close" size={24} color={theme.colors.textSecondary} />
              </TouchableOpacity>
            </View>

            <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
              <Heading level={2} style={styles.goalTitle}>
                {goal.title}
              </Heading>

              {/* Progress Overview Card */}
              <View style={[styles.progressCard, { backgroundColor: theme.colors.glassBackground }]}>
                <View style={styles.progressHeaderRow}>
                  <BodyText style={styles.progressLabel}>Overall Milestone Progress</BodyText>
                  <Heading level={3} style={{ color: theme.colors.primary }}>
                    {progress}%
                  </Heading>
                </View>

                <View
                  style={[
                    styles.progressBarTrack,
                    { backgroundColor: theme.colors.surfaceSubtle },
                  ]}
                >
                  <View
                    style={[
                      styles.progressBarFill,
                      {
                        width: `${progress}%`,
                        backgroundColor: progress === 100 ? theme.colors.success : theme.colors.primary,
                      },
                    ]}
                  />
                </View>

                <View style={styles.progressStatsRow}>
                  <Caption color="secondary">
                    {completedCount} of {totalCount} milestones completed
                  </Caption>
                  {goal.target_date && (
                    <View style={styles.targetDateRow}>
                      <Ionicons name="calendar-outline" size={12} color={theme.colors.textMuted} />
                      <Caption color="secondary" style={{ marginLeft: 4 }}>
                        Target: {formatDate(goal.target_date)}
                      </Caption>
                    </View>
                  )}
                </View>
              </View>

              {/* Description */}
              {goal.description ? (
                <View style={styles.descriptionSection}>
                  <Caption style={styles.sectionCaption}>OBJECTIVE & DELIVERABLES</Caption>
                  <BodyText style={styles.descriptionText}>{goal.description}</BodyText>
                </View>
              ) : null}

              {/* Milestones Checklist */}
              <View style={styles.milestonesSection}>
                <View style={styles.milestonesHeaderRow}>
                  <Caption style={styles.sectionCaption}>MILESTONES ({totalCount})</Caption>
                  <TouchableOpacity
                    onPress={() => onAddMilestone(goal.id)}
                    style={styles.addMilestoneBtn}
                  >
                    <Ionicons name="add" size={16} color={theme.colors.primary} />
                    <BodyText style={[styles.addMilestoneText, { color: theme.colors.primary }]}>
                      Add Milestone
                    </BodyText>
                  </TouchableOpacity>
                </View>

                {milestones.length === 0 ? (
                  <View style={[styles.emptyMilestonesCard, { backgroundColor: theme.colors.surfaceSubtle }]}>
                    <Ionicons name="flag-outline" size={24} color={theme.colors.textMuted} />
                    <Caption color="secondary" style={{ marginTop: 6, textAlign: 'center' }}>
                      No milestones created yet. Break your goal into actionable checkpoints.
                    </Caption>
                  </View>
                ) : (
                  <View style={styles.milestonesList}>
                    {milestones.map((m) => (
                      <View
                        key={m.id}
                        style={[
                          styles.milestoneItem,
                          {
                            backgroundColor: m.is_completed
                              ? theme.colors.surfaceSubtle
                              : theme.colors.glassBackground,
                            borderColor: theme.colors.border,
                          },
                        ]}
                      >
                        <TouchableOpacity
                          onPress={() => onToggleMilestone(goal.id, m.id, !m.is_completed)}
                          style={styles.checkboxTouchable}
                        >
                          <Ionicons
                            name={m.is_completed ? 'checkmark-circle' : 'ellipse-outline'}
                            size={22}
                            color={m.is_completed ? theme.colors.success : theme.colors.primary}
                          />
                        </TouchableOpacity>

                        <View style={styles.milestoneContentCol}>
                          <BodyText
                            style={[
                              styles.milestoneTitle,
                              m.is_completed && styles.completedMilestoneTitle,
                            ]}
                          >
                            {m.title}
                          </BodyText>
                          {m.target_date && (
                            <Caption color="secondary">
                              Due: {formatDate(m.target_date)}
                            </Caption>
                          )}
                          {m.description ? (
                            <Caption numberOfLines={1} color="secondary" style={{ marginTop: 2 }}>
                              {m.description}
                            </Caption>
                          ) : null}
                        </View>

                        <View style={styles.milestoneActions}>
                          <TouchableOpacity
                            onPress={() => onEditMilestone(goal.id, m)}
                            style={styles.actionIcon}
                          >
                            <Ionicons name="pencil-outline" size={16} color={theme.colors.textSecondary} />
                          </TouchableOpacity>
                          <TouchableOpacity
                            onPress={() => setMilestoneToDelete(m.id)}
                            style={styles.actionIcon}
                          >
                            <Ionicons name="trash-outline" size={16} color={theme.colors.error} />
                          </TouchableOpacity>
                        </View>
                      </View>
                    ))}
                  </View>
                )}
              </View>

              {/* Bottom Actions */}
              <View style={styles.bottomRow}>
                <SecondaryButton
                  label="Edit Goal"
                  onPress={() => {
                    onClose();
                    onEditGoal(goal);
                  }}
                  icon={<Ionicons name="pencil-outline" size={16} color={theme.colors.primary} />}
                  style={{ flex: 1 }}
                />
                <TouchableOpacity
                  onPress={() => setShowDeleteGoalConfirm(true)}
                  style={[styles.deleteIconButton, { borderColor: theme.colors.error + '40' }]}
                >
                  <Ionicons name="trash-outline" size={20} color={theme.colors.error} />
                </TouchableOpacity>
              </View>
            </ScrollView>
          </GlassCard>
        </View>
      </View>

      {/* Delete Goal Confirmation */}
      <ConfirmationModal
        visible={showDeleteGoalConfirm}
        title="Delete Goal?"
        message="Are you sure you want to delete this goal? All associated milestones will also be removed."
        confirmLabel="Delete Goal"
        isDestructive
        onConfirm={async () => {
          await onDeleteGoal(goal.id);
          setShowDeleteGoalConfirm(false);
          onClose();
        }}
        onCancel={() => setShowDeleteGoalConfirm(false)}
      />

      {/* Delete Milestone Confirmation */}
      <ConfirmationModal
        visible={!!milestoneToDelete}
        title="Delete Milestone?"
        message="Are you sure you want to remove this milestone checkpoint?"
        confirmLabel="Delete"
        isDestructive
        onConfirm={async () => {
          if (milestoneToDelete) {
            await onDeleteMilestone(goal.id, milestoneToDelete);
            setMilestoneToDelete(null);
          }
        }}
        onCancel={() => setMilestoneToDelete(null)}
      />
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 15, 25, 0.5)',
    justifyContent: 'flex-end',
  },
  sheetContainer: {
    maxHeight: '88%',
  },
  modalCard: {
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    borderBottomLeftRadius: 0,
    borderBottomRightRadius: 0,
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: Platform.OS === 'ios' ? 36 : 24,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  badgesRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 8,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  closeButton: {
    padding: 6,
  },
  scrollContent: {
    paddingBottom: 20,
  },
  goalTitle: {
    marginBottom: 14,
  },
  progressCard: {
    padding: 14,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(233, 234, 242, 0.6)',
    marginBottom: 16,
  },
  progressHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  progressLabel: {
    fontSize: 13,
    fontWeight: '600',
  },
  progressBarTrack: {
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
    marginVertical: 4,
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  progressStatsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 6,
  },
  targetDateRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  descriptionSection: {
    marginBottom: 16,
  },
  sectionCaption: {
    fontWeight: '700',
    letterSpacing: 0.8,
    marginBottom: 6,
  },
  descriptionText: {
    fontSize: 14,
    lineHeight: 20,
  },
  milestonesSection: {
    marginBottom: 16,
  },
  milestonesHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  addMilestoneBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  addMilestoneText: {
    fontSize: 13,
    fontWeight: '600',
  },
  emptyMilestonesCard: {
    padding: 16,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  milestonesList: {
    gap: 8,
  },
  milestoneItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    borderRadius: 12,
    borderWidth: 1,
  },
  checkboxTouchable: {
    padding: 4,
    marginRight: 8,
  },
  milestoneContentCol: {
    flex: 1,
  },
  milestoneTitle: {
    fontSize: 13,
    fontWeight: '600',
  },
  completedMilestoneTitle: {
    textDecorationLine: 'line-through',
    opacity: 0.6,
  },
  milestoneActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  actionIcon: {
    padding: 4,
  },
  bottomRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginTop: 10,
  },
  deleteIconButton: {
    width: 48,
    height: 48,
    borderRadius: 14,
    borderWidth: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(239, 68, 68, 0.08)',
  },
});

