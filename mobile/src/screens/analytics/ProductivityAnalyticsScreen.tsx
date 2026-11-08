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
import { useProductivityAnalytics } from '../../hooks/useAnalytics';
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

export const ProductivityAnalyticsScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<RootNavigationProp>();
  const [selectedPeriod, setSelectedPeriod] = useState<DatePeriod>('week');

  const {
    data: prod,
    isLoading,
    refetch,
    isRefetching,
  } = useProductivityAnalytics({ period: selectedPeriod });

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
          Productivity Analytics
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
            {/* Task Velocity Card */}
            <GlassCard style={styles.card}>
              <Caption style={styles.sectionCaption}>TASK EXECUTION VELOCITY</Caption>
              <View style={styles.rateRow}>
                <Heading level={1} style={[styles.rateValue, { color: theme.colors.primary }]}>
                  {prod?.completion_percentage ?? 100}%
                </Heading>
                <Caption style={styles.rateSubtitle}>Completion Rate</Caption>
              </View>

              <View style={styles.statsGrid}>
                <View style={styles.statCell}>
                  <Heading level={3} style={styles.statNum}>{prod?.completed_tasks ?? 0}</Heading>
                  <Caption>Completed</Caption>
                </View>
                <View style={styles.statCell}>
                  <Heading level={3} style={styles.statNum}>{prod?.pending_tasks ?? 0}</Heading>
                  <Caption>Pending</Caption>
                </View>
                <View style={styles.statCell}>
                  <Heading
                    level={3}
                    style={[
                      styles.statNum,
                      (prod?.overdue_tasks ?? 0) > 0 && { color: '#EF4444' },
                    ]}
                  >
                    {prod?.overdue_tasks ?? 0}
                  </Heading>
                  <Caption>Overdue</Caption>
                </View>
                <View style={styles.statCell}>
                  <Heading level={3} style={styles.statNum}>{prod?.total_tasks ?? 0}</Heading>
                  <Caption>Total Created</Caption>
                </View>
              </View>
            </GlassCard>

            {/* Planner Adherence Card */}
            <GlassCard style={styles.card}>
              <Caption style={styles.sectionCaption}>CALENDAR & TIME BLOCKING</Caption>
              <View style={styles.rateRow}>
                <Heading level={1} style={[styles.rateValue, { color: '#10B981' }]}>
                  {prod?.planner_completion_percentage ?? 100}%
                </Heading>
                <Caption style={styles.rateSubtitle}>Schedule Adherence</Caption>
              </View>

              <View style={styles.plannerRow}>
                <View style={styles.plannerBlockInfo}>
                  <BodyText style={styles.plannerNum}>
                    {prod?.completed_planner_blocks ?? 0} / {prod?.total_planner_blocks ?? 0}
                  </BodyText>
                  <Caption>Scheduled Blocks Executed</Caption>
                </View>
              </View>

              {/* Block Type Breakdown */}
              {prod?.planner_distribution && prod.planner_distribution.length > 0 && (
                <View style={styles.distributionWrap}>
                  <Caption style={styles.distribTitle}>Block Type Distribution</Caption>
                  <View style={styles.distribChips}>
                    {prod.planner_distribution.map((dist) => (
                      <View key={dist.block_type} style={styles.distChip}>
                        <BodyText style={styles.distChipText}>
                          {dist.block_type}: {dist.count}
                        </BodyText>
                      </View>
                    ))}
                  </View>
                </View>
              )}
            </GlassCard>

            {/* Daily Trend List */}
            <Heading level={3} style={styles.sectionHeading}>
              Daily Completion History
            </Heading>
            <GlassCard style={styles.card}>
              <View style={styles.trendList}>
                {prod?.daily_completion_trend?.map((item) => (
                  <View key={item.date} style={styles.trendItem}>
                    <Caption style={styles.trendItemDate}>{item.date}</Caption>
                    <View style={styles.trendTrack}>
                      <View
                        style={[
                          styles.trendFill,
                          {
                            width: `${Math.min(100, item.completed * 20)}%`,
                            backgroundColor: theme.colors.primary,
                          },
                        ]}
                      />
                    </View>
                    <BodyText style={styles.trendCount}>{item.completed} done</BodyText>
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
  plannerRow: {
    alignItems: 'center',
    marginVertical: 8,
  },
  plannerBlockInfo: {
    alignItems: 'center',
  },
  plannerNum: {
    fontSize: 16,
    fontWeight: '700',
  },
  distributionWrap: {
    marginTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    paddingTop: 10,
  },
  distribTitle: {
    fontSize: 12,
    marginBottom: 6,
  },
  distribChips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  distChip: {
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  distChipText: {
    fontSize: 12,
    color: '#4F46E5',
    fontWeight: '600',
  },
  sectionHeading: {
    marginTop: 8,
    marginBottom: 12,
    fontWeight: '700',
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
    width: 60,
    textAlign: 'right',
    fontSize: 12,
    fontWeight: '600',
  },
});

