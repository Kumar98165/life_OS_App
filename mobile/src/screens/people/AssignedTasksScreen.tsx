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
import { useAssignedTasks } from '../../hooks/usePeople';
import { AssignedTask } from '../../types/people';

export const AssignedTasksScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<any>();
  const [showCreate, setShowCreate] = useState(false);
  const [personName, setPersonName] = useState('');
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high' | 'urgent'>('medium');

  const { data: tasks, isLoading, createTask, updateTask, deleteTask } = useAssignedTasks();

  const handleSave = async () => {
    if (!personName.trim() || !title.trim()) return;
    await createTask.mutateAsync({
      person_name: personName.trim(),
      title: title.trim(),
      description: desc.trim() || undefined,
      priority,
      status: 'assigned',
    });
    setPersonName('');
    setTitle('');
    setDesc('');
    setShowCreate(false);
  };

  const renderTask = ({ item }: { item: AssignedTask }) => (
    <GlassCard style={styles.card}>
      <View style={styles.cardHeader}>
        <View style={styles.info}>
          <Heading level={3}>{item.title}</Heading>
          <TouchableOpacity onPress={() => navigation.navigate('PersonLedger', { personName: item.person_name })}>
            <Caption style={{ color: theme.colors.primary }} weight="600">Assigned to: {item.person_name}</Caption>
          </TouchableOpacity>
        </View>
        <View style={[styles.badge, { backgroundColor: item.priority === 'urgent' ? '#FF525222' : '#6C63FF22' }]}>
          <Caption style={{ color: item.priority === 'urgent' ? '#FF5252' : theme.colors.primary }} weight="600">
            {item.priority.toUpperCase()}
          </Caption>
        </View>
      </View>
      {item.description && (
        <BodyText color="secondary" numberOfLines={2} style={styles.desc}>{item.description}</BodyText>
      )}
      <View style={styles.cardFooter}>
        <Caption color="muted">Status: {item.status.toUpperCase()}</Caption>
        <View style={styles.actionRow}>
          {item.status !== 'completed' && (
            <TouchableOpacity
              style={[styles.actionBtn, { backgroundColor: theme.colors.primary }]}
              onPress={() => updateTask.mutate({ id: item.id, data: { status: 'completed' } })}
            >
              <Caption style={{ color: '#FFF' }} weight="600">Complete</Caption>
            </TouchableOpacity>
          )}
          <TouchableOpacity onPress={() => deleteTask.mutate(item.id)} style={{ marginLeft: 12 }}>
            <Ionicons name="trash-outline" size={18} color={theme.colors.error || '#FF5252'} />
          </TouchableOpacity>
        </View>
      </View>
    </GlassCard>
  );

  return (
    <SafeAreaContainer edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Heading level={1}>Assigned Tasks</Heading>
          <TouchableOpacity
            style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
            onPress={() => setShowCreate(!showCreate)}
          >
            <Ionicons name={showCreate ? 'close' : 'add'} size={24} color="#FFF" />
          </TouchableOpacity>
        </View>

        {showCreate && (
          <GlassCard style={styles.createCard}>
            <Heading level={3}>Assign New Task</Heading>
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Person Name (e.g. Rahul)"
              placeholderTextColor={theme.colors.textMuted}
              value={personName}
              onChangeText={setPersonName}
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Task Title"
              placeholderTextColor={theme.colors.textMuted}
              value={title}
              onChangeText={setTitle}
            />
            <TextInput
              style={[styles.input, styles.textArea, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Description (Optional)"
              placeholderTextColor={theme.colors.textMuted}
              value={desc}
              onChangeText={setDesc}
              multiline
            />
            <PrimaryButton label="Assign Task" onPress={handleSave} loading={createTask.isPending} />
          </GlassCard>
        )}

        <FlatList
          data={tasks || []}
          keyExtractor={(item) => item.id}
          renderItem={renderTask}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            !isLoading ? (
              <View style={styles.empty}>
                <Ionicons name="clipboard-outline" size={48} color={theme.colors.textMuted} />
                <BodyText color="secondary" style={styles.emptyText}>No assigned tasks</BodyText>
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
  textArea: { height: 60, textAlignVertical: 'top' },
  list: { paddingBottom: 100 },
  card: { padding: 14, marginBottom: 10 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  info: { flex: 1 },
  badge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 6 },
  desc: { marginVertical: 6 },
  cardFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 },
  actionRow: { flexDirection: 'row', alignItems: 'center' },
  actionBtn: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6 },
  empty: { alignItems: 'center', marginTop: 40 },
  emptyText: { marginTop: 8 },
});
