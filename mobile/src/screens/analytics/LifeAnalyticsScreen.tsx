import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import { RootNavigationProp } from '../../navigation/types';
import { DatePeriod } from '../../types/analytics';
import {
  useAnalyticsOverview,
  useLifeScore,
  useTrendsAnalytics,
} from '../../hooks/useAnalytics';
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

export const LifeAnalyticsScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<RootNavigationProp>();
  const [selectedPeriod, setSelectedPeriod] = useState<DatePeriod>('week');

  const {
    data: overview,
    isLoading: isOverviewLoading,
    refetch: refetchOverview,
    isRefetching,
  } = useAnalyticsOverview({ period: selectedPeriod });

  const {
    data: lifeScore,
    isLoading: isScoreLoading,
    refetch: refetchScore,
  } = useLifeScore({ period: selectedPeriod });

  const {
    data: trends,
    isLoading: isTrendsLoading,
    refetch: refetchTrends,
  } = useTrendsAnalytics({ period: selectedPeriod });

  const handleRefresh = async () => {
    await Promise.all([refetchOverview(), refetchScore(), refetchTrends()]);
  };

  const getTierColor = (tier?: string) => {
    switch (tier) {
      case 'Exceptional':
        return '#10B981';
      case 'Strong':
        return '#6C63FF';
      case 'Balanced':
        return '#F59E0B';
      default:
        return '#3B82F6';
    }
  };

  return (
    <SafeAreaContainer style={[styles.container, { backgroundColor: theme.colors.background }]}>
      {/* Top Header */}
      <View style={styles.headerRow}>
        <View>
          <Heading level={2} style={styles.title}>
            Life Analytics
          </Heading>
          <Caption style={styles.subtitle}>Verified Personal Insights & Score</Caption>
        </View>
        <TouchableOpacity
          style={[styles.aiButton, { backgroundColor: theme.colors.primary }]}
          onPress={() => navigation.navigate('LifeInsights')}
          accessibilityLabel="AI Insights"
        >
          <Ionicons name="sparkles" size={16} color="#FFFFFF" />
          <BodyText style={styles.aiButtonText}>AI Insights</BodyText>
        </TouchableOpacity>
      </View>

      {/* Period Selector Tabs */}
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
            onRefresh={handleRefresh}
            tintColor={theme.colors.primary}
          />
        }
        contentContainerStyle={styles.scrollContent}
      >
        {/* Life Score Gauge Card */}
        {isScoreLoading ? (
          <GlassCard style={styles.card}>
            <SkeletonLoader height={140} />
          </GlassCard>
        ) : (
          <GlassCard style={styles.card}>
            <View style={styles.scoreHeader}>
              <View>
                <Caption style={styles.scoreLabel}>OVERALL LIFE SCORE</Caption>
                <View style={styles.scoreRow}>
                  <Heading level={1} style={[styles.scoreValue, { color: getTierColor(lifeScore?.score_tier) }]}>
                    {lifeScore?.overall_score ?? 100}
                  </Heading>
                  <Heading level={3} style={styles.scoreDenominator}>
                    / 100
                  </Heading>
                </View>
              </View>
              <View
                style={[
                  styles.tierBadge,
                  { backgroundColor: `${getTierColor(lifeScore?.score_tier)}20` },
                ]}
              >
                <BodyText
                  style={[
                    styles.tierText,
                    { color: getTierColor(lifeScore?.score_tier) },
                  ]}
                >
                  {lifeScore?.score_tier ?? 'Balanced'}
                </BodyText>
              </View>
            </View>

            {/* Score Dimensions Progress */}
            <View style={styles.dimensionsList}>
              {lifeScore?.dimensions?.map((dim) => (
                <View key={dim.name} style={styles.dimRow}>
                  <View style={styles.dimLabelRow}>
                    <BodyText style={styles.dimName}>{dim.name}</BodyText>
                    <Caption style={styles.dimScore}>
                      {dim.score}% ({dim.weight}% wt)
                    </Caption>
                  </View>
                  <View style={styles.dimProgressTrack}>
                    <View
                      style={[
                        styles.dimProgressBar,
                        {
                          width: `${Math.min(100, Math.max(0, dim.score))}%`,
                          backgroundColor:
                            dim.status === 'unpenalized_no_data'
                              ? '#9CA3AF'
                              : dim.score >= 80
                              ? '#10B981'
                              : dim.score >= 50
                              ? '#F59E0B'
                              : '#EF4444',
                        },
                      ]}
                    />
                  </View>
                </View>
              ))}
            </View>

            <Caption style={styles.disclaimerText}>
              {lifeScore?.disclaimer ??
                'This score represents personal habit and goal progress and is not a medical or psychological assessment.'}
            </Caption>
          </GlassCard>
        )}

        {/* AI Executive Summary Banner */}
        <TouchableOpacity
          onPress={() => navigation.navigate('LifeInsights')}
          activeOpacity={0.85}
        >
          <GlassCard style={[styles.card, styles.aiBanner]}>
            <View style={styles.aiBannerHeader}>
              <View style={styles.aiIconWrapper}>
                <Ionicons name="bulb-outline" size={20} color="#6C63FF" />
              </View>
              <View style={styles.aiBannerTitleWrap}>
                <BodyText style={styles.aiBannerTitle}>Local AI Personal Insights</BodyText>
                <Caption style={styles.aiBannerSub}>Synthesized with Ollama Qwen 2.5</Caption>
              </View>
              <Ionicons name="chevron-forward" size={18} color="#9CA3AF" />
            </View>
            <BodyText style={styles.aiBannerSnippet}>
              {overview
                ? `You reached a ${overview.life_score}/100 Life Score with ${overview.productivity_summary.completion_percentage}% task velocity and ${overview.habits_summary.consistency_percentage}% habit consistency.`
                : 'Tap to review synthesized suggestions and action points.'}
            </BodyText>
          </GlassCard>
        </TouchableOpacity>

        {/* 4 Domain Cards Grid */}
        <Heading level={3} style={styles.sectionTitle}>
          Domain Analytics
        </Heading>

        {/* Productivity Card */}
        <TouchableOpacity
          onPress={() => navigation.navigate('ProductivityAnalytics')}
          activeOpacity={0.8}
        >
          <GlassCard style={styles.domainCard}>
            <View style={styles.domainHeader}>
              <View style={[styles.domainIcon, { backgroundColor: '#EEF2FF' }]}>
                <Ionicons name="checkmark-done" size={20} color="#6C63FF" />
              </View>
              <View style={styles.domainTitleWrap}>
                <BodyText style={styles.domainTitle}>Productivity & Planning</BodyText>
                <Caption>Tasks, Calendar & Time Blocking</Caption>
              </View>
              <Ionicons name="chevron-forward" size={18} color="#9CA3AF" />
            </View>
            <View style={styles.metricStatsRow}>
              <View style={styles.statBox}>
                <Heading level={3} style={styles.statNumber}>
                  {overview?.productivity_summary.completed_tasks ?? 0}
                </Heading>
                <Caption>Tasks Done</Caption>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statBox}>
                <Heading level={3} style={styles.statNumber}>
                  {overview?.productivity_summary.completion_percentage ?? 100}%
                </Heading>
                <Caption>Completion Rate</Caption>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statBox}>
                <Heading level={3} style={styles.statNumber}>
                  {overview?.productivity_summary.completed_planner_blocks ?? 0}
                </Heading>
                <Caption>Blocks Executed</Caption>
              </View>
            </View>
          </GlassCard>
        </TouchableOpacity>

        {/* Habit Card */}
        <TouchableOpacity
          onPress={() => navigation.navigate('HabitAnalytics')}
          activeOpacity={0.8}
        >
          <GlassCard style={styles.domainCard}>
            <View style={styles.domainHeader}>
              <View style={[styles.domainIcon, { backgroundColor: '#ECFDF5' }]}>
                <Ionicons name="flame" size={20} color="#10B981" />
              </View>
              <View style={styles.domainTitleWrap}>
                <BodyText style={styles.domainTitle}>Habits & Streaks</BodyText>
                <Caption>Routines & Daily Consistency</Caption>
              </View>
              <Ionicons name="chevron-forward" size={18} color="#9CA3AF" />
            </View>
            <View style={styles.metricStatsRow}>
              <View style={styles.statBox}>
                <Heading level={3} style={styles.statNumber}>
                  {overview?.habits_summary.consistency_percentage ?? 100}%
                </Heading>
                <Caption>Consistency</Caption>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statBox}>
                <Heading level={3} style={styles.statNumber}>
                  {overview?.habits_summary.active_habits ?? 0}
                </Heading>
                <Caption>Active Habits</Caption>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statBox}>
                <Heading level={3} style={styles.statNumber}>
                  {overview?.habits_summary.best_streak ?? 0}d
                </Heading>
                <Caption>Best Streak</Caption>
              </View>
            </View>
          </GlassCard>
        </TouchableOpacity>

        {/* Goals Card */}
        <TouchableOpacity
          onPress={() => navigation.navigate('GoalsAnalytics')}
          activeOpacity={0.8}
        >
          <GlassCard style={styles.domainCard}>
            <View style={styles.domainHeader}>
              <View style={[styles.domainIcon, { backgroundColor: '#FEF3C7' }]}>
                <Ionicons name="flag" size={20} color="#F59E0B" />
              </View>
              <View style={styles.domainTitleWrap}>
                <BodyText style={styles.domainTitle}>Goals & Milestones</BodyText>
                <Caption>Objectives & Long-term Targets</Caption>
              </View>
              <Ionicons name="chevron-forward" size={18} color="#9CA3AF" />
            </View>
            <View style={styles.metricStatsRow}>
              <View style={styles.statBox}>
                <Heading level={3} style={styles.statNumber}>
                  {overview?.goals_summary.active_goals ?? 0}
                </Heading>
                <Caption>Active Goals</Caption>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statBox}>
                <Heading level={3} style={styles.statNumber}>
                  {overview?.goals_summary.completion_percentage ?? 0}%
                </Heading>
                <Caption>Completed</Caption>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statBox}>
                <Heading level={3} style={styles.statNumber}>
                  {overview?.goals_summary.upcoming_deadlines_count ?? 0}
                </Heading>
                <Caption>Due Soon</Caption>
              </View>
            </View>
          </GlassCard>
        </TouchableOpacity>

        {/* Finance Card */}
        <TouchableOpacity
          onPress={() => navigation.navigate('FinanceAnalytics')}
          activeOpacity={0.8}
        >
          <GlassCard style={styles.domainCard}>
            <View style={styles.domainHeader}>
              <View style={[styles.domainIcon, { backgroundColor: '#F0FDF4' }]}>
                <Ionicons name="wallet" size={20} color="#16A34A" />
              </View>
              <View style={styles.domainTitleWrap}>
                <BodyText style={styles.domainTitle}>Financial Discipline</BodyText>
                <Caption>Cash Flow, Savings & Budgets</Caption>
              </View>
              <Ionicons name="chevron-forward" size={18} color="#9CA3AF" />
            </View>
            <View style={styles.metricStatsRow}>
              <View style={styles.statBox}>
                <Heading level={3} style={styles.statNumber}>
                  ${overview?.finance_summary.net_savings ?? '0.00'}
                </Heading>
                <Caption>Net Savings</Caption>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statBox}>
                <Heading level={3} style={styles.statNumber}>
                  {overview?.finance_summary.savings_rate ?? 0}%
                </Heading>
                <Caption>Savings Rate</Caption>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statBox}>
                <Heading level={3} style={styles.statNumber}>
                  ${overview?.finance_summary.total_expenses ?? '0.00'}
                </Heading>
                <Caption>Expenses</Caption>
              </View>
            </View>
          </GlassCard>
        </TouchableOpacity>

        {/* Activity Trend Series */}
        <Heading level={3} style={styles.sectionTitle}>
          Activity Velocity Trend
        </Heading>
        <GlassCard style={styles.card}>
          {isTrendsLoading ? (
            <SkeletonLoader height={100} />
          ) : (
            <View style={styles.trendList}>
              {trends?.daily_trends?.map((item) => (
                <View key={item.date} style={styles.trendRow}>
                  <Caption style={styles.trendDate}>{item.date.slice(5)}</Caption>
                  <View style={styles.trendBarContainer}>
                    <View
                      style={[
                        styles.trendBarTasks,
                        { flex: Math.max(item.tasks_completed, 0.1) },
                      ]}
                    />
                    <View
                      style={[
                        styles.trendBarHabits,
                        { flex: Math.max(item.habits_completed, 0.1) },
                      ]}
                    />
                  </View>
                  <Caption style={styles.trendTotal}>{item.total_activity}</Caption>
                </View>
              ))}
              <View style={styles.trendLegend}>
                <View style={styles.legendItem}>
                  <View style={[styles.legendDot, { backgroundColor: '#6C63FF' }]} />
                  <Caption>Tasks</Caption>
                </View>
                <View style={styles.legendItem}>
                  <View style={[styles.legendDot, { backgroundColor: '#10B981' }]} />
                  <Caption>Habits</Caption>
                </View>
              </View>
            </View>
          )}
        </GlassCard>
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
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 8,
  },
  title: {
    fontWeight: '700',
  },
  subtitle: {
    color: '#6B7280',
    marginTop: 2,
  },
  aiButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 20,
    gap: 6,
  },
  aiButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 13,
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
  scoreHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  scoreLabel: {
    letterSpacing: 1,
    color: '#6B7280',
    fontWeight: '700',
    fontSize: 11,
  },
  scoreRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginTop: 4,
  },
  scoreValue: {
    fontSize: 38,
    fontWeight: '800',
  },
  scoreDenominator: {
    fontSize: 18,
    color: '#9CA3AF',
    marginLeft: 4,
  },
  tierBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  tierText: {
    fontSize: 13,
    fontWeight: '700',
  },
  dimensionsList: {
    marginTop: 14,
    gap: 10,
  },
  dimRow: {
    gap: 4,
  },
  dimLabelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  dimName: {
    fontSize: 13,
    fontWeight: '600',
  },
  dimScore: {
    fontSize: 12,
    color: '#6B7280',
  },
  dimProgressTrack: {
    height: 6,
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    overflow: 'hidden',
  },
  dimProgressBar: {
    height: '100%',
    borderRadius: 4,
  },
  disclaimerText: {
    marginTop: 12,
    fontSize: 11,
    color: '#9CA3AF',
    fontStyle: 'italic',
  },
  aiBanner: {
    backgroundColor: '#F5F3FF',
    borderColor: '#DDD6FE',
    borderWidth: 1,
  },
  aiBannerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  aiIconWrapper: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#EDE9FE',
    alignItems: 'center',
    justifyContent: 'center',
  },
  aiBannerTitleWrap: {
    flex: 1,
  },
  aiBannerTitle: {
    fontWeight: '700',
    fontSize: 14,
    color: '#4C1D95',
  },
  aiBannerSub: {
    fontSize: 11,
    color: '#6D28D9',
  },
  aiBannerSnippet: {
    marginTop: 10,
    fontSize: 12,
    color: '#5B21B6',
    lineHeight: 18,
  },
  sectionTitle: {
    marginTop: 8,
    marginBottom: 12,
    fontWeight: '700',
  },
  domainCard: {
    marginBottom: 14,
    padding: 16,
    borderRadius: 16,
  },
  domainHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 14,
  },
  domainIcon: {
    width: 38,
    height: 38,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  domainTitleWrap: {
    flex: 1,
  },
  domainTitle: {
    fontWeight: '700',
    fontSize: 15,
  },
  metricStatsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    paddingVertical: 10,
    paddingHorizontal: 8,
  },
  statBox: {
    flex: 1,
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 16,
    fontWeight: '700',
  },
  statDivider: {
    width: 1,
    height: 24,
    backgroundColor: '#E5E7EB',
  },
  trendList: {
    gap: 8,
  },
  trendRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  trendDate: {
    width: 40,
    fontSize: 11,
    color: '#6B7280',
  },
  trendBarContainer: {
    flex: 1,
    flexDirection: 'row',
    height: 10,
    borderRadius: 5,
    backgroundColor: '#F3F4F6',
    overflow: 'hidden',
  },
  trendBarTasks: {
    backgroundColor: '#6C63FF',
  },
  trendBarHabits: {
    backgroundColor: '#10B981',
  },
  trendTotal: {
    width: 24,
    textAlign: 'right',
    fontSize: 12,
    fontWeight: '600',
  },
  trendLegend: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 20,
    marginTop: 10,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  legendDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
});

