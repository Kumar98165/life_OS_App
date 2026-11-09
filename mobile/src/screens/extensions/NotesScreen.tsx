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
import { useNotes, useNoteFolders } from '../../hooks/useExtensions';
import { NoteItem } from '../../types/extensions';

export const NotesScreen: React.FC = () => {
  const { theme } = useTheme();
  const [search, setSearch] = useState('');
  const [selectedFolder, setSelectedFolder] = useState<string | undefined>();
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const { data: notes, isLoading, createNote, deleteNote } = useNotes({
    search: search || undefined,
    folder_id: selectedFolder,
  });
  const { data: folders } = useNoteFolders();

  const handleSave = async () => {
    if (!title.trim()) return;
    await createNote.mutateAsync({
      title: title.trim(),
      content: content.trim(),
      folder_id: selectedFolder,
    });
    setTitle('');
    setContent('');
    setShowCreate(false);
  };

  const renderNote = ({ item }: { item: NoteItem }) => (
    <GlassCard style={styles.noteCard}>
      <View style={styles.noteHeader}>
        <View style={styles.titleRow}>
          {item.is_pinned && (
            <Ionicons name="pin" size={16} color={theme.colors.primary} style={styles.pinIcon} />
          )}
          <Heading level={3} numberOfLines={1}>{item.title}</Heading>
        </View>
        <TouchableOpacity onPress={() => deleteNote.mutate(item.id)}>
          <Ionicons name="trash-outline" size={18} color={theme.colors.error || '#FF5252'} />
        </TouchableOpacity>
      </View>
      <BodyText color="secondary" numberOfLines={3} style={styles.noteContent}>
        {item.content || 'No content...'}
      </BodyText>
      <View style={styles.noteFooter}>
        <Caption color="muted">{new Date(item.updated_at).toLocaleDateString()}</Caption>
        {item.folder && (
          <View style={[styles.badge, { backgroundColor: item.folder.color_hex + '22' }]}>
            <Caption style={{ color: item.folder.color_hex }}>{item.folder.name}</Caption>
          </View>
        )}
      </View>
    </GlassCard>
  );

  return (
    <SafeAreaContainer edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Heading level={1}>Notes & Docs</Heading>
          <TouchableOpacity
            style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
            onPress={() => setShowCreate(!showCreate)}
          >
            <Ionicons name={showCreate ? 'close' : 'add'} size={24} color="#FFF" />
          </TouchableOpacity>
        </View>

        <TextInput
          style={[styles.searchInput, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
          placeholder="Search notes..."
          placeholderTextColor={theme.colors.textMuted}
          value={search}
          onChangeText={setSearch}
        />

        {showCreate && (
          <GlassCard style={styles.createCard}>
            <Heading level={3}>New Note</Heading>
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Title"
              placeholderTextColor={theme.colors.textMuted}
              value={title}
              onChangeText={setTitle}
            />
            <TextInput
              style={[styles.input, styles.textArea, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Content..."
              placeholderTextColor={theme.colors.textMuted}
              value={content}
              onChangeText={setContent}
              multiline
            />
            <PrimaryButton label="Save Note" onPress={handleSave} loading={createNote.isPending} />
          </GlassCard>
        )}

        <FlatList
          data={notes || []}
          keyExtractor={(item) => item.id}
          renderItem={renderNote}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            !isLoading ? (
              <View style={styles.empty}>
                <Ionicons name="document-text-outline" size={48} color={theme.colors.textMuted} />
                <BodyText color="secondary" style={styles.emptyText}>No notes found</BodyText>
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
  searchInput: { padding: 12, borderRadius: 10, marginBottom: 12 },
  createCard: { padding: 16, marginBottom: 12 },
  input: { padding: 10, borderRadius: 8, marginVertical: 6 },
  textArea: { height: 80, textAlignVertical: 'top' },
  list: { paddingBottom: 100 },
  noteCard: { padding: 14, marginBottom: 10 },
  noteHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  titleRow: { flexDirection: 'row', alignItems: 'center', flex: 1 },
  pinIcon: { marginRight: 6 },
  noteContent: { marginVertical: 8 },
  noteFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  badge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 6 },
  empty: { alignItems: 'center', marginTop: 40 },
  emptyText: { marginTop: 8 },
});
