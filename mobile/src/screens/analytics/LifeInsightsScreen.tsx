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
import { useAIInsights } from '../../hooks/useAnalytics';
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

export const LifeInsightsScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<RootNavigationProp>();
  const [selectedPeriod, setSelectedPeriod] = useState<DatePeriod>('week');

  const {
    data: insights,
    isLoading,
    refetch,
    isRefetching,
  } = useAIInsights({ period: selectedPeriod });

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
          AI Personal Insights
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
            <SkeletonLoader height={220} />
          </GlassCard>
        ) : (
          <>
            {/* Model Provenance Banner */}
            <View style={styles.provenanceBanner}>
              <Ionicons
                name={insights?.is_fallback ? 'hardware-chip-outline' : 'sparkles'}
                size={16}
                color={insights?.is_fallback ? '#6B7280' : '#6C63FF'}
              />
              <Caption style={styles.provenanceText}>
                {insights?.is_fallback
                  ? 'Deterministic Analytics Engine'
                  : 'Synthesized via Deterministic Rules Engine (Zero Cloud Telemetry)'}
              </Caption>
            </View>

            {/* Executive Summary Card */}
            <GlassCard style={styles.execCard}>
              <View style={styles.execHeader}>
                <Ionicons name="newspaper-outline" size={20} color="#6C63FF" />
                <Heading level={3} style={styles.execHeading}>
                  Executive Summary
                </Heading>
              </View>
              <BodyText style={styles.execBody}>
                {insights?.executive_summary ??
                  'Review your habits, task execution, and budget metrics for this cycle.'}
              </BodyText>
            </GlassCard>

            {/* Observation Cards */}
            <Heading level={3} style={styles.sectionHeading}>
              Domain Observations
            </Heading>

            {/* Productivity */}
            <GlassCard style={styles.obsCard}>
              <View style={styles.obsHeader}>
                <Ionicons name="checkbox-outline" size={18} color="#6C63FF" />
                <BodyText style={styles.obsTitle}>Productivity Patterns</BodyText>
              </View>
              <BodyText style={styles.obsBody}>
                {insights?.productivity_observation ??
                  'Maintain continuous task execution and focus time blocks.'}
              </BodyText>
            </GlassCard>

            {/* Habits */}
            <GlassCard style={styles.obsCard}>
              <View style={styles.obsHeader}>
                <Ionicons name="flame-outline" size={18} color="#10B981" />
                <BodyText style={styles.obsTitle}>Habit Adherence</BodyText>
              </View>
              <BodyText style={styles.obsBody}>
                {insights?.habit_observation ??
                  'Consistent evening check-ins protect your streak velocity.'}
              </BodyText>
            </GlassCard>

            {/* Finance */}
            <GlassCard style={styles.obsCard}>
              <View style={styles.obsHeader}>
                <Ionicons name="cash-outline" size={18} color="#16A34A" />
                <BodyText style={styles.obsTitle}>Financial Discipline</BodyText>
              </View>
              <BodyText style={styles.obsBody}>
                {insights?.financial_observation ??
                  'Category expenses are tracked against monthly budget limits.'}
              </BodyText>
            </GlassCard>

            {/* Actionable Recommendations */}
            <Heading level={3} style={styles.sectionHeading}>
              Actionable Recommendations
            </Heading>
            <GlassCard style={styles.card}>
              <View style={styles.recsList}>
                {insights?.actionable_recommendations?.map((rec, index) => (
                  <View key={index} style={styles.recRow}>
                    <View style={styles.recNumberBadge}>
                      <BodyText style={styles.recNumber}>{index + 1}</BodyText>
                    </View>
                    <BodyText style={styles.recText}>{rec}</BodyText>
                  </View>
                ))}
              </View>
            </GlassCard>

            {/* Disclaimer Box */}
            <View style={styles.disclaimerBox}>
              <Ionicons name="information-circle-outline" size={16} color="#9CA3AF" />
              <Caption style={styles.disclaimerText}>
                LifeOS insights are computed from your verified personal records.
                They are not medical, psychological, financial, or clinical advice.
              </Caption>
            </View>
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
  provenanceBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: '#F3F4F6',
    borderRadius: 8,
    paddingVertical: 6,
    paddingHorizontal: 10,
    marginBottom: 12,
  },
  provenanceText: {
    fontSize: 11,
    color: '#4B5563',
    flex: 1,
  },
  card: {
    marginBottom: 16,
    padding: 16,
    borderRadius: 16,
  },
  execCard: {
    backgroundColor: '#FAF5FF',
    borderColor: '#E9D5FF',
    borderWidth: 1,
    padding: 16,
    borderRadius: 16,
    marginBottom: 16,
  },
  execHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  execHeading: {
    fontSize: 16,
    fontWeight: '700',
    color: '#581C87',
  },
  execBody: {
    fontSize: 14,
    lineHeight: 20,
    color: '#6B21A8',
  },
  sectionHeading: {
    marginTop: 8,
    marginBottom: 12,
    fontWeight: '700',
  },
  obsCard: {
    marginBottom: 12,
    padding: 14,
    borderRadius: 14,
  },
  obsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 6,
  },
  obsTitle: {
    fontWeight: '700',
    fontSize: 14,
  },
  obsBody: {
    fontSize: 13,
    color: '#4B5563',
    lineHeight: 18,
  },
  recsList: {
    gap: 12,
  },
  recRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 10,
  },
  recNumberBadge: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: '#EEF2FF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  recNumber: {
    fontSize: 12,
    fontWeight: '700',
    color: '#6C63FF',
  },
  recText: {
    flex: 1,
    fontSize: 13,
    lineHeight: 18,
  },
  disclaimerBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 8,
    paddingHorizontal: 8,
  },
  disclaimerText: {
    flex: 1,
    fontSize: 11,
    color: '#9CA3AF',
    fontStyle: 'italic',
  },
});

