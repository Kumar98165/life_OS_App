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
import { usePersonalItems } from '../../hooks/usePeople';
import { PersonalItem } from '../../types/people';

export const ItemLendingScreen: React.FC = () => {
  const { theme } = useTheme();
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [category, setCategory] = useState('electronics');
  const [selectedLendItem, setSelectedLendItem] = useState<string | null>(null);
  const [lendToPerson, setLendToPerson] = useState('');

  const { data: items, isLoading, createItem, lendItem, returnItem, deleteItem } = usePersonalItems();

  const handleSave = async () => {
    if (!name.trim()) return;
    await createItem.mutateAsync({
      name: name.trim(),
      description: desc.trim() || undefined,
      category,
    });
    setName('');
    setDesc('');
    setShowCreate(false);
  };

  const handleLend = async (itemId: string) => {
    if (!lendToPerson.trim()) return;
    await lendItem.mutateAsync({
      id: itemId,
      data: { person_name: lendToPerson.trim() },
    });
    setSelectedLendItem(null);
    setLendToPerson('');
  };

  const renderItem = ({ item }: { item: PersonalItem }) => (
    <GlassCard style={styles.card}>
      <View style={styles.cardRow}>
        <View style={styles.iconCircle}>
          <Ionicons name="cube-outline" size={20} color={theme.colors.primary} />
        </View>
        <View style={styles.info}>
          <Heading level={3}>{item.name}</Heading>
          <Caption color="secondary">{item.category} • {item.initial_condition}</Caption>
          {item.currently_with ? (
            <Caption style={{ color: '#FF9100' }} weight="600">With: {item.currently_with}</Caption>
          ) : (
            <Caption style={{ color: '#00C853' }} weight="600">Available</Caption>
          )}
        </View>

        <View style={styles.actionCol}>
          {item.status === 'lent' ? (
            <TouchableOpacity
              style={[styles.smallBtn, { backgroundColor: '#00C853' }]}
              onPress={() => returnItem.mutate({ id: item.id })}
            >
              <Caption style={{ color: '#FFF' }} weight="600">Return</Caption>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity
              style={[styles.smallBtn, { backgroundColor: theme.colors.primary }]}
              onPress={() => setSelectedLendItem(item.id)}
            >
              <Caption style={{ color: '#FFF' }} weight="600">Lend</Caption>
            </TouchableOpacity>
          )}
        </View>
      </View>

      {selectedLendItem === item.id && (
        <View style={styles.inlineLend}>
          <TextInput
            style={[styles.input, styles.lendInput, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
            placeholder="Lend to (Person Name)"
            placeholderTextColor={theme.colors.textMuted}
            value={lendToPerson}
            onChangeText={setLendToPerson}
          />
          <TouchableOpacity
            style={[styles.smallBtn, { backgroundColor: theme.colors.primary }]}
            onPress={() => handleLend(item.id)}
          >
            <Caption style={{ color: '#FFF' }} weight="600">Confirm</Caption>
          </TouchableOpacity>
          <TouchableOpacity onPress={() => setSelectedLendItem(null)} style={{ marginLeft: 8 }}>
            <Ionicons name="close-circle-outline" size={22} color={theme.colors.textMuted} />
          </TouchableOpacity>
        </View>
      )}
    </GlassCard>
  );

  return (
    <SafeAreaContainer edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Heading level={1}>Personal Item Lending</Heading>
          <TouchableOpacity
            style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
            onPress={() => setShowCreate(!showCreate)}
          >
            <Ionicons name={showCreate ? 'close' : 'add'} size={24} color="#FFF" />
          </TouchableOpacity>
        </View>

        {showCreate && (
          <GlassCard style={styles.createCard}>
            <Heading level={3}>Register Belonging / Item</Heading>
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Item Name (e.g. Sony Camera)"
              placeholderTextColor={theme.colors.textMuted}
              value={name}
              onChangeText={setName}
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Description (Optional)"
              placeholderTextColor={theme.colors.textMuted}
              value={desc}
              onChangeText={setDesc}
            />
            <PrimaryButton label="Save Item" onPress={handleSave} loading={createItem.isPending} />
          </GlassCard>
        )}

        <FlatList
          data={items || []}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            !isLoading ? (
              <View style={styles.empty}>
                <Ionicons name="cube-outline" size={48} color={theme.colors.textMuted} />
                <BodyText color="secondary" style={styles.emptyText}>No items registered</BodyText>
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
  cardRow: { flexDirection: 'row', alignItems: 'center' },
  iconCircle: { width: 38, height: 38, borderRadius: 19, backgroundColor: '#6C63FF22', justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  info: { flex: 1 },
  actionCol: { alignItems: 'flex-end' },
  smallBtn: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 6 },
  inlineLend: { flexDirection: 'row', alignItems: 'center', marginTop: 10, paddingTop: 8, borderTopWidth: 1, borderTopColor: '#E0E0E022' },
  lendInput: { flex: 1, marginVertical: 0, marginRight: 8 },
  empty: { alignItems: 'center', marginTop: 40 },
  emptyText: { marginTop: 8 },
});
