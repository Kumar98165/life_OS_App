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
  useTasks,
  useTaskCategories,
  useCreateTask,
  useUpdateTask,
  useToggleCompleteTask,
  useDeleteTask,
} from '../../hooks/useTasks';
import { Task, TaskPriority, TaskStatus } from '../../types/task';
import { TaskFormValues } from '../../schemas/task';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  SearchInput,
  PrimaryButton,
  Heading,
  BodyText,
  Caption,
  SkeletonLoader,
  EmptyState,
  ErrorState,
  Toast,
  CreateEditTaskModal,
  TaskDetailsModal,
} from '../../components';

const STATUS_FILTERS: { id: string; label: string }[] = [
  { id: '', label: 'All' },
  { id: 'pending', label: 'Pending' },
  { id: 'in_progress', label: 'In Progress' },
  { id: 'completed', label: 'Completed' },
];

const PRIORITY_FILTERS: { id: string; label: string }[] = [
  { id: '', label: 'All Priorities' },
  { id: 'urgent', label: 'Urgent' },
  { id: 'high', label: 'High' },
  { id: 'medium', label: 'Medium' },
  { id: 'low', label: 'Low' },
];

export const TasksScreen: React.FC = () => {
  const { theme } = useTheme();

  // Filters state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [selectedPriority, setSelectedPriority] = useState<string>('');

  // Modals state
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [taskToEdit, setTaskToEdit] = useState<Task | null>(null);
  const [selectedTaskDetails, setSelectedTaskDetails] = useState<Task | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Queries & Mutations
  const filterParams = useMemo(
    () => ({
      search: searchQuery.trim() || undefined,
      status: selectedStatus || undefined,
      priority: selectedPriority || undefined,
      per_page: 50,
    }),
    [searchQuery, selectedStatus, selectedPriority]
  );

  const { data, isLoading, isError, refetch, isRefetching } = useTasks(filterParams);
  const { data: categories = [] } = useTaskCategories();

  const createTaskMutation = useCreateTask();
  const updateTaskMutation = useUpdateTask();
  const toggleCompleteMutation = useToggleCompleteTask();
  const deleteTaskMutation = useDeleteTask();

  const tasks = data?.tasks || [];
  const totalTasksCount = data?.meta?.total || 0;

  const handleCreateOrUpdateTask = async (values: TaskFormValues) => {
    try {
      if (taskToEdit) {
        await updateTaskMutation.mutateAsync({
          id: taskToEdit.id,
          payload: {
            title: values.title,
            description: values.description,
            category_id: values.category_id,
            priority: values.priority,
            due_date: values.due_date,
            estimated_minutes: values.estimated_minutes,
          },
        });
        setToastMessage('Task updated successfully');
      } else {
        await createTaskMutation.mutateAsync({
          title: values.title,
          description: values.description,
          category_id: values.category_id,
          priority: values.priority,
          due_date: values.due_date,
          estimated_minutes: values.estimated_minutes,
        });
        setToastMessage('Task created successfully');
      }
      setTimeout(() => setToastMessage(null), 3000);
      setTaskToEdit(null);
    } catch (err: any) {
      setToastMessage(err.message || 'Operation failed');
      setTimeout(() => setToastMessage(null), 4000);
    }
  };

  const handleToggleTask = async (task: Task) => {
    try {
      await toggleCompleteMutation.mutateAsync(task.id);
      // If modal is open, update selectedTaskDetails state
      if (selectedTaskDetails?.id === task.id) {
        setSelectedTaskDetails((prev) =>
          prev
            ? {
              ...prev,
              status: prev.status === 'completed' ? 'pending' : 'completed',
              completed_at: prev.status === 'completed' ? null : new Date().toISOString(),
            }
            : null
        );
      }
    } catch (err: any) {
      setToastMessage(err.message || 'Failed to update task state');
      setTimeout(() => setToastMessage(null), 3000);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await deleteTaskMutation.mutateAsync(taskId);
      setToastMessage('Task deleted');
      setTimeout(() => setToastMessage(null), 3000);
    } catch (err: any) {
      setToastMessage(err.message || 'Failed to delete task');
      setTimeout(() => setToastMessage(null), 3000);
    }
  };

  return (
    <SafeAreaContainer edges={['top']}>
      <ScrollContainer
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={() => {
              refetch();
            }}
            tintColor={theme.colors.primary}
            colors={[theme.colors.primary]}
          />
        }
      >
        {/* Top Header */}
        <View style={styles.topHeader}>
          <View>
            <Caption color="secondary" style={styles.kicker}>
              ORGANIZATION ENGINE
            </Caption>
            <View style={styles.titleRow}>
              <Heading level={1}>Tasks</Heading>
              <View
                style={[
                  styles.countPill,
                  { backgroundColor: `${theme.colors.primary}18` },
                ]}
              >
                <Caption weight="700" style={{ color: theme.colors.primary }}>
                  {totalTasksCount}
                </Caption>
              </View>
            </View>
          </View>

          <PrimaryButton
            label="+ New Task"
            onPress={() => {
              setTaskToEdit(null);
              setIsCreateModalOpen(true);
            }}
            fullWidth={false}
            style={styles.newBtn}
          />
        </View>

        {/* Search Bar */}
        <SearchInput
          value={searchQuery}
          onChangeText={setSearchQuery}
          onClear={() => setSearchQuery('')}
          placeholder="Search tasks..."
          style={styles.searchInput}
        />

        {/* Status Filter Chips */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.filterChipsRow}
        >
          {STATUS_FILTERS.map((f) => {
            const isSelected = selectedStatus === f.id;
            return (
              <TouchableOpacity
                key={f.id}
                onPress={() => setSelectedStatus(f.id)}
                style={[
                  styles.filterChip,
                  {
                    backgroundColor: isSelected
                      ? theme.colors.primary
                      : theme.colors.glassBackgroundSolid,
                    borderColor: isSelected
                      ? theme.colors.primary
                      : theme.colors.glassBorder,
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

        {/* Priority Filter Chips */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={[styles.filterChipsRow, { marginBottom: 18 }]}
        >
          {PRIORITY_FILTERS.map((p) => {
            const isSelected = selectedPriority === p.id;
            return (
              <TouchableOpacity
                key={p.id}
                onPress={() => setSelectedPriority(p.id)}
                style={[
                  styles.filterChip,
                  styles.priorityFilterChip,
                  {
                    backgroundColor: isSelected
                      ? `${theme.colors.primary}22`
                      : theme.colors.glassBackgroundSolid,
                    borderColor: isSelected
                      ? theme.colors.primary
                      : theme.colors.glassBorder,
                  },
                ]}
              >
                <Caption
                  weight={isSelected ? '700' : '500'}
                  style={{
                    color: isSelected ? theme.colors.primary : theme.colors.textMuted,
                    fontSize: 11,
                  }}
                >
                  {p.label}
                </Caption>
              </TouchableOpacity>
            );
          })}
        </ScrollView>

        {/* Task List */}
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <SkeletonLoader height={72} borderRadius={14} style={{ marginBottom: 12 }} />
            <SkeletonLoader height={72} borderRadius={14} style={{ marginBottom: 12 }} />
            <SkeletonLoader height={72} borderRadius={14} style={{ marginBottom: 12 }} />
          </View>
        ) : isError ? (
          <ErrorState
            title="Failed to load tasks"
            message="Unable to communicate with LifeOS server. Check your connection and retry."
            onRetry={refetch}
          />
        ) : tasks.length === 0 ? (
          <GlassCard elevation="subtle" style={styles.emptyCard}>
            <EmptyState
              icon="checkbox-outline"
              title={searchQuery ? 'No matching tasks' : 'No tasks created yet'}
              description={
                searchQuery
                  ? `No tasks match "${searchQuery}". Clear your search or create a new task.`
                  : 'Start capturing your daily priorities, deep work blocks, and deliverables.'
              }
              actionLabel="+ Create First Task"
              onActionPress={() => {
                setTaskToEdit(null);
                setIsCreateModalOpen(true);
              }}
            />
          </GlassCard>
        ) : (
          <View style={styles.tasksList}>
            {tasks.map((task) => {
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
                  onPress={() => setSelectedTaskDetails(task)}
                  activeOpacity={0.8}
                  style={[
                    styles.taskCard,
                    {
                      backgroundColor: theme.colors.glassBackgroundSolid,
                      borderColor: theme.colors.glassBorder,
                    },
                    theme.shadows.subtle,
                  ]}
                  accessibilityRole="button"
                  accessibilityLabel={`${task.title}, priority ${task.priority}`}
                >
                  {/* Left Priority Strip */}
                  <View
                    style={[
                      styles.priorityStrip,
                      { backgroundColor: priorityColor },
                    ]}
                  />

                  {/* Complete/Uncomplete Checkbox button */}
                  <TouchableOpacity
                    onPress={() => handleToggleTask(task)}
                    hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
                    style={styles.checkSlot}
                    accessibilityRole="checkbox"
                    accessibilityState={{ checked: isCompleted }}
                  >
                    <Ionicons
                      name={isCompleted ? 'checkmark-circle' : 'ellipse-outline'}
                      size={24}
                      color={isCompleted ? theme.colors.success : theme.colors.textMuted}
                    />
                  </TouchableOpacity>

                  {/* Task details */}
                  <View style={styles.taskContent}>
                    <BodyText
                      weight="600"
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

                    <View style={styles.taskMetaRow}>
                      {task.category && (
                        <View
                          style={[
                            styles.categoryTag,
                            { backgroundColor: `${task.category.color_hex}18` },
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

                      {task.due_date ? (
                        <View style={styles.dueDateRow}>
                          <Ionicons
                            name="calendar-outline"
                            size={12}
                            color={theme.colors.textMuted}
                          />
                          <Caption color="secondary" style={styles.dueText}>
                            {new Date(task.due_date).toLocaleDateString([], {
                              month: 'short',
                              day: 'numeric',
                            })}
                          </Caption>
                        </View>
                      ) : null}
                    </View>
                  </View>

                  {/* Chevron Right */}
                  <Ionicons
                    name="chevron-forward"
                    size={18}
                    color={theme.colors.textMuted}
                    style={styles.chevron}
                  />
                </TouchableOpacity>
              );
            })}
          </View>
        )}
      </ScrollContainer>

      {/* Create / Edit Modal */}
      <CreateEditTaskModal
        visible={isCreateModalOpen || !!taskToEdit}
        taskToEdit={taskToEdit}
        categories={categories}
        isLoading={createTaskMutation.isPending || updateTaskMutation.isPending}
        onClose={() => {
          setIsCreateModalOpen(false);
          setTaskToEdit(null);
        }}
        onSubmit={handleCreateOrUpdateTask}
      />

      {/* Task Details Modal */}
      <TaskDetailsModal
        visible={!!selectedTaskDetails}
        task={selectedTaskDetails}
        onClose={() => setSelectedTaskDetails(null)}
        onEdit={(task) => {
          setTaskToEdit(task);
        }}
        onToggleComplete={handleToggleTask}
        onDelete={handleDeleteTask}
      />

      {/* Notification Toast */}
      <Toast visible={!!toastMessage} message={toastMessage || ''} type="success" />
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  scrollContent: {
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 110,
  },
  topHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  kicker: {
    letterSpacing: 0.8,
    fontWeight: '600',
    marginBottom: 2,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  countPill: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  newBtn: {
    paddingHorizontal: 16,
  },
  searchInput: {
    marginBottom: 12,
  },
  filterChipsRow: {
    gap: 8,
    marginBottom: 8,
  },
  filterChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 12,
    borderWidth: 1,
  },
  priorityFilterChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 10,
  },
  loadingContainer: {
    paddingTop: 8,
  },
  emptyCard: {
    padding: 16,
    marginTop: 10,
  },
  tasksList: {
    gap: 10,
  },
  taskCard: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 16,
    borderWidth: 1,
    overflow: 'hidden',
    paddingVertical: 14,
    paddingRight: 14,
  },
  priorityStrip: {
    width: 5,
    alignSelf: 'stretch',
    marginRight: 10,
  },
  checkSlot: {
    paddingHorizontal: 6,
  },
  taskContent: {
    flex: 1,
    paddingRight: 8,
  },
  taskTitle: {
    fontSize: 15,
    marginBottom: 4,
  },
  taskMetaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  categoryTag: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  dueDateRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dueText: {
    marginLeft: 4,
    fontSize: 11,
  },
  chevron: {
    marginLeft: 4,
  },
});
