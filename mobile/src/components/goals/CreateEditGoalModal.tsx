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
import { goalFormSchema, GoalFormData } from '../../schemas/goal';
import { Goal, GoalPriority, GoalStatus } from '../../types/goal';
import {
  GlassCard,
  GlassInput,
  PrimaryButton,
  SecondaryButton,
  Heading,
  BodyText,
  Caption,
} from '../../components';

export interface CreateEditGoalModalProps {
  visible: boolean;
  goalToEdit?: Goal | null;
  isLoading?: boolean;
  onClose: () => void;
  onSubmit: (values: GoalFormData) => Promise<void>;
}

const PRIORITIES: { id: GoalPriority; label: string; colorKey: string }[] = [
  { id: 'low', label: 'Low', colorKey: 'textSecondary' },
  { id: 'medium', label: 'Medium', colorKey: 'primary' },
  { id: 'high', label: 'High', colorKey: 'warning' },
];

const STATUSES: { id: GoalStatus; label: string }[] = [
  { id: 'in_progress', label: 'In Progress' },
  { id: 'not_started', label: 'Not Started' },
  { id: 'paused', label: 'Paused' },
  { id: 'completed', label: 'Completed' },
  { id: 'cancelled', label: 'Cancelled' },
];

const PRESET_CATEGORIES = ['Career', 'Health', 'Finance', 'Learning', 'Personal', 'Projects'];

export const CreateEditGoalModal: React.FC<CreateEditGoalModalProps> = ({
  visible,
  goalToEdit,
  isLoading = false,
  onClose,
  onSubmit,
}) => {
  const { theme } = useTheme();
  const isEditing = !!goalToEdit;
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    control,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<GoalFormData>({
    resolver: zodResolver(goalFormSchema),
    defaultValues: {
      title: '',
      description: '',
      priority: 'medium',
      status: 'in_progress',
      target_date: '',
      category: 'Career',
    },
  });

  const selectedPriority = watch('priority');
  const selectedStatus = watch('status');
  const selectedCategory = watch('category');

  useEffect(() => {
    setSubmitError(null);
    if (goalToEdit) {
      let dateStr = '';
      if (goalToEdit.target_date) {
        const d = new Date(goalToEdit.target_date);
        dateStr = d.toISOString().split('T')[0];
      }
      reset({
        title: goalToEdit.title,
        description: goalToEdit.description || '',
        priority: goalToEdit.priority || 'medium',
        status: goalToEdit.status || 'in_progress',
        target_date: dateStr,
        category: goalToEdit.category || 'Career',
      });
    } else {
      reset({
        title: '',
        description: '',
        priority: 'medium',
        status: 'in_progress',
        target_date: '',
        category: 'Career',
      });
    }
  }, [goalToEdit, reset, visible]);

  const handleFormSubmit = async (data: GoalFormData) => {
    setSubmitError(null);
    try {
      await onSubmit(data);
      onClose();
    } catch (err: any) {
      setSubmitError(err?.message || 'Failed to save goal');
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent
      onRequestClose={onClose}
    >
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.modalBackdrop}
      >
        <View style={styles.sheetContainer}>
          <GlassCard style={styles.modalCard}>
            <View style={styles.headerRow}>
              <View>
                <Heading level={3}>{isEditing ? 'Edit Goal' : 'Create New Goal'}</Heading>
                <Caption color="secondary">Define a measurable long-term vision</Caption>
              </View>
              <TouchableOpacity
                onPress={onClose}
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                style={styles.closeButton}
              >
                <Ionicons name="close" size={24} color={theme.colors.textSecondary} />
              </TouchableOpacity>
            </View>

            {submitError && (
              <View style={[styles.errorBanner, { backgroundColor: theme.colors.error + '18' }]}>
                <Ionicons name="alert-circle-outline" size={18} color={theme.colors.error} />
                <BodyText style={[styles.errorBannerText, { color: theme.colors.error }]}>
                  {submitError}
                </BodyText>
              </View>
            )}

            <ScrollView
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.scrollContent}
              keyboardShouldPersistTaps="handled"
            >
              {/* Title Field */}
              <Controller
                control={control}
                name="title"
                render={({ field: { onChange, onBlur, value } }) => (
                  <GlassInput
                    label="Goal Title *"
                    placeholder="e.g. Become a Principal Cloud Architect"
                    value={value}
                    onChangeText={onChange}
                    onBlur={onBlur}
                    error={errors.title?.message}
                  />
                )}
              />

              {/* Target Date */}
              <Controller
                control={control}
                name="target_date"
                render={({ field: { onChange, onBlur, value } }) => (
                  <GlassInput
                    label="Target Date (YYYY-MM-DD)"
                    placeholder="2026-12-31"
                    value={value || ''}
                    onChangeText={onChange}
                    onBlur={onBlur}
                    error={errors.target_date?.message}
                  />
                )}
              />

              {/* Priority Selector */}
              <View style={styles.sectionContainer}>
                <Caption style={styles.sectionLabel}>PRIORITY</Caption>
                <View style={styles.pillsRow}>
                  {PRIORITIES.map((p) => {
                    const isSelected = selectedPriority === p.id;
                    return (
                      <TouchableOpacity
                        key={p.id}
                        onPress={() => setValue('priority', p.id)}
                        style={[
                          styles.priorityPill,
                          {
                            backgroundColor: isSelected
                              ? theme.colors.primary + '18'
                              : theme.colors.glassBackground,
                            borderColor: isSelected ? theme.colors.primary : theme.colors.border,
                          },
                        ]}
                      >
                        <BodyText
                          style={[
                            styles.pillText,
                            {
                              color: isSelected ? theme.colors.primary : theme.colors.textPrimary,
                              fontWeight: isSelected ? '600' : '400',
                            },
                          ]}
                        >
                          {p.label}
                        </BodyText>
                      </TouchableOpacity>
                    );
                  })}
                </View>
              </View>

              {/* Status Selector (when editing) */}
              {isEditing && (
                <View style={styles.sectionContainer}>
                  <Caption style={styles.sectionLabel}>STATUS</Caption>
                  <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                    {STATUSES.map((st) => {
                      const isSelected = selectedStatus === st.id;
                      return (
                        <TouchableOpacity
                          key={st.id}
                          onPress={() => setValue('status', st.id)}
                          style={[
                            styles.statusPill,
                            {
                              backgroundColor: isSelected
                                ? theme.colors.primary + '18'
                                : theme.colors.glassBackground,
                              borderColor: isSelected ? theme.colors.primary : theme.colors.border,
                            },
                          ]}
                        >
                          <BodyText
                            style={[
                              styles.pillText,
                              {
                                color: isSelected ? theme.colors.primary : theme.colors.textPrimary,
                                fontWeight: isSelected ? '600' : '400',
                              },
                            ]}
                          >
                            {st.label}
                          </BodyText>
                        </TouchableOpacity>
                      );
                    })}
                  </ScrollView>
                </View>
              )}

              {/* Category Pills */}
              <View style={styles.sectionContainer}>
                <Caption style={styles.sectionLabel}>CATEGORY</Caption>
                <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                  {PRESET_CATEGORIES.map((cat) => {
                    const isSelected = selectedCategory === cat;
                    return (
                      <TouchableOpacity
                        key={cat}
                        onPress={() => setValue('category', cat)}
                        style={[
                          styles.categoryPill,
                          {
                            backgroundColor: isSelected
                              ? theme.colors.primary + '18'
                              : theme.colors.glassBackground,
                            borderColor: isSelected ? theme.colors.primary : theme.colors.border,
                          },
                        ]}
                      >
                        <BodyText
                          style={[
                            styles.pillText,
                            {
                              color: isSelected ? theme.colors.primary : theme.colors.textPrimary,
                              fontWeight: isSelected ? '600' : '400',
                            },
                          ]}
                        >
                          {cat}
                        </BodyText>
                      </TouchableOpacity>
                    );
                  })}
                </ScrollView>
              </View>

              {/* Description */}
              <Controller
                control={control}
                name="description"
                render={({ field: { onChange, onBlur, value } }) => (
                  <GlassInput
                    label="Description & Success Metrics"
                    placeholder="Why this goal matters and what defines success..."
                    value={value || ''}
                    onChangeText={onChange}
                    onBlur={onBlur}
                    multiline
                    numberOfLines={4}
                    error={errors.description?.message}
                  />
                )}
              />

              {/* Action Buttons */}
              <View style={styles.buttonRow}>
                <SecondaryButton
                  label="Cancel"
                  onPress={onClose}
                  style={styles.cancelButton}
                  disabled={isLoading}
                />
                <PrimaryButton
                  label={isEditing ? 'Save Changes' : 'Create Goal'}
                  onPress={() => handleSubmit(handleFormSubmit)()}
                  loading={isLoading}
                  style={styles.submitButton}
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
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 15, 25, 0.5)',
    justifyContent: 'flex-end',
  },
  sheetContainer: {
    maxHeight: '90%',
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
  closeButton: {
    padding: 6,
  },
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 12,
    marginBottom: 12,
    gap: 8,
  },
  errorBannerText: {
    flex: 1,
    fontSize: 13,
  },
  scrollContent: {
    paddingBottom: 20,
  },
  sectionContainer: {
    marginVertical: 10,
  },
  sectionLabel: {
    marginBottom: 8,
    fontWeight: '600',
    letterSpacing: 0.8,
  },
  pillsRow: {
    flexDirection: 'row',
    gap: 10,
  },
  priorityPill: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 14,
    borderWidth: 1,
    alignItems: 'center',
  },
  statusPill: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 14,
    borderWidth: 1,
    marginRight: 8,
  },
  categoryPill: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 14,
    borderWidth: 1,
    marginRight: 8,
  },
  pillText: {
    fontSize: 13,
  },
  buttonRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 16,
    gap: 12,
  },
  cancelButton: {
    flex: 1,
  },
  submitButton: {
    flex: 2,
  },
});

