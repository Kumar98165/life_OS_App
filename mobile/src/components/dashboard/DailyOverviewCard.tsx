import React from 'react';
import { View, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../theme';
import { GlassCard } from '../glass/GlassCard';
import { Heading, BodyText, Caption } from '../common/Typography';
import { DailyTaskProgress } from '../../types';

export interface DailyOverviewCardProps {
  progress: DailyTaskProgress;
}

export const DailyOverviewCard: React.FC<DailyOverviewCardProps> = ({ progress }) => {
  const { theme } = useTheme();
  const { completed, total, percentage, motivationalMessage } = progress;

  return (
    <GlassCard elevation="floating" style={styles.card}>
      {/* Header Row */}
      <View style={styles.headerRow}>
        <View>
          <Caption color="secondary" style={styles.sectionLabel}>
            DAILY PROGRESS
          </Caption>
          <Heading level={2} style={styles.title}>
            Today's Overview
          </Heading>
        </View>
        <View
          style={[
            styles.percentagePill,
            { backgroundColor: `${theme.colors.primary}18` },
          ]}
        >
          <Heading level={3} style={{ color: theme.colors.primary }}>
            {percentage}%
          </Heading>
        </View>
      </View>

      {/* Stats counter */}
      <View style={styles.statsRow}>
        <BodyText weight="600" color="primary">
          {total === 0
            ? '0 tasks scheduled'
            : `${completed} of ${total} tasks completed`}
        </BodyText>
        <Caption color="secondary">
          {total === 0 ? 'Rest day' : `${total - completed} remaining`}
        </Caption>
      </View>

      {/* Progress Bar */}
      <View
        style={[
          styles.progressBarBg,
          { backgroundColor: theme.colors.surfaceSubtle },
        ]}
      >
        <LinearGradient
          colors={[theme.colors.primary, theme.colors.primaryDark]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={[
            styles.progressBarFill,
            {
              width: `${Math.min(Math.max(percentage, total > 0 ? 3 : 0), 100)}%`,
            },
          ]}
        />
      </View>

      {/* Motivational message */}
      <View style={styles.motivationRow}>
        <BodyText variant="small" color="secondary" style={styles.motivationText}>
          {motivationalMessage}
        </BodyText>
      </View>
    </GlassCard>
  );
};

const styles = StyleSheet.create({
  card: {
    padding: 20,
    marginBottom: 20,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionLabel: {
    letterSpacing: 0.8,
    fontWeight: '600',
    marginBottom: 2,
  },
  title: {
    marginTop: 2,
  },
  percentagePill: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  progressBarBg: {
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 14,
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  motivationRow: {
    paddingTop: 4,
  },
  motivationText: {
    lineHeight: 18,
  },
});

