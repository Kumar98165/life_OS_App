import React, { useEffect } from 'react';
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
import { Habit, HabitFrequency } from '../../types/habit';
import { habitFormSchema, HabitFormData } from '../../schemas/habit';
import { GlassCard } from '../glass/GlassCard';
import { GlassInput } from '../common/FormInputs';
import { PrimaryButton, SecondaryButton } from '../common/Buttons';
import { Heading, BodyText, Caption } from '../common/Typography';

const PALETTE = [
  '#6C63FF', // Brand Indigo
  '#10B981', // Emerald Success
  '#3B82F6', // Blue Info
  '#F59E0B', // Amber Warning
  '#EF4444', // Red Coral
  '#EC4899', // Pink
  '#8B5CF6', // Purple
  '#14B8A6', // Teal
];

const ICONS: Array<{ name: keyof typeof Ionicons.glyphMap; label: string }> = [
  { name: 'flame', label: 'Streak' },
  { name: 'fitness', label: 'Workout' },
  { name: 'book', label: 'Reading' },
  { name: 'water', label: 'Water' },
  { name: 'leaf', label: 'Mind' },
  { name: 'walk', label: 'Walk' },
  { name: 'code-slash', label: 'Code' },
  { name: 'moon', label: 'Sleep' },
];

export interface CreateEditHabitModalProps {
  visible: boolean;
  habitToEdit?: Habit | null;
  onClose: () => void;
  onSubmit: (data: HabitFormData) => Promise<void>;
  isLoading?: boolean;
}

export const CreateEditHabitModal: React.FC<CreateEditHabitModalProps> = ({
  visible,
  habitToEdit,
  onClose,
  onSubmit,
  isLoading = false,
}) => {
  const { theme } = useTheme();

  const isEditing = !!habitToEdit;

  const {
    control,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors },
  } = useForm<HabitFormData>({
    resolver: zodResolver(habitFormSchema),
    defaultValues: {
      title: '',
      description: '',
      frequency: 'daily',
      target_days_per_week: 7,
      color_hex: '#6C63FF',
      icon: 'flame',
    },
  });

  const selectedFrequency = watch('frequency');
  const selectedColor = watch('color_hex');
  const selectedIcon = watch('icon');
  const targetDays = watch('target_days_per_week');

  useEffect(() => {
    if (habitToEdit) {
      reset({
        title: habitToEdit.title,
        description: habitToEdit.description || '',
        frequency: habitToEdit.frequency,
        target_days_per_week: habitToEdit.target_days_per_week || 7,
        color_hex: habitToEdit.color_hex || '#6C63FF',
        icon: habitToEdit.icon || 'flame',
      });
    } else {
      reset({
        title: '',
        description: '',
        frequency: 'daily',
        target_days_per_week: 7,
        color_hex: '#6C63FF',
        icon: 'flame',
      });
    }
  }, [habitToEdit, reset, visible]);

  const handleFormSubmit = async (data: HabitFormData) => {
    await onSubmit(data);
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.overlay}
      >
        <TouchableOpacity style={styles.backdrop} activeOpacity={1} onPress={onClose} />

        <GlassCard elevation="floating" style={styles.sheetContainer}>
          <View style={styles.header}>
            <Heading level={2}>{isEditing ? 'Edit Habit' : 'Track New Habit'}</Heading>
            <TouchableOpacity
              onPress={onClose}
              style={[styles.closeBtn, { borderColor: theme.colors.glassBorder }]}
              accessibilityRole="button"
              accessibilityLabel="Close modal"
            >
              <Ionicons name="close" size={20} color={theme.colors.textPrimary} />
            </TouchableOpacity>
          </View>

          <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollBody}>
            {/* Title Field */}
            <Controller
              control={control}
              name="title"
              render={({ field: { onChange, onBlur, value } }) => (
                <GlassInput
                  label="Habit Title"
                  required
                  placeholder="e.g. Morning Meditation, Reading"
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
                  label="Description"
                  placeholder="Optional details, cues, or routine trigger"
                  value={value || ''}
                  onChangeText={onChange}
                  onBlur={onBlur}
                  multiline
                  numberOfLines={2}
                  error={errors.description?.message}
                />
              )}
            />

            {/* Frequency Selection */}
            <View style={styles.fieldGroup}>
              <Caption weight="600" style={styles.fieldLabel}>
                FREQUENCY <Caption style={{ color: theme.colors.error }}>*</Caption>
              </Caption>
              <View style={styles.pillRow}>
                {(['daily', 'weekdays', 'weekly'] as HabitFrequency[]).map((freq) => {
                  const isSelected = selectedFrequency === freq;
                  const label =
                    freq === 'daily'
                      ? 'Every Day'
                      : freq === 'weekdays'
                      ? 'Mon – Fri'
                      : 'Weekly Target';

                  return (
                    <TouchableOpacity
                      key={freq}
                      onPress={() => {
                        setValue('frequency', freq);
                        if (freq === 'daily') setValue('target_days_per_week', 7);
                        if (freq === 'weekdays') setValue('target_days_per_week', 5);
                        if (freq === 'weekly') setValue('target_days_per_week', 3);
                      }}
                      style={[
                        styles.pillOption,
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
                        {label}
                      </Caption>
                    </TouchableOpacity>
                  );
                })}
              </View>
            </View>

            {/* Target Days Per Week (for weekly frequency) */}
            {selectedFrequency === 'weekly' && (
              <View style={styles.fieldGroup}>
                <Caption weight="600" style={styles.fieldLabel}>
                  WEEKLY TARGET (DAYS)
                </Caption>
                <View style={styles.targetRow}>
                  {[1, 2, 3, 4, 5, 6].map((num) => {
                    const isSelected = targetDays === num;
                    return (
                      <TouchableOpacity
                        key={num}
                        onPress={() => setValue('target_days_per_week', num)}
                        style={[
                          styles.targetNumCircle,
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
                          weight="700"
                          style={{
                            color: isSelected ? '#FFFFFF' : theme.colors.textPrimary,
                          }}
                        >
                          {num}
                        </Caption>
                      </TouchableOpacity>
                    );
                  })}
                </View>
              </View>
            )}

            {/* Color Palette */}
            <View style={styles.fieldGroup}>
              <Caption weight="600" style={styles.fieldLabel}>
                ACCENT COLOR
              </Caption>
              <View style={styles.colorRow}>
                {PALETTE.map((hex) => {
                  const isSelected = selectedColor?.toLowerCase() === hex.toLowerCase();
                  return (
                    <TouchableOpacity
                      key={hex}
                      onPress={() => setValue('color_hex', hex)}
                      style={[
                        styles.colorCircle,
                        { backgroundColor: hex },
                        isSelected && styles.colorCircleSelected,
                      ]}
                    >
                      {isSelected && <Ionicons name="checkmark" size={16} color="#FFFFFF" />}
                    </TouchableOpacity>
                  );
                })}
              </View>
            </View>

            {/* Icon Picker */}
            <View style={styles.fieldGroup}>
              <Caption weight="600" style={styles.fieldLabel}>
                HABIT ICON
              </Caption>
              <View style={styles.iconRow}>
                {ICONS.map((ic) => {
                  const isSelected = selectedIcon === ic.name;
                  return (
                    <TouchableOpacity
                      key={ic.name}
                      onPress={() => setValue('icon', ic.name)}
                      style={[
                        styles.iconChoice,
                        {
                          backgroundColor: isSelected
                            ? `${selectedColor || theme.colors.primary}20`
                            : theme.colors.glassBackgroundSolid,
                          borderColor: isSelected
                            ? selectedColor || theme.colors.primary
                            : theme.colors.glassBorder,
                        },
                      ]}
                    >
                      <Ionicons
                        name={ic.name}
                        size={20}
                        color={
                          isSelected
                            ? selectedColor || theme.colors.primary
                            : theme.colors.textSecondary
                        }
                      />
                    </TouchableOpacity>
                  );
                })}
              </View>
            </View>

            {/* Actions */}
            <View style={styles.actionButtons}>
              <View style={styles.btnWrapper}>
                <SecondaryButton label="Cancel" onPress={onClose} disabled={isLoading} />
              </View>
              <View style={styles.btnWrapper}>
                <PrimaryButton
                  label={isEditing ? 'Save Changes' : 'Start Habit'}
                  onPress={() => handleSubmit((data) => handleFormSubmit(data))()}
                  loading={isLoading}
                />
              </View>
            </View>
          </ScrollView>
        </GlassCard>
      </KeyboardAvoidingView>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  backdrop: {
    ...StyleSheet.absoluteFill,
    backgroundColor: 'rgba(15, 23, 42, 0.45)',
  },
  sheetContainer: {
    maxHeight: '90%',
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: Platform.OS === 'ios' ? 40 : 24,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  closeBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  scrollBody: {
    paddingBottom: 20,
  },
  fieldGroup: {
    marginBottom: 18,
  },
  fieldLabel: {
    marginBottom: 8,
    letterSpacing: 0.5,
  },
  pillRow: {
    flexDirection: 'row',
    gap: 8,
  },
  pillOption: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  targetRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 4,
  },
  targetNumCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  colorRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4,
  },
  colorCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  colorCircleSelected: {
    borderWidth: 2,
    borderColor: '#FFFFFF',
    elevation: 4,
  },
  iconRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  iconChoice: {
    width: 44,
    height: 44,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 12,
  },
  btnWrapper: {
    flex: 1,
  },
});
