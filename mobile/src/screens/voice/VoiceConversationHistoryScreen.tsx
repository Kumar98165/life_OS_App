import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { useAIConversations, useAIDeleteConversation } from '../../hooks/useAI';
import { AIConversation } from '../../types/ai';

interface VoiceConversationHistoryScreenProps {
  navigation: any;
}

export function VoiceConversationHistoryScreen({ navigation }: VoiceConversationHistoryScreenProps) {
  const { theme } = useTheme();
  const insets = useSafeAreaInsets();

  const { data: conversations = [], isLoading, refetch } = useAIConversations();
  const deleteMutation = useAIDeleteConversation();
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = (id: string, title: string) => {
    Alert.alert(
      'Delete Conversation',
      `Are you sure you want to delete "${title}"? This cannot be undone.`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => {
            setDeletingId(id);
            deleteMutation.mutate(id, {
              onSettled: () => setDeletingId(null),
            });
          },
        },
      ]
    );
  };

  const handleSelectConversation = (conv: AIConversation) => {
    // Navigate to VoiceAssistantScreen or AIAssistantScreen with this thread
    navigation.navigate('VoiceAssistant', { conversationId: conv.id });
  };

  const renderItem = ({ item }: { item: AIConversation }) => {
    const isDeleting = deletingId === item.id;
    const formattedDate = item.updated_at
      ? new Date(item.updated_at).toLocaleDateString([], {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })
      : '';

    return (
      <TouchableOpacity
        onPress={() => handleSelectConversation(item)}
        style={[
          styles.itemCard,
          { backgroundColor: theme.colors.surface, borderColor: theme.colors.border },
        ]}
        accessibilityRole="button"
        accessibilityLabel={`Conversation: ${item.title}`}
      >
        <View style={[styles.iconCircle, { backgroundColor: `${theme.colors.primary}15` }]}>
          <Ionicons name="chatbubble-ellipses-outline" size={20} color={theme.colors.primary} />
        </View>

        <View style={styles.itemContent}>
          <Text style={[styles.itemTitle, { color: theme.colors.textPrimary }]} numberOfLines={1}>
            {item.title || 'Voice Dialogue'}
          </Text>
          <View style={styles.itemMeta}>
            <Text style={[styles.itemDate, { color: theme.colors.textSecondary }]}>{formattedDate}</Text>
            {item.messages_count !== undefined && (
              <Text style={[styles.itemCount, { color: theme.colors.textSecondary }]}>
                • {item.messages_count} {item.messages_count === 1 ? 'message' : 'messages'}
              </Text>
            )}
          </View>
        </View>

        <TouchableOpacity
          onPress={() => handleDelete(item.id, item.title)}
          disabled={isDeleting}
          style={styles.deleteButton}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          {isDeleting ? (
            <ActivityIndicator size="small" color={theme.colors.error || '#EF4444'} />
          ) : (
            <Ionicons name="trash-outline" size={18} color={theme.colors.textSecondary} />
          )}
        </TouchableOpacity>
      </TouchableOpacity>
    );
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background, paddingTop: insets.top }]}>
      {/* Header */}
      <View style={[styles.header, { borderBottomColor: theme.colors.border }]}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          <Ionicons name="arrow-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <View style={styles.headerTitleContainer}>
          <Text style={[styles.headerTitle, { color: theme.colors.textPrimary }]}>Voice & Chat History</Text>
          <Text style={[styles.headerSubtitle, { color: theme.colors.textSecondary }]}>
            Shared with LifeOS Assistant
          </Text>
        </View>
      </View>

      {/* List */}
      {isLoading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      ) : conversations.length === 0 ? (
        <View style={styles.emptyContainer}>
          <View style={[styles.emptyIconCircle, { backgroundColor: `${theme.colors.primary}15` }]}>
            <Ionicons name="mic-outline" size={40} color={theme.colors.primary} />
          </View>
          <Text style={[styles.emptyTitle, { color: theme.colors.textPrimary }]}>No Dialogue History</Text>
          <Text style={[styles.emptySubtitle, { color: theme.colors.textSecondary }]}>
            Conversations conducted via voice or chat appear here for easy continuation.
          </Text>
        </View>
      ) : (
        <FlatList
          data={conversations}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.listContent}
          onRefresh={refetch}
          refreshing={isLoading}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  backButton: {
    marginRight: 12,
  },
  headerTitleContainer: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
  },
  headerSubtitle: {
    fontSize: 12,
    marginTop: 2,
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  listContent: {
    padding: 16,
  },
  itemCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    borderRadius: 14,
    borderWidth: StyleSheet.hairlineWidth,
    marginBottom: 10,
  },
  iconCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  itemContent: {
    flex: 1,
  },
  itemTitle: {
    fontSize: 15,
    fontWeight: '600',
    marginBottom: 4,
  },
  itemMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  itemDate: {
    fontSize: 12,
  },
  itemCount: {
    fontSize: 12,
  },
  deleteButton: {
    padding: 6,
    marginLeft: 8,
  },
  emptyContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 32,
  },
  emptyIconCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 6,
  },
  emptySubtitle: {
    fontSize: 13,
    textAlign: 'center',
    lineHeight: 18,
  },
});
