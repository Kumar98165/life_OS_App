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
import { plannerBlockFormSchema, PlannerBlockFormData } from '../../schemas/planner';
import { PlannerBlock, PlannerBlockType, PlannerBlockStatus } from '../../types/planner';
import { Task } from '../../types/task';
import {
  GlassCard,
  GlassInput,
  PrimaryButton,
  SecondaryButton,
  Heading,
  BodyText,
  Caption,
} from '../../components';

export interface CreateEditPlannerBlockModalProps {
  visible: boolean;
  blockToEdit?: PlannerBlock | null;
  initialDate?: string;
  initialStartTime?: string;
  tasks?: Task[];
  isLoading?: boolean;
  onClose: () => void;
  onSubmit: (values: PlannerBlockFormData) => Promise<void>;
}

const BLOCK_TYPES: { id: PlannerBlockType; label: string; icon: keyof typeof Ionicons.glyphMap; color: string }[] = [
  { id: 'work', label: 'Work', icon: 'briefcase-outline', color: '#6C63FF' },
  { id: 'task', label: 'Task', icon: 'checkmark-circle-outline', color: '#22C55E' },
  { id: 'learning', label: 'Learning', icon: 'book-outline', color: '#3B82F6' },
  { id: 'meeting', label: 'Meeting', icon: 'people-outline', color: '#EC4899' },
  { id: 'focus', label: 'Focus', icon: 'flash-outline', color: '#8B5CF6' },
  { id: 'personal', label: 'Personal', icon: 'person-outline', color: '#F59E0B' },
  { id: 'break', label: 'Break', icon: 'cafe-outline', color: '#10B981' },
  { id: 'routine', label: 'Routine', icon: 'repeat-outline', color: '#64748B' },
  { id: 'other', label: 'Other', icon: 'ellipsis-horizontal-outline', color: '#94A3B8' },
];

const PRESET_COLORS = [
  '#6C63FF',
  '#22C55E',
  '#3B82F6',
  '#EC4899',
  '#8B5CF6',
  '#F59E0B',
  '#10B981',
  '#EF4444',
];

export const CreateEditPlannerBlockModal: React.FC<CreateEditPlannerBlockModalProps> = ({
  visible,
  blockToEdit,
  initialDate,
  initialStartTime,
  tasks = [],
  isLoading = false,
  onClose,
  onSubmit,
}) => {
  const { theme } = useTheme();
  const isEditing = !!blockToEdit;
  const [submitError, setSubmitError] = useState<string | null>(null);

  const getTodayDateStr = () => {
    const d = new Date();
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const {
    control,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<PlannerBlockFormData>({
    resolver: zodResolver(plannerBlockFormSchema),
    defaultValues: {
      title: '',
      description: '',
      block_type: 'work',
      status: 'scheduled',
      date: initialDate || getTodayDateStr(),
      start_time: initialStartTime || '09:00',
      end_time: '10:00',
      task_id: null,
      color_hex: '#6C63FF',
    },
  });

  const selectedType = watch('block_type');
  const selectedTaskId = watch('task_id');
  const selectedColor = watch('color_hex');

  useEffect(() => {
    setSubmitError(null);
    if (blockToEdit) {
      const startDt = new Date(blockToEdit.start_time);
      const endDt = new Date(blockToEdit.end_time);

      const year = startDt.getFullYear();
      const month = String(startDt.getMonth() + 1).padStart(2, '0');
      const day = String(startDt.getDate()).padStart(2, '0');

      const startH = String(startDt.getHours()).padStart(2, '0');
      const startM = String(startDt.getMinutes()).padStart(2, '0');
      const endH = String(endDt.getHours()).padStart(2, '0');
      const endM = String(endDt.getMinutes()).padStart(2, '0');

      reset({
        title: blockToEdit.title,
        description: blockToEdit.description || '',
        block_type: blockToEdit.block_type,
        status: blockToEdit.status,
        date: `${year}-${month}-${day}`,
        start_time: `${startH}:${startM}`,
        end_time: `${endH}:${endM}`,
        task_id: blockToEdit.task_id || null,
        color_hex: blockToEdit.color_hex || '#6C63FF',
      });
    } else {
      reset({
        title: '',
        description: '',
        block_type: 'work',
        status: 'scheduled',
        date: initialDate || getTodayDateStr(),
        start_time: initialStartTime || '09:00',
        end_time: '10:00',
        task_id: null,
        color_hex: '#6C63FF',
      });
    }
  }, [blockToEdit, initialDate, initialStartTime, reset, visible]);

  const handleFormSubmit = async (data: PlannerBlockFormData) => {
    setSubmitError(null);
    try {
      await onSubmit(data);
      onClose();
    } catch (err: any) {
      setSubmitError(err?.message || 'Failed to schedule planner block');
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
                <Heading level={3}>
                  {isEditing ? 'Edit Schedule Block' : 'Schedule New Block'}
                </Heading>
                <Caption color="secondary">Reserve focused time in your day</Caption>
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
                    label="Block Title *"
                    placeholder="e.g. System Architecture Design"
                    value={value}
                    onChangeText={onChange}
                    onBlur={onBlur}
                    error={errors.title?.message}
                  />
                )}
              />

              {/* Date & Time Row */}
              <View style={styles.row}>
                <View style={styles.flex1}>
                  <Controller
                    control={control}
                    name="date"
                    render={({ field: { onChange, onBlur, value } }) => (
                      <GlassInput
                        label="Date (YYYY-MM-DD) *"
                        placeholder="2026-11-08"
                        value={value}
                        onChangeText={onChange}
                        onBlur={onBlur}
                        error={errors.date?.message}
                      />
                    )}
                  />
                </View>
              </View>

              <View style={styles.row}>
                <View style={styles.flex1}>
                  <Controller
                    control={control}
                    name="start_time"
                    render={({ field: { onChange, onBlur, value } }) => (
                      <GlassInput
                        label="Start Time (HH:MM) *"
                        placeholder="09:00"
                        value={value}
                        onChangeText={onChange}
                        onBlur={onBlur}
                        error={errors.start_time?.message}
                      />
                    )}
                  />
                </View>
                <View style={{ width: 12 }} />
                <View style={styles.flex1}>
                  <Controller
                    control={control}
                    name="end_time"
                    render={({ field: { onChange, onBlur, value } }) => (
                      <GlassInput
                        label="End Time (HH:MM) *"
                        placeholder="10:00"
                        value={value}
                        onChangeText={onChange}
                        onBlur={onBlur}
                        error={errors.end_time?.message}
                      />
                    )}
                  />
                </View>
              </View>

              {/* Activity Type Selection */}
              <View style={styles.sectionContainer}>
                <Caption style={styles.sectionLabel}>ACTIVITY TYPE</Caption>
                <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.typeScroll}>
                  {BLOCK_TYPES.map((bt) => {
                    const isSelected = selectedType === bt.id;
                    return (
                      <TouchableOpacity
                        key={bt.id}
                        onPress={() => {
                          setValue('block_type', bt.id);
                          if (!isEditing && !selectedColor) {
                            setValue('color_hex', bt.color);
                          }
                        }}
                        style={[
                          styles.typePill,
                          {
                            backgroundColor: isSelected
                              ? theme.colors.primary + '18'
                              : theme.colors.glassBackground,
                            borderColor: isSelected ? theme.colors.primary : theme.colors.border,
                          },
                        ]}
                      >
                        <Ionicons
                          name={bt.icon}
                          size={16}
                          color={isSelected ? theme.colors.primary : theme.colors.textSecondary}
                        />
                        <BodyText
                          style={[
                            styles.typePillText,
                            {
                              color: isSelected ? theme.colors.primary : theme.colors.textPrimary,
                              fontWeight: isSelected ? '600' : '400',
                            },
                          ]}
                        >
                          {bt.label}
                        </BodyText>
                      </TouchableOpacity>
                    );
                  })}
                </ScrollView>
              </View>

              {/* Link to Task (Optional) */}
              {tasks.length > 0 && (
                <View style={styles.sectionContainer}>
                  <Caption style={styles.sectionLabel}>LINKED TASK (OPTIONAL)</Caption>
                  <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.typeScroll}>
                    <TouchableOpacity
                      onPress={() => setValue('task_id', null)}
                      style={[
                        styles.taskPill,
                        {
                          backgroundColor: !selectedTaskId
                            ? theme.colors.primary + '18'
                            : theme.colors.glassBackground,
                          borderColor: !selectedTaskId ? theme.colors.primary : theme.colors.border,
                        },
                      ]}
                    >
                      <BodyText
                        style={[
                          styles.typePillText,
                          {
                            color: !selectedTaskId ? theme.colors.primary : theme.colors.textSecondary,
                            fontWeight: !selectedTaskId ? '600' : '400',
                          },
                        ]}
                      >
                        None
                      </BodyText>
                    </TouchableOpacity>

                    {tasks.map((t) => {
                      const isTaskSelected = selectedTaskId === t.id;
                      return (
                        <TouchableOpacity
                          key={t.id}
                          onPress={() => {
                            setValue('task_id', t.id);
                            if (!watch('title')) {
                              setValue('title', t.title);
                            }
                          }}
                          style={[
                            styles.taskPill,
                            {
                              backgroundColor: isTaskSelected
                                ? theme.colors.primary + '18'
                                : theme.colors.glassBackground,
                              borderColor: isTaskSelected ? theme.colors.primary : theme.colors.border,
                            },
                          ]}
                        >
                          <Ionicons
                            name="checkmark-circle-outline"
                            size={14}
                            color={isTaskSelected ? theme.colors.primary : theme.colors.textSecondary}
                          />
                          <BodyText
                            numberOfLines={1}
                            style={[
                              styles.typePillText,
                              {
                                color: isTaskSelected ? theme.colors.primary : theme.colors.textPrimary,
                                fontWeight: isTaskSelected ? '600' : '400',
                              },
                            ]}
                          >
                            {t.title}
                          </BodyText>
                        </TouchableOpacity>
                      );
                    })}
                  </ScrollView>
                </View>
              )}

              {/* Color Preset Picker */}
              <View style={styles.sectionContainer}>
                <Caption style={styles.sectionLabel}>COLOR ACCENT</Caption>
                <View style={styles.colorPaletteRow}>
                  {PRESET_COLORS.map((hex) => {
                    const isPicked = selectedColor === hex;
                    return (
                      <TouchableOpacity
                        key={hex}
                        onPress={() => setValue('color_hex', hex)}
                        style={[
                          styles.colorCircle,
                          { backgroundColor: hex },
                          isPicked && { borderWidth: 3, borderColor: theme.colors.textPrimary },
                        ]}
                      >
                        {isPicked && <Ionicons name="checkmark" size={14} color="#FFF" />}
                      </TouchableOpacity>
                    );
                  })}
                </View>
              </View>

              {/* Description */}
              <Controller
                control={control}
                name="description"
                render={({ field: { onChange, onBlur, value } }) => (
                  <GlassInput
                    label="Notes / Agenda (Optional)"
                    placeholder="Objectives, deliverables, or agenda details..."
                    value={value || ''}
                    onChangeText={onChange}
                    onBlur={onBlur}
                    multiline
                    numberOfLines={3}
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
                  label={isEditing ? 'Save Changes' : 'Schedule Block'}
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
  row: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  flex1: {
    flex: 1,
  },
  sectionContainer: {
    marginVertical: 10,
  },
  sectionLabel: {
    marginBottom: 8,
    fontWeight: '600',
    letterSpacing: 0.8,
  },
  typeScroll: {
    flexDirection: 'row',
  },
  typePill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
    borderWidth: 1,
    marginRight: 8,
    gap: 6,
  },
  taskPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
    borderWidth: 1,
    marginRight: 8,
    maxWidth: 200,
    gap: 6,
  },
  typePillText: {
    fontSize: 13,
  },
  colorPaletteRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  colorCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
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
