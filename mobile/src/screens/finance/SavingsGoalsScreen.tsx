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
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import {
  useSavingsGoals,
  useCreateSavingsGoal,
  useUpdateSavingsGoal,
  useDeleteSavingsGoal,
  useAddSavingsContribution,
  useFinanceAccounts,
} from '../../hooks/useFinance';
import { SavingsGoal } from '../../types/finance';
import {
  SafeAreaContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  SkeletonLoader,
  EmptyState,
} from '../../components';

export const SavingsGoalsScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation();

  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [contributeModalVisible, setContributeModalVisible] = useState(false);
  const [targetGoal, setTargetGoal] = useState<SavingsGoal | null>(null);

  // Form State - Goal
  const [title, setTitle] = useState('');
  const [targetAmount, setTargetAmount] = useState('');
  const [notes, setNotes] = useState('');
  const [goalError, setGoalError] = useState<string | null>(null);

  // Form State - Contribution
  const [contribAmount, setContribAmount] = useState('');
  const [contribNote, setContribNote] = useState('');
  const [contribError, setContribError] = useState<string | null>(null);

  const { data: goals, isLoading, isRefetching, refetch } = useSavingsGoals();
  const { data: accounts } = useFinanceAccounts(false);

  const createGoalMutation = useCreateSavingsGoal();
  const deleteGoalMutation = useDeleteSavingsGoal();
  const contributeMutation = useAddSavingsContribution();

  const openCreateModal = () => {
    setTitle('');
    setTargetAmount('');
    setNotes('');
    setGoalError(null);
    setCreateModalVisible(true);
  };

  const openContributeModal = (goal: SavingsGoal) => {
    setTargetGoal(goal);
    setContribAmount('');
    setContribNote('');
    setContribError(null);
    setContributeModalVisible(true);
  };

  const handleCreateGoal = async () => {
    if (!title.trim()) {
      setGoalError('Please enter a goal title.');
      return;
    }
    const targetNum = parseFloat(targetAmount);
    if (isNaN(targetNum) || targetNum <= 0) {
      setGoalError('Target amount must be greater than 0.');
      return;
    }

    try {
      await createGoalMutation.mutateAsync({
        title: title.trim(),
        target_amount: targetNum.toFixed(2),
        notes: notes.trim() || undefined,
      });
      setCreateModalVisible(false);
    } catch (err: any) {
      setGoalError(err?.response?.data?.message || err?.message || 'Failed to create goal.');
    }
  };

  const handleContribute = async () => {
    if (!targetGoal) return;
    const amountNum = parseFloat(contribAmount);
    if (isNaN(amountNum) || amountNum <= 0) {
      setContribError('Contribution amount must be greater than 0.');
      return;
    }

    try {
      const defaultAcc = accounts?.find((a) => a.is_default) || accounts?.[0];
      await contributeMutation.mutateAsync({
        goalId: targetGoal.id,
        payload: {
          amount: amountNum.toFixed(2),
          account_id: defaultAcc?.id,
          note: contribNote.trim() || undefined,
        },
      });
      setContributeModalVisible(false);
    } catch (err: any) {
      setContribError(err?.response?.data?.message || err?.message || 'Failed to deposit contribution.');
    }
  };

  const handleDelete = (goal: SavingsGoal) => {
    Alert.alert('Delete Goal', `Delete "${goal.title}"?`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: async () => {
          try {
            await deleteGoalMutation.mutateAsync(goal.id);
          } catch (err: any) {
            Alert.alert('Error', err?.message || 'Failed to delete goal.');
          }
        },
      },
    ]);
  };

  const renderGoalItem = ({ item }: { item: SavingsGoal }) => {
    const isCompleted = item.progress_percentage >= 100 || item.status === 'completed';
    return (
      <GlassCard style={styles.goalCard}>
        <View style={styles.cardHeaderRow}>
          <View style={styles.goalTitleRow}>
            <View style={[styles.goalIconBox, { backgroundColor: item.color_hex + '20' }]}>
              <Ionicons
                name={isCompleted ? 'checkmark-circle' : 'flag'}
                size={18}
                color={item.color_hex || theme.colors.primary}
              />
            </View>
            <View style={{ marginLeft: 10 }}>
              <BodyText weight="bold">{item.title}</BodyText>
              {item.target_date && (
                <Caption color={theme.colors.textMuted}>
                  Target: {new Date(item.target_date).toLocaleDateString()}
                </Caption>
              )}
            </View>
          </View>

          <TouchableOpacity onPress={() => handleDelete(item)}>
            <Ionicons name="trash-outline" size={16} color={theme.colors.textMuted} />
          </TouchableOpacity>
        </View>

        <View style={styles.amountNumbersRow}>
          <BodyText size="sm" color={theme.colors.textMuted}>
            Saved ${parseFloat(item.current_amount).toFixed(2)} of ${parseFloat(item.target_amount).toFixed(2)}
          </BodyText>
          <BodyText weight="bold" color={theme.colors.primary} size="sm">
            {item.progress_percentage}%
          </BodyText>
        </View>

        <View style={[styles.progressBg, { backgroundColor: theme.colors.surfaceSubtle }]}>
          <View
            style={[
              styles.progressFill,
              {
                width: `${Math.min(item.progress_percentage, 100)}%`,
                backgroundColor: isCompleted ? theme.colors.success : item.color_hex || theme.colors.primary,
              },
            ]}
          />
        </View>

        <View style={styles.cardActionsRow}>
          <TouchableOpacity
            style={[styles.contributeBtn, { backgroundColor: theme.colors.primary }]}
            onPress={() => openContributeModal(item)}
          >
            <Ionicons name="add" size={16} color="#FFFFFF" style={{ marginRight: 4 }} />
            <Caption weight="bold" color="#FFFFFF">
              Add Funds
            </Caption>
          </TouchableOpacity>
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
          <Heading level={2}>Savings Goals</Heading>
          <TouchableOpacity
            onPress={openCreateModal}
            style={[styles.iconButton, { backgroundColor: theme.colors.primary }]}
          >
            <Ionicons name="add" size={22} color="#FFFFFF" />
          </TouchableOpacity>
        </View>

        {isLoading ? (
          <View style={{ gap: 10, marginTop: 10 }}>
            <SkeletonLoader width="100%" height={120} borderRadius={16} />
            <SkeletonLoader width="100%" height={120} borderRadius={16} />
          </View>
        ) : (
          <FlatList
            data={goals || []}
            keyExtractor={(item) => item.id}
            renderItem={renderGoalItem}
            contentContainerStyle={styles.listContent}
            initialNumToRender={8}
            maxToRenderPerBatch={6}
            windowSize={5}
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
                title="No Savings Goals"
                description="Create a savings goal for an emergency fund, vacation, or milestone."
                actionLabel="Create Goal"
                onActionPress={openCreateModal}
              />
            }
          />
        )}

        {/* Create Goal Modal */}
        <Modal
          visible={createModalVisible}
          animationType="slide"
          transparent
          onRequestClose={() => setCreateModalVisible(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={[styles.modalCard, { backgroundColor: theme.colors.surface }]}>
              <View style={styles.modalHeader}>
                <Heading level={3}>New Savings Goal</Heading>
                <TouchableOpacity onPress={() => setCreateModalVisible(false)}>
                  <Ionicons name="close" size={22} color={theme.colors.textPrimary} />
                </TouchableOpacity>
              </View>

              {goalError && (
                <Caption color={theme.colors.error} style={{ marginBottom: 10 }}>
                  {goalError}
                </Caption>
              )}

              <Caption color={theme.colors.textMuted} style={{ marginBottom: 4 }}>
                GOAL TITLE
              </Caption>
              <TextInput
                style={[styles.input, { borderColor: theme.colors.border, color: theme.colors.textPrimary }]}
                placeholder="e.g. Emergency Fund, New Laptop"
                placeholderTextColor={theme.colors.textMuted}
                value={title}
                onChangeText={setTitle}
              />

              <Caption color={theme.colors.textMuted} style={{ marginTop: 12, marginBottom: 4 }}>
                TARGET AMOUNT ($)
              </Caption>
              <TextInput
                style={[styles.input, { borderColor: theme.colors.border, color: theme.colors.textPrimary }]}
                placeholder="2000.00"
                placeholderTextColor={theme.colors.textMuted}
                keyboardType="decimal-pad"
                value={targetAmount}
                onChangeText={setTargetAmount}
              />

              <Caption color={theme.colors.textMuted} style={{ marginTop: 12, marginBottom: 4 }}>
                NOTES (OPTIONAL)
              </Caption>
              <TextInput
                style={[styles.input, { borderColor: theme.colors.border, color: theme.colors.textPrimary }]}
                placeholder="Milestone notes or target timeline"
                placeholderTextColor={theme.colors.textMuted}
                value={notes}
                onChangeText={setNotes}
              />

              <TouchableOpacity
                style={[styles.saveBtn, { backgroundColor: theme.colors.primary }]}
                onPress={handleCreateGoal}
                disabled={createGoalMutation.isPending}
              >
                {createGoalMutation.isPending ? (
                  <ActivityIndicator size="small" color="#FFFFFF" />
                ) : (
                  <BodyText weight="bold" color="#FFFFFF">
                    Create Goal
                  </BodyText>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </Modal>

        {/* Add Contribution Modal */}
        <Modal
          visible={contributeModalVisible}
          animationType="slide"
          transparent
          onRequestClose={() => setContributeModalVisible(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={[styles.modalCard, { backgroundColor: theme.colors.surface }]}>
              <View style={styles.modalHeader}>
                <Heading level={3}>Add Funds: {targetGoal?.title}</Heading>
                <TouchableOpacity onPress={() => setContributeModalVisible(false)}>
                  <Ionicons name="close" size={22} color={theme.colors.textPrimary} />
                </TouchableOpacity>
              </View>

              {contribError && (
                <Caption color={theme.colors.error} style={{ marginBottom: 10 }}>
                  {contribError}
                </Caption>
              )}

              <Caption color={theme.colors.textMuted} style={{ marginBottom: 4 }}>
                CONTRIBUTION AMOUNT ($)
              </Caption>
              <TextInput
                style={[styles.input, { borderColor: theme.colors.border, color: theme.colors.textPrimary }]}
                placeholder="100.00"
                placeholderTextColor={theme.colors.textMuted}
                keyboardType="decimal-pad"
                value={contribAmount}
                onChangeText={setContribAmount}
                autoFocus
              />

              <Caption color={theme.colors.textMuted} style={{ marginTop: 12, marginBottom: 4 }}>
                NOTE (OPTIONAL)
              </Caption>
              <TextInput
                style={[styles.input, { borderColor: theme.colors.border, color: theme.colors.textPrimary }]}
                placeholder="e.g. Monthly transfer, bonus allocation"
                placeholderTextColor={theme.colors.textMuted}
                value={contribNote}
                onChangeText={setContribNote}
              />

              <TouchableOpacity
                style={[styles.saveBtn, { backgroundColor: theme.colors.primary }]}
                onPress={handleContribute}
                disabled={contributeMutation.isPending}
              >
                {contributeMutation.isPending ? (
                  <ActivityIndicator size="small" color="#FFFFFF" />
                ) : (
                  <BodyText weight="bold" color="#FFFFFF">
                    Deposit Contribution
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
    marginBottom: 16,
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  listContent: {
    paddingBottom: 24,
  },
  goalCard: {
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
  goalTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  goalIconBox: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
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
  cardActionsRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 12,
  },
  contributeBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
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
    fontSize: 15,
  },
  saveBtn: {
    paddingVertical: 14,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 16,
  },
});

