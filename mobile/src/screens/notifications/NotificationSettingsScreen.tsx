import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  Switch,
  TextInput,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import {
  useNotificationPreferences,
  useUpdateNotificationPreferences,
} from '../../hooks/useNotifications';
import { pushNotificationService } from '../../services/pushNotificationService';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  SkeletonLoader,
} from '../../components';

export const NotificationSettingsScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation();

  const { data: preferences, isLoading, refetch } = useNotificationPreferences();
  const updatePrefMutation = useUpdateNotificationPreferences();

  const [tasksEnabled, setTasksEnabled] = useState(true);
  const [plannerEnabled, setPlannerEnabled] = useState(true);
  const [habitsEnabled, setHabitsEnabled] = useState(true);
  const [goalsEnabled, setGoalsEnabled] = useState(true);
  const [financeEnabled, setFinanceEnabled] = useState(true);

  const [pushEnabled, setPushEnabled] = useState(true);
  const [inAppEnabled, setInAppEnabled] = useState(true);

  const [quietHoursEnabled, setQuietHoursEnabled] = useState(false);
  const [quietHoursStart, setQuietHoursStart] = useState('22:00');
  const [quietHoursEnd, setQuietHoursEnd] = useState('08:00');
  const [timezone, setTimezone] = useState('UTC');

  useEffect(() => {
    if (preferences) {
      setTasksEnabled(preferences.tasks_enabled);
      setPlannerEnabled(preferences.planner_enabled);
      setHabitsEnabled(preferences.habits_enabled);
      setGoalsEnabled(preferences.goals_enabled);
      setFinanceEnabled(preferences.finance_enabled);
      setPushEnabled(preferences.push_enabled);
      setInAppEnabled(preferences.in_app_enabled);
      setQuietHoursEnabled(preferences.quiet_hours_enabled);
      setQuietHoursStart(preferences.quiet_hours_start);
      setQuietHoursEnd(preferences.quiet_hours_end);
      setTimezone(preferences.timezone);
    }
  }, [preferences]);

  const handleToggle = (key: string, value: boolean) => {
    updatePrefMutation.mutate({ [key]: value });
  };

  const handleEnablePush = async () => {
    const res = await pushNotificationService.registerForPushNotifications();
    if (res.status === 'granted') {
      setPushEnabled(true);
      updatePrefMutation.mutate({ push_enabled: true });
      Alert.alert('Push Notifications Enabled', 'Device successfully registered for LifeOS push alerts.');
    } else if (res.status === 'denied') {
      Alert.alert(
        'Permission Denied',
        'Push notifications are blocked in your system settings. In-app alerts will continue to work.'
      );
    } else {
      Alert.alert(
        'Platform Notice',
        res.error || 'Push notifications are not supported in this runtime environment.'
      );
    }
  };

  const handleSaveQuietHours = () => {
    const timeRegex = /^([01]\d|2[0-3]):[0-5]\d$/;
    if (!timeRegex.test(quietHoursStart) || !timeRegex.test(quietHoursEnd)) {
      Alert.alert('Invalid Format', 'Please enter hours in 24-hour format (e.g. 22:00 and 08:00).');
      return;
    }

    updatePrefMutation.mutate({
      quiet_hours_start: quietHoursStart,
      quiet_hours_end: quietHoursEnd,
    });
    Alert.alert('Quiet Hours Updated', `Do Not Disturb is set from ${quietHoursStart} to ${quietHoursEnd}.`);
  };

  return (
    <SafeAreaContainer>
      <ScrollContainer>
        {/* Header */}
        <View style={styles.headerRow}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={[styles.iconButton, { backgroundColor: theme.colors.surfaceSubtle }]}
          >
            <Ionicons name="arrow-back" size={20} color={theme.colors.textPrimary} />
          </TouchableOpacity>
          <Heading level={2}>Notification Settings</Heading>
          <View style={{ width: 40 }} />
        </View>

        {isLoading ? (
          <View style={{ gap: 12, marginTop: 10 }}>
            <SkeletonLoader width="100%" height={120} borderRadius={16} />
            <SkeletonLoader width="100%" height={120} borderRadius={16} />
          </View>
        ) : (
          <>
            {/* Category Preferences */}
            <Heading level={3} style={styles.sectionTitle}>
              Notification Categories
            </Heading>
            <GlassCard style={styles.card}>
              <View style={styles.settingRow}>
                <View style={styles.labelCol}>
                  <BodyText weight="600">Task Reminders</BodyText>
                  <Caption color="muted">Due dates, deadlines, and overdue tasks</Caption>
                </View>
                <Switch
                  value={tasksEnabled}
                  onValueChange={(val) => {
                    setTasksEnabled(val);
                    handleToggle('tasks_enabled', val);
                  }}
                  trackColor={{ false: theme.colors.surfaceSubtle, true: theme.colors.primary }}
                  thumbColor="#FFFFFF"
                />
              </View>

              <View style={[styles.divider, { backgroundColor: theme.colors.divider }]} />

              <View style={styles.settingRow}>
                <View style={styles.labelCol}>
                  <BodyText weight="600">Planner & Calendar</BodyText>
                  <Caption color="muted">Upcoming schedule blocks & time intervals</Caption>
                </View>
                <Switch
                  value={plannerEnabled}
                  onValueChange={(val) => {
                    setPlannerEnabled(val);
                    handleToggle('planner_enabled', val);
                  }}
                  trackColor={{ false: theme.colors.surfaceSubtle, true: theme.colors.primary }}
                  thumbColor="#FFFFFF"
                />
              </View>

              <View style={[styles.divider, { backgroundColor: theme.colors.divider }]} />

              <View style={styles.settingRow}>
                <View style={styles.labelCol}>
                  <BodyText weight="600">Habit Streaks</BodyText>
                  <Caption color="muted">Daily habit check-in nudges</Caption>
                </View>
                <Switch
                  value={habitsEnabled}
                  onValueChange={(val) => {
                    setHabitsEnabled(val);
                    handleToggle('habits_enabled', val);
                  }}
                  trackColor={{ false: theme.colors.surfaceSubtle, true: theme.colors.primary }}
                  thumbColor="#FFFFFF"
                />
              </View>

              <View style={[styles.divider, { backgroundColor: theme.colors.divider }]} />

              <View style={styles.settingRow}>
                <View style={styles.labelCol}>
                  <BodyText weight="600">Goals & Milestones</BodyText>
                  <Caption color="muted">Milestone deadlines and goal progress</Caption>
                </View>
                <Switch
                  value={goalsEnabled}
                  onValueChange={(val) => {
                    setGoalsEnabled(val);
                    handleToggle('goals_enabled', val);
                  }}
                  trackColor={{ false: theme.colors.surfaceSubtle, true: theme.colors.primary }}
                  thumbColor="#FFFFFF"
                />
              </View>

              <View style={[styles.divider, { backgroundColor: theme.colors.divider }]} />

              <View style={styles.settingRow}>
                <View style={styles.labelCol}>
                  <BodyText weight="600">Finance Alerts</BodyText>
                  <Caption color="muted">Budget overrun warnings and savings goals</Caption>
                </View>
                <Switch
                  value={financeEnabled}
                  onValueChange={(val) => {
                    setFinanceEnabled(val);
                    handleToggle('finance_enabled', val);
                  }}
                  trackColor={{ false: theme.colors.surfaceSubtle, true: theme.colors.primary }}
                  thumbColor="#FFFFFF"
                />
              </View>
            </GlassCard>

            {/* Delivery Channels */}
            <Heading level={3} style={styles.sectionTitle}>
              Delivery Channels
            </Heading>
            <GlassCard style={styles.card}>
              <View style={styles.settingRow}>
                <View style={styles.labelCol}>
                  <BodyText weight="600">In-App Notifications</BodyText>
                  <Caption color="muted">Bell badges & notification center</Caption>
                </View>
                <Switch
                  value={inAppEnabled}
                  onValueChange={(val) => {
                    setInAppEnabled(val);
                    handleToggle('in_app_enabled', val);
                  }}
                  trackColor={{ false: theme.colors.surfaceSubtle, true: theme.colors.primary }}
                  thumbColor="#FFFFFF"
                />
              </View>

              <View style={[styles.divider, { backgroundColor: theme.colors.divider }]} />

              <View style={styles.settingRow}>
                <View style={styles.labelCol}>
                  <BodyText weight="600">Expo Push Notifications</BodyText>
                  <Caption color="muted">Lock screen and device banner alerts</Caption>
                </View>
                <Switch
                  value={pushEnabled}
                  onValueChange={(val) => {
                    if (val) {
                      handleEnablePush();
                    } else {
                      setPushEnabled(false);
                      handleToggle('push_enabled', false);
                    }
                  }}
                  trackColor={{ false: theme.colors.surfaceSubtle, true: theme.colors.primary }}
                  thumbColor="#FFFFFF"
                />
              </View>
            </GlassCard>

            {/* Quiet Hours (Do Not Disturb) */}
            <Heading level={3} style={styles.sectionTitle}>
              Quiet Hours
            </Heading>
            <GlassCard style={styles.card}>
              <View style={styles.settingRow}>
                <View style={styles.labelCol}>
                  <BodyText weight="600">Enable Quiet Hours</BodyText>
                  <Caption color="muted">Suppress push notifications during sleep</Caption>
                </View>
                <Switch
                  value={quietHoursEnabled}
                  onValueChange={(val) => {
                    setQuietHoursEnabled(val);
                    handleToggle('quiet_hours_enabled', val);
                  }}
                  trackColor={{ false: theme.colors.surfaceSubtle, true: theme.colors.primary }}
                  thumbColor="#FFFFFF"
                />
              </View>

              {quietHoursEnabled && (
                <>
                  <View style={[styles.divider, { backgroundColor: theme.colors.divider }]} />
                  <View style={styles.timeInputsRow}>
                    <View style={styles.timeInputBox}>
                      <Caption color="muted" style={{ marginBottom: 4 }}>
                        START (24H)
                      </Caption>
                      <TextInput
                        style={[styles.input, { borderColor: theme.colors.border, color: theme.colors.textPrimary }]}
                        value={quietHoursStart}
                        onChangeText={setQuietHoursStart}
                        placeholder="22:00"
                        placeholderTextColor={theme.colors.textMuted}
                        maxLength={5}
                      />
                    </View>

                    <View style={styles.timeInputBox}>
                      <Caption color="muted" style={{ marginBottom: 4 }}>
                        END (24H)
                      </Caption>
                      <TextInput
                        style={[styles.input, { borderColor: theme.colors.border, color: theme.colors.textPrimary }]}
                        value={quietHoursEnd}
                        onChangeText={setQuietHoursEnd}
                        placeholder="08:00"
                        placeholderTextColor={theme.colors.textMuted}
                        maxLength={5}
                      />
                    </View>

                    <TouchableOpacity
                      style={[styles.saveHoursBtn, { backgroundColor: theme.colors.primary }]}
                      onPress={handleSaveQuietHours}
                    >
                      <Caption weight="700" style={{ color: '#FFFFFF' }}>
                        Save
                      </Caption>
                    </TouchableOpacity>
                  </View>
                </>
              )}
            </GlassCard>

            {/* Timezone Info */}
            <GlassCard style={[styles.card, { marginTop: 12, marginBottom: 32 }]}>
              <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                <Ionicons name="time-outline" size={20} color={theme.colors.primary} />
                <View style={{ marginLeft: 10, flex: 1 }}>
                  <BodyText weight="600" variant="small">Active User Timezone</BodyText>
                  <Caption color="muted">{timezone}</Caption>
                </View>
              </View>
            </GlassCard>
          </>
        )}
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
  sectionTitle: {
    marginBottom: 10,
    marginTop: 8,
  },
  card: {
    padding: 16,
    borderRadius: 16,
    marginBottom: 16,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 6,
  },
  labelCol: {
    flex: 1,
    marginRight: 12,
  },
  divider: {
    height: 1,
    marginVertical: 10,
  },
  timeInputsRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 12,
    marginTop: 8,
  },
  timeInputBox: {
    flex: 1,
  },
  input: {
    borderWidth: 1,
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  saveHoursBtn: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
});

