import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { GlassCard } from '../glass/GlassCard';
import { SectionHeader } from '../layout/SectionHeader';
import { BodyText, Caption } from '../common/Typography';
import { SkeletonLoader, EmptyState, ErrorState } from '../feedback/FeedbackComponents';
import { Task } from '../../types';

export interface TodayTasksSectionProps {
  tasks: Task[];
  isLoading?: boolean;
  isError?: boolean;
  onRetry?: () => void;
  onViewAll?: () => void;
  onTaskPress?: (task: Task) => void;
  onAddTask?: () => void;
}

export const TodayTasksSection: React.FC<TodayTasksSectionProps> = ({
  tasks,
  isLoading = false,
  isError = false,
  onRetry,
  onViewAll,
  onTaskPress,
  onAddTask,
}) => {
  const { theme } = useTheme();

  return (
    <View style={styles.container}>
      <SectionHeader
        title="Today's Tasks"
        actionText={tasks.length > 0 ? 'View All' : undefined}
        onActionPress={onViewAll}
      />

      {isLoading ? (
        <View style={styles.skeletonContainer}>
          <SkeletonLoader height={64} borderRadius={12} style={{ marginBottom: 10 }} />
          <SkeletonLoader height={64} borderRadius={12} style={{ marginBottom: 10 }} />
        </View>
      ) : isError ? (
        <ErrorState
          title="Could not load tasks"
          message="Unable to retrieve today's tasks from server."
          onRetry={onRetry}
        />
      ) : tasks.length === 0 ? (
        <GlassCard elevation="subtle" style={styles.emptyCard}>
          <EmptyState
            icon="checkbox-outline"
            title="No tasks scheduled for today"
            description="Take time to plan your day or add your first task to start organizing your priorities."
            actionLabel="Add Task"
            onActionPress={onAddTask}
          />
        </GlassCard>
      ) : (
        <View style={styles.taskList}>
          {tasks.slice(0, 4).map((task) => {
            const isCompleted = task.status === 'completed';
            const priorityColor =
              task.priority === 'urgent'
                ? theme.colors.error
                : task.priority === 'high'
                ? theme.colors.warning
                : task.priority === 'medium'
                ? theme.colors.primary
                : theme.colors.textMuted;

            return (
              <TouchableOpacity
                key={task.id}
                onPress={() => onTaskPress?.(task)}
                activeOpacity={0.8}
                style={[
                  styles.taskItem,
                  {
                    backgroundColor: theme.colors.glassBackgroundSolid,
                    borderColor: theme.colors.glassBorder,
                  },
                  theme.shadows.subtle,
                ]}
                accessibilityRole="button"
                accessibilityLabel={`${task.title}, priority ${task.priority}`}
              >
                <View style={styles.taskLeft}>
                  <Ionicons
                    name={isCompleted ? 'checkmark-circle' : 'ellipse-outline'}
                    size={22}
                    color={isCompleted ? theme.colors.success : theme.colors.textMuted}
                  />
                  <View style={styles.taskTitleCol}>
                    <BodyText
                      weight="500"
                      style={[
                        styles.taskTitle,
                        isCompleted && {
                          textDecorationLine: 'line-through',
                          color: theme.colors.textMuted,
                        },
                      ]}
                    >
                      {task.title}
                    </BodyText>
                    {task.due_date ? (
                      <Caption color="secondary">
                        Due {new Date(task.due_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </Caption>
                    ) : null}
                  </View>
                </View>

                {/* Priority Badge */}
                <View
                  style={[
                    styles.priorityBadge,
                    { backgroundColor: `${priorityColor}15` },
                  ]}
                >
                  <Caption
                    weight="600"
                    style={{ color: priorityColor, fontSize: 10, textTransform: 'uppercase' }}
                  >
                    {task.priority}
                  </Caption>
                </View>
              </TouchableOpacity>
            );
          })}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 24,
  },
  skeletonContainer: {
    paddingVertical: 4,
  },
  emptyCard: {
    padding: 16,
  },
  taskList: {
    gap: 10,
  },
  taskItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
  },
  taskLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    paddingRight: 10,
  },
  taskTitleCol: {
    marginLeft: 12,
    flex: 1,
  },
  taskTitle: {
    fontSize: 14,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 8,
  },
});
