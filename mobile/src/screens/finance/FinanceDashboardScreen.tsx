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
import { useFinanceDashboard, useFinanceInsights } from '../../hooks/useFinance';
import { RootNavigationProp } from '../../navigation/types';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  SkeletonLoader,
  EmptyState,
  ErrorState,
} from '../../components';

export const FinanceDashboardScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<RootNavigationProp>();

  const [currentMonth, setCurrentMonth] = useState<string>(() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
  });

  const [showAiInsights, setShowAiInsights] = useState(false);

  const {
    data: dashboardData,
    isLoading: isDashLoading,
    isError: isDashError,
    refetch: refetchDash,
    isRefetching,
  } = useFinanceDashboard(currentMonth);

  const {
    data: insightsData,
    isLoading: isInsightsLoading,
    refetch: refetchInsights,
  } = useFinanceInsights(currentMonth);

  const handlePrevMonth = () => {
    const [y, m] = currentMonth.split('-').map(Number);
    const prevDate = new Date(y, m - 2, 1);
    setCurrentMonth(
      `${prevDate.getFullYear()}-${String(prevDate.getMonth() + 1).padStart(2, '0')}`
    );
  };

  const handleNextMonth = () => {
    const [y, m] = currentMonth.split('-').map(Number);
    const nextDate = new Date(y, m, 1);
    setCurrentMonth(
      `${nextDate.getFullYear()}-${String(nextDate.getMonth() + 1).padStart(2, '0')}`
    );
  };

  const onRefresh = () => {
    refetchDash();
    refetchInsights();
  };

  const formatMonthTitle = (mStr: string) => {
    const [y, m] = mStr.split('-').map(Number);
    const d = new Date(y, m - 1, 1);
    return d.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
  };

  const netSavingsNum = dashboardData ? parseFloat(dashboardData.monthly_net_savings) : 0;

  return (
    <SafeAreaContainer>
      <ScrollContainer
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={onRefresh}
            tintColor={theme.colors.primary}
          />
        }
      >
        {/* Top Header */}
        <View style={styles.headerRow}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={[styles.iconButton, { backgroundColor: theme.colors.surfaceSubtle }]}
            accessibilityRole="button"
            accessibilityLabel="Go back"
          >
            <Ionicons name="arrow-back" size={20} color={theme.colors.textPrimary} />
          </TouchableOpacity>

          <View style={styles.monthSelector}>
            <TouchableOpacity onPress={handlePrevMonth} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
              <Ionicons name="chevron-back" size={18} color={theme.colors.primary} />
            </TouchableOpacity>
            <BodyText weight="bold" style={styles.monthTitle}>
              {formatMonthTitle(currentMonth)}
            </BodyText>
            <TouchableOpacity onPress={handleNextMonth} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
              <Ionicons name="chevron-forward" size={18} color={theme.colors.primary} />
            </TouchableOpacity>
          </View>

          <TouchableOpacity
            onPress={() => navigation.navigate('FinanceSettings')}
            style={[styles.iconButton, { backgroundColor: theme.colors.surfaceSubtle }]}
            accessibilityRole="button"
            accessibilityLabel="Finance settings"
          >
            <Ionicons name="settings-outline" size={20} color={theme.colors.textPrimary} />
          </TouchableOpacity>
        </View>

        {isDashLoading ? (
          <View style={styles.loadingContainer}>
            <SkeletonLoader width="100%" height={160} borderRadius={16} />
            <View style={{ height: 16 }} />
            <SkeletonLoader width="100%" height={80} borderRadius={16} />
            <View style={{ height: 16 }} />
            <SkeletonLoader width="100%" height={120} borderRadius={16} />
          </View>
        ) : isDashError || !dashboardData ? (
          <ErrorState
            title="Failed to Load Finances"
            message="Could not retrieve your financial summary. Pull down to retry."
            onRetry={onRefresh}
          />
        ) : (
          <>
            {/* Primary Net Worth / Balance Card */}
            <GlassCard variant="elevated" style={styles.balanceCard}>
              <View style={styles.balanceHeader}>
                <Caption color={theme.colors.textMuted}>TOTAL NET WORTH</Caption>
                <View style={[styles.badge, { backgroundColor: theme.colors.primaryLight + '30' }]}>
                  <BodyText size="xs" color={theme.colors.primary} weight="semiBold">
                    {dashboardData.accounts.length} Active {dashboardData.accounts.length === 1 ? 'Account' : 'Accounts'}
                  </BodyText>
                </View>
              </View>
              <Heading level={1} style={styles.balanceAmount}>
                ${parseFloat(dashboardData.total_balance).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </Heading>

              {/* Monthly Overview Pill Row */}
              <View style={[styles.statsRow, { borderTopColor: theme.colors.divider }]}>
                <View style={styles.statCol}>
                  <Caption color={theme.colors.textMuted}>Income</Caption>
                  <BodyText weight="bold" color={theme.colors.success}>
                    +${parseFloat(dashboardData.monthly_income).toFixed(2)}
                  </BodyText>
                </View>
                <View style={[styles.statDivider, { backgroundColor: theme.colors.divider }]} />
                <View style={styles.statCol}>
                  <Caption color={theme.colors.textMuted}>Expenses</Caption>
                  <BodyText weight="bold" color={theme.colors.error}>
                    -${parseFloat(dashboardData.monthly_expenses).toFixed(2)}
                  </BodyText>
                </View>
                <View style={[styles.statDivider, { backgroundColor: theme.colors.divider }]} />
                <View style={styles.statCol}>
                  <Caption color={theme.colors.textMuted}>Net Savings</Caption>
                  <BodyText
                    weight="bold"
                    color={netSavingsNum >= 0 ? theme.colors.success : theme.colors.error}
                  >
                    {netSavingsNum >= 0 ? '+' : ''}${netSavingsNum.toFixed(2)}
                  </BodyText>
                </View>
              </View>
            </GlassCard>

            {/* Quick Actions Bar */}
            <View style={styles.actionsBar}>
              <TouchableOpacity
                style={[styles.primaryActionBtn, { backgroundColor: theme.colors.primary }]}
                onPress={() => navigation.navigate('AddTransaction')}
                activeOpacity={0.85}
              >
                <Ionicons name="add-circle" size={20} color="#FFFFFF" style={{ marginRight: 6 }} />
                <BodyText weight="bold" color="#FFFFFF">
                  Add Transaction
                </BodyText>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.secondaryActionBtn, { backgroundColor: theme.colors.surface }]}
                onPress={() => navigation.navigate('AccountsManagement')}
              >
                <Ionicons name="wallet-outline" size={18} color={theme.colors.primary} />
                <Caption weight="medium" style={{ marginTop: 2 }}>Accounts</Caption>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.secondaryActionBtn, { backgroundColor: theme.colors.surface }]}
                onPress={() => navigation.navigate('BudgetManagement')}
              >
                <Ionicons name="pie-chart-outline" size={18} color={theme.colors.primary} />
                <Caption weight="medium" style={{ marginTop: 2 }}>Budgets</Caption>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.secondaryActionBtn, { backgroundColor: theme.colors.surface }]}
                onPress={() => navigation.navigate('SavingsGoals')}
              >
                <Ionicons name="flag-outline" size={18} color={theme.colors.primary} />
                <Caption weight="medium" style={{ marginTop: 2 }}>Goals</Caption>
              </TouchableOpacity>
            </View>

            {/* AI Insights Card */}
            <GlassCard style={styles.insightsCard}>
              <TouchableOpacity
                style={styles.insightsToggleRow}
                onPress={() => setShowAiInsights(!showAiInsights)}
                activeOpacity={0.7}
              >
                <View style={styles.insightsTitleRow}>
                  <View style={[styles.sparkIconBox, { backgroundColor: theme.colors.primary + '20' }]}>
                    <Ionicons name="sparkles" size={16} color={theme.colors.primary} />
                  </View>
                  <View style={{ marginLeft: 10 }}>
                    <BodyText weight="bold">Smart Financial Insights</BodyText>
                    <Caption color={theme.colors.textMuted}>Automated Financial Analysis</Caption>
                  </View>
                </View>
                <Ionicons
                  name={showAiInsights ? 'chevron-up' : 'chevron-down'}
                  size={18}
                  color={theme.colors.textMuted}
                />
              </TouchableOpacity>

              {showAiInsights && (
                <View style={styles.insightsContent}>
                  {isInsightsLoading ? (
                    <SkeletonLoader width="100%" height={60} borderRadius={8} />
                  ) : insightsData ? (
                    <>
                      <View style={styles.insightsPillsRow}>
                        <View style={[styles.insightPill, { backgroundColor: theme.colors.surfaceSubtle }]}>
                          <Caption color={theme.colors.textMuted}>Savings Rate</Caption>
                          <BodyText weight="bold" color={theme.colors.primary}>
                            {insightsData.savings_rate}%
                          </BodyText>
                        </View>
                        {insightsData.top_spending_category && (
                          <View style={[styles.insightPill, { backgroundColor: theme.colors.surfaceSubtle }]}>
                            <Caption color={theme.colors.textMuted}>Top Expense</Caption>
                            <BodyText weight="bold" color={theme.colors.error} numberOfLines={1}>
                              {insightsData.top_spending_category.name} ({insightsData.top_spending_category.percentage}%)
                            </BodyText>
                          </View>
                        )}
                        <View style={[styles.insightPill, { backgroundColor: theme.colors.surfaceSubtle }]}>
                          <Caption color={theme.colors.textMuted}>Budgets</Caption>
                          <BodyText
                            weight="bold"
                            color={insightsData.budget_status.over_budget_count > 0 ? theme.colors.error : theme.colors.success}
                          >
                            {insightsData.budget_status.over_budget_count} Over Limit
                          </BodyText>
                        </View>
                      </View>

                      <View style={[styles.aiObservationBox, { backgroundColor: theme.colors.background }]}>
                        <BodyText size="sm" color={theme.colors.textPrimary}>
                          {insightsData.ai_observations}
                        </BodyText>
                      </View>
                    </>
                  ) : (
                    <Caption color={theme.colors.textMuted}>No insights available for this month.</Caption>
                  )}
                </View>
              )}
            </GlassCard>

            {/* Budget Utilization Section */}
            {dashboardData.budgets && dashboardData.budgets.length > 0 && (
              <View style={styles.sectionContainer}>
                <View style={styles.sectionHeader}>
                  <Heading level={3}>Monthly Budgets</Heading>
                  <TouchableOpacity onPress={() => navigation.navigate('BudgetManagement')}>
                    <BodyText size="sm" color={theme.colors.primary} weight="semiBold">
                      View All
                    </BodyText>
                  </TouchableOpacity>
                </View>

                {dashboardData.budgets.slice(0, 3).map((b) => {
                  const pct = b.utilization_percentage || 0;
                  const barColor = pct >= 100 ? theme.colors.error : pct >= 80 ? theme.colors.warning : theme.colors.success;
                  return (
                    <GlassCard key={b.id} style={styles.budgetCard}>
                      <View style={styles.budgetRow}>
                        <BodyText weight="semiBold">{b.category_name || 'Overall Budget'}</BodyText>
                        <BodyText size="sm" weight="bold">
                          ${parseFloat(b.spent_amount || '0').toFixed(0)} / ${parseFloat(b.amount).toFixed(0)}
                        </BodyText>
                      </View>
                      <View style={[styles.progressBarBg, { backgroundColor: theme.colors.surfaceSubtle }]}>
                        <View
                          style={[
                            styles.progressBarFill,
                            {
                              width: `${Math.min(pct, 100)}%`,
                              backgroundColor: barColor,
                            },
                          ]}
                        />
                      </View>
                      <View style={styles.budgetMeta}>
                        <Caption color={b.is_over_budget ? theme.colors.error : theme.colors.textMuted}>
                          {b.is_over_budget
                            ? `Over budget by $${(parseFloat(b.spent_amount || '0') - parseFloat(b.amount)).toFixed(2)}`
                            : `$${parseFloat(b.remaining_amount || '0').toFixed(2)} remaining`}
                        </Caption>
                        <Caption weight="bold" color={barColor}>
                          {pct}%
                        </Caption>
                      </View>
                    </GlassCard>
                  );
                })}
              </View>
            )}

            {/* Expense Category Breakdown */}
            {dashboardData.category_breakdown && dashboardData.category_breakdown.length > 0 && (
              <View style={styles.sectionContainer}>
                <Heading level={3} style={{ marginBottom: 12 }}>Spending by Category</Heading>
                <GlassCard style={{ padding: 16 }}>
                  {dashboardData.category_breakdown.slice(0, 5).map((cat) => (
                    <View key={cat.category_id} style={styles.categoryItem}>
                      <View style={styles.categoryMetaRow}>
                        <View style={styles.categoryNameRow}>
                          <View
                            style={[
                              styles.catDot,
                              { backgroundColor: cat.color_hex || theme.colors.primary },
                            ]}
                          />
                          <BodyText size="sm" weight="medium">
                            {cat.name}
                          </BodyText>
                        </View>
                        <View style={styles.categoryAmountRow}>
                          <BodyText size="sm" weight="bold">
                            ${parseFloat(cat.total_amount).toFixed(2)}
                          </BodyText>
                          <Caption color={theme.colors.textMuted} style={{ marginLeft: 6 }}>
                            ({cat.percentage}%)
                          </Caption>
                        </View>
                      </View>
                      <View style={[styles.progressBarBg, { backgroundColor: theme.colors.surfaceSubtle }]}>
                        <View
                          style={[
                            styles.progressBarFill,
                            {
                              width: `${Math.min(cat.percentage, 100)}%`,
                              backgroundColor: cat.color_hex || theme.colors.primary,
                            },
                          ]}
                        />
                      </View>
                    </View>
                  ))}
                </GlassCard>
              </View>
            )}

            {/* Recent Transactions Section */}
            <View style={styles.sectionContainer}>
              <View style={styles.sectionHeader}>
                <Heading level={3}>Recent Transactions</Heading>
                <TouchableOpacity onPress={() => navigation.navigate('TransactionHistory')}>
                  <BodyText size="sm" color={theme.colors.primary} weight="semiBold">
                    See All
                  </BodyText>
                </TouchableOpacity>
              </View>

              {dashboardData.recent_transactions.length === 0 ? (
                <EmptyState
                  title="No Transactions Yet"
                  description="Start by adding your first transaction for this month."
                  actionLabel="Add Transaction"
                  onAction={() => navigation.navigate('AddTransaction')}
                />
              ) : (
                dashboardData.recent_transactions.map((tx) => {
                  const isIncome = tx.transaction_type === 'income';
                  return (
                    <TouchableOpacity
                      key={tx.id}
                      onPress={() => navigation.navigate('TransactionDetail', { transactionId: tx.id })}
                      activeOpacity={0.7}
                    >
                      <GlassCard style={styles.txCard}>
                        <View style={styles.txRow}>
                          <View
                            style={[
                              styles.txIconBox,
                              {
                                backgroundColor: isIncome
                                  ? theme.colors.success + '20'
                                  : theme.colors.error + '20',
                              },
                            ]}
                          >
                            <Ionicons
                              name={isIncome ? 'arrow-down' : 'arrow-up'}
                              size={18}
                              color={isIncome ? theme.colors.success : theme.colors.error}
                            />
                          </View>
                          <View style={styles.txMain}>
                            <BodyText weight="semiBold" numberOfLines={1}>
                              {tx.description}
                            </BodyText>
                            <Caption color={theme.colors.textMuted}>
                              {tx.category_name || 'General'} • {tx.account_name || 'Account'}
                            </Caption>
                          </View>
                          <View style={styles.txAmountCol}>
                            <BodyText
                              weight="bold"
                              color={isIncome ? theme.colors.success : theme.colors.textPrimary}
                            >
                              {isIncome ? '+' : '-'}${parseFloat(tx.amount).toFixed(2)}
                            </BodyText>
                            <Caption color={theme.colors.textMuted}>
                              {new Date(tx.transaction_date).toLocaleDateString(undefined, {
                                month: 'short',
                                day: 'numeric',
                              })}
                            </Caption>
                          </View>
                        </View>
                      </GlassCard>
                    </TouchableOpacity>
                  );
                })
              )}
            </View>
          </>
        )}
      </ScrollContainer>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  monthSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  monthTitle: {
    marginHorizontal: 12,
  },
  loadingContainer: {
    paddingVertical: 20,
  },
  balanceCard: {
    padding: 20,
    borderRadius: 20,
    marginBottom: 16,
  },
  balanceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  balanceAmount: {
    marginVertical: 12,
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderTopWidth: 1,
    paddingTop: 14,
    marginTop: 4,
  },
  statCol: {
    flex: 1,
    alignItems: 'center',
  },
  statDivider: {
    width: 1,
    height: 28,
  },
  actionsBar: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    gap: 8,
  },
  primaryActionBtn: {
    flex: 1.8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 16,
    elevation: 2,
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
  },
  secondaryActionBtn: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  insightsCard: {
    padding: 16,
    borderRadius: 16,
    marginBottom: 16,
  },
  insightsToggleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  insightsTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sparkIconBox: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  insightsContent: {
    marginTop: 14,
  },
  insightsPillsRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 10,
  },
  insightPill: {
    flex: 1,
    padding: 8,
    borderRadius: 10,
    alignItems: 'center',
  },
  aiObservationBox: {
    padding: 12,
    borderRadius: 10,
    marginTop: 4,
  },
  sectionContainer: {
    marginBottom: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  budgetCard: {
    padding: 14,
    borderRadius: 14,
    marginBottom: 8,
  },
  budgetRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  progressBarBg: {
    height: 6,
    borderRadius: 3,
    overflow: 'hidden',
    marginVertical: 4,
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 3,
  },
  budgetMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 4,
  },
  categoryItem: {
    marginBottom: 12,
  },
  categoryMetaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  categoryNameRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  catDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 8,
  },
  categoryAmountRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  txCard: {
    padding: 12,
    borderRadius: 14,
    marginBottom: 8,
  },
  txRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  txIconBox: {
    width: 38,
    height: 38,
    borderRadius: 19,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  txMain: {
    flex: 1,
  },
  txAmountCol: {
    alignItems: 'flex-end',
  },
});

