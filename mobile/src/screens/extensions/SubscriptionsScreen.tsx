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
import { useSubscriptions } from '../../hooks/useExtensions';
import { SubscriptionItem } from '../../types/extensions';

export const SubscriptionsScreen: React.FC = () => {
  const { theme } = useTheme();
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState('');
  const [amount, setAmount] = useState('');
  const [cycle, setCycle] = useState<'monthly' | 'yearly'>('monthly');

  const { data: subs, summary, isLoading, createSubscription, deleteSubscription } = useSubscriptions();

  const handleSave = async () => {
    if (!name.trim() || !amount.trim()) return;
    const renewal = new Date();
    renewal.setMonth(renewal.getMonth() + 1);

    await createSubscription.mutateAsync({
      name: name.trim(),
      amount: parseFloat(amount),
      billing_cycle: cycle,
      renewal_date: renewal.toISOString().split('T')[0],
    });
    setName('');
    setAmount('');
    setShowCreate(false);
  };

  const renderSub = ({ item }: { item: SubscriptionItem }) => (
    <GlassCard style={styles.card}>
      <View style={styles.cardRow}>
        <View style={styles.info}>
          <Heading level={3}>{item.name}</Heading>
          <Caption color="secondary">Renews: {item.renewal_date}</Caption>
        </View>
        <View style={styles.amountBox}>
          <Heading level={3} style={{ color: theme.colors.primary }}>${item.amount.toFixed(2)}</Heading>
          <Caption color="muted">/{item.billing_cycle}</Caption>
        </View>
        <TouchableOpacity onPress={() => deleteSubscription.mutate(item.id)} style={{ marginLeft: 12 }}>
          <Ionicons name="trash-outline" size={18} color={theme.colors.error || '#FF5252'} />
        </TouchableOpacity>
      </View>
    </GlassCard>
  );

  return (
    <SafeAreaContainer edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Heading level={1}>Subscriptions</Heading>
          <TouchableOpacity
            style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
            onPress={() => setShowCreate(!showCreate)}
          >
            <Ionicons name={showCreate ? 'close' : 'add'} size={24} color="#FFF" />
          </TouchableOpacity>
        </View>

        {summary.data && (
          <GlassCard style={styles.summaryCard}>
            <View style={styles.summaryCol}>
              <Caption color="secondary">Active</Caption>
              <Heading level={2}>{summary.data.active_count}</Heading>
            </View>
            <View style={styles.summaryCol}>
              <Caption color="secondary">Monthly Cost</Caption>
              <Heading level={2} style={{ color: theme.colors.primary }}>${summary.data.estimated_monthly_expense.toFixed(2)}</Heading>
            </View>
          </GlassCard>
        )}

        {showCreate && (
          <GlassCard style={styles.createCard}>
            <Heading level={3}>New Subscription</Heading>
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Service Name (e.g. Netflix)"
              placeholderTextColor={theme.colors.textMuted}
              value={name}
              onChangeText={setName}
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Amount (e.g. 14.99)"
              placeholderTextColor={theme.colors.textMuted}
              value={amount}
              onChangeText={setAmount}
              keyboardType="decimal-pad"
            />
            <PrimaryButton label="Save Subscription" onPress={handleSave} loading={createSubscription.isPending} />
          </GlassCard>
        )}

        <FlatList
          data={subs || []}
          keyExtractor={(item) => item.id}
          renderItem={renderSub}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            !isLoading ? (
              <View style={styles.empty}>
                <Ionicons name="card-outline" size={48} color={theme.colors.textMuted} />
                <BodyText color="secondary" style={styles.emptyText}>No active subscriptions</BodyText>
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
  summaryCard: { flexDirection: 'row', padding: 16, marginBottom: 12, justifyContent: 'space-around' },
  summaryCol: { alignItems: 'center' },
  createCard: { padding: 16, marginBottom: 12 },
  input: { padding: 10, borderRadius: 8, marginVertical: 4 },
  list: { paddingBottom: 100 },
  card: { padding: 14, marginBottom: 10 },
  cardRow: { flexDirection: 'row', alignItems: 'center' },
  info: { flex: 1 },
  amountBox: { alignItems: 'flex-end' },
  empty: { alignItems: 'center', marginTop: 40 },
  emptyText: { marginTop: 8 },
});
