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
import { useFinancialAnalytics } from '../../hooks/useAnalytics';
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
  { label: 'Month', value: 'month' },
  { label: 'Year', value: 'year' },
];

export const FinanceAnalyticsScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<RootNavigationProp>();
  const [selectedPeriod, setSelectedPeriod] = useState<DatePeriod>('month');

  const {
    data: fin,
    isLoading,
    refetch,
    isRefetching,
  } = useFinancialAnalytics({ period: selectedPeriod });

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
          Financial Analytics
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
            {/* Net Savings & Rate Card */}
            <GlassCard style={styles.card}>
              <Caption style={styles.sectionCaption}>CASH FLOW & SAVINGS RATE</Caption>
              <View style={styles.rateRow}>
                <Heading
                  level={1}
                  style={[
                    styles.rateValue,
                    {
                      color:
                        parseFloat(fin?.net_savings ?? '0') >= 0
                          ? '#10B981'
                          : '#EF4444',
                    },
                  ]}
                >
                  ${fin?.net_savings ?? '0.00'}
                </Heading>
                <Caption style={styles.rateSubtitle}>
                  Net Savings • {fin?.savings_rate ?? 0}% Savings Rate
                </Caption>
              </View>

              <View style={styles.statsGrid}>
                <View style={styles.statCell}>
                  <Heading level={3} style={[styles.statNum, { color: '#10B981' }]}>
                    ${fin?.total_income ?? '0.00'}
                  </Heading>
                  <Caption>Income</Caption>
                </View>
                <View style={styles.statDivider} />
                <View style={styles.statCell}>
                  <Heading level={3} style={[styles.statNum, { color: '#EF4444' }]}>
                    ${fin?.total_expenses ?? '0.00'}
                  </Heading>
                  <Caption>Expenses</Caption>
                </View>
                <View style={styles.statDivider} />
                <View style={styles.statCell}>
                  <Heading level={3} style={styles.statNum}>
                    {fin?.budget_adherence_percentage ?? 100}%
                  </Heading>
                  <Caption>Budget Adherence</Caption>
                </View>
              </View>
            </GlassCard>

            {/* Category Spending Breakdown */}
            <Heading level={3} style={styles.sectionHeading}>
              Spending by Category
            </Heading>
            <GlassCard style={styles.card}>
              {fin?.spending_by_category && fin.spending_by_category.length > 0 ? (
                <View style={styles.categoryList}>
                  {fin.spending_by_category.map((cat) => (
                    <View key={cat.category_id} style={styles.categoryRow}>
                      <View style={styles.catHeader}>
                        <View style={styles.catNameWrap}>
                          <View
                            style={[
                              styles.catDot,
                              { backgroundColor: cat.color_hex || '#6C63FF' },
                            ]}
                          />
                          <BodyText style={styles.catName}>{cat.name}</BodyText>
                        </View>
                        <BodyText style={styles.catAmount}>
                          ${cat.amount} ({cat.percentage}%)
                        </BodyText>
                      </View>
                      <View style={styles.catTrack}>
                        <View
                          style={[
                            styles.catFill,
                            {
                              width: `${Math.min(100, cat.percentage)}%`,
                              backgroundColor: cat.color_hex || '#6C63FF',
                            },
                          ]}
                        />
                      </View>
                    </View>
                  ))}
                </View>
              ) : (
                <Caption style={styles.emptyNote}>
                  No expense transactions logged in this period.
                </Caption>
              )}
            </GlassCard>

            {/* Savings Goals Velocity */}
            {fin?.savings_goals_progress && fin.savings_goals_progress.length > 0 && (
              <>
                <Heading level={3} style={styles.sectionHeading}>
                  Savings Goals
                </Heading>
                {fin.savings_goals_progress.map((sg) => (
                  <GlassCard key={sg.id} style={styles.sgCard}>
                    <View style={styles.sgHeader}>
                      <BodyText style={styles.sgName}>{sg.name}</BodyText>
                      <Heading level={3} style={styles.sgPercent}>
                        {sg.progress_percentage}%
                      </Heading>
                    </View>
                    <View style={styles.sgTrack}>
                      <View
                        style={[
                          styles.sgFill,
                          {
                            width: `${Math.min(100, sg.progress_percentage)}%`,
                            backgroundColor: '#10B981',
                          },
                        ]}
                      />
                    </View>
                    <Caption style={styles.sgAmountText}>
                      ${sg.current_amount} of ${sg.target_amount} saved
                    </Caption>
                  </GlassCard>
                ))}
              </>
            )}
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
    alignItems: 'center',
  },
  statCell: {
    flex: 1,
    alignItems: 'center',
  },
  statNum: {
    fontSize: 17,
    fontWeight: '700',
  },
  statDivider: {
    width: 1,
    height: 24,
    backgroundColor: '#E5E7EB',
  },
  sectionHeading: {
    marginTop: 8,
    marginBottom: 12,
    fontWeight: '700',
  },
  categoryList: {
    gap: 14,
  },
  categoryRow: {
    gap: 6,
  },
  catHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  catNameWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  catDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  catName: {
    fontSize: 14,
    fontWeight: '600',
  },
  catAmount: {
    fontSize: 13,
    color: '#6B7280',
    fontWeight: '600',
  },
  catTrack: {
    height: 6,
    backgroundColor: '#E5E7EB',
    borderRadius: 3,
    overflow: 'hidden',
  },
  catFill: {
    height: '100%',
    borderRadius: 3,
  },
  emptyNote: {
    textAlign: 'center',
    marginVertical: 12,
    color: '#9CA3AF',
  },
  sgCard: {
    marginBottom: 12,
    padding: 14,
    borderRadius: 14,
  },
  sgHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sgName: {
    fontSize: 15,
    fontWeight: '600',
  },
  sgPercent: {
    fontSize: 16,
    fontWeight: '700',
    color: '#10B981',
  },
  sgTrack: {
    height: 6,
    backgroundColor: '#E5E7EB',
    borderRadius: 3,
    marginTop: 10,
    overflow: 'hidden',
  },
  sgFill: {
    height: '100%',
    borderRadius: 3,
  },
  sgAmountText: {
    marginTop: 6,
    color: '#6B7280',
  },
});

