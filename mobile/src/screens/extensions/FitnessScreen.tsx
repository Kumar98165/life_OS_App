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
import { useFitness } from '../../hooks/useExtensions';
import { WorkoutItem } from '../../types/extensions';

export const FitnessScreen: React.FC = () => {
  const { theme } = useTheme();
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState('');
  const [minutes, setMinutes] = useState('30');
  const [calories, setCalories] = useState('200');

  const { workouts, stats, createWorkout } = useFitness();

  const handleSave = async () => {
    if (!title.trim()) return;
    await createWorkout.mutateAsync({
      title: title.trim(),
      duration_minutes: parseInt(minutes, 10) || 30,
      calories_burned: parseInt(calories, 10) || 0,
      workout_type: 'strength',
    });
    setTitle('');
    setShowCreate(false);
  };

  const renderWorkout = ({ item }: { item: WorkoutItem }) => (
    <GlassCard style={styles.card}>
      <View style={styles.cardRow}>
        <View style={styles.iconCircle}>
          <Ionicons name="barbell-outline" size={20} color={theme.colors.primary} />
        </View>
        <View style={styles.info}>
          <Heading level={3}>{item.title}</Heading>
          <Caption color="secondary">{item.duration_minutes} mins • {item.workout_date}</Caption>
        </View>
        {item.calories_burned && (
          <View style={styles.calBox}>
            <BodyText weight="bold" style={{ color: theme.colors.primary }}>{item.calories_burned}</BodyText>
            <Caption color="muted">kcal</Caption>
          </View>
        )}
      </View>
    </GlassCard>
  );

  return (
    <SafeAreaContainer edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Heading level={1}>Fitness & Activity</Heading>
          <TouchableOpacity
            style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
            onPress={() => setShowCreate(!showCreate)}
          >
            <Ionicons name={showCreate ? 'close' : 'add'} size={24} color="#FFF" />
          </TouchableOpacity>
        </View>

        {stats.data && (
          <GlassCard style={styles.statsCard}>
            <View style={styles.statCol}>
              <Caption color="secondary">Workouts</Caption>
              <Heading level={2}>{stats.data.total_workouts}</Heading>
            </View>
            <View style={styles.statCol}>
              <Caption color="secondary">Total Time</Caption>
              <Heading level={2}>{stats.data.total_minutes}m</Heading>
            </View>
            <View style={styles.statCol}>
              <Caption color="secondary">Burned</Caption>
              <Heading level={2} style={{ color: theme.colors.primary }}>{stats.data.total_calories}</Heading>
            </View>
          </GlassCard>
        )}

        {showCreate && (
          <GlassCard style={styles.createCard}>
            <Heading level={3}>Log Workout</Heading>
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Workout Name (e.g. Upper Body Push)"
              placeholderTextColor={theme.colors.textMuted}
              value={title}
              onChangeText={setTitle}
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Duration (Minutes)"
              placeholderTextColor={theme.colors.textMuted}
              value={minutes}
              onChangeText={setMinutes}
              keyboardType="number-pad"
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Calories Burned"
              placeholderTextColor={theme.colors.textMuted}
              value={calories}
              onChangeText={setCalories}
              keyboardType="number-pad"
            />
            <PrimaryButton label="Log Session" onPress={handleSave} loading={createWorkout.isPending} />
          </GlassCard>
        )}

        <FlatList
          data={workouts.data || []}
          keyExtractor={(item) => item.id}
          renderItem={renderWorkout}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            !workouts.isLoading ? (
              <View style={styles.empty}>
                <Ionicons name="fitness-outline" size={48} color={theme.colors.textMuted} />
                <BodyText color="secondary" style={styles.emptyText}>No workouts logged yet</BodyText>
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
  statsCard: { flexDirection: 'row', padding: 16, marginBottom: 12, justifyContent: 'space-around' },
  statCol: { alignItems: 'center' },
  createCard: { padding: 16, marginBottom: 12 },
  input: { padding: 10, borderRadius: 8, marginVertical: 4 },
  list: { paddingBottom: 100 },
  card: { padding: 14, marginBottom: 10 },
  cardRow: { flexDirection: 'row', alignItems: 'center' },
  iconCircle: { width: 36, height: 36, borderRadius: 18, backgroundColor: '#6C63FF22', justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  info: { flex: 1 },
  calBox: { alignItems: 'flex-end' },
  empty: { alignItems: 'center', marginTop: 40 },
  emptyText: { marginTop: 8 },
});
