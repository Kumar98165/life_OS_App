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
import { useTrips } from '../../hooks/useExtensions';
import { TripItem } from '../../types/extensions';

export const TravelScreen: React.FC = () => {
  const { theme } = useTheme();
  const [showCreate, setShowCreate] = useState(false);
  const [destination, setDestination] = useState('');
  const [title, setTitle] = useState('');
  const [budget, setBudget] = useState('');

  const { data: trips, isLoading, createTrip } = useTrips();

  const handleSave = async () => {
    if (!destination.trim() || !title.trim()) return;
    const today = new Date().toISOString().split('T')[0];
    const nextWeek = new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0];

    await createTrip.mutateAsync({
      destination: destination.trim(),
      title: title.trim(),
      start_date: today,
      end_date: nextWeek,
      budget: parseFloat(budget) || 0,
    });
    setDestination('');
    setTitle('');
    setBudget('');
    setShowCreate(false);
  };

  const renderTrip = ({ item }: { item: TripItem }) => (
    <GlassCard style={styles.card}>
      <View style={styles.headerRow}>
        <View style={styles.info}>
          <Heading level={3}>{item.title}</Heading>
          <Caption color="secondary">{item.destination}</Caption>
          <Caption color="muted">{item.start_date} → {item.end_date}</Caption>
        </View>
        <View style={styles.statusBox}>
          <Caption style={{ color: theme.colors.primary }} weight="600">{item.status.toUpperCase()}</Caption>
          <BodyText weight="bold">${item.budget.toFixed(0)}</BodyText>
        </View>
      </View>
    </GlassCard>
  );

  return (
    <SafeAreaContainer edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Heading level={1}>Travel Planner</Heading>
          <TouchableOpacity
            style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
            onPress={() => setShowCreate(!showCreate)}
          >
            <Ionicons name={showCreate ? 'close' : 'add'} size={24} color="#FFF" />
          </TouchableOpacity>
        </View>

        {showCreate && (
          <GlassCard style={styles.createCard}>
            <Heading level={3}>New Trip</Heading>
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Trip Title (e.g. Kyoto Vacation)"
              placeholderTextColor={theme.colors.textMuted}
              value={title}
              onChangeText={setTitle}
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Destination (e.g. Kyoto, Japan)"
              placeholderTextColor={theme.colors.textMuted}
              value={destination}
              onChangeText={setDestination}
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Budget (USD)"
              placeholderTextColor={theme.colors.textMuted}
              value={budget}
              onChangeText={setBudget}
              keyboardType="decimal-pad"
            />
            <PrimaryButton label="Save Trip" onPress={handleSave} loading={createTrip.isPending} />
          </GlassCard>
        )}

        <FlatList
          data={trips || []}
          keyExtractor={(item) => item.id}
          renderItem={renderTrip}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            !isLoading ? (
              <View style={styles.empty}>
                <Ionicons name="airplane-outline" size={48} color={theme.colors.textMuted} />
                <BodyText color="secondary" style={styles.emptyText}>No upcoming trips</BodyText>
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
  headerRow: { flexDirection: 'row', justifyContent: 'space-between' },
  info: { flex: 1 },
  statusBox: { alignItems: 'flex-end' },
  empty: { alignItems: 'center', marginTop: 40 },
  emptyText: { marginTop: 8 },
});
