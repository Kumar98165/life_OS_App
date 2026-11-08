import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
  Switch,
  Modal,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../../theme';
import {
  useConfirmedMemories,
  usePendingSuggestions,
  useMemorySettings,
  useAIMemoryMutations,
} from '../../../hooks/useAIMemory';
import {
  AIMemory,
  AIMemoryCategory,
} from '../../../types/aiMemory';
import {
  SafeAreaContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  ConfirmationModal,
  Toast,
} from '../../../components';

const CATEGORIES: { label: string; value: AIMemoryCategory | 'all'; icon: string }[] = [
  { label: 'All', value: 'all', icon: 'apps-outline' },
  { label: 'Preferences', value: 'preference', icon: 'heart-outline' },
  { label: 'Context', value: 'personal_context', icon: 'briefcase-outline' },
  { label: 'Goals', value: 'goal_decision', icon: 'flag-outline' },
  { label: 'Routines', value: 'routine_pattern', icon: 'repeat-outline' },
  { label: 'Facts', value: 'fact', icon: 'information-circle-outline' },
];

export const AIMemoryScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation();

  // Active Tab: 'confirmed' | 'pending' | 'settings'
  const [activeTab, setActiveTab] = useState<'confirmed' | 'pending' | 'settings'>('confirmed');
  const [selectedCategory, setSelectedCategory] = useState<AIMemoryCategory | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Modals state
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingMemory, setEditingMemory] = useState<AIMemory | null>(null);
  const [formKey, setFormKey] = useState('');
  const [formValue, setFormValue] = useState('');
  const [formCategory, setFormCategory] = useState<AIMemoryCategory>('fact');

  // Deletion / rejection confirm
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);
  const [rejectTargetId, setRejectTargetId] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Queries & Mutations
  const {
    data: confirmedData,
    isLoading: isConfirmedLoading,
  } = useConfirmedMemories(selectedCategory, searchQuery);

  const {
    data: pendingData,
    isLoading: isPendingLoading,
  } = usePendingSuggestions();

  const { data: settingsData } = useMemorySettings();

  const {
    createMemory,
    updateMemory,
    deleteMemory,
    approveSuggestion,
    rejectSuggestion,
    archiveMemory,
    updateSettings,
  } = useAIMemoryMutations();

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const confirmedList = confirmedData?.memories || [];
  const pendingList = pendingData?.suggestions || [];
  const memoryEnabled = settingsData?.ai_memory_enabled ?? true;

  const handleOpenCreateModal = () => {
    setEditingMemory(null);
    setFormKey('');
    setFormValue('');
    setFormCategory('fact');
    setIsEditModalOpen(true);
  };

  const handleOpenEditModal = (mem: AIMemory) => {
    setEditingMemory(mem);
    setFormKey(mem.memory_key);
    setFormValue(mem.memory_value);
    setFormCategory(mem.memory_type);
    setIsEditModalOpen(true);
  };

  const handleSaveMemory = async () => {
    const key = formKey.trim();
    const val = formValue.trim();
    if (!key || !val) {
      showToast('Key and value cannot be empty');
      return;
    }

    try {
      if (editingMemory) {
        if (editingMemory.status === 'pending') {
          await approveSuggestion.mutateAsync({
            id: editingMemory.id,
            payload: {
              memory_key: key,
              memory_value: val,
              memory_type: formCategory,
            },
          });
          showToast('Suggestion edited and approved!');
        } else {
          await updateMemory.mutateAsync({
            id: editingMemory.id,
            payload: {
              memory_key: key,
              memory_value: val,
              memory_type: formCategory,
            },
          });
          showToast('Memory updated successfully');
        }
      } else {
        await createMemory.mutateAsync({
          memory_key: key,
          memory_value: val,
          memory_type: formCategory,
        });
        showToast('Memory created successfully');
      }
      setIsEditModalOpen(false);
    } catch (err: any) {
      showToast(err.message || 'Operation failed');
    }
  };

  const handleApproveQuick = async (mem: AIMemory) => {
    try {
      await approveSuggestion.mutateAsync({ id: mem.id });
      showToast('Memory approved and active!');
    } catch (err: any) {
      showToast(err.message || 'Approval failed');
    }
  };

  const handleConfirmDelete = async () => {
    if (!deleteTargetId) return;
    try {
      await deleteMemory.mutateAsync(deleteTargetId);
      showToast('Memory deleted');
    } catch (err: any) {
      showToast(err.message || 'Failed to delete');
    } finally {
      setDeleteTargetId(null);
    }
  };

  const handleConfirmReject = async () => {
    if (!rejectTargetId) return;
    try {
      await rejectSuggestion.mutateAsync(rejectTargetId);
      showToast('Suggestion dismissed');
    } catch (err: any) {
      showToast(err.message || 'Failed to dismiss');
    } finally {
      setRejectTargetId(null);
    }
  };

  const handleArchive = async (id: string) => {
    try {
      await archiveMemory.mutateAsync(id);
      showToast('Memory archived');
    } catch (err: any) {
      showToast(err.message || 'Failed to archive');
    }
  };

  const handleToggleSettings = async (val: boolean) => {
    try {
      await updateSettings.mutateAsync(val);
      showToast(val ? 'Memory personalization enabled' : 'Memory personalization disabled');
    } catch (err: any) {
      showToast('Failed to update settings');
    }
  };

  return (
    <SafeAreaContainer style={styles.safeContainer}>
      {/* Header */}
      <View style={[styles.header, { borderBottomColor: theme.colors.glassBorder }]}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={[styles.backBtn, { borderColor: theme.colors.glassBorder }]}
          accessibilityRole="button"
          accessibilityLabel="Go back"
        >
          <Ionicons name="arrow-back" size={20} color={theme.colors.textPrimary} />
        </TouchableOpacity>

        <View style={styles.headerTitleWrap}>
          <Heading level={3}>Digital Brain</Heading>
          <Caption color="secondary">AI Personal Knowledge & Memory</Caption>
        </View>

        <TouchableOpacity
          onPress={handleOpenCreateModal}
          style={[styles.addBtn, { backgroundColor: theme.colors.primary }]}
          accessibilityRole="button"
          accessibilityLabel="Add memory"
        >
          <Ionicons name="add" size={22} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

      {/* Tabs */}
      <View style={[styles.tabBar, { backgroundColor: theme.colors.glassBackground }]}>
        <TouchableOpacity
          onPress={() => setActiveTab('confirmed')}
          style={[
            styles.tabItem,
            activeTab === 'confirmed' && { borderBottomColor: theme.colors.primary, borderBottomWidth: 2 },
          ]}
        >
          <BodyText
            weight={activeTab === 'confirmed' ? '700' : '500'}
            color={activeTab === 'confirmed' ? 'primary' : 'secondary'}
          >
            Confirmed ({confirmedList.length})
          </BodyText>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => setActiveTab('pending')}
          style={[
            styles.tabItem,
            activeTab === 'pending' && { borderBottomColor: theme.colors.primary, borderBottomWidth: 2 },
          ]}
        >
          <View style={styles.tabBadgeRow}>
            <BodyText
              weight={activeTab === 'pending' ? '700' : '500'}
              color={activeTab === 'pending' ? 'primary' : 'secondary'}
            >
              Pending Review
            </BodyText>
            {pendingList.length > 0 && (
              <View style={[styles.badgePill, { backgroundColor: theme.colors.warning }]}>
                <Caption style={styles.badgeText}>{pendingList.length}</Caption>
              </View>
            )}
          </View>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => setActiveTab('settings')}
          style={[
            styles.tabItem,
            activeTab === 'settings' && { borderBottomColor: theme.colors.primary, borderBottomWidth: 2 },
          ]}
        >
          <BodyText
            weight={activeTab === 'settings' ? '700' : '500'}
            color={activeTab === 'settings' ? 'primary' : 'secondary'}
          >
            Privacy & Settings
          </BodyText>
        </TouchableOpacity>
      </View>

      {/* TAB 1: CONFIRMED MEMORIES */}
      {activeTab === 'confirmed' && (
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {/* Search bar */}
          <View
            style={[
              styles.searchBar,
              {
                backgroundColor: theme.colors.glassBackground,
                borderColor: theme.colors.glassBorder,
              },
            ]}
          >
            <Ionicons name="search-outline" size={18} color={theme.colors.textSecondary} />
            <TextInput
              style={[styles.searchInput, { color: theme.colors.textPrimary }]}
              placeholder="Search memories..."
              placeholderTextColor={theme.colors.textSecondary}
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
            {searchQuery.length > 0 && (
              <TouchableOpacity onPress={() => setSearchQuery('')}>
                <Ionicons name="close-circle" size={16} color={theme.colors.textSecondary} />
              </TouchableOpacity>
            )}
          </View>

          {/* Category Chips */}
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.categoryScroll}
          >
            {CATEGORIES.map((cat) => {
              const isSelected = selectedCategory === cat.value;
              return (
                <TouchableOpacity
                  key={cat.value}
                  onPress={() => setSelectedCategory(cat.value)}
                  style={[
                    styles.catChip,
                    {
                      borderColor: isSelected ? theme.colors.primary : theme.colors.glassBorder,
                      backgroundColor: isSelected
                        ? `${theme.colors.primary}18`
                        : theme.colors.glassBackground,
                    },
                  ]}
                >
                  <Ionicons
                    name={cat.icon as any}
                    size={14}
                    color={isSelected ? theme.colors.primary : theme.colors.textSecondary}
                  />
                  <BodyText
                    variant="small"
                    weight={isSelected ? '700' : '400'}
                    color={isSelected ? 'primary' : 'secondary'}
                    style={{ marginLeft: 4 }}
                  >
                    {cat.label}
                  </BodyText>
                </TouchableOpacity>
              );
            })}
          </ScrollView>

          {/* Memory List */}
          {isConfirmedLoading ? (
            <ActivityIndicator size="large" color={theme.colors.primary} style={{ marginTop: 40 }} />
          ) : confirmedList.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Ionicons name="bulb-outline" size={48} color={theme.colors.textSecondary} />
              <Heading level={3} align="center" style={{ marginTop: 12 }}>
                No Confirmed Memories
              </Heading>
              <BodyText color="secondary" align="center" style={{ marginTop: 4 }}>
                Add personal preferences or routines, or review pending suggestions extracted from your AI conversations.
              </BodyText>
            </View>
          ) : (
            confirmedList.map((mem) => (
              <GlassCard key={mem.id} style={styles.memoryCard}>
                <View style={styles.cardHeader}>
                  <View
                    style={[
                      styles.categoryBadge,
                      { backgroundColor: `${theme.colors.primary}15` },
                    ]}
                  >
                    <Caption style={{ color: theme.colors.primary, fontWeight: '600' }}>
                      {mem.memory_type.replace('_', ' ').toUpperCase()}
                    </Caption>
                  </View>

                  <View style={styles.cardActions}>
                    <TouchableOpacity
                      onPress={() => handleOpenEditModal(mem)}
                      style={styles.actionIconBtn}
                      accessibilityLabel="Edit memory"
                    >
                      <Ionicons name="pencil-outline" size={17} color={theme.colors.textPrimary} />
                    </TouchableOpacity>
                    <TouchableOpacity
                      onPress={() => handleArchive(mem.id)}
                      style={styles.actionIconBtn}
                      accessibilityLabel="Archive memory"
                    >
                      <Ionicons name="archive-outline" size={17} color={theme.colors.textSecondary} />
                    </TouchableOpacity>
                    <TouchableOpacity
                      onPress={() => setDeleteTargetId(mem.id)}
                      style={styles.actionIconBtn}
                      accessibilityLabel="Delete memory"
                    >
                      <Ionicons name="trash-outline" size={17} color={theme.colors.error} />
                    </TouchableOpacity>
                  </View>
                </View>

                <BodyText weight="700" style={styles.memKey}>
                  {mem.memory_key}
                </BodyText>
                <BodyText color="secondary" style={styles.memVal}>
                  {mem.memory_value}
                </BodyText>

                <View style={styles.cardFooter}>
                  <Caption color="secondary">
                    Confidence: {Math.round(mem.confidence * 100)}%
                  </Caption>
                  {mem.last_accessed_at && (
                    <Caption color="secondary">
                      Used {new Date(mem.last_accessed_at).toLocaleDateString()}
                    </Caption>
                  )}
                </View>
              </GlassCard>
            ))
          )}
        </ScrollView>
      )}

      {/* TAB 2: PENDING SUGGESTIONS */}
      {activeTab === 'pending' && (
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          <GlassCard style={styles.infoBanner}>
            <Ionicons name="shield-checkmark-outline" size={20} color={theme.colors.primary} />
            <BodyText variant="small" style={{ flex: 1, marginLeft: 8 }}>
              Candidate memories are never accessed by the AI until you explicitly approve them. You retain complete control over your digital brain.
            </BodyText>
          </GlassCard>

          {isPendingLoading ? (
            <ActivityIndicator size="large" color={theme.colors.primary} style={{ marginTop: 40 }} />
          ) : pendingList.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Ionicons name="checkmark-done-circle-outline" size={48} color={theme.colors.success} />
              <Heading level={3} align="center" style={{ marginTop: 12 }}>
                All Caught Up!
              </Heading>
              <BodyText color="secondary" align="center" style={{ marginTop: 4 }}>
                No candidate memories waiting for review. As you chat with LifeOS, suggestions will appear here for your confirmation.
              </BodyText>
            </View>
          ) : (
            pendingList.map((suggestion) => (
              <GlassCard key={suggestion.id} style={styles.suggestionCard}>
                <View style={styles.cardHeader}>
                  <View
                    style={[
                      styles.categoryBadge,
                      { backgroundColor: `${theme.colors.warning}20` },
                    ]}
                  >
                    <Caption style={{ color: theme.colors.warning, fontWeight: '700' }}>
                      CANDIDATE: {suggestion.memory_type.replace('_', ' ').toUpperCase()}
                    </Caption>
                  </View>
                  <Caption color="secondary">
                    {Math.round(suggestion.confidence * 100)}% Match
                  </Caption>
                </View>

                <BodyText weight="700" style={styles.memKey}>
                  {suggestion.memory_key}
                </BodyText>
                <BodyText color="secondary" style={styles.memVal}>
                  {suggestion.memory_value}
                </BodyText>

                {/* Action Buttons */}
                <View style={styles.pendingBtnRow}>
                  <TouchableOpacity
                    onPress={() => handleApproveQuick(suggestion)}
                    style={[styles.pendingBtn, { backgroundColor: theme.colors.success }]}
                  >
                    <Ionicons name="checkmark" size={16} color="#FFFFFF" />
                    <BodyText variant="small" weight="700" style={{ color: '#FFFFFF', marginLeft: 4 }}>
                      Approve
                    </BodyText>
                  </TouchableOpacity>

                  <TouchableOpacity
                    onPress={() => handleOpenEditModal(suggestion)}
                    style={[
                      styles.pendingBtn,
                      {
                        backgroundColor: theme.colors.glassBackground,
                        borderColor: theme.colors.glassBorder,
                        borderWidth: 1,
                      },
                    ]}
                  >
                    <Ionicons name="pencil-outline" size={16} color={theme.colors.textPrimary} />
                    <BodyText variant="small" weight="700" style={{ marginLeft: 4 }}>
                      Edit & Approve
                    </BodyText>
                  </TouchableOpacity>

                  <TouchableOpacity
                    onPress={() => setRejectTargetId(suggestion.id)}
                    style={[styles.pendingBtn, { backgroundColor: `${theme.colors.error}18` }]}
                  >
                    <Ionicons name="close" size={16} color={theme.colors.error} />
                    <BodyText
                      variant="small"
                      weight="700"
                      style={{ color: theme.colors.error, marginLeft: 4 }}
                    >
                      Reject
                    </BodyText>
                  </TouchableOpacity>
                </View>
              </GlassCard>
            ))
          )}
        </ScrollView>
      )}

      {/* TAB 3: PRIVACY & SETTINGS */}
      {activeTab === 'settings' && (
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          <GlassCard style={styles.settingsCard}>
            <View style={styles.settingRow}>
              <View style={{ flex: 1, marginRight: 12 }}>
                <BodyText weight="700">Personalization & Memory Retrieval</BodyText>
                <Caption color="secondary" style={{ marginTop: 2 }}>
                  When enabled, confirmed personal memories are retrieved to make assistant recommendations personal and context-aware.
                </Caption>
              </View>
              <Switch
                value={memoryEnabled}
                onValueChange={handleToggleSettings}
                trackColor={{ false: theme.colors.glassBorder, true: theme.colors.primary }}
              />
            </View>
          </GlassCard>

          <GlassCard style={styles.settingsCard}>
            <Heading level={3} style={{ marginBottom: 12 }}>
              Privacy & Local Guarantee
            </Heading>

            <View style={styles.privacyItem}>
              <Ionicons name="server-outline" size={20} color={theme.colors.primary} />
              <View style={{ flex: 1, marginLeft: 12 }}>
                <BodyText weight="500">100% Local Intelligence</BodyText>
                <Caption color="secondary">
                  Your memories, tasks, and conversations never leave your device. All LLM queries run against your local Ollama engine.
                </Caption>
              </View>
            </View>

            <View style={styles.privacyItem}>
              <Ionicons name="hand-left-outline" size={20} color={theme.colors.warning} />
              <View style={{ flex: 1, marginLeft: 12 }}>
                <BodyText weight="500">Explicit Approval Requirement</BodyText>
                <Caption color="secondary">
                  The AI cannot silently write to your confirmed memory. Candidate memories stay in review until you explicitly approve or edit them.
                </Caption>
              </View>
            </View>

            <View style={styles.privacyItem}>
              <Ionicons name="trash-bin-outline" size={20} color={theme.colors.error} />
              <View style={{ flex: 1, marginLeft: 12 }}>
                <BodyText weight="500">Right to be Forgotten</BodyText>
                <Caption color="secondary">
                  You can permanently delete or archive any memory at any time. Archived memories are instantly excluded from future prompts.
                </Caption>
              </View>
            </View>
          </GlassCard>
        </ScrollView>
      )}

      {/* CREATE / EDIT MODAL */}
      <Modal
        visible={isEditModalOpen}
        animationType="slide"
        transparent
        onRequestClose={() => setIsEditModalOpen(false)}
      >
        <View style={styles.modalOverlay}>
          <View
            style={[
              styles.modalContent,
              {
                backgroundColor: theme.colors.surface,
                borderColor: theme.colors.glassBorder,
              },
            ]}
          >
            <View style={styles.modalHeader}>
              <Heading level={3}>
                {editingMemory
                  ? editingMemory.status === 'pending'
                    ? 'Review & Approve'
                    : 'Edit Memory'
                  : 'New Personal Memory'}
              </Heading>
              <TouchableOpacity onPress={() => setIsEditModalOpen(false)}>
                <Ionicons name="close" size={22} color={theme.colors.textPrimary} />
              </TouchableOpacity>
            </View>

            {/* Title / Key Input */}
            <BodyText weight="500" style={{ marginTop: 12, marginBottom: 4 }}>
              Title / Short Key
            </BodyText>
            <TextInput
              style={[
                styles.modalInput,
                {
                  color: theme.colors.textPrimary,
                  borderColor: theme.colors.glassBorder,
                  backgroundColor: theme.colors.glassBackground,
                },
              ]}
              placeholder="e.g. Prefers morning workout"
              placeholderTextColor={theme.colors.textSecondary}
              value={formKey}
              onChangeText={setFormKey}
            />

            {/* Content / Value Input */}
            <BodyText weight="500" style={{ marginTop: 12, marginBottom: 4 }}>
              Memory Statement / Fact
            </BodyText>
            <TextInput
              style={[
                styles.modalInput,
                styles.modalTextArea,
                {
                  color: theme.colors.textPrimary,
                  borderColor: theme.colors.glassBorder,
                  backgroundColor: theme.colors.glassBackground,
                },
              ]}
              placeholder="e.g. User exercises at 7:00 AM before starting work."
              placeholderTextColor={theme.colors.textSecondary}
              multiline
              numberOfLines={4}
              value={formValue}
              onChangeText={setFormValue}
            />

            {/* Category selection */}
            <BodyText weight="500" style={{ marginTop: 12, marginBottom: 4 }}>
              Category
            </BodyText>
            <View style={styles.categorySelectGrid}>
              {CATEGORIES.filter((c) => c.value !== 'all').map((cat) => {
                const isSelected = formCategory === cat.value;
                return (
                  <TouchableOpacity
                    key={cat.value}
                    onPress={() => setFormCategory(cat.value as AIMemoryCategory)}
                    style={[
                      styles.catSelectChip,
                      {
                        borderColor: isSelected ? theme.colors.primary : theme.colors.glassBorder,
                        backgroundColor: isSelected
                          ? `${theme.colors.primary}20`
                          : theme.colors.glassBackground,
                      },
                    ]}
                  >
                    <Ionicons
                      name={cat.icon as any}
                      size={14}
                      color={isSelected ? theme.colors.primary : theme.colors.textSecondary}
                    />
                    <Caption
                      style={{
                        marginLeft: 4,
                        color: isSelected ? theme.colors.primary : theme.colors.textSecondary,
                        fontWeight: isSelected ? '700' : '500',
                      }}
                    >
                      {cat.label}
                    </Caption>
                  </TouchableOpacity>
                );
              })}
            </View>

            {/* Save Button */}
            <TouchableOpacity
              onPress={handleSaveMemory}
              style={[styles.saveBtn, { backgroundColor: theme.colors.primary }]}
            >
              <BodyText weight="700" style={{ color: '#FFFFFF' }}>
                {editingMemory?.status === 'pending' ? 'Confirm & Approve Memory' : 'Save Memory'}
              </BodyText>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        visible={!!deleteTargetId}
        title="Delete Memory"
        message="Are you sure you want to permanently delete this memory? This cannot be undone."
        confirmLabel="Delete"
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleteTargetId(null)}
      />

      {/* Reject Confirmation Modal */}
      <ConfirmationModal
        visible={!!rejectTargetId}
        title="Reject Suggestion"
        message="Dismiss this suggested memory? It will not be saved."
        confirmLabel="Reject"
        onConfirm={handleConfirmReject}
        onCancel={() => setRejectTargetId(null)}
      />

      {/* Toast */}
      {toastMessage && <Toast message={toastMessage} visible={!!toastMessage} />}
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  safeContainer: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
  },
  backBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitleWrap: {
    flex: 1,
    marginLeft: 12,
  },
  addBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabBar: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingTop: 8,
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 10,
  },
  tabBadgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  badgePill: {
    marginLeft: 4,
    paddingHorizontal: 5,
    paddingVertical: 1,
    borderRadius: 8,
  },
  badgeText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 10,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    borderWidth: 1,
    paddingHorizontal: 12,
    height: 44,
    marginBottom: 12,
  },
  searchInput: {
    flex: 1,
    marginLeft: 8,
    fontSize: 14,
  },
  categoryScroll: {
    paddingBottom: 12,
  },
  catChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    marginRight: 8,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 60,
    paddingHorizontal: 24,
  },
  memoryCard: {
    padding: 14,
    borderRadius: 14,
    marginBottom: 12,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  categoryBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  cardActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionIconBtn: {
    marginLeft: 12,
  },
  memKey: {
    fontSize: 15,
    marginBottom: 4,
  },
  memVal: {
    fontSize: 13,
    lineHeight: 18,
    marginBottom: 8,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 0.5,
    borderTopColor: 'rgba(0,0,0,0.06)',
    paddingTop: 6,
  },
  infoBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 12,
    marginBottom: 16,
  },
  suggestionCard: {
    padding: 14,
    borderRadius: 14,
    marginBottom: 12,
  },
  pendingBtnRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 12,
    gap: 8,
  },
  pendingBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    borderRadius: 8,
  },
  settingsCard: {
    padding: 16,
    borderRadius: 14,
    marginBottom: 16,
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  privacyItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 14,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.45)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    borderWidth: 1,
    padding: 20,
    paddingBottom: 36,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  modalInput: {
    borderWidth: 1,
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 14,
  },
  modalTextArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  categorySelectGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginVertical: 8,
  },
  catSelectChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
    borderWidth: 1,
  },
  saveBtn: {
    marginTop: 18,
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
