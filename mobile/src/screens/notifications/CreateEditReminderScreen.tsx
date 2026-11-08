import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  Switch,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { useTheme } from '../../theme';
import {
  useCreateReminder,
  useUpdateReminder,
  useReminders,
} from '../../hooks/useNotifications';
import { RootNavigationProp, RootStackParamList } from '../../navigation/types';
import { RecurrenceRule } from '../../types/notification';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
} from '../../components';

const RECURRENCE_RULES: { label: string; value: RecurrenceRule }[] = [
  { label: 'Daily', value: 'daily' },
  { label: 'Weekdays', value: 'weekdays' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' },
];

export const CreateEditReminderScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<RootNavigationProp>();
  const route = useRoute<RouteProp<RootStackParamList, 'CreateEditReminder'>>();
  const reminderId = route.params?.reminderId;

  const { data: reminderData } = useReminders();
  const existingReminder = (reminderData?.reminders || []).find((r) => r.id === reminderId);

  const [title, setTitle] = useState(existingReminder?.title || '');
  const [description, setDescription] = useState(existingReminder?.description || '');
  const [minutesFromNow, setMinutesFromNow] = useState<number>(60); // Default in 1 hour
  const [isRecurring, setIsRecurring] = useState(existingReminder?.is_recurring || false);
  const [recurrenceRule, setRecurrenceRule] = useState<RecurrenceRule>(
    existingReminder?.recurrence_rule || 'daily'
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const createReminderMutation = useCreateReminder();
  const updateReminderMutation = useUpdateReminder();

  const handleSave = async () => {
    if (!title.trim()) {
      setErrorMessage('Please enter a title for this reminder.');
      return;
    }

    const scheduledDate = new Date(Date.now() + minutesFromNow * 60 * 1000);

    try {
      if (reminderId) {
        await updateReminderMutation.mutateAsync({
          id: reminderId,
          payload: {
            title: title.trim(),
            description: description.trim() || undefined,
            reminder_time: scheduledDate.toISOString(),
            is_recurring: isRecurring,
            recurrence_rule: isRecurring ? recurrenceRule : undefined,
          },
        });
      } else {
        await createReminderMutation.mutateAsync({
          title: title.trim(),
          description: description.trim() || undefined,
          reminder_time: scheduledDate.toISOString(),
          is_recurring: isRecurring,
          recurrence_rule: isRecurring ? recurrenceRule : undefined,
        });
      }
      navigation.goBack();
    } catch (err: any) {
      setErrorMessage(err?.response?.data?.message || err?.message || 'Failed to save reminder.');
    }
  };

  const isSubmitting = createReminderMutation.isPending || updateReminderMutation.isPending;

  return (
    <SafeAreaContainer>
      <ScrollContainer>
        {/* Header */}
        <View style={styles.headerRow}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={[styles.iconButton, { backgroundColor: theme.colors.surfaceSubtle }]}
          >
            <Ionicons name="close" size={22} color={theme.colors.textPrimary} />
          </TouchableOpacity>
          <Heading level={2}>{reminderId ? 'Edit Reminder' : 'New Reminder'}</Heading>
          <View style={{ width: 40 }} />
        </View>

        {errorMessage && (
          <View style={[styles.errorBox, { backgroundColor: theme.colors.errorLight + '40' }]}>
            <Ionicons name="alert-circle" size={18} color={theme.colors.error} />
            <BodyText variant="small" style={{ marginLeft: 8, flex: 1, color: theme.colors.error }}>
              {errorMessage}
            </BodyText>
          </View>
        )}

        {/* Title Input */}
        <GlassCard style={styles.card}>
          <Caption color="muted" style={{ marginBottom: 6 }}>
            TITLE
          </Caption>
          <TextInput
            style={[styles.input, { color: theme.colors.textPrimary }]}
            placeholder="e.g. Drink water, Call accountant, Review goals"
            placeholderTextColor={theme.colors.textMuted}
            value={title}
            onChangeText={setTitle}
            autoFocus={!reminderId}
          />
        </GlassCard>

        {/* Description Input */}
        <GlassCard style={styles.card}>
          <Caption color="muted" style={{ marginBottom: 6 }}>
            NOTE / DESCRIPTION (OPTIONAL)
          </Caption>
          <TextInput
            style={[styles.multilineInput, { color: theme.colors.textPrimary }]}
            placeholder="Add extra context or instructions..."
            placeholderTextColor={theme.colors.textMuted}
            value={description}
            onChangeText={setDescription}
            multiline
            numberOfLines={3}
          />
        </GlassCard>

        {/* Schedule Presets */}
        <Heading level={3} style={styles.sectionTitle}>
          Trigger Time
        </Heading>
        <View style={styles.presetGrid}>
          {[
            { label: 'In 15 Min', value: 15 },
            { label: 'In 1 Hour', value: 60 },
            { label: 'In 3 Hours', value: 180 },
            { label: 'Tomorrow (24h)', value: 1440 },
          ].map((preset) => {
            const isSelected = minutesFromNow === preset.value;
            return (
              <TouchableOpacity
                key={preset.value}
                onPress={() => setMinutesFromNow(preset.value)}
                style={[
                  styles.presetChip,
                  {
                    backgroundColor: isSelected ? theme.colors.primary : theme.colors.surface,
                    borderColor: isSelected ? theme.colors.primary : theme.colors.border,
                  },
                ]}
              >
                <BodyText
                  variant="small"
                  weight="600"
                  style={{ color: isSelected ? '#FFFFFF' : theme.colors.textPrimary }}
                >
                  {preset.label}
                </BodyText>
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Recurring Toggle */}
        <GlassCard style={[styles.card, { marginTop: 12 }]}>
          <View style={styles.toggleRow}>
            <View>
              <BodyText weight="600">Recurring Reminder</BodyText>
              <Caption color="muted">Automatically schedule next occurrence</Caption>
            </View>
            <Switch
              value={isRecurring}
              onValueChange={setIsRecurring}
              trackColor={{ false: theme.colors.surfaceSubtle, true: theme.colors.primary }}
              thumbColor="#FFFFFF"
            />
          </View>

          {isRecurring && (
            <>
              <View style={[styles.divider, { backgroundColor: theme.colors.divider }]} />
              <Caption color="muted" style={{ marginBottom: 8 }}>
                RECURRENCE FREQUENCY
              </Caption>
              <View style={styles.ruleGrid}>
                {RECURRENCE_RULES.map((rule) => {
                  const isSelected = recurrenceRule === rule.value;
                  return (
                    <TouchableOpacity
                      key={rule.value}
                      onPress={() => setRecurrenceRule(rule.value)}
                      style={[
                        styles.ruleChip,
                        {
                          backgroundColor: isSelected ? theme.colors.primary : theme.colors.surfaceSubtle,
                        },
                      ]}
                    >
                      <Caption
                        weight="700"
                        style={{ color: isSelected ? '#FFFFFF' : theme.colors.textPrimary }}
                      >
                        {rule.label}
                      </Caption>
                    </TouchableOpacity>
                  );
                })}
              </View>
            </>
          )}
        </GlassCard>

        {/* Save Button */}
        <TouchableOpacity
          style={[
            styles.submitBtn,
            { backgroundColor: theme.colors.primary, opacity: isSubmitting ? 0.7 : 1 },
          ]}
          onPress={handleSave}
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <ActivityIndicator size="small" color="#FFFFFF" />
          ) : (
            <BodyText weight="700" style={{ color: '#FFFFFF' }}>
              {reminderId ? 'Update Reminder' : 'Set Reminder'}
            </BodyText>
          )}
        </TouchableOpacity>
      </ScrollContainer>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  errorBox: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 12,
    marginBottom: 16,
  },
  card: {
    padding: 16,
    borderRadius: 16,
    marginBottom: 14,
  },
  input: {
    fontSize: 16,
    paddingVertical: 4,
  },
  multilineInput: {
    fontSize: 15,
    minHeight: 60,
    textAlignVertical: 'top',
    paddingVertical: 4,
  },
  sectionTitle: {
    marginBottom: 10,
    marginTop: 6,
  },
  presetGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 8,
  },
  presetChip: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 14,
    borderWidth: 1,
  },
  toggleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  divider: {
    height: 1,
    marginVertical: 12,
  },
  ruleGrid: {
    flexDirection: 'row',
    gap: 8,
  },
  ruleChip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 12,
  },
  submitBtn: {
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 20,
    marginBottom: 40,
  },
});

