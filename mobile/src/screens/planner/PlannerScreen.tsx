import React, { useState, useMemo } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  ScrollView,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import {
  usePlannerBlocks,
  usePlannerSummary,
  useCreatePlannerBlock,
  useUpdatePlannerBlock,
  useUpdatePlannerStatus,
  useDeletePlannerBlock,
} from '../../hooks/usePlanner';
import { useTasks } from '../../hooks/useTasks';
import { PlannerBlock, PlannerBlockStatus } from '../../types/planner';
import { PlannerBlockFormData } from '../../schemas/planner';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  PrimaryButton,
  Heading,
  BodyText,
  Caption,
  SkeletonLoader,
  EmptyState,
  ErrorState,
  Toast,
} from '../../components';
import { CreateEditPlannerBlockModal, PlannerBlockDetailsModal } from '../../components/planner';

type CalendarViewMode = 'day' | 'week' | 'month';

export const PlannerScreen: React.FC = () => {
  const { theme } = useTheme();

  // Selected date state (defaults to today)
  const [selectedDate, setSelectedDate] = useState<Date>(() => new Date());
  const [viewMode, setViewMode] = useState<CalendarViewMode>('day');

  // Modals state
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [blockToEdit, setBlockToEdit] = useState<PlannerBlock | null>(null);
  const [selectedBlockDetails, setSelectedBlockDetails] = useState<PlannerBlock | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Helper date strings
  const selectedDateStr = useMemo(() => {
    const year = selectedDate.getFullYear();
    const month = String(selectedDate.getMonth() + 1).padStart(2, '0');
    const day = String(selectedDate.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }, [selectedDate]);

  // Compute date range for query depending on viewMode
  const queryRange = useMemo(() => {
    if (viewMode === 'day') {
      const start = new Date(selectedDate);
      start.setHours(0, 0, 0, 0);
      const end = new Date(selectedDate);
      end.setHours(23, 59, 59, 999);
      return {
        start_date: start.toISOString(),
        end_date: end.toISOString(),
      };
    } else if (viewMode === 'week') {
      const start = new Date(selectedDate);
      const dayOfWeek = start.getDay();
      start.setDate(start.getDate() - dayOfWeek);
      start.setHours(0, 0, 0, 0);
      const end = new Date(start);
      end.setDate(end.getDate() + 6);
      end.setHours(23, 59, 59, 999);
      return {
        start_date: start.toISOString(),
        end_date: end.toISOString(),
      };
    } else {
      // Month
      const start = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1, 0, 0, 0);
      const end = new Date(selectedDate.getFullYear(), selectedDate.getMonth() + 1, 0, 23, 59, 59);
      return {
        start_date: start.toISOString(),
        end_date: end.toISOString(),
      };
    }
  }, [selectedDate, viewMode]);

  // Queries & Mutations
  const {
    data: blocksData,
    isLoading: isLoadingBlocks,
    isError: isBlocksError,
    refetch: refetchBlocks,
  } = usePlannerBlocks({
    start_date: queryRange.start_date,
    end_date: queryRange.end_date,
    per_page: 100,
  });

  const {
    data: summaryData,
    isLoading: isLoadingSummary,
    refetch: refetchSummary,
  } = usePlannerSummary(selectedDateStr);

  const { data: tasksData } = useTasks({ status: 'pending', per_page: 100 });

  const createBlockMutation = useCreatePlannerBlock();
  const updateBlockMutation = useUpdatePlannerBlock();
  const updateStatusMutation = useUpdatePlannerStatus();
  const deleteBlockMutation = useDeletePlannerBlock();

  const blocks = blocksData?.blocks || [];
  const tasks = tasksData?.tasks || [];

  // Date Navigation handlers
  const handlePrev = () => {
    const next = new Date(selectedDate);
    if (viewMode === 'day') {
      next.setDate(next.getDate() - 1);
    } else if (viewMode === 'week') {
      next.setDate(next.getDate() - 7);
    } else {
      next.setMonth(next.getMonth() - 1);
    }
    setSelectedDate(next);
  };

  const handleNext = () => {
    const next = new Date(selectedDate);
    if (viewMode === 'day') {
      next.setDate(next.getDate() + 1);
    } else if (viewMode === 'week') {
      next.setDate(next.getDate() + 7);
    } else {
      next.setMonth(next.getMonth() + 1);
    }
    setSelectedDate(next);
  };

  const handleToday = () => {
    setSelectedDate(new Date());
  };

  const handleRefresh = async () => {
    await Promise.all([refetchBlocks(), refetchSummary()]);
  };

  // Block Modal Submit (Create or Update)
  const handleModalSubmit = async (formData: PlannerBlockFormData) => {
    // Construct local ISO start and end
    const [startH, startM] = formData.start_time.split(':').map(Number);
    const [endH, endM] = formData.end_time.split(':').map(Number);

    const [y, m, d] = formData.date.split('-').map(Number);
    const startObj = new Date(y, m - 1, d, startH, startM, 0);
    const endObj = new Date(y, m - 1, d, endH, endM, 0);

    const payload = {
      title: formData.title,
      description: formData.description || null,
      start_time: startObj.toISOString(),
      end_time: endObj.toISOString(),
      block_type: formData.block_type,
      status: formData.status,
      task_id: formData.task_id || null,
      color_hex: formData.color_hex || null,
    };

    if (blockToEdit) {
      await updateBlockMutation.mutateAsync({
        blockId: blockToEdit.id,
        payload,
      });
      setToastMessage('Schedule block updated');
      setBlockToEdit(null);
    } else {
      await createBlockMutation.mutateAsync(payload);
      setToastMessage('Schedule block reserved');
    }
  };

  const handleStatusUpdate = async (blockId: string, status: PlannerBlockStatus) => {
    await updateStatusMutation.mutateAsync({ blockId, status });
    setToastMessage(`Block marked as ${status}`);
    if (selectedBlockDetails && selectedBlockDetails.id === blockId) {
      setSelectedBlockDetails((prev) => (prev ? { ...prev, status } : null));
    }
  };

  const handleDeleteBlock = async (blockId: string) => {
    await deleteBlockMutation.mutateAsync(blockId);
    setToastMessage('Schedule block removed');
    setSelectedBlockDetails(null);
  };

  // Generate 7-day strip centered around selected date
  const dayStrip = useMemo(() => {
    const list = [];
    for (let offset = -3; offset <= 3; offset++) {
      const d = new Date(selectedDate);
      d.setDate(d.getDate() + offset);
      list.push(d);
    }
    return list;
  }, [selectedDate]);

  const formatHeaderDate = (d: Date) => {
    return d.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
  };

  const formatSlotTime = (iso: string) => {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
  };

  const isToday = (d: Date) => {
    const now = new Date();
    return (
      d.getDate() === now.getDate() &&
      d.getMonth() === now.getMonth() &&
      d.getFullYear() === now.getFullYear()
    );
  };

  const isSelected = (d: Date) => {
    return (
      d.getDate() === selectedDate.getDate() &&
      d.getMonth() === selectedDate.getMonth() &&
      d.getFullYear() === selectedDate.getFullYear()
    );
  };

  return (
    <SafeAreaContainer>
      {/* Top Header */}
      <View style={styles.header}>
        <View>
          <Caption color="secondary">CALENDAR & TIME-BLOCKING</Caption>
          <Heading level={2}>Daily Planner</Heading>
        </View>
        <View style={styles.headerRight}>
          <TouchableOpacity
            onPress={handleToday}
            style={[styles.todayButton, { borderColor: theme.colors.border }]}
          >
            <BodyText style={[styles.todayButtonText, { color: theme.colors.primary }]}>
              Today
            </BodyText>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => {
              setBlockToEdit(null);
              setIsCreateModalOpen(true);
            }}
            style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
          >
            <Ionicons name="add" size={24} color="#FFF" />
          </TouchableOpacity>
        </View>
      </View>

      {/* View Mode Switcher */}
      <View style={styles.viewModeRow}>
        {(['day', 'week', 'month'] as CalendarViewMode[]).map((mode) => {
          const isActive = viewMode === mode;
          return (
            <TouchableOpacity
              key={mode}
              onPress={() => setViewMode(mode)}
              style={[
                styles.viewModeTab,
                {
                  backgroundColor: isActive
                    ? theme.colors.primary
                    : theme.colors.glassBackground,
                },
              ]}
            >
              <BodyText
                style={[
                  styles.viewModeText,
                  {
                    color: isActive ? '#FFF' : theme.colors.textSecondary,
                    fontWeight: isActive ? '600' : '400',
                  },
                ]}
              >
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </BodyText>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Date Navigation Bar */}
      <View style={styles.dateNavRow}>
        <TouchableOpacity onPress={handlePrev} style={styles.navArrow}>
          <Ionicons name="chevron-back" size={20} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <BodyText style={styles.dateNavTitle}>{formatHeaderDate(selectedDate)}</BodyText>
        <TouchableOpacity onPress={handleNext} style={styles.navArrow}>
          <Ionicons name="chevron-forward" size={20} color={theme.colors.textPrimary} />
        </TouchableOpacity>
      </View>

      {/* 7-Day Quick Strip (Day View) */}
      {viewMode === 'day' && (
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.stripScroll}
        >
          {dayStrip.map((d, index) => {
            const selected = isSelected(d);
            const today = isToday(d);
            return (
              <TouchableOpacity
                key={index}
                onPress={() => setSelectedDate(d)}
                style={[
                  styles.stripCard,
                  {
                    backgroundColor: selected
                      ? theme.colors.primary
                      : theme.colors.glassBackground,
                    borderColor: selected
                      ? theme.colors.primary
                      : today
                      ? theme.colors.primary + '60'
                      : theme.colors.border,
                  },
                ]}
              >
                <Caption
                  style={{
                    color: selected
                      ? '#FFF'
                      : today
                      ? theme.colors.primary
                      : theme.colors.textSecondary,
                    fontWeight: '600',
                  }}
                >
                  {d.toLocaleDateString(undefined, { weekday: 'narrow' })}
                </Caption>
                <Heading
                  level={3}
                  style={{
                    color: selected ? '#FFF' : theme.colors.textPrimary,
                    marginTop: 4,
                  }}
                >
                  {d.getDate()}
                </Heading>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      )}

      {/* Main Content Area */}
      <ScrollContainer
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={isLoadingBlocks && !blocks.length}
            onRefresh={() => {
              handleRefresh();
            }}
            tintColor={theme.colors.primary}
          />
        }
      >
        {/* Daily Summary Metrics Widget */}
        {summaryData && (
          <GlassCard style={styles.metricsCard}>
            <View style={styles.metricsHeader}>
              <View>
                <Heading level={3}>Daily Schedule</Heading>
                <Caption color="secondary">
                  {summaryData.total_blocks} reservations • {summaryData.total_scheduled_minutes} mins total
                </Caption>
              </View>
              <View
                style={[
                  styles.rateBadge,
                  {
                    backgroundColor:
                      summaryData.completion_rate === 100
                        ? theme.colors.success + '20'
                        : theme.colors.primary + '18',
                  },
                ]}
              >
                <BodyText
                  style={[
                    styles.rateText,
                    {
                      color:
                        summaryData.completion_rate === 100
                          ? theme.colors.success
                          : theme.colors.primary,
                    },
                  ]}
                >
                  {summaryData.completion_rate}% Done
                </BodyText>
              </View>
            </View>
          </GlassCard>
        )}

        {/* Content based on state */}
        {isLoadingBlocks && !blocks.length ? (
          <View style={styles.loadingContainer}>
            <SkeletonLoader width="100%" height={80} borderRadius={16} />
            <View style={{ height: 12 }} />
            <SkeletonLoader width="100%" height={80} borderRadius={16} />
            <View style={{ height: 12 }} />
            <SkeletonLoader width="100%" height={80} borderRadius={16} />
          </View>
        ) : isBlocksError ? (
          <ErrorState
            title="Unable to load planner"
            message="We could not retrieve your schedule blocks. Please check your connection."
            onRetry={handleRefresh}
          />
        ) : blocks.length === 0 ? (
          <EmptyState
            title="No Blocks Scheduled"
            description={`Your schedule is completely clear for ${selectedDateStr}. Plan your work sessions, focus blocks, or tasks now.`}
            actionLabel="Schedule First Block"
            onActionPress={() => {
              setBlockToEdit(null);
              setIsCreateModalOpen(true);
            }}
          />
        ) : (
          <View style={styles.timelineList}>
            {blocks.map((block) => {
              const startFormatted = formatSlotTime(block.start_time);
              const endFormatted = formatSlotTime(block.end_time);
              const isBlockCompleted = block.status === 'completed';

              return (
                <TouchableOpacity
                  key={block.id}
                  onPress={() => setSelectedBlockDetails(block)}
                  activeOpacity={0.8}
                  style={styles.blockRow}
                >
                  {/* Time Column */}
                  <View style={styles.timeCol}>
                    <BodyText style={styles.startTimeText}>{startFormatted}</BodyText>
                    <Caption style={styles.endTimeText}>{endFormatted}</Caption>
                  </View>

                  {/* Block Card */}
                  <GlassCard
                    style={[
                      styles.blockCard,
                      {
                        borderLeftColor: block.color_hex || theme.colors.primary,
                        borderLeftWidth: 4,
                        opacity: block.status === 'cancelled' ? 0.5 : 1,
                      },
                    ]}
                  >
                    <View style={styles.blockCardHeader}>
                      <BodyText
                        numberOfLines={1}
                        style={[
                          styles.blockTitle,
                          isBlockCompleted && styles.completedBlockTitle,
                        ]}
                      >
                        {block.title}
                      </BodyText>
                      <View
                        style={[
                          styles.statusBadge,
                          {
                            backgroundColor:
                              block.status === 'completed'
                                ? theme.colors.success + '20'
                                : block.status === 'cancelled'
                                ? theme.colors.error + '20'
                                : theme.colors.primary + '18',
                          },
                        ]}
                      >
                        <BodyText
                          style={[
                            styles.statusBadgeText,
                            {
                              color:
                                block.status === 'completed'
                                ? theme.colors.success
                                : block.status === 'cancelled'
                                ? theme.colors.error
                                : theme.colors.primary,
                            },
                          ]}
                        >
                          {block.status}
                        </BodyText>
                      </View>
                    </View>

                    {/* Linked task or description preview */}
                    {block.task && (
                      <View style={styles.taskBadge}>
                        <Ionicons
                          name="checkmark-circle-outline"
                          size={12}
                          color={theme.colors.primary}
                        />
                        <Caption numberOfLines={1} style={{ color: theme.colors.primary }}>
                          Task: {block.task.title}
                        </Caption>
                      </View>
                    )}

                    {block.description ? (
                      <Caption numberOfLines={1} color="secondary" style={styles.descPreview}>
                        {block.description}
                      </Caption>
                    ) : null}
                  </GlassCard>
                </TouchableOpacity>
              );
            })}
          </View>
        )}
      </ScrollContainer>

      {/* Create / Edit Block Modal */}
      <CreateEditPlannerBlockModal
        visible={isCreateModalOpen}
        blockToEdit={blockToEdit}
        initialDate={selectedDateStr}
        tasks={tasks}
        isLoading={createBlockMutation.isPending || updateBlockMutation.isPending}
        onClose={() => {
          setIsCreateModalOpen(false);
          setBlockToEdit(null);
        }}
        onSubmit={handleModalSubmit}
      />

      {/* Block Details Modal */}
      <PlannerBlockDetailsModal
        visible={!!selectedBlockDetails}
        block={selectedBlockDetails}
        onClose={() => setSelectedBlockDetails(null)}
        onEdit={(block) => {
          setBlockToEdit(block);
          setIsCreateModalOpen(true);
        }}
        onDelete={handleDeleteBlock}
        onUpdateStatus={handleStatusUpdate}
      />

      {/* Notification Toast */}
      <Toast
        visible={!!toastMessage}
        message={toastMessage || ''}
        type="success"
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
    paddingTop: 12,
    paddingBottom: 8,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  todayButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    borderWidth: 1,
  },
  todayButtonText: {
    fontSize: 13,
    fontWeight: '600',
  },
  addButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  viewModeRow: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 6,
    gap: 8,
  },
  viewModeTab: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 12,
    alignItems: 'center',
  },
  viewModeText: {
    fontSize: 13,
  },
  dateNavRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 8,
  },
  navArrow: {
    padding: 6,
  },
  dateNavTitle: {
    fontSize: 15,
    fontWeight: '600',
  },
  stripScroll: {
    paddingHorizontal: 20,
    paddingVertical: 8,
    gap: 8,
  },
  stripCard: {
    width: 48,
    height: 64,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  metricsCard: {
    padding: 16,
    borderRadius: 18,
    marginBottom: 16,
  },
  metricsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  rateBadge: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 10,
  },
  rateText: {
    fontSize: 12,
    fontWeight: '700',
  },
  loadingContainer: {
    marginTop: 10,
  },
  timelineList: {
    gap: 12,
  },
  blockRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
  },
  timeCol: {
    width: 60,
    alignItems: 'flex-end',
    paddingTop: 8,
  },
  startTimeText: {
    fontSize: 13,
    fontWeight: '600',
  },
  endTimeText: {
    fontSize: 11,
  },
  blockCard: {
    flex: 1,
    padding: 12,
    borderRadius: 16,
  },
  blockCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  blockTitle: {
    fontSize: 14,
    fontWeight: '600',
    flex: 1,
    marginRight: 8,
  },
  completedBlockTitle: {
    textDecorationLine: 'line-through',
    opacity: 0.6,
  },
  statusBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
  },
  statusBadgeText: {
    fontSize: 10,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  taskBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 6,
  },
  descPreview: {
    marginTop: 4,
  },
});
