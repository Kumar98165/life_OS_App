import React, { useEffect, useState } from 'react';
import {
  View,
  StyleSheet,
  Modal,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { taskFormSchema, TaskFormValues } from '../../schemas/task';
import { Task, TaskPriority, TaskCategory } from '../../types/task';
import {
  GlassCard,
  GlassInput,
  PrimaryButton,
  SecondaryButton,
  Heading,
  BodyText,
  Caption,
} from '../../components';

export interface CreateEditTaskModalProps {
  visible: boolean;
  taskToEdit?: Task | null;
  categories: TaskCategory[];
  isLoading?: boolean;
  onClose: () => void;
  onSubmit: (values: TaskFormValues) => Promise<void>;
}

const PRIORITIES: { id: TaskPriority; label: string; colorKey: string }[] = [
  { id: 'low', label: 'Low', colorKey: 'textMuted' },
  { id: 'medium', label: 'Medium', colorKey: 'primary' },
  { id: 'high', label: 'High', colorKey: 'warning' },
  { id: 'urgent', label: 'Urgent', colorKey: 'error' },
];

export const CreateEditTaskModal: React.FC<CreateEditTaskModalProps> = ({
  visible,
  taskToEdit,
  categories,
  isLoading = false,
  onClose,
  onSubmit,
}) => {
  const { theme } = useTheme();
  const isEditing = !!taskToEdit;

  const {
    control,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<TaskFormValues>({
    resolver: zodResolver(taskFormSchema),
    defaultValues: {
      title: '',
      description: '',
      category_id: null,
      priority: 'medium',
      due_date: null,
      estimated_minutes: null,
    },
  });

  const selectedPriority = watch('priority');
  const selectedCategoryId = watch('category_id');
  const selectedDueDate = watch('due_date');

  useEffect(() => {
    if (taskToEdit) {
      reset({
        title: taskToEdit.title,
        description: taskToEdit.description || '',
        category_id: taskToEdit.category_id || null,
        priority: taskToEdit.priority,
        due_date: taskToEdit.due_date || null,
        estimated_minutes: taskToEdit.estimated_minutes || null,
      });
    } else {
      reset({
        title: '',
        description: '',
        category_id: null,
        priority: 'medium',
        due_date: null,
        estimated_minutes: null,
      });
    }
  }, [taskToEdit, reset, visible]);

  const setDueDateQuick = (type: 'today' | 'tomorrow' | 'next_week' | 'clear') => {
    if (type === 'clear') {
      setValue('due_date', null);
      return;
    }
    const d = new Date();
    if (type === 'tomorrow') {
      d.setDate(d.getDate() + 1);
    } else if (type === 'next_week') {
      d.setDate(d.getDate() + 7);
    }
    setValue('due_date', d.toISOString());
  };

  const handleFormSubmit = async (values: TaskFormValues) => {
    await onSubmit(values);
    onClose();
  };

  return (
    <Modal visible={visible} transparent animationType="slide">
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.modalOverlay}
      >
        <View style={styles.sheetContainer}>
          <GlassCard elevation="floating" style={styles.sheetCard}>
            <View style={styles.headerRow}>
              <Heading level={2}>{isEditing ? 'Edit Task' : 'New Task'}</Heading>
              <TouchableOpacity
                onPress={onClose}
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                accessibilityRole="button"
                accessibilityLabel="Close"
              >
                <Ionicons name="close-circle-outline" size={26} color={theme.colors.textMuted} />
              </TouchableOpacity>
            </View>

            <ScrollView showsVerticalScrollIndicator={false} style={styles.formScroll}>
              {/* Title Field */}
              <Controller
                control={control}
                name="title"
                render={({ field: { onChange, onBlur, value } }) => (
                  <GlassInput
                    label="Task Title"
                    required
                    placeholder="e.g. Prepare system sprint deliverables"
                    value={value}
                    onChangeText={onChange}
                    onBlur={onBlur}
                    error={errors.title?.message}
                  />
                )}
              />

              {/* Description Field */}
              <Controller
                control={control}
                name="description"
                render={({ field: { onChange, onBlur, value } }) => (
                  <GlassInput
                    label="Description (Optional)"
                    placeholder="Add details, notes, or subtask links..."
                    multiline
                    numberOfLines={3}
                    style={{ minHeight: 70 }}
                    value={value || ''}
                    onChangeText={onChange}
                    onBlur={onBlur}
                  />
                )}
              />

              {/* Priority Selection */}
              <BodyText weight="600" style={styles.sectionLabel}>
                Priority Level
              </BodyText>
              <View style={styles.priorityRow}>
                {PRIORITIES.map((p) => {
                  const isSelected = selectedPriority === p.id;
                  const activeColor =
                    p.id === 'urgent'
                      ? theme.colors.error
                      : p.id === 'high'
                      ? theme.colors.warning
                      : p.id === 'medium'
                      ? theme.colors.primary
                      : theme.colors.textMuted;

                  return (
                    <TouchableOpacity
                      key={p.id}
                      onPress={() => setValue('priority', p.id)}
                      style={[
                        styles.priorityChip,
                        {
                          borderColor: isSelected ? activeColor : theme.colors.glassBorder,
                          backgroundColor: isSelected
                            ? `${activeColor}20`
                            : theme.colors.glassBackgroundSolid,
                        },
                      ]}
                      accessibilityRole="button"
                    >
                      <Caption
                        weight="600"
                        style={{
                          color: isSelected ? activeColor : theme.colors.textSecondary,
                        }}
                      >
                        {p.label}
                      </Caption>
                    </TouchableOpacity>
                  );
                })}
              </View>

              {/* Categories Selection */}
              {categories.length > 0 && (
                <>
                  <BodyText weight="600" style={styles.sectionLabel}>
                    Category
                  </BodyText>
                  <ScrollView
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    contentContainerStyle={styles.categoryRow}
                  >
                    <TouchableOpacity
                      onPress={() => setValue('category_id', null)}
                      style={[
                        styles.categoryChip,
                        {
                          borderColor: !selectedCategoryId
                            ? theme.colors.primary
                            : theme.colors.glassBorder,
                          backgroundColor: !selectedCategoryId
                            ? `${theme.colors.primary}18`
                            : theme.colors.glassBackgroundSolid,
                        },
                      ]}
                    >
                      <Caption weight="600" style={{ color: !selectedCategoryId ? theme.colors.primary : theme.colors.textSecondary }}>
                        None
                      </Caption>
                    </TouchableOpacity>
                    {categories.map((cat) => {
                      const isSelected = selectedCategoryId === cat.id;
                      return (
                        <TouchableOpacity
                          key={cat.id}
                          onPress={() => setValue('category_id', cat.id)}
                          style={[
                            styles.categoryChip,
                            {
                              borderColor: isSelected ? cat.color_hex : theme.colors.glassBorder,
                              backgroundColor: isSelected
                                ? `${cat.color_hex}22`
                                : theme.colors.glassBackgroundSolid,
                            },
                          ]}
                        >
                          <Caption weight="600" style={{ color: isSelected ? cat.color_hex : theme.colors.textSecondary }}>
                            {cat.name}
                          </Caption>
                        </TouchableOpacity>
                      );
                    })}
                  </ScrollView>
                </>
              )}

              {/* Due Date Quick Buttons */}
              <BodyText weight="600" style={styles.sectionLabel}>
                Due Schedule {selectedDueDate ? `(${new Date(selectedDueDate).toLocaleDateString()})` : ''}
              </BodyText>
              <View style={styles.dueRow}>
                {(['today', 'tomorrow', 'next_week', 'clear'] as const).map((opt) => (
                  <TouchableOpacity
                    key={opt}
                    onPress={() => setDueDateQuick(opt)}
                    style={[
                      styles.dueChip,
                      {
                        backgroundColor: theme.colors.glassBackgroundSolid,
                        borderColor: theme.colors.glassBorder,
                      },
                    ]}
                  >
                    <Caption
                      weight="600"
                      style={{
                        color: opt === 'clear' ? theme.colors.error : theme.colors.primary,
                        textTransform: 'capitalize',
                      }}
                    >
                      {opt.replace('_', ' ')}
                    </Caption>
                  </TouchableOpacity>
                ))}
              </View>

              {/* Action Buttons */}
              <View style={styles.actionsRow}>
                <SecondaryButton
                  label="Cancel"
                  onPress={onClose}
                  style={{ flex: 1 }}
                  fullWidth={false}
                />
                <PrimaryButton
                  label={isEditing ? 'Save Changes' : 'Create Task'}
                  loading={isLoading}
                  onPress={() => {
                    handleSubmit((values) => handleFormSubmit(values))();
                  }}
                  style={{ flex: 2 }}
                  fullWidth={false}
                />
              </View>
            </ScrollView>
          </GlassCard>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.45)',
    justifyContent: 'flex-end',
  },
  sheetContainer: {
    maxHeight: '90%',
  },
  sheetCard: {
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 34,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  formScroll: {
    maxHeight: 520,
  },
  sectionLabel: {
    marginTop: 14,
    marginBottom: 8,
    fontSize: 13,
  },
  priorityRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 4,
  },
  priorityChip: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  categoryRow: {
    gap: 8,
    paddingVertical: 2,
    marginBottom: 4,
  },
  categoryChip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 12,
    borderWidth: 1,
  },
  dueRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 24,
  },
  dueChip: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 10,
    borderWidth: 1,
    alignItems: 'center',
  },
  actionsRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 8,
    marginBottom: 12,
  },
});
