import React from 'react';
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
import { useGoalAnalytics } from '../../hooks/useAnalytics';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  SkeletonLoader,
} from '../../components';

export const GoalsAnalyticsScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<RootNavigationProp>();

  const {
    data: goals,
    isLoading,
    refetch,
    isRefetching,
  } = useGoalAnalytics();

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
          Goal Velocity
        </Heading>
        <View style={styles.backButton} />
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
            {/* Overall Milestones & Velocity Card */}
            <GlassCard style={styles.card}>
              <Caption style={styles.sectionCaption}>MILESTONE EXECUTION</Caption>
              <View style={styles.rateRow}>
                <Heading level={1} style={[styles.rateValue, { color: '#F59E0B' }]}>
                  {goals?.milestone_completion_percentage ?? 100}%
                </Heading>
                <Caption style={styles.rateSubtitle}>Milestone Completion Velocity</Caption>
              </View>

              <View style={styles.statsGrid}>
                <View style={styles.statCell}>
                  <Heading level={3} style={styles.statNum}>{goals?.active_goals ?? 0}</Heading>
                  <Caption>Active Goals</Caption>
                </View>
                <View style={styles.statCell}>
                  <Heading level={3} style={styles.statNum}>{goals?.completed_goals ?? 0}</Heading>
                  <Caption>Achieved</Caption>
                </View>
                <View style={styles.statCell}>
                  <Heading level={3} style={styles.statNum}>
                    {goals?.completed_milestones ?? 0}/{goals?.total_milestones ?? 0}
                  </Heading>
                  <Caption>Milestones</Caption>
                </View>
              </View>
            </GlassCard>

            {/* Upcoming Deadlines */}
            {goals?.upcoming_deadlines && goals.upcoming_deadlines.length > 0 && (
              <>
                <Heading level={3} style={styles.sectionHeading}>
                  Approaching Target Dates
                </Heading>
                <GlassCard style={styles.card}>
                  <View style={styles.deadlinesList}>
                    {goals.upcoming_deadlines.map((d) => (
                      <View key={d.id} style={styles.deadlineRow}>
                        <View style={styles.deadlinesInfo}>
                          <BodyText style={styles.deadlineTitle}>{d.title}</BodyText>
                          <Caption>Target: {d.target_date.slice(0, 10)}</Caption>
                        </View>
                        <View
                          style={[
                            styles.countdownBadge,
                            { backgroundColor: d.is_overdue ? '#FEE2E2' : '#FEF3C7' },
                          ]}
                        >
                          <BodyText
                            style={[
                              styles.countdownText,
                              { color: d.is_overdue ? '#DC2626' : '#D97706' },
                            ]}
                          >
                            {d.is_overdue ? 'Overdue' : `${d.days_remaining}d left`}
                          </BodyText>
                        </View>
                      </View>
                    ))}
                  </View>
                </GlassCard>
              </>
            )}

            {/* Goal Progress Cards */}
            <Heading level={3} style={styles.sectionHeading}>
              Active Goals Progress
            </Heading>

            {goals?.goals_progress?.map((g) => (
              <GlassCard key={g.id} style={styles.goalCard}>
                <View style={styles.goalHeader}>
                  <View style={styles.goalTitleWrap}>
                    <BodyText style={styles.goalTitle}>{g.title}</BodyText>
                    {g.category && <Caption style={styles.categoryBadge}>{g.category}</Caption>}
                  </View>
                  <Heading level={3} style={styles.goalPercent}>
                    {g.progress_percentage}%
                  </Heading>
                </View>
                <View style={styles.goalTrack}>
                  <View
                    style={[
                      styles.goalFill,
                      {
                        width: `${Math.min(100, g.progress_percentage)}%`,
                        backgroundColor:
                          g.progress_percentage >= 100
                            ? '#10B981'
                            : g.progress_percentage >= 50
                            ? '#6C63FF'
                            : '#F59E0B',
                      },
                    ]}
                  />
                </View>
                {g.target_date && (
                  <Caption style={styles.goalTarget}>Target: {g.target_date.slice(0, 10)}</Caption>
                )}
              </GlassCard>
            ))}
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
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 40,
    paddingTop: 8,
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
  deadlinesList: {
    gap: 12,
  },
  deadlineRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  deadlinesInfo: {
    flex: 1,
  },
  deadlineTitle: {
    fontSize: 14,
    fontWeight: '600',
  },
  countdownBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  countdownText: {
    fontSize: 12,
    fontWeight: '700',
  },
  goalCard: {
    marginBottom: 12,
    padding: 14,
    borderRadius: 14,
  },
  goalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  goalTitleWrap: {
    flex: 1,
    marginRight: 8,
  },
  goalTitle: {
    fontSize: 15,
    fontWeight: '600',
  },
  categoryBadge: {
    color: '#6C63FF',
    marginTop: 2,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  goalPercent: {
    fontSize: 16,
    fontWeight: '700',
  },
  goalTrack: {
    height: 6,
    backgroundColor: '#E5E7EB',
    borderRadius: 3,
    marginTop: 10,
    overflow: 'hidden',
  },
  goalFill: {
    height: '100%',
    borderRadius: 3,
  },
  goalTarget: {
    marginTop: 6,
    color: '#6B7280',
  },
});

