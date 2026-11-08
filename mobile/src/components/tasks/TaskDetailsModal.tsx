import React, { useState } from 'react';
import { View, StyleSheet, Modal, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { Task } from '../../types/task';
import {
  GlassCard,
  Heading,
  BodyText,
  Caption,
  PrimaryButton,
  SecondaryButton,
  ConfirmationModal,
} from '../../components';

export interface TaskDetailsModalProps {
  visible: boolean;
  task: Task | null;
  onClose: () => void;
  onEdit: (task: Task) => void;
  onToggleComplete: (task: Task) => Promise<void>;
  onDelete: (taskId: string) => Promise<void>;
}

export const TaskDetailsModal: React.FC<TaskDetailsModalProps> = ({
  visible,
  task,
  onClose,
  onEdit,
  onToggleComplete,
  onDelete,
}) => {
  const { theme } = useTheme();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  if (!task) return null;

  const isCompleted = task.status === 'completed';

  const priorityColor =
    task.priority === 'urgent'
      ? theme.colors.error
      : task.priority === 'high'
      ? theme.colors.warning
      : task.priority === 'medium'
      ? theme.colors.primary
      : theme.colors.textMuted;

  const handleToggle = async () => {
    setIsToggling(true);
    try {
      await onToggleComplete(task);
    } finally {
      setIsToggling(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(task.id);
      setShowDeleteConfirm(false);
      onClose();
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={styles.overlay}>
        <GlassCard elevation="floating" style={styles.card}>
          {/* Header */}
          <View style={styles.topRow}>
            <View style={styles.badgesRow}>
              {/* Status Badge */}
              <View
                style={[
                  styles.badge,
                  {
                    backgroundColor: isCompleted
                      ? `${theme.colors.success}20`
                      : `${theme.colors.primary}20`,
                  },
                ]}
              >
                <Caption
                  weight="600"
                  style={{
                    color: isCompleted ? theme.colors.success : theme.colors.primary,
                    textTransform: 'uppercase',
                    fontSize: 10,
                  }}
                >
                  {task.status}
                </Caption>
              </View>

              {/* Priority Badge */}
              <View
                style={[
                  styles.badge,
                  { backgroundColor: `${priorityColor}20` },
                ]}
              >
                <Caption
                  weight="600"
                  style={{ color: priorityColor, textTransform: 'uppercase', fontSize: 10 }}
                >
                  {task.priority}
                </Caption>
              </View>

              {/* Category Badge */}
              {task.category && (
                <View
                  style={[
                    styles.badge,
                    { backgroundColor: `${task.category.color_hex}22` },
                  ]}
                >
                  <Caption
                    weight="600"
                    style={{ color: task.category.color_hex, fontSize: 10 }}
                  >
                    {task.category.name}
                  </Caption>
                </View>
              )}
            </View>

            <TouchableOpacity onPress={onClose} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
              <Ionicons name="close" size={24} color={theme.colors.textMuted} />
            </TouchableOpacity>
          </View>

          {/* Title */}
          <Heading level={2} style={styles.title}>
            {task.title}
          </Heading>

          {/* Description */}
          {task.description ? (
            <ScrollView style={styles.descScroll}>
              <BodyText color="secondary" style={styles.description}>
                {task.description}
              </BodyText>
            </ScrollView>
          ) : (
            <Caption color="muted" style={styles.noDesc}>
              No additional notes or description provided.
            </Caption>
          )}

          {/* Dates metadata */}
          <View style={styles.metaContainer}>
            {task.due_date && (
              <View style={styles.metaRow}>
                <Ionicons name="calendar-outline" size={16} color={theme.colors.primary} />
                <BodyText variant="small" style={styles.metaLabel}>
                  Due Date:
                </BodyText>
                <BodyText variant="small" weight="600">
                  {new Date(task.due_date).toLocaleDateString()}
                </BodyText>
              </View>
            )}

            {task.completed_at && (
              <View style={styles.metaRow}>
                <Ionicons name="checkmark-done" size={16} color={theme.colors.success} />
                <BodyText variant="small" style={styles.metaLabel}>
                  Completed:
                </BodyText>
                <BodyText variant="small" weight="600">
                  {new Date(task.completed_at).toLocaleDateString()}
                </BodyText>
              </View>
            )}

            <View style={styles.metaRow}>
              <Ionicons name="time-outline" size={16} color={theme.colors.textMuted} />
              <BodyText variant="small" style={styles.metaLabel}>
                Created:
              </BodyText>
              <Caption color="secondary">
                {new Date(task.created_at).toLocaleDateString()}
              </Caption>
            </View>
          </View>

          {/* Actions */}
          <View style={styles.actionsContainer}>
            <PrimaryButton
              label={isCompleted ? 'Reopen Task' : 'Mark as Completed'}
              loading={isToggling}
              icon={
                <Ionicons
                  name={isCompleted ? 'arrow-undo-outline' : 'checkmark-circle-outline'}
                  size={18}
                  color="#FFFFFF"
                />
              }
              onPress={handleToggle}
              style={{ marginBottom: 10 }}
            />

            <View style={styles.secondaryActions}>
              <SecondaryButton
                label="Edit Task"
                icon={<Ionicons name="pencil-outline" size={16} color={theme.colors.textPrimary} />}
                onPress={() => {
                  onClose();
                  onEdit(task);
                }}
                style={{ flex: 1 }}
                fullWidth={false}
              />
              <SecondaryButton
                label="Delete"
                icon={<Ionicons name="trash-outline" size={16} color={theme.colors.error} />}
                onPress={() => setShowDeleteConfirm(true)}
                style={{ flex: 1 }}
                fullWidth={false}
              />
            </View>
          </View>
        </GlassCard>
      </View>

      {/* Delete Confirmation */}
      <ConfirmationModal
        visible={showDeleteConfirm}
        title="Delete Task"
        message={`Are you sure you want to permanently delete "${task.title}"? This action cannot be undone.`}
        confirmLabel={isDeleting ? 'Deleting...' : 'Delete Task'}
        cancelLabel="Keep Task"
        isDestructive
        onConfirm={handleDelete}
        onCancel={() => setShowDeleteConfirm(false)}
      />
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.45)',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  card: {
    padding: 22,
    maxHeight: '82%',
  },
  topRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  badgesRow: {
    flexDirection: 'row',
    gap: 6,
    flexWrap: 'wrap',
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 8,
  },
  title: {
    fontSize: 20,
    marginBottom: 10,
  },
  descScroll: {
    maxHeight: 140,
    marginBottom: 14,
  },
  description: {
    lineHeight: 22,
  },
  noDesc: {
    fontStyle: 'italic',
    marginBottom: 14,
  },
  metaContainer: {
    gap: 8,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.06)',
    marginBottom: 18,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metaLabel: {
    marginLeft: 8,
    marginRight: 6,
    color: '#85859A',
  },
  actionsContainer: {},
  secondaryActions: {
    flexDirection: 'row',
    gap: 10,
  },
});
