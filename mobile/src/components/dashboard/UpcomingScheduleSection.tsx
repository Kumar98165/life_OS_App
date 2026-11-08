import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { GlassCard } from '../glass/GlassCard';
import { SectionHeader } from '../layout/SectionHeader';
import { BodyText, Caption } from '../common/Typography';
import { SkeletonLoader, EmptyState } from '../feedback/FeedbackComponents';
import { usePlannerBlocks } from '../../hooks/usePlanner';
import { PlannerBlock } from '../../types/planner';

export interface UpcomingScheduleSectionProps {
  onViewAll: () => void;
  onBlockPress?: (block: PlannerBlock) => void;
  onSchedulePress?: () => void;
}

export const UpcomingScheduleSection: React.FC<UpcomingScheduleSectionProps> = ({
  onViewAll,
  onBlockPress,
  onSchedulePress,
}) => {
  const { theme } = useTheme();

  // Query today's blocks
  const today = new Date();
  const startOfDay = new Date(today);
  startOfDay.setHours(0, 0, 0, 0);
  const endOfDay = new Date(today);
  endOfDay.setHours(23, 59, 59, 999);

  const { data, isLoading } = usePlannerBlocks({
    start_date: startOfDay.toISOString(),
    end_date: endOfDay.toISOString(),
    status: 'scheduled',
    per_page: 5,
  });

  const blocks = data?.blocks || [];

  const formatTime = (iso: string) => {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
  };

  return (
    <View style={styles.container}>
      <SectionHeader
        title="Upcoming Schedule"
        actionText="View Planner"
        onActionPress={onViewAll}
      />

      {isLoading ? (
        <View style={styles.skeletonContainer}>
          <SkeletonLoader height={68} borderRadius={14} style={{ marginBottom: 10 }} />
          <SkeletonLoader height={68} borderRadius={14} style={{ marginBottom: 10 }} />
        </View>
      ) : blocks.length === 0 ? (
        <GlassCard elevation="subtle" style={styles.emptyCard}>
          <EmptyState
            icon="calendar-outline"
            title="No schedule blocks today"
            description="Time-block your day to focus on deep work and daily routines."
            actionLabel="Plan Your Day"
            onActionPress={onSchedulePress || onViewAll}
          />
        </GlassCard>
      ) : (
        <View style={styles.blocksList}>
          {blocks.map((block) => (
            <TouchableOpacity
              key={block.id}
              activeOpacity={0.8}
              onPress={() => onBlockPress && onBlockPress(block)}
            >
              <GlassCard
                elevation="subtle"
                style={[
                  styles.blockCard,
                  {
                    borderLeftColor: block.color_hex || theme.colors.primary,
                    borderLeftWidth: 4,
                  },
                ]}
              >
                <View style={styles.timeBadge}>
                  <Caption style={styles.timeText}>{formatTime(block.start_time)}</Caption>
                  <Caption style={styles.timeSubtext}>{formatTime(block.end_time)}</Caption>
                </View>

                <View style={styles.infoCol}>
                  <BodyText numberOfLines={1} style={styles.blockTitle}>
                    {block.title}
                  </BodyText>
                  {block.task ? (
                    <View style={styles.taskTag}>
                      <Ionicons
                        name="checkmark-circle-outline"
                        size={12}
                        color={theme.colors.primary}
                      />
                      <Caption numberOfLines={1} style={{ color: theme.colors.primary }}>
                        {block.task.title}
                      </Caption>
                    </View>
                  ) : (
                    <Caption color="secondary" style={styles.typeText}>
                      {block.block_type.toUpperCase()}
                    </Caption>
                  )}
                </View>

                <Ionicons
                  name="chevron-forward"
                  size={16}
                  color={theme.colors.textSecondary}
                  style={styles.chevron}
                />
              </GlassCard>
            </TouchableOpacity>
          ))}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 12,
  },
  skeletonContainer: {
    marginVertical: 4,
  },
  emptyCard: {
    padding: 16,
    borderRadius: 16,
  },
  blocksList: {
    gap: 8,
  },
  blockCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 14,
  },
  timeBadge: {
    width: 68,
    borderRightWidth: 1,
    borderRightColor: 'rgba(233, 234, 242, 0.6)',
    paddingRight: 8,
    marginRight: 10,
  },
  timeText: {
    fontWeight: '700',
    fontSize: 12,
  },
  timeSubtext: {
    fontSize: 10,
    opacity: 0.7,
  },
  infoCol: {
    flex: 1,
  },
  blockTitle: {
    fontSize: 14,
    fontWeight: '600',
  },
  taskTag: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 2,
  },
  typeText: {
    fontSize: 11,
    letterSpacing: 0.5,
    marginTop: 2,
  },
  chevron: {
    marginLeft: 8,
  },
});

