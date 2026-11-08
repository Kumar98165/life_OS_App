import React, { useState, useMemo } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  FlatList,
  RefreshControl,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import { useFinanceTransactions } from '../../hooks/useFinance';
import { RootNavigationProp } from '../../navigation/types';
import { FinancialTransaction, TransactionType } from '../../types/finance';
import {
  SafeAreaContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  EmptyState,
  SkeletonLoader,
} from '../../components';

export const TransactionHistoryScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<RootNavigationProp>();

  const [selectedType, setSelectedType] = useState<TransactionType | undefined>(undefined);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const {
    data: txData,
    isLoading,
    isRefetching,
    refetch,
  } = useFinanceTransactions({
    transaction_type: selectedType,
    limit: 100,
  });

  const filteredTransactions = useMemo(() => {
    const list = txData?.transactions || [];
    if (!searchQuery.trim()) return list;
    const q = searchQuery.toLowerCase();
    return list.filter(
      (t) =>
        t.description.toLowerCase().includes(q) ||
        (t.category_name && t.category_name.toLowerCase().includes(q)) ||
        (t.account_name && t.account_name.toLowerCase().includes(q))
    );
  }, [txData, searchQuery]);

  const renderTransactionItem = ({ item }: { item: FinancialTransaction }) => {
    const isIncome = item.transaction_type === 'income';
    return (
      <TouchableOpacity
        onPress={() => navigation.navigate('TransactionDetail', { transactionId: item.id })}
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
                {item.description}
              </BodyText>
              <Caption color={theme.colors.textMuted}>
                {item.category_name || 'General'} • {item.account_name || 'Account'}
              </Caption>
            </View>

            <View style={styles.txAmountCol}>
              <BodyText
                weight="bold"
                color={isIncome ? theme.colors.success : theme.colors.textPrimary}
              >
                {isIncome ? '+' : '-'}${parseFloat(item.amount).toFixed(2)}
              </BodyText>
              <Caption color={theme.colors.textMuted}>
                {new Date(item.transaction_date).toLocaleDateString(undefined, {
                  month: 'short',
                  day: 'numeric',
                })}
              </Caption>
            </View>
          </View>
        </GlassCard>
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaContainer>
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.headerRow}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={[styles.iconButton, { backgroundColor: theme.colors.surfaceSubtle }]}
          >
            <Ionicons name="arrow-back" size={20} color={theme.colors.textPrimary} />
          </TouchableOpacity>
          <Heading level={2}>Transactions</Heading>
          <TouchableOpacity
            onPress={() => navigation.navigate('AddTransaction')}
            style={[styles.iconButton, { backgroundColor: theme.colors.primary }]}
          >
            <Ionicons name="add" size={22} color="#FFFFFF" />
          </TouchableOpacity>
        </View>

        {/* Search Bar */}
        <View style={[styles.searchBox, { backgroundColor: theme.colors.surfaceSubtle }]}>
          <Ionicons name="search" size={18} color={theme.colors.textMuted} />
          <TextInput
            style={[styles.searchInput, { color: theme.colors.textPrimary }]}
            placeholder="Search by description, category, account..."
            placeholderTextColor={theme.colors.textMuted}
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery('')}>
              <Ionicons name="close-circle" size={18} color={theme.colors.textMuted} />
            </TouchableOpacity>
          )}
        </View>

        {/* Type Filter Chips */}
        <View style={styles.filterRow}>
          {[
            { label: 'All', value: undefined },
            { label: 'Expenses', value: 'expense' as TransactionType },
            { label: 'Income', value: 'income' as TransactionType },
          ].map((f) => {
            const isSelected = selectedType === f.value;
            return (
              <TouchableOpacity
                key={f.label}
                onPress={() => setSelectedType(f.value)}
                style={[
                  styles.filterChip,
                  {
                    backgroundColor: isSelected ? theme.colors.primary : theme.colors.surface,
                    borderColor: isSelected ? theme.colors.primary : theme.colors.border,
                  },
                ]}
              >
                <BodyText
                  size="xs"
                  weight="semiBold"
                  color={isSelected ? '#FFFFFF' : theme.colors.textPrimary}
                >
                  {f.label}
                </BodyText>
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Transactions List */}
        {isLoading ? (
          <View style={{ gap: 8, marginTop: 10 }}>
            <SkeletonLoader width="100%" height={64} borderRadius={14} />
            <SkeletonLoader width="100%" height={64} borderRadius={14} />
            <SkeletonLoader width="100%" height={64} borderRadius={14} />
          </View>
        ) : (
          <FlatList
            data={filteredTransactions}
            keyExtractor={(item) => item.id}
            renderItem={renderTransactionItem}
            contentContainerStyle={styles.listContent}
            initialNumToRender={15}
            maxToRenderPerBatch={10}
            windowSize={7}
            removeClippedSubviews={Platform.OS !== 'web'}
            refreshControl={
              <RefreshControl
                refreshing={isRefetching}
                onRefresh={() => {
                  refetch();
                }}
                tintColor={theme.colors.primary}
              />
            }
            ListEmptyComponent={
              <EmptyState
                title="No Transactions Found"
                description={
                  searchQuery
                    ? 'No transactions matched your search criteria.'
                    : 'No transactions recorded yet.'
                }
                actionLabel="Add Transaction"
                onActionPress={() => navigation.navigate('AddTransaction')}
              />
            }
          />
        )}
      </View>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 16,
  },
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
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 14,
    marginBottom: 12,
  },
  searchInput: {
    flex: 1,
    fontSize: 14,
    marginHorizontal: 8,
    padding: 0,
  },
  filterRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  filterChip: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
  },
  listContent: {
    paddingBottom: 24,
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

