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
import { milestoneFormSchema, MilestoneFormData } from '../../schemas/goal';
import { GoalMilestone } from '../../types/goal';
import {
  GlassCard,
  GlassInput,
  PrimaryButton,
  SecondaryButton,
  Heading,
  BodyText,
  Caption,
} from '../../components';

export interface CreateEditMilestoneModalProps {
  visible: boolean;
  milestoneToEdit?: GoalMilestone | null;
  isLoading?: boolean;
  onClose: () => void;
  onSubmit: (values: MilestoneFormData) => Promise<void>;
}

export const CreateEditMilestoneModal: React.FC<CreateEditMilestoneModalProps> = ({
  visible,
  milestoneToEdit,
  isLoading = false,
  onClose,
  onSubmit,
}) => {
  const { theme } = useTheme();
  const isEditing = !!milestoneToEdit;
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<MilestoneFormData>({
    resolver: zodResolver(milestoneFormSchema),
    defaultValues: {
      title: '',
      description: '',
      target_date: '',
      sort_order: 0,
    },
  });

  useEffect(() => {
    setSubmitError(null);
    if (milestoneToEdit) {
      let dateStr = '';
      if (milestoneToEdit.target_date) {
        const d = new Date(milestoneToEdit.target_date);
        dateStr = d.toISOString().split('T')[0];
      }
      reset({
        title: milestoneToEdit.title,
        description: milestoneToEdit.description || '',
        target_date: dateStr,
        sort_order: milestoneToEdit.sort_order || 0,
      });
    } else {
      reset({
        title: '',
        description: '',
        target_date: '',
        sort_order: 0,
      });
    }
  }, [milestoneToEdit, reset, visible]);

  const handleFormSubmit = async (data: MilestoneFormData) => {
    setSubmitError(null);
    try {
      await onSubmit(data);
      onClose();
    } catch (err: any) {
      setSubmitError(err?.message || 'Failed to save milestone');
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
                  {isEditing ? 'Edit Milestone' : 'Add Milestone'}
                </Heading>
                <Caption color="secondary">Measurable checkpoint towards your goal</Caption>
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
                    label="Milestone Title *"
                    placeholder="e.g. Complete Spring Boot REST API"
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
                    label="Due Date (YYYY-MM-DD)"
                    placeholder="2026-11-30"
                    value={value || ''}
                    onChangeText={onChange}
                    onBlur={onBlur}
                    error={errors.target_date?.message}
                  />
                )}
              />

              {/* Description */}
              <Controller
                control={control}
                name="description"
                render={({ field: { onChange, onBlur, value } }) => (
                  <GlassInput
                    label="Details & Acceptance Criteria"
                    placeholder="Key deliverables or test criteria..."
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
                  label={isEditing ? 'Save Changes' : 'Add Milestone'}
                  onPress={() => handleSubmit((data) => handleFormSubmit(data))()}
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
