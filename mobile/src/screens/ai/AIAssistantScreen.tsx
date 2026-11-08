import React, { useState, useRef, useEffect, useMemo } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Modal,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';
import { useTheme } from '../../theme';
import {
  useAIConversations,
  useAIConversationHistory,
  useAISendMessage,
  useAIDeleteConversation,
  useAIHealth,
} from '../../hooks/useAI';
import { AIMessage } from '../../types/ai';
import {
  SafeAreaContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  ConfirmationModal,
  Toast,
} from '../../components';

const STARTER_PROMPTS = [
  { icon: 'checkbox-outline', text: 'What tasks do I have scheduled for today?' },
  { icon: 'flame-outline', text: 'How are my habit streaks doing?' },
  { icon: 'flag-outline', text: 'Give me an overview of my active goals.' },
  { icon: 'calendar-outline', text: 'What does my planner schedule look like?' },
];

export const AIAssistantScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation();
  const route = useRoute<any>();

  const [activeConversationId, setActiveConversationId] = useState<string | null>(
    route.params?.conversationId || null
  );
  const [inputText, setInputText] = useState('');
  const [localMessages, setLocalMessages] = useState<AIMessage[]>([]);
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);
  const [convToDelete, setConvToDelete] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const scrollViewRef = useRef<any>(null);

  // Queries & Mutations
  const { data: conversations = [], refetch: refetchConversations } = useAIConversations();
  const { data: historyData, isLoading: isHistoryLoading } = useAIConversationHistory(
    activeConversationId
  );
  const { data: healthData } = useAIHealth();
  const sendMessageMutation = useAISendMessage();
  const deleteConversationMutation = useAIDeleteConversation();

  // Sync server history into local state
  useEffect(() => {
    if (historyData?.messages) {
      setLocalMessages(historyData.messages);
    } else if (!activeConversationId) {
      setLocalMessages([]);
    }
  }, [historyData, activeConversationId]);

  // Auto scroll to bottom when messages update
  useEffect(() => {
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);
  }, [localMessages, sendMessageMutation.isPending]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const activeConversation = useMemo(() => {
    return conversations.find((c) => c.id === activeConversationId);
  }, [conversations, activeConversationId]);

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || inputText).trim();
    if (!text || sendMessageMutation.isPending) return;

    setInputText('');

    // Optimistically add user message
    const tempUserMsg: AIMessage = {
      id: `temp-${Date.now()}`,
      conversation_id: activeConversationId || '',
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };
    setLocalMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await sendMessageMutation.mutateAsync({
        message: text,
        conversationId: activeConversationId || undefined,
      });

      if (!activeConversationId && response.conversation_id) {
        setActiveConversationId(response.conversation_id);
      }

      setLocalMessages((prev) => [
        ...prev.filter((m) => m.id !== tempUserMsg.id),
        response.user_message,
        response.assistant_message,
      ]);
    } catch (err: any) {
      showToast(err.message || 'Failed to get response from local AI.');
    }
  };

  const handleStartNewChat = () => {
    setActiveConversationId(null);
    setLocalMessages([]);
    setIsHistoryModalOpen(false);
  };

  const handleSelectConversation = (convId: string) => {
    setActiveConversationId(convId);
    setIsHistoryModalOpen(false);
  };

  const handleDeleteConversation = async () => {
    if (!convToDelete) return;
    try {
      await deleteConversationMutation.mutateAsync(convToDelete);
      showToast('Conversation deleted');
      if (activeConversationId === convToDelete) {
        setActiveConversationId(null);
        setLocalMessages([]);
      }
      setConvToDelete(null);
      refetchConversations();
    } catch (err: any) {
      showToast(err.message || 'Failed to delete conversation');
    }
  };

  return (
    <SafeAreaContainer edges={['top']}>
      {/* Toast Feedback */}
      <Toast visible={!!toastMessage} message={toastMessage || ''} type="info" />

      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={[styles.backBtn, { borderColor: theme.colors.glassBorder }]}
            accessibilityRole="button"
            accessibilityLabel="Go back"
          >
            <Ionicons name="chevron-back" size={20} color={theme.colors.textPrimary} />
          </TouchableOpacity>
          <View style={styles.headerTitleGroup}>
            <Heading level={2} numberOfLines={1}>
              {activeConversation?.title || 'LifeOS AI'}
            </Heading>
            <View style={styles.badgeRow}>
              <View
                style={[
                  styles.onlineDot,
                  {
                    backgroundColor:
                      healthData?.healthy && healthData?.model_available
                        ? theme.colors.success
                        : theme.colors.warning,
                  },
                ]}
              />
              <Caption color="secondary" style={styles.modelPill}>
                {healthData?.model || 'Qwen 2.5 3B'} • Local
              </Caption>
            </View>
          </View>
        </View>

        <View style={styles.headerActions}>
          <TouchableOpacity
            onPress={() => (navigation as any).navigate('AIMemory')}
            style={[styles.iconActionBtn, { borderColor: theme.colors.glassBorder }]}
            accessibilityRole="button"
            accessibilityLabel="Digital Brain and Memory"
          >
            <Ionicons name="hardware-chip-outline" size={20} color={theme.colors.primary} />
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => setIsHistoryModalOpen(true)}
            style={[styles.iconActionBtn, { borderColor: theme.colors.glassBorder }]}
            accessibilityRole="button"
            accessibilityLabel="Chat history"
          >
            <Ionicons name="time-outline" size={20} color={theme.colors.textPrimary} />
          </TouchableOpacity>

          <TouchableOpacity
            onPress={handleStartNewChat}
            style={[styles.iconActionBtn, { borderColor: theme.colors.glassBorder }]}
            accessibilityRole="button"
            accessibilityLabel="New conversation"
          >
            <Ionicons name="add" size={22} color={theme.colors.primary} />
          </TouchableOpacity>
        </View>
      </View>

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
        style={styles.container}
      >
        {/* Messages List / Empty State */}
        <ScrollView
          ref={scrollViewRef}
          contentContainerStyle={styles.messagesScroll}
          showsVerticalScrollIndicator={false}
        >
          {localMessages.length === 0 && !isHistoryLoading ? (
            <View style={styles.emptyContainer}>
              <View
                style={[
                  styles.sparkleCircle,
                  { backgroundColor: `${theme.colors.primary}15` },
                ]}
              >
                <Ionicons name="sparkles" size={38} color={theme.colors.primary} />
              </View>
              <Heading level={2} align="center" style={styles.emptyTitle}>
                How can LifeOS assist you?
              </Heading>
              <BodyText color="secondary" align="center" style={styles.emptyDesc}>
                I run locally and have access to your authorized tasks, habits, schedule, and goals.
              </BodyText>

              {/* Starter Prompt Pills */}
              <View style={styles.starterGrid}>
                {STARTER_PROMPTS.map((p, idx) => (
                  <TouchableOpacity
                    key={idx}
                    activeOpacity={0.8}
                    onPress={() => handleSend(p.text)}
                    style={[
                      styles.starterCard,
                      {
                        backgroundColor: theme.colors.glassBackgroundSolid,
                        borderColor: theme.colors.glassBorder,
                      },
                      theme.shadows.subtle,
                    ]}
                  >
                    <Ionicons
                      name={p.icon as any}
                      size={18}
                      color={theme.colors.primary}
                      style={{ marginRight: 10 }}
                    />
                    <Caption weight="600" style={styles.starterText}>
                      {p.text}
                    </Caption>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          ) : (
            <View style={styles.messagesList}>
              {localMessages.map((msg) => {
                const isUser = msg.role === 'user';
                return (
                  <View
                    key={msg.id}
                    style={[
                      styles.messageRow,
                      isUser ? styles.userMessageRow : styles.assistantMessageRow,
                    ]}
                  >
                    {!isUser && (
                      <View
                        style={[
                          styles.avatarCircle,
                          { backgroundColor: `${theme.colors.primary}20` },
                        ]}
                      >
                        <Ionicons name="sparkles" size={14} color={theme.colors.primary} />
                      </View>
                    )}

                    <View
                      style={[
                        styles.messageBubble,
                        isUser
                          ? [styles.userBubble, { backgroundColor: theme.colors.primary }]
                          : [
                              styles.assistantBubble,
                              {
                                backgroundColor: theme.colors.glassBackgroundSolid,
                                borderColor: theme.colors.glassBorder,
                              },
                              theme.shadows.subtle,
                            ],
                      ]}
                    >
                      <BodyText
                        style={{
                          color: isUser ? '#FFFFFF' : theme.colors.textPrimary,
                          lineHeight: 22,
                        }}
                      >
                        {msg.content}
                      </BodyText>
                    </View>
                  </View>
                );
              })}

              {/* Generating / Typing Indicator */}
              {sendMessageMutation.isPending && (
                <View style={[styles.messageRow, styles.assistantMessageRow]}>
                  <View
                    style={[
                      styles.avatarCircle,
                      { backgroundColor: `${theme.colors.primary}20` },
                    ]}
                  >
                    <Ionicons name="sparkles" size={14} color={theme.colors.primary} />
                  </View>
                  <View
                    style={[
                      styles.messageBubble,
                      styles.assistantBubble,
                      {
                        backgroundColor: theme.colors.glassBackgroundSolid,
                        borderColor: theme.colors.glassBorder,
                        flexDirection: 'row',
                        alignItems: 'center',
                        paddingVertical: 12,
                      },
                    ]}
                  >
                    <ActivityIndicator size="small" color={theme.colors.primary} />
                    <Caption color="secondary" style={{ marginLeft: 8 }}>
                      LifeOS is thinking...
                    </Caption>
                  </View>
                </View>
              )}
            </View>
          )}
        </ScrollView>

        {/* Input Composer */}
        <View
          style={[
            styles.composerContainer,
            {
              backgroundColor: theme.colors.glassBackgroundSolid,
              borderTopColor: theme.colors.glassBorder,
            },
          ]}
        >
          <View
            style={[
              styles.inputWrapper,
              {
                backgroundColor: theme.colors.surfaceSubtle,
                borderColor: theme.colors.glassBorder,
              },
            ]}
          >
            <TextInput
              style={[styles.input, { color: theme.colors.textPrimary }]}
              placeholder="Ask LifeOS about your day..."
              placeholderTextColor={theme.colors.textMuted}
              value={inputText}
              onChangeText={setInputText}
              multiline
              maxLength={2000}
            />

            <TouchableOpacity
              onPress={() => handleSend()}
              disabled={!inputText.trim() || sendMessageMutation.isPending}
              style={[
                styles.sendBtn,
                {
                  backgroundColor:
                    inputText.trim() && !sendMessageMutation.isPending
                      ? theme.colors.primary
                      : theme.colors.surfaceSubtle,
                },
              ]}
              accessibilityRole="button"
              accessibilityLabel="Send message"
            >
              <Ionicons
                name="arrow-up"
                size={20}
                color={
                  inputText.trim() && !sendMessageMutation.isPending
                    ? '#FFFFFF'
                    : theme.colors.textMuted
                }
              />
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>

      {/* Conversation History Modal */}
      <Modal
        visible={isHistoryModalOpen}
        animationType="slide"
        transparent
        onRequestClose={() => setIsHistoryModalOpen(false)}
      >
        <View style={styles.historyModalOverlay}>
          <TouchableOpacity
            style={styles.modalBackdrop}
            activeOpacity={1}
            onPress={() => setIsHistoryModalOpen(false)}
          />

          <GlassCard elevation="floating" style={styles.historySheet}>
            <View style={styles.historyHeader}>
              <Heading level={2}>Chat Threads</Heading>
              <TouchableOpacity
                onPress={() => setIsHistoryModalOpen(false)}
                style={[styles.iconActionBtn, { borderColor: theme.colors.glassBorder }]}
              >
                <Ionicons name="close" size={20} color={theme.colors.textPrimary} />
              </TouchableOpacity>
            </View>

            <TouchableOpacity
              onPress={handleStartNewChat}
              style={[styles.newChatRow, { borderColor: theme.colors.primary }]}
            >
              <Ionicons name="add-circle-outline" size={22} color={theme.colors.primary} />
              <BodyText weight="600" style={{ color: theme.colors.primary, marginLeft: 8 }}>
                Start New Chat Thread
              </BodyText>
            </TouchableOpacity>

            <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.historyList}>
              {conversations.length === 0 ? (
                <Caption color="secondary" align="center" style={{ marginTop: 24 }}>
                  No previous conversations yet.
                </Caption>
              ) : (
                conversations.map((conv) => {
                  const isSelected = conv.id === activeConversationId;
                  return (
                    <TouchableOpacity
                      key={conv.id}
                      onPress={() => handleSelectConversation(conv.id)}
                      style={[
                        styles.historyItem,
                        {
                          backgroundColor: isSelected
                            ? `${theme.colors.primary}12`
                            : theme.colors.glassBackgroundSolid,
                          borderColor: isSelected
                            ? theme.colors.primary
                            : theme.colors.glassBorder,
                        },
                      ]}
                    >
                      <View style={{ flex: 1, marginRight: 8 }}>
                        <BodyText weight={isSelected ? '700' : '500'} numberOfLines={1}>
                          {conv.title}
                        </BodyText>
                        <Caption color="secondary">
                          {new Date(conv.updated_at).toLocaleDateString()}
                        </Caption>
                      </View>

                      <TouchableOpacity
                        onPress={(e) => {
                          e.stopPropagation();
                          setConvToDelete(conv.id);
                        }}
                        style={styles.deleteThreadBtn}
                      >
                        <Ionicons name="trash-outline" size={18} color={theme.colors.textMuted} />
                      </TouchableOpacity>
                    </TouchableOpacity>
                  );
                })
              )}
            </ScrollView>
          </GlassCard>
        </View>
      </Modal>

      {/* Delete Thread Confirmation */}
      <ConfirmationModal
        visible={!!convToDelete}
        title="Delete Conversation?"
        message="This conversation thread and all its dialogue turns will be permanently deleted."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        isDestructive
        onCancel={() => setConvToDelete(null)}
        onConfirm={handleDeleteConversation}
      />
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 8,
    paddingBottom: 12,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: 10,
  },
  backBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  headerTitleGroup: {
    flex: 1,
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 2,
  },
  onlineDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  modelPill: {
    fontSize: 12,
  },
  headerActions: {
    flexDirection: 'row',
    gap: 8,
  },
  iconActionBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  container: {
    flex: 1,
  },
  messagesScroll: {
    flexGrow: 1,
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 20,
  },
  emptyContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 16,
    paddingTop: 40,
  },
  sparkleCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  emptyTitle: {
    marginBottom: 8,
  },
  emptyDesc: {
    lineHeight: 22,
    marginBottom: 28,
  },
  starterGrid: {
    width: '100%',
    gap: 10,
  },
  starterCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    borderRadius: 16,
    borderWidth: 1,
  },
  starterText: {
    flex: 1,
  },
  messagesList: {
    gap: 14,
  },
  messageRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  userMessageRow: {
    justifyContent: 'flex-end',
  },
  assistantMessageRow: {
    justifyContent: 'flex-start',
  },
  avatarCircle: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
    marginBottom: 4,
  },
  messageBubble: {
    maxWidth: '82%',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
  },
  userBubble: {
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    borderBottomLeftRadius: 4,
    borderWidth: 1,
  },
  composerContainer: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderTopWidth: StyleSheet.hairlineWidth,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 24,
    borderWidth: 1,
    paddingHorizontal: 14,
    paddingVertical: 6,
  },
  input: {
    flex: 1,
    maxHeight: 100,
    fontSize: 15,
    paddingVertical: 6,
  },
  sendBtn: {
    width: 34,
    height: 34,
    borderRadius: 17,
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 8,
  },
  historyModalOverlay: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  modalBackdrop: {
    ...StyleSheet.absoluteFill,
    backgroundColor: 'rgba(15, 23, 42, 0.45)',
  },
  historySheet: {
    maxHeight: '75%',
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: Platform.OS === 'ios' ? 40 : 24,
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  newChatRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 14,
    borderWidth: 1,
    marginBottom: 16,
  },
  historyList: {
    gap: 10,
    paddingBottom: 20,
  },
  historyItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 14,
    borderRadius: 16,
    borderWidth: 1,
  },
  deleteThreadBtn: {
    padding: 6,
  },
});
