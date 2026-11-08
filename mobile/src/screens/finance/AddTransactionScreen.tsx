import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
  Switch,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { useTheme } from '../../theme';
import {
  useFinanceAccounts,
  useFinanceCategories,
  useCreateTransaction,
  useUpdateTransaction,
  useFinanceTransaction,
} from '../../hooks/useFinance';
import { RootNavigationProp, RootStackParamList } from '../../navigation/types';
import { TransactionType } from '../../types/finance';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  Toast,
} from '../../components';

export const AddTransactionScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<RootNavigationProp>();
  const route = useRoute<RouteProp<RootStackParamList, 'AddTransaction'>>();
  const editingId = route.params?.transactionId;

  const [type, setType] = useState<TransactionType>('expense');
  const [amount, setAmount] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [selectedAccountId, setSelectedAccountId] = useState<string>('');
  const [selectedCategoryId, setSelectedCategoryId] = useState<string>('');
  const [isRecurring, setIsRecurring] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Queries
  const { data: accounts, isLoading: accountsLoading } = useFinanceAccounts(false);
  const { data: categories, isLoading: categoriesLoading } = useFinanceCategories(type);
  const { data: existingTx, isLoading: txLoading } = useFinanceTransaction(editingId || null);

  // Mutations
  const createTxMutation = useCreateTransaction();
  const updateTxMutation = useUpdateTransaction();

  // Set default account when loaded
  useEffect(() => {
    if (accounts && accounts.length > 0 && !selectedAccountId) {
      const defaultAcc = accounts.find((a) => a.is_default) || accounts[0];
      setSelectedAccountId(defaultAcc.id);
    }
  }, [accounts, selectedAccountId]);

  // Populate fields if editing
  useEffect(() => {
    if (existingTx) {
      setType(existingTx.transaction_type);
      setAmount(existingTx.amount);
      setDescription(existingTx.description);
      setSelectedAccountId(existingTx.account_id);
      setSelectedCategoryId(existingTx.category_id || '');
      setIsRecurring(existingTx.is_recurring);
    }
  }, [existingTx]);

  // Filter categories matching current transaction type
  const activeCategories = (categories || []).filter(
    (c) => c.category_type === type
  );

  const handleSave = async () => {
    setErrorMessage(null);
    const parsedAmount = parseFloat(amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      setErrorMessage('Please enter a valid amount greater than 0.');
      return;
    }
    if (!description.trim()) {
      setErrorMessage('Please provide a brief description.');
      return;
    }
    if (!selectedAccountId) {
      setErrorMessage('Please select an account.');
      return;
    }

    try {
      if (editingId) {
        await updateTxMutation.mutateAsync({
          id: editingId,
          payload: {
            amount: parsedAmount.toFixed(2),
            transaction_type: type,
            description: description.trim(),
            account_id: selectedAccountId,
            category_id: selectedCategoryId || undefined,
            is_recurring: isRecurring,
          },
        });
      } else {
        await createTxMutation.mutateAsync({
          amount: parsedAmount.toFixed(2),
          transaction_type: type,
          description: description.trim(),
          account_id: selectedAccountId,
          category_id: selectedCategoryId || undefined,
          is_recurring: isRecurring,
        });
      }
      navigation.goBack();
    } catch (err: any) {
      const msg = err?.response?.data?.message || err?.message || 'Failed to save transaction.';
      setErrorMessage(msg);
    }
  };

  const isSubmitting = createTxMutation.isPending || updateTxMutation.isPending;

  return (
    <SafeAreaContainer>
      <ScrollContainer>
        {/* Header */}
        <View style={styles.headerRow}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={[styles.iconButton, { backgroundColor: theme.colors.surfaceSubtle }]}
          >
            <Ionicons name="close" size={22} color={theme.colors.textPrimary} />
          </TouchableOpacity>
          <Heading level={2}>{editingId ? 'Edit Transaction' : 'New Transaction'}</Heading>
          <View style={{ width: 40 }} />
        </View>

        {errorMessage && (
          <View style={[styles.errorBox, { backgroundColor: theme.colors.errorLight + '40' }]}>
            <Ionicons name="alert-circle" size={18} color={theme.colors.error} />
            <BodyText size="sm" color={theme.colors.error} style={{ marginLeft: 8, flex: 1 }}>
              {errorMessage}
            </BodyText>
          </View>
        )}

        {/* Type Segmented Control */}
        <View style={[styles.segmentContainer, { backgroundColor: theme.colors.surfaceSubtle }]}>
          <TouchableOpacity
            style={[
              styles.segmentBtn,
              type === 'expense' && { backgroundColor: theme.colors.error },
            ]}
            onPress={() => {
              setType('expense');
              setSelectedCategoryId('');
            }}
          >
            <BodyText
              weight="bold"
              color={type === 'expense' ? '#FFFFFF' : theme.colors.textMuted}
            >
              Expense
            </BodyText>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.segmentBtn,
              type === 'income' && { backgroundColor: theme.colors.success },
            ]}
            onPress={() => {
              setType('income');
              setSelectedCategoryId('');
            }}
          >
            <BodyText
              weight="bold"
              color={type === 'income' ? '#FFFFFF' : theme.colors.textMuted}
            >
              Income
            </BodyText>
          </TouchableOpacity>
        </View>

        {/* Amount Input */}
        <GlassCard style={styles.amountCard}>
          <Caption color={theme.colors.textMuted} style={{ marginBottom: 4 }}>
            AMOUNT
          </Caption>
          <View style={styles.amountInputRow}>
            <Heading level={1} color={type === 'income' ? theme.colors.success : theme.colors.error}>
              $
            </Heading>
            <TextInput
              style={[
                styles.amountInput,
                { color: type === 'income' ? theme.colors.success : theme.colors.textPrimary },
              ]}
              placeholder="0.00"
              placeholderTextColor={theme.colors.textMuted}
              keyboardType="decimal-pad"
              value={amount}
              onChangeText={setAmount}
              autoFocus={!editingId}
            />
          </View>
        </GlassCard>

        {/* Description Field */}
        <GlassCard style={styles.inputCard}>
          <Caption color={theme.colors.textMuted} style={{ marginBottom: 6 }}>
            DESCRIPTION
          </Caption>
          <TextInput
            style={[styles.textInput, { color: theme.colors.textPrimary }]}
            placeholder="e.g. Grocery shopping, Salary deposit"
            placeholderTextColor={theme.colors.textMuted}
            value={description}
            onChangeText={setDescription}
          />
        </GlassCard>

        {/* Account Selector */}
        <View style={styles.section}>
          <Caption color={theme.colors.textMuted} style={{ marginBottom: 8 }}>
            SELECT ACCOUNT
          </Caption>
          {accountsLoading ? (
            <ActivityIndicator size="small" color={theme.colors.primary} />
          ) : (
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipsScroll}>
              {(accounts || []).map((acc) => {
                const isSelected = selectedAccountId === acc.id;
                return (
                  <TouchableOpacity
                    key={acc.id}
                    onPress={() => setSelectedAccountId(acc.id)}
                    style={[
                      styles.accountChip,
                      {
                        backgroundColor: isSelected ? theme.colors.primary : theme.colors.surface,
                        borderColor: isSelected ? theme.colors.primary : theme.colors.border,
                      },
                    ]}
                  >
                    <Ionicons
                      name="wallet-outline"
                      size={16}
                      color={isSelected ? '#FFFFFF' : theme.colors.textPrimary}
                    />
                    <BodyText
                      size="sm"
                      weight="semiBold"
                      color={isSelected ? '#FFFFFF' : theme.colors.textPrimary}
                      style={{ marginLeft: 6 }}
                    >
                      {acc.name}
                    </BodyText>
                  </TouchableOpacity>
                );
              })}
            </ScrollView>
          )}
        </View>

        {/* Category Selector */}
        <View style={styles.section}>
          <Caption color={theme.colors.textMuted} style={{ marginBottom: 8 }}>
            SELECT CATEGORY
          </Caption>
          {categoriesLoading ? (
            <ActivityIndicator size="small" color={theme.colors.primary} />
          ) : (
            <View style={styles.categoryWrap}>
              {activeCategories.map((cat) => {
                const isSelected = selectedCategoryId === cat.id;
                return (
                  <TouchableOpacity
                    key={cat.id}
                    onPress={() => setSelectedCategoryId(isSelected ? '' : cat.id)}
                    style={[
                      styles.categoryChip,
                      {
                        backgroundColor: isSelected ? (cat.color_hex || theme.colors.primary) : theme.colors.surface,
                        borderColor: isSelected ? (cat.color_hex || theme.colors.primary) : theme.colors.border,
                      },
                    ]}
                  >
                    <View
                      style={[
                        styles.catColorIndicator,
                        { backgroundColor: cat.color_hex || theme.colors.primary },
                      ]}
                    />
                    <BodyText
                      size="xs"
                      weight="semiBold"
                      color={isSelected ? '#FFFFFF' : theme.colors.textPrimary}
                    >
                      {cat.name}
                    </BodyText>
                  </TouchableOpacity>
                );
              })}
            </View>
          )}
        </View>

        {/* Recurring Toggle */}
        <GlassCard style={styles.toggleCard}>
          <View style={styles.toggleRow}>
            <View>
              <BodyText weight="semiBold">Recurring Transaction</BodyText>
              <Caption color={theme.colors.textMuted}>Occurs periodically</Caption>
            </View>
            <Switch
              value={isRecurring}
              onValueChange={setIsRecurring}
              trackColor={{ false: theme.colors.surfaceSubtle, true: theme.colors.primary }}
              thumbColor="#FFFFFF"
            />
          </View>
        </GlassCard>

        {/* Submit Button */}
        <TouchableOpacity
          style={[
            styles.submitBtn,
            { backgroundColor: theme.colors.primary, opacity: isSubmitting ? 0.7 : 1 },
          ]}
          onPress={handleSave}
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <ActivityIndicator size="small" color="#FFFFFF" />
          ) : (
            <BodyText weight="bold" color="#FFFFFF" size="md">
              {editingId ? 'Update Transaction' : 'Save Transaction'}
            </BodyText>
          )}
        </TouchableOpacity>
      </ScrollContainer>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
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
  errorBox: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 12,
    marginBottom: 16,
  },
  segmentContainer: {
    flexDirection: 'row',
    padding: 4,
    borderRadius: 14,
    marginBottom: 16,
  },
  segmentBtn: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  amountCard: {
    padding: 16,
    borderRadius: 16,
    marginBottom: 12,
  },
  amountInputRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  amountInput: {
    flex: 1,
    fontSize: 32,
    fontWeight: 'bold',
    marginLeft: 8,
    padding: 0,
  },
  inputCard: {
    padding: 14,
    borderRadius: 14,
    marginBottom: 16,
  },
  textInput: {
    fontSize: 16,
    paddingVertical: 4,
  },
  section: {
    marginBottom: 16,
  },
  chipsScroll: {
    gap: 8,
    paddingVertical: 4,
  },
  accountChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 1,
  },
  categoryWrap: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  categoryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
    borderWidth: 1,
  },
  catColorIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  toggleCard: {
    padding: 14,
    borderRadius: 14,
    marginBottom: 24,
  },
  toggleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  submitBtn: {
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 40,
    elevation: 3,
    shadowOpacity: 0.15,
    shadowOffset: { width: 0, height: 3 },
  },
});

