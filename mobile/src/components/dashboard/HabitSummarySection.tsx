import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { GlassCard } from '../glass/GlassCard';
import { SectionHeader } from '../layout/SectionHeader';
import { BodyText, Caption, Heading } from '../common/Typography';
import { HabitSummary } from '../../types';

export interface HabitSummarySectionProps {
  summary: HabitSummary;
  onViewAll?: () => void;
  onTrackHabit?: () => void;
}

export const HabitSummarySection: React.FC<HabitSummarySectionProps> = ({
  summary,
  onViewAll,
  onTrackHabit,
}) => {
  const { theme } = useTheme();
  const { activeCount, completedTodayCount, completionRate } = summary;

  return (
    <View style={styles.container}>
      <SectionHeader
        title="Habits & Streaks"
        actionText={activeCount > 0 ? 'View All' : undefined}
        onActionPress={onViewAll}
      />

      <GlassCard elevation="subtle" style={styles.card}>
        {activeCount === 0 ? (
          <View style={styles.emptyContent}>
            <View
              style={[
                styles.emptyIconCircle,
                { backgroundColor: `${theme.colors.success}15` },
              ]}
            >
              <Ionicons name="flame-outline" size={28} color={theme.colors.success} />
            </View>
            <BodyText weight="600" align="center" style={styles.emptyTitle}>
              No habits being tracked
            </BodyText>
            <Caption color="secondary" align="center" style={styles.emptyDesc}>
              Build consistent daily routines and track positive habit streaks.
            </Caption>
            {onTrackHabit && (
              <TouchableOpacity
                onPress={onTrackHabit}
                style={[
                  styles.addHabitBtn,
                  { borderColor: theme.colors.primary },
                ]}
                accessibilityRole="button"
              >
                <Caption weight="600" style={{ color: theme.colors.primary }}>
                  + Track a Habit
                </Caption>
              </TouchableOpacity>
            )}
          </View>
        ) : (
          <View style={styles.statsRow}>
            <View style={styles.statCol}>
              <Heading level={2} style={{ color: theme.colors.textPrimary }}>
                {activeCount}
              </Heading>
              <Caption color="secondary">Active Habits</Caption>
            </View>

            <View style={[styles.divider, { backgroundColor: theme.colors.glassBorder }]} />

            <View style={styles.statCol}>
              <Heading level={2} style={{ color: theme.colors.success }}>
                {completedTodayCount}
              </Heading>
              <Caption color="secondary">Done Today</Caption>
            </View>

            <View style={[styles.divider, { backgroundColor: theme.colors.glassBorder }]} />

            <View style={styles.statCol}>
              <Heading level={2} style={{ color: theme.colors.primary }}>
                {completionRate}%
              </Heading>
              <Caption color="secondary">Consistency</Caption>
            </View>
          </View>
        )}
      </GlassCard>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 24,
  },
  card: {
    padding: 18,
  },
  emptyContent: {
    alignItems: 'center',
    paddingVertical: 10,
  },
  emptyIconCircle: {
    width: 52,
    height: 52,
    borderRadius: 26,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
  },
  emptyTitle: {
    marginBottom: 4,
  },
  emptyDesc: {
    maxWidth: 240,
    lineHeight: 18,
    marginBottom: 12,
  },
  addHabitBtn: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 12,
    borderWidth: 1,
    marginTop: 4,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  statCol: {
    alignItems: 'center',
    flex: 1,
  },
  divider: {
    width: 1,
    height: 36,
  },
});
