import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  RefreshControl,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import { useAutomations, usePauseAutomation, useResumeAutomation, useExecuteAutomation } from '../../hooks/useAutomations';
import { AutomationDefinition } from '../../types/automation';

export const AutomationDashboardScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<any>();
  const { data: automations = [], isLoading, isRefetching, refetch } = useAutomations();
  const pauseMutation = usePauseAutomation();
  const resumeMutation = useResumeAutomation();
  const executeMutation = useExecuteAutomation();

  const [executingId, setExecutingId] = useState<string | null>(null);

  const handleRunNow = async (item: AutomationDefinition) => {
    setExecutingId(item.id);
    try {
      const exec = await executeMutation.mutateAsync({ id: item.id });
      navigation.navigate('AutomationExecutionHistory', { executionId: exec.id });
    } catch (e) {
      // error handled by state
    } finally {
      setExecutingId(null);
    }
  };

  const handleTogglePause = (item: AutomationDefinition) => {
    if (item.is_paused) {
      resumeMutation.mutate(item.id);
    } else {
      pauseMutation.mutate(item.id);
    }
  };

  const renderAutomationCard = ({ item }: { item: AutomationDefinition }) => {
    const isPaused = item.is_paused;
    const isRunning = executingId === item.id;

    return (
      <View style={[styles.card, { backgroundColor: '#FFFFFF', borderColor: theme.colors.border }]}>
        <View style={styles.cardHeader}>
          <View style={styles.titleArea}>
            <View style={[styles.categoryBadge, { backgroundColor: `${theme.colors.primary}15` }]}>
              <Text style={[styles.categoryText, { color: theme.colors.primary }]}>
                {item.category.toUpperCase()}
              </Text>
            </View>
            <Text style={[styles.cardTitle, { color: theme.colors.textPrimary }]}>{item.title}</Text>
          </View>
          <TouchableOpacity
            onPress={() => handleTogglePause(item)}
            style={[styles.pauseBtn, { backgroundColor: isPaused ? '#FEF3C7' : '#F3F4F6' }]}
          >
            <Ionicons
              name={isPaused ? 'play' : 'pause'}
              size={16}
              color={isPaused ? '#D97706' : '#6B7280'}
            />
          </TouchableOpacity>
        </View>

        {item.description ? (
          <Text style={[styles.cardDesc, { color: theme.colors.textSecondary }]} numberOfLines={2}>
            {item.description}
          </Text>
        ) : null}

        <View style={styles.metaRow}>
          <View style={styles.metaItem}>
            <Ionicons name="time-outline" size={14} color={theme.colors.textSecondary} />
            <Text style={[styles.metaText, { color: theme.colors.textSecondary }]}>
              {item.trigger_type === 'scheduled'
                ? `${item.scheduled_days || 'Daily'} @ ${item.scheduled_time || '08:00'}`
                : 'Manual Trigger'}
            </Text>
          </View>
          <View style={styles.metaItem}>
            <Ionicons name="checkmark-done-outline" size={14} color="#10B981" />
            <Text style={[styles.metaText, { color: '#10B981' }]}>
              {item.total_runs} runs
            </Text>
          </View>
        </View>

        <View style={styles.cardActions}>
          <TouchableOpacity
            style={[styles.actionBtn, { borderColor: theme.colors.border }]}
            onPress={() => navigation.navigate('AutomationDetail', { id: item.id })}
          >
            <Text style={[styles.actionBtnText, { color: theme.colors.textPrimary }]}>Details</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.runBtn,
              { backgroundColor: theme.colors.primary, opacity: isRunning || isPaused ? 0.6 : 1 },
            ]}
            disabled={isRunning || isPaused}
            onPress={() => handleRunNow(item)}
          >
            {isRunning ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <>
                <Ionicons name="flash-outline" size={14} color="#FFFFFF" />
                <Text style={styles.runBtnText}>Run Now</Text>
              </>
            )}
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      {/* Header */}
      <View style={[styles.header, { borderBottomColor: theme.colors.border }]}>
        <View>
          <Text style={[styles.title, { color: theme.colors.textPrimary }]}>AI Automations</Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            Autonomous multi-domain intelligence
          </Text>
        </View>
        <View style={styles.headerBtns}>
          <TouchableOpacity
            style={[styles.iconBtn, { backgroundColor: '#FFFFFF', borderColor: theme.colors.border }]}
            onPress={() => navigation.navigate('AutomationTemplates')}
          >
            <Ionicons name="add" size={20} color={theme.colors.primary} />
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.iconBtn, { backgroundColor: '#FFFFFF', borderColor: theme.colors.border }]}
            onPress={() => navigation.navigate('AutomationExecutionHistory')}
          >
            <Ionicons name="list-outline" size={20} color={theme.colors.textPrimary} />
          </TouchableOpacity>
        </View>
      </View>

      {/* List */}
      {isLoading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      ) : (
        <FlatList
          data={automations}
          keyExtractor={(item) => item.id}
          renderItem={renderAutomationCard}
          contentContainerStyle={styles.listContent}
          initialNumToRender={8}
          maxToRenderPerBatch={6}
          windowSize={5}
          removeClippedSubviews={Platform.OS !== 'web'}
          refreshControl={
            <RefreshControl
              refreshing={isRefetching}
              onRefresh={() => {
                refetch();
              }}
              tintColor={theme.colors.primary}
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Ionicons name="cube-outline" size={48} color={theme.colors.textSecondary} />
              <Text style={[styles.emptyTitle, { color: theme.colors.textPrimary }]}>No Automations Set Up</Text>
              <Text style={[styles.emptySubtitle, { color: theme.colors.textSecondary }]}>
                Browse predefined templates to launch autonomous daily schedules, reviews, or habit triage.
              </Text>
              <TouchableOpacity
                style={[styles.templateBtn, { backgroundColor: theme.colors.primary }]}
                onPress={() => navigation.navigate('AutomationTemplates')}
              >
                <Text style={styles.templateBtnText}>Browse Templates</Text>
              </TouchableOpacity>
            </View>
          }
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
  },
  title: {
    fontSize: 22,
    fontWeight: '700',
  },
  subtitle: {
    fontSize: 13,
    marginTop: 2,
  },
  headerBtns: {
    flexDirection: 'row',
    gap: 8,
  },
  iconBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    borderWidth: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContent: {
    padding: 16,
    gap: 14,
  },
  card: {
    borderRadius: 16,
    borderWidth: 1,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  titleArea: {
    flex: 1,
  },
  categoryBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    marginBottom: 6,
  },
  categoryText: {
    fontSize: 10,
    fontWeight: '700',
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  pauseBtn: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  cardDesc: {
    fontSize: 13,
    lineHeight: 18,
    marginTop: 8,
  },
  metaRow: {
    flexDirection: 'row',
    gap: 16,
    marginTop: 12,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  metaText: {
    fontSize: 12,
    fontWeight: '500',
  },
  cardActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 10,
    marginTop: 14,
    paddingTop: 12,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#E5E7EB',
  },
  actionBtn: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
  },
  actionBtnText: {
    fontSize: 13,
    fontWeight: '600',
  },
  runBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  runBtnText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '600',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    padding: 32,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 40,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginTop: 12,
  },
  emptySubtitle: {
    fontSize: 13,
    textAlign: 'center',
    marginTop: 6,
    lineHeight: 18,
  },
  templateBtn: {
    marginTop: 16,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 10,
  },
  templateBtnText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 14,
  },
});
