import React, { useState } from 'react';
import { View, StyleSheet, FlatList, TouchableOpacity, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import {
  SafeAreaContainer,
  Heading,
  BodyText,
  Caption,
  GlassCard,
  PrimaryButton,
} from '../../components';
import { useBills } from '../../hooks/useExtensions';
import { BillItem } from '../../types/extensions';

export const BillsScreen: React.FC = () => {
  const { theme } = useTheme();
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState('');
  const [amount, setAmount] = useState('');

  const { data: bills, isLoading, createBill, recordPayment } = useBills();

  const handleSave = async () => {
    if (!title.trim() || !amount.trim()) return;
    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + 14);

    await createBill.mutateAsync({
      title: title.trim(),
      amount: parseFloat(amount),
      due_date: dueDate.toISOString().split('T')[0],
      category: 'utility',
      frequency: 'monthly',
    });
    setTitle('');
    setAmount('');
    setShowCreate(false);
  };

  const renderBill = ({ item }: { item: BillItem }) => (
    <GlassCard style={styles.card}>
      <View style={styles.cardRow}>
        <View style={styles.info}>
          <Heading level={3}>{item.title}</Heading>
          <Caption color="secondary">Due: {item.due_date} • {item.frequency}</Caption>
        </View>
        <View style={styles.actionCol}>
          <Heading level={3} style={{ color: theme.colors.primary }}>${item.amount.toFixed(2)}</Heading>
          {item.status !== 'paid' ? (
            <TouchableOpacity
              style={[styles.payButton, { backgroundColor: theme.colors.primary }]}
              onPress={() => recordPayment.mutate({ billId: item.id, data: { amount_paid: item.amount } })}
            >
              <Caption style={{ color: '#FFF' }} weight="600">Mark Paid</Caption>
            </TouchableOpacity>
          ) : (
            <Caption style={{ color: '#4CAF50' }} weight="600">PAID</Caption>
          )}
        </View>
      </View>
    </GlassCard>
  );

  return (
    <SafeAreaContainer edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Heading level={1}>Bills & Utilities</Heading>
          <TouchableOpacity
            style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
            onPress={() => setShowCreate(!showCreate)}
          >
            <Ionicons name={showCreate ? 'close' : 'add'} size={24} color="#FFF" />
          </TouchableOpacity>
        </View>

        {showCreate && (
          <GlassCard style={styles.createCard}>
            <Heading level={3}>New Bill</Heading>
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Bill Title (e.g. Electric Bill)"
              placeholderTextColor={theme.colors.textMuted}
              value={title}
              onChangeText={setTitle}
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Amount (USD)"
              placeholderTextColor={theme.colors.textMuted}
              value={amount}
              onChangeText={setAmount}
              keyboardType="decimal-pad"
            />
            <PrimaryButton label="Save Bill" onPress={handleSave} loading={createBill.isPending} />
          </GlassCard>
        )}

        <FlatList
          data={bills || []}
          keyExtractor={(item) => item.id}
          renderItem={renderBill}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            !isLoading ? (
              <View style={styles.empty}>
                <Ionicons name="receipt-outline" size={48} color={theme.colors.textMuted} />
                <BodyText color="secondary" style={styles.emptyText}>No pending bills</BodyText>
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
  createCard: { padding: 16, marginBottom: 12 },
  input: { padding: 10, borderRadius: 8, marginVertical: 4 },
  list: { paddingBottom: 100 },
  card: { padding: 14, marginBottom: 10 },
  cardRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  info: { flex: 1 },
  actionCol: { alignItems: 'flex-end' },
  payButton: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6, marginTop: 4 },
  empty: { alignItems: 'center', marginTop: 40 },
  emptyText: { marginTop: 8 },
});
