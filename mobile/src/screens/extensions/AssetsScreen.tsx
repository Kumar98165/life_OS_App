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
import { useAssets } from '../../hooks/useExtensions';
import { PersonalAssetItem } from '../../types/extensions';

export const AssetsScreen: React.FC = () => {
  const { theme } = useTheme();
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState('');
  const [price, setPrice] = useState('');
  const [serial, setSerial] = useState('');

  const { data: assets, isLoading, createAsset } = useAssets();

  const handleSave = async () => {
    if (!name.trim()) return;
    await createAsset.mutateAsync({
      name: name.trim(),
      purchase_price: parseFloat(price) || undefined,
      serial_number: serial.trim() || undefined,
      category: 'electronics',
    });
    setName('');
    setPrice('');
    setSerial('');
    setShowCreate(false);
  };

  const renderAsset = ({ item }: { item: PersonalAssetItem }) => (
    <GlassCard style={styles.card}>
      <View style={styles.cardRow}>
        <View style={styles.info}>
          <Heading level={3}>{item.name}</Heading>
          <Caption color="secondary">{item.category} • {item.status.toUpperCase()}</Caption>
          {item.serial_number && <Caption color="muted">S/N: {item.serial_number}</Caption>}
        </View>
        {item.purchase_price != null && (
          <Heading level={3} style={{ color: theme.colors.primary }}>${item.purchase_price.toFixed(0)}</Heading>
        )}
      </View>
    </GlassCard>
  );

  return (
    <SafeAreaContainer edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Heading level={1}>Personal Assets</Heading>
          <TouchableOpacity
            style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
            onPress={() => setShowCreate(!showCreate)}
          >
            <Ionicons name={showCreate ? 'close' : 'add'} size={24} color="#FFF" />
          </TouchableOpacity>
        </View>

        {showCreate && (
          <GlassCard style={styles.createCard}>
            <Heading level={3}>Register Asset</Heading>
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Item Name (e.g. MacBook Pro)"
              placeholderTextColor={theme.colors.textMuted}
              value={name}
              onChangeText={setName}
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Purchase Price"
              placeholderTextColor={theme.colors.textMuted}
              value={price}
              onChangeText={setPrice}
              keyboardType="decimal-pad"
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Serial Number (Optional)"
              placeholderTextColor={theme.colors.textMuted}
              value={serial}
              onChangeText={setSerial}
            />
            <PrimaryButton label="Save Asset" onPress={handleSave} loading={createAsset.isPending} />
          </GlassCard>
        )}

        <FlatList
          data={assets || []}
          keyExtractor={(item) => item.id}
          renderItem={renderAsset}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            !isLoading ? (
              <View style={styles.empty}>
                <Ionicons name="cube-outline" size={48} color={theme.colors.textMuted} />
                <BodyText color="secondary" style={styles.emptyText}>No assets registered</BodyText>
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
  empty: { alignItems: 'center', marginTop: 40 },
  emptyText: { marginTop: 8 },
});
