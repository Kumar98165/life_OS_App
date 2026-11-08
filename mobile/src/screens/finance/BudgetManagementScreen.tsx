import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  Modal,
  TextInput,
  Alert,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import {
  useFinanceBudgets,
  useFinanceCategories,
  useCreateBudget,
  useUpdateBudget,
  useDeleteBudget,
} from '../../hooks/useFinance';
import { Budget } from '../../types/finance';
import {
  SafeAreaContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  SkeletonLoader,
  EmptyState,
} from '../../components';

export const BudgetManagementScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation();

  const [currentMonth, setCurrentMonth] = useState<string>(() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
  });

  const [modalVisible, setModalVisible] = useState(false);
  const [editingBudget, setEditingBudget] = useState<Budget | null>(null);
  const [selectedCategoryId, setSelectedCategoryId] = useState<string | null>(null);
  const [amount, setAmount] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { data: budgets, isLoading, isRefetching, refetch } = useFinanceBudgets(currentMonth);
  const { data: categories } = useFinanceCategories('expense');

  const createBudgetMutation = useCreateBudget();
  const updateBudgetMutation = useUpdateBudget();
  const deleteBudgetMutation = useDeleteBudget();

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

  const formatMonthTitle = (mStr: string) => {
    const [y, m] = mStr.split('-').map(Number);
    const d = new Date(y, m - 1, 1);
    return d.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
  };

  const openCreateModal = () => {
    setEditingBudget(null);
    setSelectedCategoryId(null);
    setAmount('');
    setErrorMessage(null);
    setModalVisible(true);
  };

  const openEditModal = (b: Budget) => {
    setEditingBudget(b);
    setSelectedCategoryId(b.category_id || null);
    setAmount(b.amount);
    setErrorMessage(null);
    setModalVisible(true);
  };

  const handleSave = async () => {
    const parsedAmount = parseFloat(amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      setErrorMessage('Please enter an amount greater than 0.');
      return;
    }

    try {
      if (editingBudget) {
        await updateBudgetMutation.mutateAsync({
          id: editingBudget.id,
          payload: { amount: parsedAmount.toFixed(2) },
        });
      } else {
        await createBudgetMutation.mutateAsync({
          month: currentMonth,
          category_id: selectedCategoryId,
          amount: parsedAmount.toFixed(2),
        });
      }
      setModalVisible(false);
    } catch (err: any) {
      setErrorMessage(err?.response?.data?.message || err?.message || 'Failed to save budget.');
    }
  };

  const handleDelete = (budget: Budget) => {
    Alert.alert(
      'Delete Budget',
      `Delete budget for ${budget.category_name || 'Overall'}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteBudgetMutation.mutateAsync(budget.id);
            } catch (err: any) {
              Alert.alert('Error', err?.message || 'Failed to delete budget.');
            }
          },
        },
      ]
    );
  };

  const renderBudgetItem = ({ item }: { item: Budget }) => {
    const pct = item.utilization_percentage || 0;
    const barColor =
      pct >= 100
        ? theme.colors.error
        : pct >= 80
        ? theme.colors.warning
        : theme.colors.success;

    return (
      <GlassCard style={styles.budgetCard}>
        <View style={styles.cardHeaderRow}>
          <View style={styles.categoryTitleRow}>
            <View
              style={[
                styles.dot,
                { backgroundColor: item.category_color || theme.colors.primary },
              ]}
            />
            <BodyText weight="bold">{item.category_name || 'Overall Monthly'}</BodyText>
          </View>
          <View style={{ flexDirection: 'row', alignItems: 'center' }}>
            <TouchableOpacity onPress={() => openEditModal(item)} style={{ marginRight: 12 }}>
              <Ionicons name="pencil-outline" size={16} color={theme.colors.primary} />
            </TouchableOpacity>
            <TouchableOpacity onPress={() => handleDelete(item)}>
              <Ionicons name="trash-outline" size={16} color={theme.colors.error} />
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.amountNumbersRow}>
          <BodyText size="sm" color={theme.colors.textMuted}>
            Spent ${parseFloat(item.spent_amount || '0').toFixed(2)} of ${parseFloat(item.amount).toFixed(2)}
          </BodyText>
          <BodyText weight="bold" color={barColor} size="sm">
            {pct}%
          </BodyText>
        </View>

        <View style={[styles.progressBg, { backgroundColor: theme.colors.surfaceSubtle }]}>
          <View
            style={[
              styles.progressFill,
              { width: `${Math.min(pct, 100)}%`, backgroundColor: barColor },
            ]}
          />
        </View>

        <View style={styles.metaRow}>
          <Caption color={item.is_over_budget ? theme.colors.error : theme.colors.textMuted}>
            {item.is_over_budget
              ? `Over limit by $${(parseFloat(item.spent_amount || '0') - parseFloat(item.amount)).toFixed(2)}`
              : `$${parseFloat(item.remaining_amount || '0').toFixed(2)} left`}
          </Caption>
        </View>
      </GlassCard>
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
          <Heading level={2}>Budgets</Heading>
          <TouchableOpacity
            onPress={openCreateModal}
            style={[styles.iconButton, { backgroundColor: theme.colors.primary }]}
          >
            <Ionicons name="add" size={22} color="#FFFFFF" />
          </TouchableOpacity>
        </View>

        {/* Month Picker Row */}
        <View style={styles.monthRow}>
          <TouchableOpacity onPress={handlePrevMonth}>
            <Ionicons name="chevron-back" size={20} color={theme.colors.primary} />
          </TouchableOpacity>
          <BodyText weight="bold">{formatMonthTitle(currentMonth)}</BodyText>
          <TouchableOpacity onPress={handleNextMonth}>
            <Ionicons name="chevron-forward" size={20} color={theme.colors.primary} />
          </TouchableOpacity>
        </View>

        {isLoading ? (
          <View style={{ gap: 10, marginTop: 10 }}>
            <SkeletonLoader width="100%" height={90} borderRadius={16} />
            <SkeletonLoader width="100%" height={90} borderRadius={16} />
          </View>
        ) : (
          <FlatList
            data={budgets || []}
            keyExtractor={(item) => item.id}
            renderItem={renderBudgetItem}
            contentContainerStyle={styles.listContent}
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
                title="No Budgets Set"
                description={`You haven't set any budgets for ${formatMonthTitle(currentMonth)}.`}
                actionLabel="Create Budget"
                onActionPress={openCreateModal}
              />
            }
          />
        )}

        {/* Create / Edit Modal */}
        <Modal
          visible={modalVisible}
          animationType="slide"
          transparent
          onRequestClose={() => setModalVisible(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={[styles.modalCard, { backgroundColor: theme.colors.surface }]}>
              <View style={styles.modalHeader}>
                <Heading level={3}>{editingBudget ? 'Edit Budget' : 'New Budget'}</Heading>
                <TouchableOpacity onPress={() => setModalVisible(false)}>
                  <Ionicons name="close" size={22} color={theme.colors.textPrimary} />
                </TouchableOpacity>
              </View>

              {errorMessage && (
                <Caption color={theme.colors.error} style={{ marginBottom: 10 }}>
                  {errorMessage}
                </Caption>
              )}

              <Caption color={theme.colors.textMuted} style={{ marginBottom: 4 }}>
                BUDGET AMOUNT ($)
              </Caption>
              <TextInput
                style={[styles.input, { borderColor: theme.colors.border, color: theme.colors.textPrimary }]}
                placeholder="500.00"
                placeholderTextColor={theme.colors.textMuted}
                keyboardType="decimal-pad"
                value={amount}
                onChangeText={setAmount}
                autoFocus
              />

              {!editingBudget && (
                <>
                  <Caption color={theme.colors.textMuted} style={{ marginTop: 12, marginBottom: 6 }}>
                    CATEGORY
                  </Caption>
                  <View style={styles.catGrid}>
                    <TouchableOpacity
                      onPress={() => setSelectedCategoryId(null)}
                      style={[
                        styles.catPill,
                        {
                          backgroundColor:
                            selectedCategoryId === null ? theme.colors.primary : theme.colors.surfaceSubtle,
                        },
                      ]}
                    >
                      <Caption
                        weight="semiBold"
                        color={selectedCategoryId === null ? '#FFFFFF' : theme.colors.textPrimary}
                      >
                        Overall Monthly
                      </Caption>
                    </TouchableOpacity>

                    {(categories || []).map((c) => (
                      <TouchableOpacity
                        key={c.id}
                        onPress={() => setSelectedCategoryId(c.id)}
                        style={[
                          styles.catPill,
                          {
                            backgroundColor:
                              selectedCategoryId === c.id ? theme.colors.primary : theme.colors.surfaceSubtle,
                          },
                        ]}
                      >
                        <Caption
                          weight="semiBold"
                          color={selectedCategoryId === c.id ? '#FFFFFF' : theme.colors.textPrimary}
                        >
                          {c.name}
                        </Caption>
                      </TouchableOpacity>
                    ))}
                  </View>
                </>
              )}

              <TouchableOpacity
                style={[styles.saveBtn, { backgroundColor: theme.colors.primary }]}
                onPress={handleSave}
                disabled={createBudgetMutation.isPending || updateBudgetMutation.isPending}
              >
                {createBudgetMutation.isPending || updateBudgetMutation.isPending ? (
                  <ActivityIndicator size="small" color="#FFFFFF" />
                ) : (
                  <BodyText weight="bold" color="#FFFFFF">
                    {editingBudget ? 'Update Budget' : 'Save Budget'}
                  </BodyText>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </Modal>
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
    marginBottom: 12,
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  monthRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 16,
    paddingVertical: 8,
    marginBottom: 16,
  },
  listContent: {
    paddingBottom: 24,
  },
  budgetCard: {
    padding: 16,
    borderRadius: 16,
    marginBottom: 12,
  },
  cardHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  categoryTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 8,
  },
  amountNumbersRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  progressBg: {
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
  metaRow: {
    marginTop: 6,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'center',
    padding: 20,
  },
  modalCard: {
    borderRadius: 20,
    padding: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  input: {
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 18,
    fontWeight: 'bold',
  },
  catGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 20,
    maxHeight: 160,
  },
  catPill: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
  },
  saveBtn: {
    paddingVertical: 14,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 10,
  },
});

