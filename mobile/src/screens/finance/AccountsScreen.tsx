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
  useFinanceAccounts,
  useCreateAccount,
  useUpdateAccount,
  useDeleteAccount,
} from '../../hooks/useFinance';
import { FinancialAccount, AccountType } from '../../types/finance';
import {
  SafeAreaContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  SkeletonLoader,
  EmptyState,
} from '../../components';

const ACCOUNT_TYPES: { label: string; value: AccountType }[] = [
  { label: 'Bank Account', value: 'bank' },
  { label: 'Cash Wallet', value: 'cash' },
  { label: 'Credit Card', value: 'credit' },
  { label: 'Savings Vault', value: 'savings' },
  { label: 'Investment', value: 'investment' },
  { label: 'Other', value: 'other' },
];

export const AccountsScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation();

  const [includeArchived, setIncludeArchived] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingAccount, setEditingAccount] = useState<FinancialAccount | null>(null);

  // Form State
  const [name, setName] = useState('');
  const [accountType, setAccountType] = useState<AccountType>('bank');
  const [initialBalance, setInitialBalance] = useState('0.00');
  const [isDefault, setIsDefault] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { data: accounts, isLoading, isRefetching, refetch } = useFinanceAccounts(includeArchived);
  const createAccountMutation = useCreateAccount();
  const updateAccountMutation = useUpdateAccount();
  const deleteAccountMutation = useDeleteAccount();

  const openCreateModal = () => {
    setEditingAccount(null);
    setName('');
    setAccountType('bank');
    setInitialBalance('0.00');
    setIsDefault(false);
    setErrorMessage(null);
    setModalVisible(true);
  };

  const openEditModal = (acc: FinancialAccount) => {
    setEditingAccount(acc);
    setName(acc.name);
    setAccountType(acc.account_type);
    setInitialBalance(acc.balance);
    setIsDefault(acc.is_default);
    setErrorMessage(null);
    setModalVisible(true);
  };

  const handleSave = async () => {
    if (!name.trim()) {
      setErrorMessage('Account name is required.');
      return;
    }
    const balanceNum = parseFloat(initialBalance);
    if (isNaN(balanceNum)) {
      setErrorMessage('Please enter a valid numeric balance.');
      return;
    }

    try {
      if (editingAccount) {
        await updateAccountMutation.mutateAsync({
          id: editingAccount.id,
          payload: {
            name: name.trim(),
            account_type: accountType,
            is_default: isDefault,
          },
        });
      } else {
        await createAccountMutation.mutateAsync({
          name: name.trim(),
          account_type: accountType,
          balance: balanceNum.toFixed(2),
          is_default: isDefault,
        });
      }
      setModalVisible(false);
    } catch (err: any) {
      setErrorMessage(err?.response?.data?.message || err?.message || 'Failed to save account.');
    }
  };

  const handleToggleArchive = async (acc: FinancialAccount) => {
    try {
      await updateAccountMutation.mutateAsync({
        id: acc.id,
        payload: { is_archived: !acc.is_archived },
      });
    } catch (err: any) {
      Alert.alert('Error', err?.message || 'Failed to update account.');
    }
  };

  const renderAccountItem = ({ item }: { item: FinancialAccount }) => {
    return (
      <GlassCard style={styles.accountCard}>
        <View style={styles.cardHeaderRow}>
          <View style={styles.titleRow}>
            <View style={[styles.iconBox, { backgroundColor: item.color_hex + '20' }]}>
              <Ionicons name="wallet-outline" size={20} color={item.color_hex || theme.colors.primary} />
            </View>
            <View style={{ marginLeft: 10 }}>
              <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                <BodyText weight="bold">{item.name}</BodyText>
                {item.is_default && (
                  <View style={[styles.defaultBadge, { backgroundColor: theme.colors.primary + '20' }]}>
                    <Caption weight="bold" color={theme.colors.primary}>Default</Caption>
                  </View>
                )}
              </View>
              <Caption color={theme.colors.textMuted}>
                {item.account_type.toUpperCase()} • {item.currency}
              </Caption>
            </View>
          </View>

          <View style={styles.balanceCol}>
            <Heading level={3}>
              ${parseFloat(item.balance).toFixed(2)}
            </Heading>
          </View>
        </View>

        <View style={[styles.divider, { backgroundColor: theme.colors.divider }]} />

        <View style={styles.cardActionsRow}>
          <TouchableOpacity
            style={styles.actionLink}
            onPress={() => openEditModal(item)}
          >
            <Ionicons name="pencil-outline" size={16} color={theme.colors.primary} />
            <BodyText size="xs" color={theme.colors.primary} weight="semiBold" style={{ marginLeft: 4 }}>
              Edit
            </BodyText>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionLink}
            onPress={() => handleToggleArchive(item)}
          >
            <Ionicons
              name={item.is_archived ? 'arrow-undo-outline' : 'archive-outline'}
              size={16}
              color={theme.colors.textMuted}
            />
            <BodyText size="xs" color={theme.colors.textMuted} weight="semiBold" style={{ marginLeft: 4 }}>
              {item.is_archived ? 'Unarchive' : 'Archive'}
            </BodyText>
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
          <Heading level={2}>Financial Accounts</Heading>
          <TouchableOpacity
            onPress={openCreateModal}
            style={[styles.iconButton, { backgroundColor: theme.colors.primary }]}
          >
            <Ionicons name="add" size={22} color="#FFFFFF" />
          </TouchableOpacity>
        </View>

        {/* Archive filter toggle */}
        <View style={styles.filterRow}>
          <TouchableOpacity
            style={[
              styles.filterPill,
              !includeArchived && { backgroundColor: theme.colors.primary },
            ]}
            onPress={() => setIncludeArchived(false)}
          >
            <BodyText size="xs" weight="semiBold" color={!includeArchived ? '#FFFFFF' : theme.colors.textMuted}>
              Active Accounts
            </BodyText>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.filterPill,
              includeArchived && { backgroundColor: theme.colors.primary },
            ]}
            onPress={() => setIncludeArchived(true)}
          >
            <BodyText size="xs" weight="semiBold" color={includeArchived ? '#FFFFFF' : theme.colors.textMuted}>
              Include Archived
            </BodyText>
          </TouchableOpacity>
        </View>

        {isLoading ? (
          <View style={{ gap: 10, marginTop: 10 }}>
            <SkeletonLoader width="100%" height={90} borderRadius={16} />
            <SkeletonLoader width="100%" height={90} borderRadius={16} />
          </View>
        ) : (
          <FlatList
            data={accounts || []}
            keyExtractor={(item) => item.id}
            renderItem={renderAccountItem}
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
                title="No Accounts Found"
                description="Add an account such as a Bank Account or Cash Wallet to track balances."
                actionLabel="Create Account"
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
                <Heading level={3}>{editingAccount ? 'Edit Account' : 'New Account'}</Heading>
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
                ACCOUNT NAME
              </Caption>
              <TextInput
                style={[styles.input, { borderColor: theme.colors.border, color: theme.colors.textPrimary }]}
                placeholder="e.g. Chase Checking, Cash"
                placeholderTextColor={theme.colors.textMuted}
                value={name}
                onChangeText={setName}
              />

              {!editingAccount && (
                <>
                  <Caption color={theme.colors.textMuted} style={{ marginTop: 10, marginBottom: 4 }}>
                    INITIAL BALANCE
                  </Caption>
                  <TextInput
                    style={[styles.input, { borderColor: theme.colors.border, color: theme.colors.textPrimary }]}
                    placeholder="0.00"
                    placeholderTextColor={theme.colors.textMuted}
                    keyboardType="decimal-pad"
                    value={initialBalance}
                    onChangeText={setInitialBalance}
                  />
                </>
              )}

              <Caption color={theme.colors.textMuted} style={{ marginTop: 10, marginBottom: 6 }}>
                ACCOUNT TYPE
              </Caption>
              <View style={styles.typeGrid}>
                {ACCOUNT_TYPES.map((t) => (
                  <TouchableOpacity
                    key={t.value}
                    onPress={() => setAccountType(t.value)}
                    style={[
                      styles.typeChip,
                      {
                        backgroundColor: accountType === t.value ? theme.colors.primary : theme.colors.surfaceSubtle,
                      },
                    ]}
                  >
                    <Caption
                      weight="semiBold"
                      color={accountType === t.value ? '#FFFFFF' : theme.colors.textPrimary}
                    >
                      {t.label}
                    </Caption>
                  </TouchableOpacity>
                ))}
              </View>

              <TouchableOpacity
                style={[styles.saveBtn, { backgroundColor: theme.colors.primary }]}
                onPress={handleSave}
                disabled={createAccountMutation.isPending || updateAccountMutation.isPending}
              >
                {createAccountMutation.isPending || updateAccountMutation.isPending ? (
                  <ActivityIndicator size="small" color="#FFFFFF" />
                ) : (
                  <BodyText weight="bold" color="#FFFFFF">
                    {editingAccount ? 'Update Account' : 'Save Account'}
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
  filterRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  filterPill: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 14,
  },
  listContent: {
    paddingBottom: 24,
  },
  accountCard: {
    padding: 16,
    borderRadius: 16,
    marginBottom: 12,
  },
  cardHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconBox: {
    width: 38,
    height: 38,
    borderRadius: 19,
    alignItems: 'center',
    justifyContent: 'center',
  },
  defaultBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    marginLeft: 6,
  },
  balanceCol: {
    alignItems: 'flex-end',
  },
  divider: {
    height: 1,
    marginVertical: 12,
  },
  cardActionsRow: {
    flexDirection: 'row',
    gap: 16,
  },
  actionLink: {
    flexDirection: 'row',
    alignItems: 'center',
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
    elevation: 5,
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
  typeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 20,
  },
  typeChip: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 10,
  },
  saveBtn: {
    paddingVertical: 14,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
});

