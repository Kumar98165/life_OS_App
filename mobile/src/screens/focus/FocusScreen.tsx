import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  Modal,
  Alert,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  PrimaryButton,
  Toast,
} from '../../components';
import {
  useFocusGoal,
  useActiveFocusSession,
  useFocusStats,
  useFocusSessions,
} from '../../hooks/useFocus';
import { useTasks } from '../../hooks/useTasks';

export const FocusScreen: React.FC = () => {
  const { theme } = useTheme();
  const { data: goal, updateGoal } = useFocusGoal();
  const {
    data: activeSession,
    startSession,
    pauseSession,
    resumeSession,
    stopSession,
    logDistraction,
    isStarting,
    isStopping,
  } = useActiveFocusSession();
  const { data: stats, refetch: refetchStats } = useFocusStats();
  const { data: sessionHistory, refetch: refetchHistory } = useFocusSessions(1);
  const { data: tasksData } = useTasks();

  // Local Timer countdown state (seconds remaining)
  const [secondsLeft, setSecondsLeft] = useState<number>(25 * 60);
  const [timerRunning, setTimerRunning] = useState<boolean>(false);
  const [distractionModalVisible, setDistractionModalVisible] = useState<boolean>(false);
  const [distractionDesc, setDistractionDesc] = useState<string>('');
  const [distractionType, setDistractionType] = useState<'internal' | 'external'>('internal');
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [sessionTitle, setSessionTitle] = useState<string>('Deep Work Sprint');
  const [selectedPreset, setSelectedPreset] = useState<'25/5' | '50/10' | 'custom'>('25/5');
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const initialDurationSeconds = useRef<number>(25 * 60);

  // Sync state if active session exists from server (App restart recovery)
  useEffect(() => {
    if (activeSession) {
      const isPaused = activeSession.status === 'paused';
      setTimerRunning(!isPaused);

      // Estimate remaining seconds from start_time and target_duration_minutes
      const startMs = new Date(activeSession.start_time).getTime();
      const targetSec = activeSession.target_duration_minutes * 60;
      initialDurationSeconds.current = targetSec;

      const elapsedSec = isPaused
        ? activeSession.actual_duration_seconds
        : Math.max(0, Math.floor((Date.now() - startMs) / 1000));
      const rem = Math.max(0, targetSec - elapsedSec);
      setSecondsLeft(rem);
    } else {
      setTimerRunning(false);
      const defaultMins = selectedPreset === '25/5' ? 25 : selectedPreset === '50/10' ? 50 : (goal?.custom_work_minutes || 25);
      setSecondsLeft(defaultMins * 60);
      initialDurationSeconds.current = defaultMins * 60;
    }
  }, [activeSession, selectedPreset, goal]);

  // Tick interval
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (timerRunning && secondsLeft > 0) {
      interval = setInterval(() => {
        setSecondsLeft((prev) => {
          if (prev <= 1) {
            handleCompleteSession();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [timerRunning, secondsLeft, activeSession]);

  const handleStartSession = async (type: 'work' | 'short_break' | 'long_break' = 'work') => {
    try {
      let targetMins = 25;
      if (type === 'work') {
        targetMins = selectedPreset === '25/5' ? 25 : selectedPreset === '50/10' ? 50 : (goal?.custom_work_minutes || 25);
      } else if (type === 'short_break') {
        targetMins = selectedPreset === '25/5' ? 5 : selectedPreset === '50/10' ? 10 : (goal?.custom_break_minutes || 5);
      } else {
        targetMins = goal?.custom_long_break_minutes || 15;
      }

      initialDurationSeconds.current = targetMins * 60;
      setSecondsLeft(targetMins * 60);

      await startSession({
        title: type === 'work' ? sessionTitle : type === 'short_break' ? 'Short Rest' : 'Long Break',
        session_type: type,
        target_duration_minutes: targetMins,
        task_id: type === 'work' ? selectedTaskId : null,
      });
      setTimerRunning(true);
      setToastMessage(`Started ${type === 'work' ? 'focus' : 'break'} timer (${targetMins}m)`);
    } catch (err: any) {
      Alert.alert('Error', err?.message || 'Could not start focus session');
    }
  };

  const handlePauseResume = async () => {
    if (!activeSession) return;
    try {
      if (timerRunning) {
        await pauseSession(activeSession.id);
        setTimerRunning(false);
        setToastMessage('Session paused');
      } else {
        await resumeSession(activeSession.id);
        setTimerRunning(true);
        setToastMessage('Session resumed');
      }
    } catch (err: any) {
      Alert.alert('Error', err?.message || 'Failed to toggle pause');
    }
  };

  const handleStopEarly = async () => {
    if (!activeSession) return;
    Alert.alert(
      'Stop Focus Session',
      'Are you sure you want to stop early? Completed time will still be saved.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Stop',
          style: 'destructive',
          onPress: async () => {
            const elapsed = Math.max(0, initialDurationSeconds.current - secondsLeft);
            await stopSession({
              sessionId: activeSession.id,
              actual_duration_seconds: elapsed,
              notes: 'Stopped early',
            });
            setTimerRunning(false);
            refetchStats();
            refetchHistory();
            setToastMessage(`Logged ${Math.round(elapsed / 60)} minutes of focus!`);
          },
        },
      ]
    );
  };

  const handleCompleteSession = async () => {
    if (!activeSession) return;
    try {
      await stopSession({
        sessionId: activeSession.id,
        actual_duration_seconds: initialDurationSeconds.current,
        notes: 'Session finished successfully',
      });
      setTimerRunning(false);
      refetchStats();
      refetchHistory();
      setToastMessage('Pomodoro complete! Well done! 🎉');
    } catch (err: any) {
      console.warn('Complete session error', err);
    }
  };

  const handleLogDistraction = async () => {
    if (!activeSession || !distractionDesc.trim()) return;
    try {
      await logDistraction({
        sessionId: activeSession.id,
        distraction_type: distractionType,
        description: distractionDesc.trim(),
      });
      setDistractionDesc('');
      setDistractionModalVisible(false);
      setToastMessage('Distraction logged. Refocus on the task!');
    } catch (err: any) {
      Alert.alert('Error', err?.message || 'Failed to log distraction');
    }
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  return (
    <SafeAreaContainer edges={['top']}>
      <ScrollContainer contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Heading level={1}>Focus Mode</Heading>
          <Caption color="secondary">Pomodoro timer, deep work & distraction blocker</Caption>
        </View>

        {/* Stats Row */}
        <View style={styles.statsRow}>
          <GlassCard style={styles.statCard}>
            <Caption color="secondary">Today's Focus</Caption>
            <Heading level={2} style={{ color: theme.colors.primary }}>
              {stats?.today_minutes || 0}m
            </Heading>
            <Caption color="secondary">Target: {stats?.today_target_minutes || 120}m</Caption>
          </GlassCard>

          <GlassCard style={styles.statCard}>
            <Caption color="secondary">This Week</Caption>
            <Heading level={2} style={{ color: theme.colors.info }}>
              {stats?.week_minutes || 0}m
            </Heading>
            <Caption color="secondary">Target: {stats?.week_target_minutes || 600}m</Caption>
          </GlassCard>

          <GlassCard style={styles.statCard}>
            <Caption color="secondary">Total Hours</Caption>
            <Heading level={2} style={{ color: theme.colors.success }}>
              {stats?.total_focused_hours || 0}h
            </Heading>
            <Caption color="secondary">{stats?.completed_sessions_today || 0} sessions</Caption>
          </GlassCard>
        </View>

        {/* Active Timer Box */}
        <GlassCard elevation="floating" style={styles.timerCard}>
          {activeSession ? (
            <View style={styles.sessionHeader}>
              <View
                style={[
                  styles.badge,
                  {
                    backgroundColor:
                      activeSession.session_type === 'work'
                        ? `${theme.colors.primary}20`
                        : `${theme.colors.info}20`,
                  },
                ]}
              >
                <Caption weight="600" style={{ color: theme.colors.primary }}>
                  {activeSession.session_type.toUpperCase().replace('_', ' ')}
                </Caption>
              </View>
              <Heading level={3} style={styles.sessionTitle}>
                {activeSession.title}
              </Heading>
              {activeSession.task && (
                <Caption color="secondary" style={styles.linkedTaskText}>
                  Linked: {activeSession.task.title}
                </Caption>
              )}
            </View>
          ) : (
            <View style={styles.setupContainer}>
              <Caption color="secondary" style={styles.presetLabel}>
                CHOOSE PRESET
              </Caption>
              <View style={styles.presetsRow}>
                {(['25/5', '50/10', 'custom'] as const).map((p) => (
                  <TouchableOpacity
                    key={p}
                    style={[
                      styles.presetButton,
                      selectedPreset === p && {
                        backgroundColor: theme.colors.primary,
                        borderColor: theme.colors.primary,
                      },
                    ]}
                    onPress={() => setSelectedPreset(p)}
                  >
                    <Text
                      style={[
                        styles.presetButtonText,
                        selectedPreset === p && { color: '#fff', fontWeight: 'bold' },
                      ]}
                    >
                      {p === '25/5' ? '25 / 5m' : p === '50/10' ? '50 / 10m' : 'Custom'}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>

              <TextInput
                style={[styles.input, { borderColor: theme.colors.border, color: theme.colors.textPrimary }]}
                value={sessionTitle}
                onChangeText={setSessionTitle}
                placeholder="What are you focusing on?"
                placeholderTextColor={theme.colors.textMuted}
              />
            </View>
          )}

          {/* Huge Timer Display */}
          <View style={styles.timerDisplay}>
            <Text style={[styles.timerDigits, { color: theme.colors.textPrimary }]}>
              {formatTime(secondsLeft)}
            </Text>
          </View>

          {/* Action Buttons */}
          {activeSession ? (
            <View style={styles.controlsRow}>
              <TouchableOpacity
                style={[styles.actionBtn, { backgroundColor: theme.colors.surfaceSubtle }]}
                onPress={handlePauseResume}
              >
                <Ionicons
                  name={timerRunning ? 'pause' : 'play'}
                  size={24}
                  color={theme.colors.primary}
                />
                <Text style={[styles.actionBtnText, { color: theme.colors.textPrimary }]}>
                  {timerRunning ? 'Pause' : 'Resume'}
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.actionBtn, { backgroundColor: theme.colors.surfaceSubtle }]}
                onPress={() => setDistractionModalVisible(true)}
              >
                <Ionicons name="warning-outline" size={24} color="#f59e0b" />
                <Text style={[styles.actionBtnText, { color: theme.colors.textPrimary }]}>Distraction</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.actionBtn, { backgroundColor: '#ef444420' }]}
                onPress={handleStopEarly}
              >
                <Ionicons name="stop" size={24} color="#ef4444" />
                <Text style={[styles.actionBtnText, { color: '#ef4444' }]}>Stop</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View style={styles.startRow}>
              <TouchableOpacity
                style={[styles.startMainBtn, { backgroundColor: theme.colors.primary }]}
                onPress={() => handleStartSession('work')}
                disabled={isStarting}
              >
                <Ionicons name="play" size={20} color="#fff" />
                <Text style={styles.startMainBtnText}>Start Focus</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.startBreakBtn, { borderColor: theme.colors.border }]}
                onPress={() => handleStartSession('short_break')}
              >
                <Ionicons name="cafe-outline" size={18} color={theme.colors.textPrimary} />
                <Text style={[styles.startBreakBtnText, { color: theme.colors.textPrimary }]}>Break</Text>
              </TouchableOpacity>
            </View>
          )}
        </GlassCard>

        {/* Task linking suggestion */}
        {!activeSession && tasksData?.tasks && tasksData.tasks.length > 0 && (
          <GlassCard style={styles.taskListCard}>
            <Heading level={3} style={{ marginBottom: 8 }}>
              Link with a Task
            </Heading>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {tasksData.tasks.slice(0, 5).map((t) => (
                <TouchableOpacity
                  key={t.id}
                  style={[
                    styles.taskPill,
                    selectedTaskId === t.id && {
                      backgroundColor: theme.colors.primary,
                      borderColor: theme.colors.primary,
                    },
                  ]}
                  onPress={() => {
                    if (selectedTaskId === t.id) {
                      setSelectedTaskId(null);
                    } else {
                      setSelectedTaskId(t.id);
                      setSessionTitle(t.title);
                    }
                  }}
                >
                  <Text
                    numberOfLines={1}
                    style={[
                      styles.taskPillText,
                      selectedTaskId === t.id && { color: '#fff', fontWeight: 'bold' },
                    ]}
                  >
                    {t.title}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </GlassCard>
        )}

        {/* Recent Session History */}
        <View style={styles.historySection}>
          <Heading level={3} style={{ marginBottom: 12 }}>
            Recent Sessions
          </Heading>
          {sessionHistory?.sessions && sessionHistory.sessions.length > 0 ? (
            sessionHistory.sessions.slice(0, 5).map((s) => (
              <GlassCard key={s.id} style={styles.historyCard}>
                <View style={styles.historyTop}>
                  <View style={{ flex: 1 }}>
                    <BodyText weight="600">{s.title}</BodyText>
                    <Caption color="secondary">
                      {new Date(s.start_time).toLocaleDateString()} •{' '}
                      {Math.round(s.actual_duration_seconds / 60)}m focused
                    </Caption>
                  </View>
                  <View
                    style={[
                      styles.historyStatusBadge,
                      {
                        backgroundColor:
                          s.status === 'completed'
                            ? '#10b98120'
                            : s.status === 'active'
                            ? `${theme.colors.primary}20`
                            : '#ef444420',
                      },
                    ]}
                  >
                    <Caption
                      weight="600"
                      style={{
                        color:
                          s.status === 'completed'
                            ? '#10b981'
                            : s.status === 'active'
                            ? theme.colors.primary
                            : '#ef4444',
                      }}
                    >
                      {s.status}
                    </Caption>
                  </View>
                </View>
                {s.distraction_count > 0 && (
                  <Caption color="secondary" style={{ marginTop: 4 }}>
                    ⚠️ {s.distraction_count} distraction(s) logged
                  </Caption>
                )}
              </GlassCard>
            ))
          ) : (
            <Caption color="secondary">No recent focus sessions found.</Caption>
          )}
        </View>

        {/* Distraction Logging Modal */}
        <Modal
          visible={distractionModalVisible}
          transparent
          animationType="fade"
          onRequestClose={() => setDistractionModalVisible(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={[styles.modalCard, { backgroundColor: theme.colors.surface }]}>
              <Heading level={2} style={{ marginBottom: 8 }}>
                Log Distraction
              </Heading>
              <Caption color="secondary" style={{ marginBottom: 16 }}>
                Writing down distractions clears your head so you can refocus immediately.
              </Caption>

              <View style={styles.distractionTypeRow}>
                <TouchableOpacity
                  style={[
                    styles.typeBtn,
                    distractionType === 'internal' && { backgroundColor: theme.colors.primary },
                  ]}
                  onPress={() => setDistractionType('internal')}
                >
                  <Text
                    style={[
                      styles.typeBtnText,
                      distractionType === 'internal' && { color: '#fff', fontWeight: 'bold' },
                    ]}
                  >
                    Internal Urge / Thought
                  </Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[
                    styles.typeBtn,
                    distractionType === 'external' && { backgroundColor: theme.colors.primary },
                  ]}
                  onPress={() => setDistractionType('external')}
                >
                  <Text
                    style={[
                      styles.typeBtnText,
                      distractionType === 'external' && { color: '#fff', fontWeight: 'bold' },
                    ]}
                  >
                    External Interruption
                  </Text>
                </TouchableOpacity>
              </View>

              <TextInput
                style={[
                  styles.input,
                  { borderColor: theme.colors.border, color: theme.colors.textPrimary, height: 70 },
                ]}
                placeholder="What distracted you?"
                placeholderTextColor={theme.colors.textMuted}
                value={distractionDesc}
                onChangeText={setDistractionDesc}
                multiline
              />

              <View style={styles.modalActions}>
                <TouchableOpacity
                  style={[styles.cancelBtn, { borderColor: theme.colors.border }]}
                  onPress={() => setDistractionModalVisible(false)}
                >
                  <Text style={{ color: theme.colors.textPrimary }}>Cancel</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.saveBtn, { backgroundColor: theme.colors.primary }]}
                  onPress={handleLogDistraction}
                >
                  <Text style={{ color: '#fff', fontWeight: 'bold' }}>Save & Refocus</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>

        <Toast visible={!!toastMessage} message={toastMessage || ''} type="success" />
      </ScrollContainer>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  container: { paddingHorizontal: 16, paddingBottom: 100 },
  header: { marginVertical: 12 },
  statsRow: { flexDirection: 'row', gap: 8, marginBottom: 16 },
  statCard: { flex: 1, padding: 12, alignItems: 'center' },
  timerCard: { padding: 20, alignItems: 'center', marginBottom: 16 },
  sessionHeader: { alignItems: 'center', marginBottom: 12 },
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12, marginBottom: 6 },
  sessionTitle: { textAlign: 'center' },
  linkedTaskText: { marginTop: 4 },
  setupContainer: { width: '100%', marginBottom: 12 },
  presetLabel: { marginBottom: 6, fontWeight: '600' },
  presetsRow: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  presetButton: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ccc',
    alignItems: 'center',
  },
  presetButtonText: { fontSize: 13, color: '#666' },
  input: {
    width: '100%',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    marginBottom: 8,
  },
  timerDisplay: { marginVertical: 16 },
  timerDigits: { fontSize: 56, fontWeight: '700', letterSpacing: 2 },
  controlsRow: { flexDirection: 'row', gap: 12, marginTop: 8 },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 10,
  },
  actionBtnText: { fontSize: 14, fontWeight: '600' },
  startRow: { flexDirection: 'row', gap: 12, width: '100%', marginTop: 8 },
  startMainBtn: {
    flex: 2,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 12,
    borderRadius: 10,
  },
  startMainBtnText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  startBreakBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingVertical: 12,
    borderWidth: 1,
    borderRadius: 10,
  },
  startBreakBtnText: { fontSize: 14, fontWeight: '600' },
  taskListCard: { padding: 14, marginBottom: 16 },
  taskPill: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#ccc',
    marginRight: 8,
    maxWidth: 200,
  },
  taskPillText: { fontSize: 12, color: '#666' },
  historySection: { marginTop: 8 },
  historyCard: { padding: 12, marginBottom: 8 },
  historyTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  historyStatusBadge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8 },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    padding: 20,
  },
  modalCard: { padding: 20, borderRadius: 16 },
  distractionTypeRow: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  typeBtn: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ccc',
    alignItems: 'center',
  },
  typeBtnText: { fontSize: 12, color: '#666', textAlign: 'center' },
  modalActions: { flexDirection: 'row', gap: 12, marginTop: 12 },
  cancelBtn: { flex: 1, paddingVertical: 10, borderWidth: 1, borderRadius: 8, alignItems: 'center' },
  saveBtn: { flex: 1, paddingVertical: 10, borderRadius: 8, alignItems: 'center' },
});
