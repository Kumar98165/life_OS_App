import React, { useState } from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { Heading, Caption } from '../common/Typography';
import { GlassCard } from '../glass/GlassCard';

export interface DashboardTopSummaryCardProps {
  balanceFormatted?: string;
  rewardPoints?: string | number;
  onNavigateModule: (route: string) => void;
}

export const DashboardTopSummaryCard: React.FC<DashboardTopSummaryCardProps> = ({
  balanceFormatted = '₹0.00',
  rewardPoints = '100',
  onNavigateModule,
}) => {
  const { theme } = useTheme();
  const [showBalance, setShowBalance] = useState(true);

  // Unified color: matches login theme exactly
  const iconBg = theme.colors.surfaceSubtle;
  const iconColor = theme.colors.primary;

  const topActions = [
    { title: 'Money', icon: 'wallet-outline', route: 'MoneyTracking' },
    { title: 'Focus', icon: 'timer-outline', route: 'FocusDashboard' },
    { title: 'Planner', icon: 'calendar-outline', route: 'PlannerTab' },
    { title: 'Analytics', icon: 'stats-chart-outline', route: 'LifeAnalytics' },
  ];

  return (
    <GlassCard style={styles.card}>
      {/* Top Split Metrics Row */}
      <View style={[styles.kpiRow, { borderColor: theme.colors.border }]}>
        {/* Left: Net / Balance */}
        <TouchableOpacity
          style={styles.kpiBox}
          activeOpacity={0.7}
          onPress={() => onNavigateModule('FinanceDashboard')}
        >
          <View style={styles.kpiHeader}>
            <Ionicons name="wallet-outline" size={18} color={theme.colors.textSecondary} />
            <Caption color="secondary" style={styles.kpiLabel}>Net Balance</Caption>
          </View>
          <Heading level={2} style={styles.kpiValue}>
            {showBalance ? balanceFormatted : '••••••'}
          </Heading>
        </TouchableOpacity>

        {/* Center Eye Hide/Show Button */}
        <TouchableOpacity
          style={[styles.eyeBtn, { borderColor: theme.colors.border, backgroundColor: theme.colors.surfaceSubtle }]}
          onPress={() => setShowBalance((prev) => !prev)}
        >
          <Ionicons
            name={showBalance ? 'eye-outline' : 'eye-off-outline'}
            size={18}
            color={theme.colors.textSecondary}
          />
        </TouchableOpacity>

        {/* Right: Score / Productivity Points */}
        <TouchableOpacity
          style={styles.kpiBox}
          activeOpacity={0.7}
          onPress={() => onNavigateModule('LifeAnalytics')}
        >
          <View style={styles.kpiHeader}>
            <Ionicons name="ribbon-outline" size={18} color={theme.colors.primary} />
            <Caption color="secondary" style={styles.kpiLabel}>Life Score</Caption>
          </View>
          <View style={styles.pointsRow}>
            <Heading level={2} style={[styles.kpiValue, { color: theme.colors.primary }]}>
              {rewardPoints}
            </Heading>
            <Ionicons name="chevron-forward" size={16} color={theme.colors.textMuted} />
          </View>
        </TouchableOpacity>
      </View>

      {/* Top 4 Quick Hub Icons - Single Unified Color */}
      <View style={styles.actionGrid}>
        {topActions.map((act) => (
          <TouchableOpacity
            key={act.title}
            style={styles.actionItem}
            activeOpacity={0.7}
            onPress={() => onNavigateModule(act.route)}
          >
            <View style={[styles.iconBox, { backgroundColor: iconBg, borderColor: theme.colors.border }]}>
              <Ionicons name={act.icon as any} size={22} color={iconColor} />
            </View>
            <Caption weight="600" style={styles.actionTitle}>
              {act.title}
            </Caption>
          </TouchableOpacity>
        ))}
      </View>
    </GlassCard>
  );
};

const styles = StyleSheet.create({
  card: {
    padding: 16,
    marginBottom: 16,
    borderRadius: 20,
  },
  kpiRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingBottom: 16,
    borderBottomWidth: 1,
    marginBottom: 16,
  },
  kpiBox: {
    flex: 1,
  },
  kpiHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 4,
  },
  kpiLabel: {
    fontSize: 12,
  },
  kpiValue: {
    fontSize: 20,
    fontWeight: '700',
  },
  pointsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  eyeBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 8,
  },
  actionGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  actionItem: {
    alignItems: 'center',
    flex: 1,
  },
  iconBox: {
    width: 50,
    height: 50,
    borderRadius: 25,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 6,
  },
  actionTitle: {
    fontSize: 12,
  },
});
