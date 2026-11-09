import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Switch,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import {
  useDailyRoutine,
  useUpdateDailyRoutine,
  useResetPreferences,
} from '../../hooks/usePersonalization';

interface DailyRoutineScreenProps {
  navigation: any;
}

const DAYS_OF_WEEK = [
  { id: 'monday', label: 'Mon' },
  { id: 'tuesday', label: 'Tue' },
  { id: 'wednesday', label: 'Wed' },
  { id: 'thursday', label: 'Thu' },
  { id: 'friday', label: 'Fri' },
  { id: 'saturday', label: 'Sat' },
  { id: 'sunday', label: 'Sun' },
];

export function DailyRoutineScreen({ navigation }: DailyRoutineScreenProps) {
  const { theme } = useTheme();
  const insets = useSafeAreaInsets();

  const { data: routine, isLoading } = useDailyRoutine();
  const updateMutation = useUpdateDailyRoutine();
  const resetMutation = useResetPreferences();

  const [wakeTime, setWakeTime] = useState('');
  const [sleepTime, setSleepTime] = useState('');
  const [workStart, setWorkStart] = useState('');
  const [workEnd, setWorkEnd] = useState('');
  const [planningTime, setPlanningTime] = useState('');
  const [hasInitialized, setHasInitialized] = useState(false);

  // Sync state once query data loads
  if (routine && !hasInitialized) {
    setWakeTime(routine.wake_time);
    setSleepTime(routine.sleep_time);
    setWorkStart(routine.work_start);
    setWorkEnd(routine.work_end);
    setPlanningTime(routine.preferred_planning_time);
    setHasInitialized(true);
  }

  if (isLoading || !routine) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  const handleToggleDay = (dayId: string) => {
    const currentDays = routine.work_days || [];
    const updated = currentDays.includes(dayId)
      ? currentDays.filter((d) => d !== dayId)
      : [...currentDays, dayId];
    updateMutation.mutate({ work_days: updated });
  };

  const handleSaveTimes = () => {
    updateMutation.mutate(
      {
        wake_time: wakeTime,
        sleep_time: sleepTime,
        work_start: workStart,
        work_end: workEnd,
        preferred_planning_time: planningTime,
      },
      {
        onSuccess: () => {
          Alert.alert('Saved', 'Daily routine updated successfully.');
        },
      }
    );
  };

  const handleResetRoutine = () => {
    Alert.alert(
      'Reset Daily Routine',
      'Restore standard 9-5 work hours and typical sleep rhythms?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          style: 'destructive',
          onPress: () => {
            resetMutation.mutate('routine', {
              onSuccess: () => setHasInitialized(false),
            });
          },
        },
      ]
    );
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background, paddingTop: insets.top }]}>
      {/* Header */}
      <View style={[styles.header, { borderBottomColor: theme.colors.border }]}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          <Ionicons name="arrow-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <View style={styles.headerTitleContainer}>
          <Text style={[styles.headerTitle, { color: theme.colors.textPrimary }]}>Daily Rhythm & Routine</Text>
          <Text style={[styles.headerSubtitle, { color: theme.colors.textSecondary }]}>
            Working hours, focus blocks, and planning rituals
          </Text>
        </View>
        <TouchableOpacity
          onPress={handleResetRoutine}
          disabled={resetMutation.isPending}
          style={styles.resetButton}
        >
          <Ionicons name="refresh-outline" size={20} color={theme.colors.primary} />
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Working Hours & Work Days */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>Working Schedule</Text>
          <Text style={[styles.sectionSubtitle, { color: theme.colors.textSecondary }]}>
            Defines your active work window for planner suggestions and focus sessions.
          </Text>

          <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            {/* Days Chips */}
            <View style={styles.daysRow}>
              {DAYS_OF_WEEK.map((d) => {
                const isSelected = (routine.work_days || []).includes(d.id);
                return (
                  <TouchableOpacity
                    key={d.id}
                    onPress={() => handleToggleDay(d.id)}
                    style={[
                      styles.dayChip,
                      {
                        backgroundColor: isSelected ? theme.colors.primary : `${theme.colors.primary}15`,
                      },
                    ]}
                  >
                    <Text
                      style={[
                        styles.dayChipText,
                        { color: isSelected ? '#FFFFFF' : theme.colors.primary },
                      ]}
                    >
                      {d.label}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </View>

            {/* Time inputs */}
            <View style={[styles.timeRow, { borderTopColor: theme.colors.border }]}>
              <View style={styles.timeInputCol}>
                <Text style={[styles.fieldLabel, { color: theme.colors.textSecondary }]}>Work Start (24h)</Text>
                <TextInput
                  style={[styles.textInput, { color: theme.colors.textPrimary, borderColor: theme.colors.border }]}
                  value={workStart}
                  onChangeText={setWorkStart}
                  placeholder="09:00"
                  placeholderTextColor={theme.colors.textSecondary}
                  keyboardType="numbers-and-punctuation"
                  maxLength={5}
                />
              </View>

              <View style={styles.timeInputCol}>
                <Text style={[styles.fieldLabel, { color: theme.colors.textSecondary }]}>Work End (24h)</Text>
                <TextInput
                  style={[styles.textInput, { color: theme.colors.textPrimary, borderColor: theme.colors.border }]}
                  value={workEnd}
                  onChangeText={setWorkEnd}
                  placeholder="17:00"
                  placeholderTextColor={theme.colors.textSecondary}
                  keyboardType="numbers-and-punctuation"
                  maxLength={5}
                />
              </View>
            </View>
          </View>
        </View>

        {/* Sleep & Wake Rhythm */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>Sleep & Wake Rhythm</Text>
          <Text style={[styles.sectionSubtitle, { color: theme.colors.textSecondary }]}>
            Used to respect wind-down hours and calculate optimal reminder times.
          </Text>

          <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            <View style={styles.timeRow}>
              <View style={styles.timeInputCol}>
                <Text style={[styles.fieldLabel, { color: theme.colors.textSecondary }]}>Wake Up (24h)</Text>
                <TextInput
                  style={[styles.textInput, { color: theme.colors.textPrimary, borderColor: theme.colors.border }]}
                  value={wakeTime}
                  onChangeText={setWakeTime}
                  placeholder="07:00"
                  placeholderTextColor={theme.colors.textSecondary}
                  keyboardType="numbers-and-punctuation"
                  maxLength={5}
                />
              </View>

              <View style={styles.timeInputCol}>
                <Text style={[styles.fieldLabel, { color: theme.colors.textSecondary }]}>Sleep Time (24h)</Text>
                <TextInput
                  style={[styles.textInput, { color: theme.colors.textPrimary, borderColor: theme.colors.border }]}
                  value={sleepTime}
                  onChangeText={setSleepTime}
                  placeholder="23:00"
                  placeholderTextColor={theme.colors.textSecondary}
                  keyboardType="numbers-and-punctuation"
                  maxLength={5}
                />
              </View>
            </View>
          </View>
        </View>

        {/* Focus & Breaks */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>Focus Duration & Planning</Text>

          <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            <View style={[styles.switchRow, { borderBottomColor: theme.colors.border, borderBottomWidth: StyleSheet.hairlineWidth }]}>
              <View style={styles.switchInfo}>
                <Text style={[styles.optionTitle, { color: theme.colors.textPrimary }]}>Preferred Planning Time</Text>
                <Text style={[styles.optionDesc, { color: theme.colors.textSecondary }]}>
                  When LifeOS suggests daily schedule review
                </Text>
              </View>
              <TextInput
                style={[styles.smallInput, { color: theme.colors.textPrimary, borderColor: theme.colors.border }]}
                value={planningTime}
                onChangeText={setPlanningTime}
                placeholder="08:30"
                placeholderTextColor={theme.colors.textSecondary}
                keyboardType="numbers-and-punctuation"
                maxLength={5}
              />
            </View>

            <View style={[styles.switchRow, { borderBottomColor: theme.colors.border, borderBottomWidth: StyleSheet.hairlineWidth }]}>
              <View style={styles.switchInfo}>
                <Text style={[styles.optionTitle, { color: theme.colors.textPrimary }]}>Morning Routine Card</Text>
                <Text style={[styles.optionDesc, { color: theme.colors.textSecondary }]}>
                  Show proactive morning review prompts
                </Text>
              </View>
              <Switch
                value={routine.morning_routine_enabled}
                onValueChange={(val) => updateMutation.mutate({ morning_routine_enabled: val })}
                trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
              />
            </View>

            <View style={styles.switchRow}>
              <View style={styles.switchInfo}>
                <Text style={[styles.optionTitle, { color: theme.colors.textPrimary }]}>Evening Reflection</Text>
                <Text style={[styles.optionDesc, { color: theme.colors.textSecondary }]}>
                  Prompt habit check-ins and tomorrow preview
                </Text>
              </View>
              <Switch
                value={routine.evening_routine_enabled}
                onValueChange={(val) => updateMutation.mutate({ evening_routine_enabled: val })}
                trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
              />
            </View>
          </View>
        </View>

        {/* Save Button */}
        <TouchableOpacity
          onPress={handleSaveTimes}
          disabled={updateMutation.isPending}
          style={[styles.saveButton, { backgroundColor: theme.colors.primary }]}
        >
          {updateMutation.isPending ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <Text style={styles.saveButtonText}>Save Daily Routine</Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  backButton: {
    marginRight: 12,
  },
  headerTitleContainer: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
  },
  headerSubtitle: {
    fontSize: 12,
    marginTop: 2,
  },
  resetButton: {
    padding: 6,
  },
  content: {
    padding: 16,
    paddingBottom: 40,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 4,
  },
  sectionSubtitle: {
    fontSize: 13,
    marginBottom: 12,
  },
  card: {
    borderRadius: 14,
    borderWidth: StyleSheet.hairlineWidth,
    overflow: 'hidden',
  },
  daysRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    padding: 14,
  },
  dayChip: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
  },
  dayChipText: {
    fontSize: 12,
    fontWeight: '700',
  },
  timeRow: {
    flexDirection: 'row',
    padding: 14,
    gap: 16,
    borderTopWidth: StyleSheet.hairlineWidth,
  },
  timeInputCol: {
    flex: 1,
  },
  fieldLabel: {
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 6,
  },
  textInput: {
    height: 44,
    borderRadius: 10,
    borderWidth: 1,
    paddingHorizontal: 12,
    fontSize: 15,
  },
  switchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
  },
  switchInfo: {
    flex: 1,
    marginRight: 12,
  },
  optionTitle: {
    fontSize: 15,
    fontWeight: '600',
    marginBottom: 2,
  },
  optionDesc: {
    fontSize: 12,
  },
  smallInput: {
    width: 70,
    height: 38,
    borderRadius: 8,
    borderWidth: 1,
    textAlign: 'center',
    fontSize: 14,
  },
  saveButton: {
    height: 50,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
    marginBottom: 20,
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
});
