import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { GlassCard } from '../glass/GlassCard';
import { Heading, BodyText, Caption } from '../common/Typography';
import { PrimaryButton } from '../common/Buttons';

export interface FinanceQuickCardProps {
  onOpenFinance: () => void;
}

export const FinanceQuickCard: React.FC<FinanceQuickCardProps> = ({ onOpenFinance }) => {
  const { theme } = useTheme();

  return (
    <GlassCard elevation="floating" style={styles.card}>
      <View style={styles.content}>
        <View style={styles.headerRow}>
          <View
            style={[
              styles.iconCircle,
              { backgroundColor: `${theme.colors.primary}18` },
            ]}
          >
            <Ionicons name="wallet-outline" size={24} color={theme.colors.primary} />
          </View>
          <View style={styles.titleCol}>
            <View style={styles.badgeRow}>
              <Caption
                weight="700"
                style={{ color: theme.colors.primary, letterSpacing: 0.8 }}
              >
                PERSONAL FINANCE
              </Caption>
            </View>
            <Heading level={2} style={styles.title}>
              Money Management
            </Heading>
          </View>
        </View>

        <BodyText color="secondary" style={styles.description}>
          Track accounts, monitor monthly budgets, achieve savings goals, and get local AI spending insights.
        </BodyText>

        <PrimaryButton
          label="Open Money Hub"
          icon={<Ionicons name="card-outline" size={18} color="#FFFFFF" />}
          onPress={onOpenFinance}
          style={styles.button}
        />
      </View>
    </GlassCard>
  );
};

const styles = StyleSheet.create({
  card: {
    padding: 20,
    marginBottom: 28,
  },
  content: {},
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  iconCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 14,
  },
  titleCol: {
    flex: 1,
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 2,
  },
  title: {
    fontSize: 18,
  },
  description: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 16,
  },
  button: {
    width: '100%',
  },
});

