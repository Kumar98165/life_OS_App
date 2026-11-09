import React, { useState } from 'react';
import { View, StyleSheet, FlatList, TouchableOpacity, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import {
  SafeAreaContainer,
  Heading,
  BodyText,
  Caption,
  GlassCard,
  PrimaryButton,
} from '../../components';
import { useMoneyTracker } from '../../hooks/usePeople';
import { MoneyTransaction } from '../../types/people';

export const MoneyScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<any>();
  const [showCreate, setShowCreate] = useState(false);
  const [personName, setPersonName] = useState('');
  const [amount, setAmount] = useState('');
  const [txType, setTxType] = useState<'lent' | 'borrowed'>('lent');
  const [selectedTx, setSelectedTx] = useState<string | null>(null);
  const [repayAmount, setRepayAmount] = useState('');

  const { data: txs, dashboard, isLoading, createTransaction, recordRepayment, deleteTransaction } = useMoneyTracker();

  const handleSave = async () => {
    if (!personName.trim() || !amount.trim()) return;
    await createTransaction.mutateAsync({
      person_name: personName.trim(),
      amount: parseFloat(amount),
      transaction_type: txType,
      currency: 'INR',
    });
    setPersonName('');
    setAmount('');
    setShowCreate(false);
  };

  const handleRepay = async (txId: string) => {
    if (!repayAmount.trim()) return;
    await recordRepayment.mutateAsync({
      id: txId,
      data: { amount: parseFloat(repayAmount) },
    });
    setSelectedTx(null);
    setRepayAmount('');
  };

  const renderTx = ({ item }: { item: MoneyTransaction }) => (
    <GlassCard style={styles.card}>
      <View style={styles.cardRow}>
        <View style={styles.info}>
          <Heading level={3}>{item.person_name}</Heading>
          <Caption color="secondary">
            {item.transaction_type === 'lent' ? 'Lent (Receivable)' : 'Borrowed (Payable)'} • {item.transaction_date}
          </Caption>
          <Caption color="muted">Status: {item.status.toUpperCase()}</Caption>
        </View>
        <View style={styles.amountBox}>
          <Heading level={3} style={{ color: item.transaction_type === 'lent' ? '#00C853' : '#FF5252' }}>
            ₹{item.amount.toLocaleString()}
          </Heading>
          <Caption color="muted">Remaining: ₹{item.remaining_amount.toLocaleString()}</Caption>
        </View>
      </View>

      {item.remaining_amount > 0 && (
        <View style={styles.repayRow}>
          {selectedTx === item.id ? (
            <View style={styles.inlineRepay}>
              <TextInput
                style={[styles.input, styles.repayInput, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
                placeholder="Amount (₹)"
                placeholderTextColor={theme.colors.textMuted}
                value={repayAmount}
                onChangeText={setRepayAmount}
                keyboardType="decimal-pad"
              />
              <TouchableOpacity
                style={[styles.smallBtn, { backgroundColor: theme.colors.primary }]}
                onPress={() => handleRepay(item.id)}
              >
                <Caption style={{ color: '#FFF' }} weight="600">Submit</Caption>
              </TouchableOpacity>
              <TouchableOpacity onPress={() => setSelectedTx(null)} style={{ marginLeft: 8 }}>
                <Ionicons name="close-circle-outline" size={22} color={theme.colors.textMuted} />
              </TouchableOpacity>
            </View>
          ) : (
            <TouchableOpacity
              style={[styles.repayTrigger, { borderColor: theme.colors.primary }]}
              onPress={() => setSelectedTx(item.id)}
            >
              <Caption style={{ color: theme.colors.primary }} weight="600">+ Record Payment</Caption>
            </TouchableOpacity>
          )}
        </View>
      )}
    </GlassCard>
  );

  return (
    <SafeAreaContainer edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Heading level={1}>Lending & Borrowing</Heading>
          <TouchableOpacity
            style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
            onPress={() => setShowCreate(!showCreate)}
          >
            <Ionicons name={showCreate ? 'close' : 'add'} size={24} color="#FFF" />
          </TouchableOpacity>
        </View>

        {dashboard.data && (
          <GlassCard style={styles.dashboardCard}>
            <View style={styles.dashCol}>
              <Caption color="secondary">To Receive</Caption>
              <Heading level={2} style={{ color: '#00C853' }}>
                ₹{dashboard.data.outstanding_receivables.toLocaleString()}
              </Heading>
            </View>
            <View style={styles.dashCol}>
              <Caption color="secondary">To Pay</Caption>
              <Heading level={2} style={{ color: '#FF5252' }}>
                ₹{dashboard.data.outstanding_payables.toLocaleString()}
              </Heading>
            </View>
          </GlassCard>
        )}

        {showCreate && (
          <GlassCard style={styles.createCard}>
            <Heading level={3}>New Money Record</Heading>
            <View style={styles.typeSelector}>
              <TouchableOpacity
                style={[styles.typeBtn, txType === 'lent' && { backgroundColor: theme.colors.primary }]}
                onPress={() => setTxType('lent')}
              >
                <Caption style={{ color: txType === 'lent' ? '#FFF' : theme.colors.textPrimary }} weight="600">
                  Money Lent (Gave)
                </Caption>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.typeBtn, txType === 'borrowed' && { backgroundColor: theme.colors.primary }]}
                onPress={() => setTxType('borrowed')}
              >
                <Caption style={{ color: txType === 'borrowed' ? '#FFF' : theme.colors.textPrimary }} weight="600">
                  Money Borrowed (Took)
                </Caption>
              </TouchableOpacity>
            </View>
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Person Name (e.g. Rohan)"
              placeholderTextColor={theme.colors.textMuted}
              value={personName}
              onChangeText={setPersonName}
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Amount (₹)"
              placeholderTextColor={theme.colors.textMuted}
              value={amount}
              onChangeText={setAmount}
              keyboardType="decimal-pad"
            />
            <PrimaryButton label="Save Record" onPress={handleSave} loading={createTransaction.isPending} />
          </GlassCard>
        )}

        <FlatList
          data={txs || []}
          keyExtractor={(item) => item.id}
          renderItem={renderTx}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            !isLoading ? (
              <View style={styles.empty}>
                <Ionicons name="cash-outline" size={48} color={theme.colors.textMuted} />
                <BodyText color="secondary" style={styles.emptyText}>No transactions recorded</BodyText>
              </View>
            ) : undefined
          }
        />
      </View>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, paddingHorizontal: 16 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginVertical: 12 },
  addButton: { width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center' },
  dashboardCard: { flexDirection: 'row', padding: 16, marginBottom: 12, justifyContent: 'space-around' },
  dashCol: { alignItems: 'center' },
  createCard: { padding: 16, marginBottom: 12 },
  typeSelector: { flexDirection: 'row', marginVertical: 8 },
  typeBtn: { flex: 1, paddingVertical: 8, alignItems: 'center', borderRadius: 8, backgroundColor: '#E0E0E022', marginHorizontal: 4 },
  input: { padding: 10, borderRadius: 8, marginVertical: 4 },
  list: { paddingBottom: 100 },
  card: { padding: 14, marginBottom: 10 },
  cardRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  info: { flex: 1 },
  amountBox: { alignItems: 'flex-end' },
  repayRow: { marginTop: 10, paddingTop: 8, borderTopWidth: 1, borderTopColor: '#E0E0E022' },
  inlineRepay: { flexDirection: 'row', alignItems: 'center' },
  repayInput: { flex: 1, marginVertical: 0, marginRight: 8 },
  smallBtn: { paddingHorizontal: 12, paddingVertical: 8, borderRadius: 8 },
  repayTrigger: { borderWidth: 1, paddingVertical: 4, paddingHorizontal: 10, borderRadius: 6, alignSelf: 'flex-start' },
  empty: { alignItems: 'center', marginTop: 40 },
  emptyText: { marginTop: 8 },
});
