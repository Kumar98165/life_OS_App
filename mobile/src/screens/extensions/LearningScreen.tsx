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
import { useLearningGoals } from '../../hooks/useExtensions';
import { LearningGoalItem } from '../../types/extensions';

export const LearningScreen: React.FC = () => {
  const { theme } = useTheme();
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('technology');
  const [hours, setHours] = useState('50');

  const { data: goals, isLoading, createGoal, addSession } = useLearningGoals();

  const handleSave = async () => {
    if (!title.trim()) return;
    await createGoal.mutateAsync({
      title: title.trim(),
      category,
      target_hours: parseInt(hours, 10) || 50,
    });
    setTitle('');
    setShowCreate(false);
  };

  const renderGoal = ({ item }: { item: LearningGoalItem }) => (
    <GlassCard style={styles.card}>
      <View style={styles.cardHeader}>
        <View style={styles.info}>
          <Heading level={3}>{item.title}</Heading>
          <Caption color="secondary">{item.category} • {item.current_hours}h / {item.target_hours}h</Caption>
        </View>
        <TouchableOpacity
          style={[styles.sessionButton, { backgroundColor: theme.colors.primary }]}
          onPress={() => addSession.mutate({
            goalId: item.id,
            data: { duration_minutes: 60, topics_covered: 'Daily study session' },
          })}
        >
          <Ionicons name="add" size={16} color="#FFF" />
          <Caption weight="600" style={{ color: '#FFF', marginLeft: 4 }}>+1h</Caption>
        </TouchableOpacity>
      </View>
      <View style={styles.progressBar}>
        <View style={[styles.progressFill, { width: `${item.progress_percent}%`, backgroundColor: theme.colors.primary }]} />
      </View>
      <View style={styles.footer}>
        <Caption color="muted">{item.progress_percent}% Completed</Caption>
        <Caption color="secondary" weight="600">{item.status.toUpperCase()}</Caption>
      </View>
    </GlassCard>
  );

  return (
    <SafeAreaContainer edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Heading level={1}>Learning & Skills</Heading>
          <TouchableOpacity
            style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
            onPress={() => setShowCreate(!showCreate)}
          >
            <Ionicons name={showCreate ? 'close' : 'add'} size={24} color="#FFF" />
          </TouchableOpacity>
        </View>

        {showCreate && (
          <GlassCard style={styles.createCard}>
            <Heading level={3}>New Skill Goal</Heading>
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Skill / Topic (e.g. Python)"
              placeholderTextColor={theme.colors.textMuted}
              value={title}
              onChangeText={setTitle}
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Target Hours (e.g. 50)"
              placeholderTextColor={theme.colors.textMuted}
              value={hours}
              onChangeText={setHours}
              keyboardType="number-pad"
            />
            <PrimaryButton label="Save Goal" onPress={handleSave} loading={createGoal.isPending} />
          </GlassCard>
        )}

        <FlatList
          data={goals || []}
          keyExtractor={(item) => item.id}
          renderItem={renderGoal}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            !isLoading ? (
              <View style={styles.empty}>
                <Ionicons name="school-outline" size={48} color={theme.colors.textMuted} />
                <BodyText color="secondary" style={styles.emptyText}>No learning goals set</BodyText>
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
  cardHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  info: { flex: 1 },
  sessionButton: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 8 },
  progressBar: { height: 6, backgroundColor: '#E0E0E044', borderRadius: 3, marginVertical: 10, overflow: 'hidden' },
  progressFill: { height: '100%', borderRadius: 3 },
  footer: { flexDirection: 'row', justifyContent: 'space-between' },
  empty: { alignItems: 'center', marginTop: 40 },
  emptyText: { marginTop: 8 },
});
