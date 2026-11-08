import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import { RootNavigationProp } from '../../navigation/types';
import { DatePeriod } from '../../types/analytics';
import { useHabitAnalytics } from '../../hooks/useAnalytics';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  SkeletonLoader,
} from '../../components';

const PERIODS: { label: string; value: DatePeriod }[] = [
  { label: 'Week', value: 'week' },
  { label: 'Month', value: 'month' },
  { label: 'Year', value: 'year' },
];

export const HabitAnalyticsScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<RootNavigationProp>();
  const [selectedPeriod, setSelectedPeriod] = useState<DatePeriod>('week');

  const {
    data: habits,
    isLoading,
    refetch,
    isRefetching,
  } = useHabitAnalytics({ period: selectedPeriod });

  return (
    <SafeAreaContainer style={[styles.container, { backgroundColor: theme.colors.background }]}>
      {/* Header */}
      <View style={styles.headerRow}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
          accessibilityLabel="Go back"
        >
          <Ionicons name="arrow-back" size={22} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <Heading level={2} style={styles.title}>
          Habit Consistency
        </Heading>
        <View style={styles.backButton} />
      </View>

      {/* Period Tabs */}
      <View style={styles.periodRow}>
        {PERIODS.map((p) => {
          const isActive = selectedPeriod === p.value;
          return (
            <TouchableOpacity
              key={p.value}
              style={[
                styles.periodTab,
                isActive && { backgroundColor: theme.colors.primary },
              ]}
              onPress={() => setSelectedPeriod(p.value)}
            >
              <BodyText
                style={[
                  styles.periodTabText,
                  { color: isActive ? '#FFFFFF' : theme.colors.textSecondary },
                ]}
              >
                {p.label}
              </BodyText>
            </TouchableOpacity>
          );
        })}
      </View>

      <ScrollContainer
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={() => {
              refetch();
            }}
            tintColor={theme.colors.primary}
          />
        }
        contentContainerStyle={styles.scrollContent}
      >
        {isLoading ? (
          <GlassCard style={styles.card}>
            <SkeletonLoader height={180} />
          </GlassCard>
        ) : (
          <>
            {/* Overall Consistency Card */}
            <GlassCard style={styles.card}>
              <Caption style={styles.sectionCaption}>ROUTINE ADHERENCE</Caption>
              <View style={styles.rateRow}>
                <Heading level={1} style={[styles.rateValue, { color: '#10B981' }]}>
                  {habits?.consistency_percentage ?? 100}%
                </Heading>
                <Caption style={styles.rateSubtitle}>Consistency Score</Caption>
              </View>

              <View style={styles.statsGrid}>
                <View style={styles.statCell}>
                  <Heading level={3} style={styles.statNum}>{habits?.total_active_habits ?? 0}</Heading>
                  <Caption>Active Habits</Caption>
                </View>
                <View style={styles.statCell}>
                  <Heading level={3} style={styles.statNum}>{habits?.total_completed_checkins ?? 0}</Heading>
                  <Caption>Check-ins Done</Caption>
                </View>
                <View style={styles.statCell}>
                  <Heading level={3} style={styles.statNum}>{habits?.best_streak_record ?? 0}d</Heading>
                  <Caption>Longest Streak</Caption>
                </View>
              </View>
            </GlassCard>

            {/* Individual Habit Breakdown */}
            <Heading level={3} style={styles.sectionHeading}>
              Habits Breakdown
            </Heading>

            {habits?.habits_performance?.map((h) => (
              <GlassCard key={h.id} style={styles.habitCard}>
                <View style={styles.habitHeader}>
                  <View style={[styles.habitColorDot, { backgroundColor: h.color_hex || '#6C63FF' }]} />
                  <View style={styles.habitTitleWrap}>
                    <BodyText style={styles.habitTitle}>{h.title}</BodyText>
                    <Caption>{h.frequency} • {h.current_streak}d streak (best: {h.best_streak}d)</Caption>
                  </View>
                  <Heading level={3} style={[styles.habitRate, { color: h.completion_percentage >= 80 ? '#10B981' : '#F59E0B' }]}>
                    {h.completion_percentage}%
                  </Heading>
                </View>
                <View style={styles.habitProgressTrack}>
                  <View
                    style={[
                      styles.habitProgressFill,
                      {
                        width: `${Math.min(100, h.completion_percentage)}%`,
                        backgroundColor: h.color_hex || '#6C63FF',
                      },
                    ]}
                  />
                </View>
                <Caption style={styles.habitCheckinCount}>
                  {h.completed_in_period} of {h.scheduled_in_period} check-ins completed
                </Caption>
              </GlassCard>
            ))}

            {/* Daily Habit Check-in Timeline */}
            <Heading level={3} style={styles.sectionHeading}>
              Daily Check-in Activity
            </Heading>
            <GlassCard style={styles.card}>
              <View style={styles.trendList}>
                {habits?.daily_trend?.map((item) => (
                  <View key={item.date} style={styles.trendItem}>
                    <Caption style={styles.trendItemDate}>{item.date}</Caption>
                    <View style={styles.trendTrack}>
                      <View
                        style={[
                          styles.trendFill,
                          {
                            width: `${Math.min(100, item.completed * 25)}%`,
                            backgroundColor: '#10B981',
                          },
                        ]}
                      />
                    </View>
                    <BodyText style={styles.trendCount}>{item.completed} logged</BodyText>
                  </View>
                ))}
              </View>
            </GlassCard>
          </>
        )}
      </ScrollContainer>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 8,
  },
  backButton: {
    width: 36,
    height: 36,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontWeight: '700',
  },
  periodRow: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginVertical: 10,
    gap: 8,
  },
  periodTab: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 12,
    alignItems: 'center',
    backgroundColor: '#E5E7EB30',
  },
  periodTabText: {
    fontSize: 13,
    fontWeight: '600',
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  card: {
    marginBottom: 16,
    padding: 16,
    borderRadius: 16,
  },
  sectionCaption: {
    fontSize: 11,
    fontWeight: '700',
    color: '#6B7280',
    letterSpacing: 1,
  },
  rateRow: {
    marginVertical: 10,
    alignItems: 'center',
  },
  rateValue: {
    fontSize: 42,
    fontWeight: '800',
  },
  rateSubtitle: {
    color: '#6B7280',
    marginTop: 2,
  },
  statsGrid: {
    flexDirection: 'row',
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    paddingVertical: 12,
    marginTop: 10,
  },
  statCell: {
    flex: 1,
    alignItems: 'center',
  },
  statNum: {
    fontSize: 18,
    fontWeight: '700',
  },
  sectionHeading: {
    marginTop: 8,
    marginBottom: 12,
    fontWeight: '700',
  },
  habitCard: {
    marginBottom: 12,
    padding: 14,
    borderRadius: 14,
  },
  habitHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  habitColorDot: {
    width: 14,
    height: 14,
    borderRadius: 7,
  },
  habitTitleWrap: {
    flex: 1,
  },
  habitTitle: {
    fontSize: 15,
    fontWeight: '600',
  },
  habitRate: {
    fontSize: 16,
    fontWeight: '700',
  },
  habitProgressTrack: {
    height: 6,
    backgroundColor: '#E5E7EB',
    borderRadius: 3,
    marginTop: 10,
    overflow: 'hidden',
  },
  habitProgressFill: {
    height: '100%',
    borderRadius: 3,
  },
  habitCheckinCount: {
    marginTop: 6,
    color: '#6B7280',
  },
  trendList: {
    gap: 12,
  },
  trendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  trendItemDate: {
    width: 80,
    fontSize: 12,
  },
  trendTrack: {
    flex: 1,
    height: 8,
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    overflow: 'hidden',
  },
  trendFill: {
    height: '100%',
    borderRadius: 4,
  },
  trendCount: {
    width: 70,
    textAlign: 'right',
    fontSize: 12,
    fontWeight: '600',
  },
});

