import React, { useState, useMemo } from 'react';
import {
  View,
  StyleSheet,
  Modal,
  TouchableOpacity,
  ScrollView,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { Habit } from '../../types/habit';
import { useHabitStats, useHabitCheckIn, useUndoHabitCheckIn } from '../../hooks/useHabits';
import { GlassCard } from '../glass/GlassCard';
import { Heading, BodyText, Caption } from '../common/Typography';
import { ConfirmationModal } from '../feedback/FeedbackComponents';

export interface HabitDetailsModalProps {
  visible: boolean;
  habit: Habit | null;
  onClose: () => void;
  onEdit: (habit: Habit) => void;
  onDelete: (habitId: string) => Promise<void>;
  onCheckInChange?: () => void;
}

export const HabitDetailsModal: React.FC<HabitDetailsModalProps> = ({
  visible,
  habit,
  onClose,
  onEdit,
  onDelete,
  onCheckInChange,
}) => {
  const { theme } = useTheme();

  const [confirmDelete, setConfirmDelete] = useState(false);
  const [calendarOffset, setCalendarOffset] = useState<number>(0); // 0 = current month, -1 = last month

  const habitId = habit?.id || null;
  const { data: statsData, isLoading: isStatsLoading } = useHabitStats(habitId);
  const checkInMutation = useHabitCheckIn();
  const undoCheckInMutation = useUndoHabitCheckIn();

  const accentColor = habit?.color_hex || theme.colors.primary;

  // Calendar month calculation
  const calendarInfo = useMemo(() => {
    const today = new Date();
    const targetMonth = new Date(today.getFullYear(), today.getMonth() + calendarOffset, 1);
    const year = targetMonth.getFullYear();
    const month = targetMonth.getMonth();

    const monthName = targetMonth.toLocaleString('default', { month: 'long', year: 'numeric' });
    const firstDayIndex = (new Date(year, month, 1).getDay() + 6) % 7; // Monday = 0
    const totalDays = new Date(year, month + 1, 0).getDate();

    return { year, month, monthName, firstDayIndex, totalDays };
  }, [calendarOffset]);

  // Set of completed date strings YYYY-MM-DD from recent logs
  const completedDateStrings = useMemo(() => {
    const logs = statsData?.recent_logs || [];
    return new Set(
      logs.filter((l) => l.completed).map((l) => l.log_date)
    );
  }, [statsData]);

  if (!habit) return null;

  const stats = statsData?.stats || {
    current_streak: habit.current_streak,
    longest_streak: habit.longest_streak,
    total_completed_days: habit.current_streak > 0 ? 1 : 0,
    completion_rate: 0,
    weekly_consistency: 0,
    monthly_consistency: 0,
  };

  const handleToggleToday = async () => {
    if (!habit) return;
    const todayStr = new Date().toISOString().split('T')[0];

    if (habit.completed_today && habit.today_log_id) {
      await undoCheckInMutation.mutateAsync({
        habitId: habit.id,
        logId: habit.today_log_id,
      });
    } else {
      await checkInMutation.mutateAsync({
        habitId: habit.id,
        payload: { log_date: todayStr, completed: true },
      });
    }
    if (onCheckInChange) {
      onCheckInChange();
    }
  };

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <View style={styles.overlay}>
        <TouchableOpacity style={styles.backdrop} activeOpacity={1} onPress={onClose} />

        <GlassCard elevation="floating" style={styles.container}>
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.headerTitleRow}>
              <View
                style={[
                  styles.iconCircle,
                  { backgroundColor: `${accentColor}18`, borderColor: accentColor },
                ]}
              >
                <Ionicons
                  name={(habit.icon as any) || 'flame'}
                  size={24}
                  color={accentColor}
                />
              </View>
              <View style={styles.headerText}>
                <Heading level={2} numberOfLines={1}>
                  {habit.title}
                </Heading>
                <Caption color="secondary">
                  {habit.frequency === 'daily'
                    ? 'Daily Routine'
                    : habit.frequency === 'weekdays'
                    ? 'Weekdays (Mon–Fri)'
                    : `Weekly Target (${habit.target_days_per_week} days/wk)`}
                </Caption>
              </View>
            </View>

            <TouchableOpacity
              onPress={onClose}
              style={[styles.closeBtn, { borderColor: theme.colors.glassBorder }]}
              accessibilityRole="button"
            >
              <Ionicons name="close" size={20} color={theme.colors.textPrimary} />
            </TouchableOpacity>
          </View>

          <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollBody}>
            {habit.description ? (
              <BodyText color="secondary" style={styles.description}>
                {habit.description}
              </BodyText>
            ) : null}

            {/* Quick Today Action */}
            <TouchableOpacity
              onPress={handleToggleToday}
              activeOpacity={0.85}
              style={[
                styles.todayBanner,
                {
                  backgroundColor: habit.completed_today
                    ? `${theme.colors.success}15`
                    : `${accentColor}10`,
                  borderColor: habit.completed_today ? theme.colors.success : accentColor,
                },
              ]}
            >
              <View style={styles.todayBannerLeft}>
                <View
                  style={[
                    styles.checkCircle,
                    {
                      backgroundColor: habit.completed_today
                        ? theme.colors.success
                        : 'transparent',
                      borderColor: habit.completed_today ? theme.colors.success : accentColor,
                    },
                  ]}
                >
                  {habit.completed_today && (
                    <Ionicons name="checkmark" size={16} color="#FFFFFF" />
                  )}
                </View>
                <View>
                  <BodyText weight="600">
                    {habit.completed_today ? 'Completed Today!' : 'Check In for Today'}
                  </BodyText>
                  <Caption color="secondary">
                    {habit.completed_today
                      ? 'Tap to undo today’s log'
                      : 'Keep your momentum alive'}
                  </Caption>
                </View>
              </View>
              <Ionicons
                name={habit.completed_today ? 'checkmark-circle' : 'chevron-forward'}
                size={22}
                color={habit.completed_today ? theme.colors.success : accentColor}
              />
            </TouchableOpacity>

            {/* Streak & Consistency Metrics */}
            <View style={styles.metricsRow}>
              <View
                style={[
                  styles.metricCard,
                  { backgroundColor: theme.colors.glassBackgroundSolid, borderColor: theme.colors.glassBorder },
                ]}
              >
                <Heading level={2} style={{ color: theme.colors.warning }}>
                  {stats.current_streak} 🔥
                </Heading>
                <Caption color="secondary">Current Streak</Caption>
              </View>

              <View
                style={[
                  styles.metricCard,
                  { backgroundColor: theme.colors.glassBackgroundSolid, borderColor: theme.colors.glassBorder },
                ]}
              >
                <Heading level={2} style={{ color: accentColor }}>
                  {stats.longest_streak} 🏆
                </Heading>
                <Caption color="secondary">Best Streak</Caption>
              </View>

              <View
                style={[
                  styles.metricCard,
                  { backgroundColor: theme.colors.glassBackgroundSolid, borderColor: theme.colors.glassBorder },
                ]}
              >
                <Heading level={2} style={{ color: theme.colors.success }}>
                  {stats.monthly_consistency}%
                </Heading>
                <Caption color="secondary">Consistency</Caption>
              </View>
            </View>

            {/* Calendar Visualization */}
            <View
              style={[
                styles.calendarSection,
                { backgroundColor: theme.colors.glassBackgroundSolid, borderColor: theme.colors.glassBorder },
              ]}
            >
              <View style={styles.calendarHeader}>
                <Caption weight="700" style={styles.calendarTitle}>
                  {calendarInfo.monthName}
                </Caption>
                <View style={styles.monthNav}>
                  <TouchableOpacity
                    onPress={() => setCalendarOffset((prev) => prev - 1)}
                    style={[styles.navBtn, { borderColor: theme.colors.glassBorder }]}
                  >
                    <Ionicons name="chevron-back" size={16} color={theme.colors.textPrimary} />
                  </TouchableOpacity>
                  <TouchableOpacity
                    onPress={() => setCalendarOffset((prev) => Math.min(0, prev + 1))}
                    disabled={calendarOffset >= 0}
                    style={[
                      styles.navBtn,
                      { borderColor: theme.colors.glassBorder, opacity: calendarOffset >= 0 ? 0.3 : 1 },
                    ]}
                  >
                    <Ionicons name="chevron-forward" size={16} color={theme.colors.textPrimary} />
                  </TouchableOpacity>
                </View>
              </View>

              {/* Day Name Row */}
              <View style={styles.weekNamesRow}>
                {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, idx) => (
                  <Caption
                    key={idx}
                    color="secondary"
                    align="center"
                    style={styles.weekDayHeader}
                  >
                    {day}
                  </Caption>
                ))}
              </View>

              {/* Calendar Grid */}
              <View style={styles.calendarGrid}>
                {/* Empty leading cells */}
                {Array.from({ length: calendarInfo.firstDayIndex }).map((_, i) => (
                  <View key={`lead-${i}`} style={styles.dayCell} />
                ))}

                {/* Actual day cells */}
                {Array.from({ length: calendarInfo.totalDays }).map((_, i) => {
                  const dayNum = i + 1;
                  const dObj = new Date(calendarInfo.year, calendarInfo.month, dayNum);
                  const dStr = `${calendarInfo.year}-${String(calendarInfo.month + 1).padStart(2, '0')}-${String(dayNum).padStart(2, '0')}`;
                  const isCompleted = completedDateStrings.has(dStr);
                  const isToday =
                    new Date().toISOString().split('T')[0] === dStr;
                  const isFuture = dObj > new Date();
                  const isWeekend = dObj.getDay() === 0 || dObj.getDay() === 6;
                  const isUnscheduled = habit.frequency === 'weekdays' && isWeekend;
                  const isMissed = !isFuture && !isCompleted && !isUnscheduled;

                  return (
                    <View
                      key={`day-${dayNum}`}
                      style={[
                        styles.dayCell,
                        isCompleted && {
                          backgroundColor: `${theme.colors.success}25`,
                          borderColor: theme.colors.success,
                        },
                        isToday &&
                          !isCompleted && {
                            borderColor: accentColor,
                            borderWidth: 1.5,
                          },
                        isUnscheduled && {
                          backgroundColor: theme.colors.surfaceSubtle,
                          opacity: 0.5,
                        },
                      ]}
                    >
                      <Caption
                        weight={isCompleted || isToday ? '700' : '400'}
                        style={{
                          color: isCompleted
                            ? theme.colors.success
                            : isFuture
                            ? theme.colors.textMuted
                            : isMissed
                            ? theme.colors.textSecondary
                            : theme.colors.textPrimary,
                        }}
                      >
                        {dayNum}
                      </Caption>
                      {isCompleted && (
                        <View style={[styles.dot, { backgroundColor: theme.colors.success }]} />
                      )}
                    </View>
                  );
                })}
              </View>

              {/* Legend */}
              <View style={styles.legendRow}>
                <View style={styles.legendItem}>
                  <View style={[styles.legendBox, { backgroundColor: theme.colors.success }]} />
                  <Caption color="secondary">Completed</Caption>
                </View>
                <View style={styles.legendItem}>
                  <View style={[styles.legendBox, { backgroundColor: theme.colors.surfaceSubtle }]} />
                  <Caption color="secondary">Unscheduled</Caption>
                </View>
                <View style={styles.legendItem}>
                  <View style={[styles.legendBox, { borderColor: theme.colors.glassBorder, borderWidth: 1 }]} />
                  <Caption color="secondary">Missed / Empty</Caption>
                </View>
              </View>
            </View>

            {/* Bottom Edit & Delete Actions */}
            <View style={styles.footerActions}>
              <TouchableOpacity
                onPress={() => {
                  onClose();
                  onEdit(habit);
                }}
                style={[
                  styles.actionButton,
                  { backgroundColor: theme.colors.glassBackgroundSolid, borderColor: theme.colors.glassBorder },
                ]}
              >
                <Ionicons name="pencil-outline" size={18} color={theme.colors.textPrimary} />
                <BodyText weight="600" style={{ marginLeft: 6 }}>
                  Edit Habit
                </BodyText>
              </TouchableOpacity>

              <TouchableOpacity
                onPress={() => setConfirmDelete(true)}
                style={[
                  styles.actionButton,
                  { backgroundColor: `${theme.colors.error}10`, borderColor: `${theme.colors.error}30` },
                ]}
              >
                <Ionicons name="trash-outline" size={18} color={theme.colors.error} />
                <BodyText weight="600" style={{ color: theme.colors.error, marginLeft: 6 }}>
                  Delete
                </BodyText>
              </TouchableOpacity>
            </View>
          </ScrollView>
        </GlassCard>

        {/* Delete Confirmation Alert */}
        <ConfirmationModal
          visible={confirmDelete}
          title="Delete Habit?"
          message={`Are you sure you want to delete "${habit.title}"? All streak counts and check-in history will be permanently deleted.`}
          confirmLabel="Delete"
          cancelLabel="Cancel"
          isDestructive
          onCancel={() => setConfirmDelete(false)}
          onConfirm={async () => {
            setConfirmDelete(false);
            await onDelete(habit.id);
            onClose();
          }}
        />
      </View>
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
  container: {
    maxHeight: '92%',
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
  headerTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: 12,
  },
  iconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 1.5,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  headerText: {
    flex: 1,
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
  description: {
    marginBottom: 16,
    lineHeight: 22,
  },
  todayBanner: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 14,
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 16,
  },
  todayBannerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  checkCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  metricsRow: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 16,
  },
  metricCard: {
    flex: 1,
    padding: 12,
    borderRadius: 16,
    borderWidth: 1,
    alignItems: 'center',
  },
  calendarSection: {
    padding: 16,
    borderRadius: 20,
    borderWidth: 1,
    marginBottom: 20,
  },
  calendarHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  calendarTitle: {
    fontSize: 14,
    letterSpacing: 0.5,
  },
  monthNav: {
    flexDirection: 'row',
    gap: 6,
  },
  navBtn: {
    width: 30,
    height: 30,
    borderRadius: 15,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  weekNamesRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 8,
  },
  weekDayHeader: {
    width: 36,
    fontWeight: '600',
  },
  calendarGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'flex-start',
  },
  dayCell: {
    width: '14.28%',
    height: 36,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'transparent',
    marginBottom: 4,
  },
  dot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    marginTop: 2,
  },
  legendRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: 'rgba(150, 150, 150, 0.2)',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  legendBox: {
    width: 12,
    height: 12,
    borderRadius: 3,
  },
  footerActions: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 14,
    borderWidth: 1,
  },
});
