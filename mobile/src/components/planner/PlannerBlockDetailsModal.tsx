import React, { useState } from 'react';
import { View, StyleSheet, Modal, TouchableOpacity, ScrollView, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { PlannerBlock, PlannerBlockStatus } from '../../types/planner';
import {
  GlassCard,
  PrimaryButton,
  SecondaryButton,
  Heading,
  BodyText,
  Caption,
  ConfirmationModal,
} from '../../components';

export interface PlannerBlockDetailsModalProps {
  visible: boolean;
  block: PlannerBlock | null;
  onClose: () => void;
  onEdit: (block: PlannerBlock) => void;
  onDelete: (blockId: string) => Promise<void>;
  onUpdateStatus: (blockId: string, status: PlannerBlockStatus) => Promise<void>;
}

export const PlannerBlockDetailsModal: React.FC<PlannerBlockDetailsModalProps> = ({
  visible,
  block,
  onClose,
  onEdit,
  onDelete,
  onUpdateStatus,
}) => {
  const { theme } = useTheme();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  if (!block) return null;

  const startDt = new Date(block.start_time);
  const endDt = new Date(block.end_time);

  const formatTime = (d: Date) => {
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
  };

  const formatDate = (d: Date) => {
    return d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
  };

  const durationMinutes = Math.max(0, Math.round((endDt.getTime() - startDt.getTime()) / 60000));

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(block.id);
      setShowDeleteConfirm(false);
      onClose();
    } finally {
      setIsDeleting(false);
    }
  };

  const handleStatusChange = async (newStatus: PlannerBlockStatus) => {
    setIsUpdatingStatus(true);
    try {
      await onUpdateStatus(block.id, newStatus);
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const getStatusColor = (status: PlannerBlockStatus) => {
    switch (status) {
      case 'completed':
        return theme.colors.success;
      case 'cancelled':
        return theme.colors.error;
      case 'skipped':
        return theme.colors.warning;
      default:
        return theme.colors.primary;
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent
      onRequestClose={onClose}
    >
      <View style={styles.modalBackdrop}>
        <View style={styles.sheetContainer}>
          <GlassCard style={styles.modalCard}>
            <View style={styles.headerRow}>
              <View style={styles.badgeRow}>
                <View
                  style={[
                    styles.statusBadge,
                    { backgroundColor: getStatusColor(block.status) + '20' },
                  ]}
                >
                  <BodyText
                    style={[
                      styles.statusBadgeText,
                      { color: getStatusColor(block.status) },
                    ]}
                  >
                    {block.status.toUpperCase()}
                  </BodyText>
                </View>

                <View
                  style={[
                    styles.typeBadge,
                    { backgroundColor: (block.color_hex || theme.colors.primary) + '20' },
                  ]}
                >
                  <BodyText
                    style={[
                      styles.typeBadgeText,
                      { color: block.color_hex || theme.colors.primary },
                    ]}
                  >
                    {block.block_type.toUpperCase()}
                  </BodyText>
                </View>
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
              <Heading level={2} style={styles.titleText}>
                {block.title}
              </Heading>

              {/* Time Card */}
              <View style={[styles.infoCard, { backgroundColor: theme.colors.glassBackground }]}>
                <View style={styles.infoRow}>
                  <Ionicons name="calendar-outline" size={18} color={theme.colors.primary} />
                  <BodyText style={styles.infoValue}>{formatDate(startDt)}</BodyText>
                </View>
                <View style={styles.infoRow}>
                  <Ionicons name="time-outline" size={18} color={theme.colors.primary} />
                  <BodyText style={styles.infoValue}>
                    {formatTime(startDt)} – {formatTime(endDt)} ({durationMinutes} mins)
                  </BodyText>
                </View>
              </View>

              {/* Linked Task Section */}
              {block.task && (
                <View style={[styles.infoCard, { backgroundColor: theme.colors.glassBackground }]}>
                  <Caption style={styles.cardHeaderCaption}>LINKED TASK</Caption>
                  <View style={styles.taskInfoRow}>
                    <Ionicons
                      name={block.task.status === 'completed' ? 'checkmark-circle' : 'ellipse-outline'}
                      size={20}
                      color={block.task.status === 'completed' ? theme.colors.success : theme.colors.primary}
                    />
                    <View style={styles.taskTextCol}>
                      <BodyText style={styles.taskTitleText}>{block.task.title}</BodyText>
                      <Caption color="secondary">
                        Priority: {block.task.priority.toUpperCase()} | Status: {block.task.status}
                      </Caption>
                    </View>
                  </View>
                </View>
              )}

              {/* Description */}
              {block.description ? (
                <View style={styles.descriptionSection}>
                  <Caption style={styles.cardHeaderCaption}>NOTES / AGENDA</Caption>
                  <BodyText style={styles.descriptionText}>{block.description}</BodyText>
                </View>
              ) : null}

              {/* Status Action Buttons */}
              <View style={styles.statusSection}>
                <Caption style={styles.cardHeaderCaption}>UPDATE STATUS</Caption>
                <View style={styles.statusButtonsRow}>
                  {(['scheduled', 'completed', 'skipped', 'cancelled'] as PlannerBlockStatus[]).map(
                    (st) => {
                      const isCurrent = block.status === st;
                      return (
                        <TouchableOpacity
                          key={st}
                          onPress={() => handleStatusChange(st)}
                          disabled={isUpdatingStatus || isCurrent}
                          style={[
                            styles.statusBtn,
                            {
                              backgroundColor: isCurrent
                                ? getStatusColor(st)
                                : theme.colors.glassBackground,
                              borderColor: getStatusColor(st),
                              opacity: isCurrent ? 1 : 0.8,
                            },
                          ]}
                        >
                          <BodyText
                            style={[
                              styles.statusBtnText,
                              { color: isCurrent ? '#FFF' : getStatusColor(st) },
                            ]}
                          >
                            {st.charAt(0).toUpperCase() + st.slice(1)}
                          </BodyText>
                        </TouchableOpacity>
                      );
                    }
                  )}
                </View>
              </View>

              {/* Edit / Delete Buttons */}
              <View style={styles.bottomActionRow}>
                <SecondaryButton
                  label="Edit Block"
                  onPress={() => {
                    onClose();
                    onEdit(block);
                  }}
                  icon={<Ionicons name="pencil-outline" size={16} color={theme.colors.primary} />}
                  style={styles.editBtn}
                />
                <TouchableOpacity
                  onPress={() => setShowDeleteConfirm(true)}
                  style={[styles.deleteIconButton, { borderColor: theme.colors.error + '40' }]}
                >
                  <Ionicons name="trash-outline" size={20} color={theme.colors.error} />
                </TouchableOpacity>
              </View>
            </ScrollView>
          </GlassCard>
        </View>
      </View>

      <ConfirmationModal
        visible={showDeleteConfirm}
        title="Delete Schedule Block?"
        message="Are you sure you want to remove this reserved time block? If linked to a task, the task itself will not be deleted."
        confirmLabel="Delete"
        isDestructive
        onConfirm={handleDelete}
        onCancel={() => setShowDeleteConfirm(false)}
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
    maxHeight: '85%',
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
    marginBottom: 16,
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  statusBadgeText: {
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.6,
  },
  typeBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  typeBadgeText: {
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.6,
  },
  closeButton: {
    padding: 6,
  },
  scrollContent: {
    paddingBottom: 16,
  },
  titleText: {
    marginBottom: 16,
  },
  infoCard: {
    padding: 14,
    borderRadius: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(233, 234, 242, 0.6)',
  },
  cardHeaderCaption: {
    marginBottom: 8,
    fontWeight: '600',
    letterSpacing: 0.8,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginVertical: 4,
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '500',
  },
  taskInfoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  taskTextCol: {
    flex: 1,
  },
  taskTitleText: {
    fontSize: 14,
    fontWeight: '600',
  },
  descriptionSection: {
    marginVertical: 8,
  },
  descriptionText: {
    fontSize: 14,
    lineHeight: 20,
  },
  statusSection: {
    marginVertical: 12,
  },
  statusButtonsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  statusBtn: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 12,
    borderWidth: 1,
  },
  statusBtnText: {
    fontSize: 12,
    fontWeight: '600',
  },
  bottomActionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 16,
    gap: 12,
  },
  editBtn: {
    flex: 1,
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
