import React from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { useTheme } from '../../theme';
import { useFinanceTransaction, useDeleteTransaction } from '../../hooks/useFinance';
import { RootNavigationProp, RootStackParamList } from '../../navigation/types';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  ErrorState,
} from '../../components';

export const TransactionDetailScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<RootNavigationProp>();
  const route = useRoute<RouteProp<RootStackParamList, 'TransactionDetail'>>();
  const txId = route.params.transactionId;

  const { data: tx, isLoading, isError, refetch } = useFinanceTransaction(txId);
  const deleteMutation = useDeleteTransaction();

  const handleDelete = () => {
    Alert.alert(
      'Delete Transaction',
      'Are you sure you want to delete this transaction? The account balance will be restored.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteMutation.mutateAsync(txId);
              navigation.goBack();
            } catch (err: any) {
              Alert.alert('Error', err?.message || 'Failed to delete transaction.');
            }
          },
        },
      ]
    );
  };

  if (isLoading) {
    return (
      <SafeAreaContainer>
        <View style={styles.centerBox}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      </SafeAreaContainer>
    );
  }

  if (isError || !tx) {
    return (
      <SafeAreaContainer>
        <ErrorState
          title="Transaction Not Found"
          message="This transaction might have been deleted."
          onRetry={refetch}
        />
      </SafeAreaContainer>
    );
  }

  const isIncome = tx.transaction_type === 'income';

  return (
    <SafeAreaContainer>
      <ScrollContainer>
        {/* Header */}
        <View style={styles.headerRow}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={[styles.iconButton, { backgroundColor: theme.colors.surfaceSubtle }]}
          >
            <Ionicons name="arrow-back" size={20} color={theme.colors.textPrimary} />
          </TouchableOpacity>
          <Heading level={2}>Transaction Details</Heading>
          <TouchableOpacity
            onPress={() => navigation.navigate('AddTransaction', { transactionId: tx.id })}
            style={[styles.iconButton, { backgroundColor: theme.colors.surfaceSubtle }]}
          >
            <Ionicons name="pencil" size={18} color={theme.colors.primary} />
          </TouchableOpacity>
        </View>

        {/* Hero Card */}
        <GlassCard style={styles.heroCard}>
          <View
            style={[
              styles.typeBadge,
              {
                backgroundColor: isIncome
                  ? theme.colors.success + '20'
                  : theme.colors.error + '20',
              },
            ]}
          >
            <BodyText
              size="xs"
              weight="bold"
              color={isIncome ? theme.colors.success : theme.colors.error}
            >
              {tx.transaction_type.toUpperCase()}
            </BodyText>
          </View>

          <Heading
            level={1}
            color={isIncome ? theme.colors.success : theme.colors.textPrimary}
            style={styles.amountText}
          >
            {isIncome ? '+' : '-'}${parseFloat(tx.amount).toFixed(2)}
          </Heading>

          <Heading level={3} style={{ textAlign: 'center' }}>
            {tx.description}
          </Heading>
        </GlassCard>

        {/* Details List */}
        <GlassCard style={styles.detailsCard}>
          <View style={styles.detailRow}>
            <Caption color={theme.colors.textMuted}>Account</Caption>
            <BodyText weight="semiBold">{tx.account_name || 'Primary Wallet'}</BodyText>
          </View>

          <View style={[styles.divider, { backgroundColor: theme.colors.divider }]} />

          <View style={styles.detailRow}>
            <Caption color={theme.colors.textMuted}>Category</Caption>
            <View style={styles.categoryBadge}>
              <View
                style={[
                  styles.catDot,
                  { backgroundColor: tx.category_color || theme.colors.primary },
                ]}
              />
              <BodyText weight="semiBold">{tx.category_name || 'Uncategorized'}</BodyText>
            </View>
          </View>

          <View style={[styles.divider, { backgroundColor: theme.colors.divider }]} />

          <View style={styles.detailRow}>
            <Caption color={theme.colors.textMuted}>Date & Time</Caption>
            <BodyText weight="semiBold">
              {new Date(tx.transaction_date).toLocaleString(undefined, {
                dateStyle: 'medium',
                timeStyle: 'short',
              })}
            </BodyText>
          </View>

          <View style={[styles.divider, { backgroundColor: theme.colors.divider }]} />

          <View style={styles.detailRow}>
            <Caption color={theme.colors.textMuted}>Recurring</Caption>
            <BodyText weight="semiBold">{tx.is_recurring ? 'Yes (Recurring)' : 'No'}</BodyText>
          </View>
        </GlassCard>

        {/* Delete Action Button */}
        <TouchableOpacity
          style={[styles.deleteBtn, { borderColor: theme.colors.error }]}
          onPress={handleDelete}
          disabled={deleteMutation.isPending}
        >
          {deleteMutation.isPending ? (
            <ActivityIndicator size="small" color={theme.colors.error} />
          ) : (
            <BodyText weight="bold" color={theme.colors.error}>
              Delete Transaction
            </BodyText>
          )}
        </TouchableOpacity>
      </ScrollContainer>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  centerBox: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  heroCard: {
    alignItems: 'center',
    paddingVertical: 24,
    paddingHorizontal: 16,
    borderRadius: 20,
    marginBottom: 16,
  },
  typeBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    marginBottom: 10,
  },
  amountText: {
    marginBottom: 8,
  },
  detailsCard: {
    padding: 16,
    borderRadius: 16,
    marginBottom: 24,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  divider: {
    height: 1,
    marginVertical: 4,
  },
  categoryBadge: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  catDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  deleteBtn: {
    paddingVertical: 14,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    marginBottom: 40,
  },
});

