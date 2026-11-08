import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { GlassCard } from '../glass/GlassCard';
import { SectionHeader } from '../layout/SectionHeader';
import { BodyText, Caption } from '../common/Typography';
import { SkeletonLoader, EmptyState } from '../feedback/FeedbackComponents';
import { Goal } from '../../types';

export interface ActiveGoalsSectionProps {
  goals: Goal[];
  isLoading?: boolean;
  onViewAll?: () => void;
  onGoalPress?: (goal: Goal) => void;
  onCreateGoal?: () => void;
}

export const ActiveGoalsSection: React.FC<ActiveGoalsSectionProps> = ({
  goals,
  isLoading = false,
  onViewAll,
  onGoalPress,
  onCreateGoal,
}) => {
  const { theme } = useTheme();

  return (
    <View style={styles.container}>
      <SectionHeader
        title="Active Goals"
        actionText={goals.length > 0 ? 'View All' : undefined}
        onActionPress={onViewAll}
      />

      {isLoading ? (
        <View style={styles.skeletonContainer}>
          <SkeletonLoader height={74} borderRadius={14} style={{ marginBottom: 10 }} />
        </View>
      ) : goals.length === 0 ? (
        <GlassCard elevation="subtle" style={styles.emptyCard}>
          <EmptyState
            icon="trophy-outline"
            title="No active goals yet"
            description="Set milestones for your personal growth, career targets, or fitness aspirations."
            actionLabel="Create Goal"
            onActionPress={onCreateGoal}
          />
        </GlassCard>
      ) : (
        <View style={styles.goalsList}>
          {goals.slice(0, 3).map((goal) => {
            const progress = Math.min(Math.max(Math.round(goal.progress_percent), 0), 100);

            return (
              <TouchableOpacity
                key={goal.id}
                onPress={() => onGoalPress?.(goal)}
                activeOpacity={0.8}
                style={[
                  styles.goalCard,
                  {
                    backgroundColor: theme.colors.glassBackgroundSolid,
                    borderColor: theme.colors.glassBorder,
                  },
                  theme.shadows.subtle,
                ]}
                accessibilityRole="button"
                accessibilityLabel={`${goal.title}, ${progress}% complete`}
              >
                <View style={styles.goalHeader}>
                  <BodyText weight="600" style={styles.goalTitle}>
                    {goal.title}
                  </BodyText>
                  <Caption weight="600" style={{ color: theme.colors.primary }}>
                    {progress}%
                  </Caption>
                </View>

                {/* Progress bar */}
                <View
                  style={[
                    styles.progressBarBg,
                    { backgroundColor: theme.colors.surfaceSubtle },
                  ]}
                >
                  <View
                    style={[
                      styles.progressBarFill,
                      {
                        width: `${progress}%`,
                        backgroundColor: theme.colors.primary,
                      },
                    ]}
                  />
                </View>

                {goal.target_date ? (
                  <View style={styles.goalFooter}>
                    <Ionicons name="calendar-outline" size={12} color={theme.colors.textMuted} />
                    <Caption color="secondary" style={{ marginLeft: 4 }}>
                      Target: {new Date(goal.target_date).toLocaleDateString()}
                    </Caption>
                  </View>
                ) : null}
              </TouchableOpacity>
            );
          })}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 24,
  },
  skeletonContainer: {
    paddingVertical: 4,
  },
  emptyCard: {
    padding: 16,
  },
  goalsList: {
    gap: 10,
  },
  goalCard: {
    padding: 16,
    borderRadius: 14,
    borderWidth: 1,
  },
  goalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  goalTitle: {
    fontSize: 14,
    flex: 1,
    paddingRight: 8,
  },
  progressBarBg: {
    height: 6,
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 3,
  },
  goalFooter: {
    flexDirection: 'row',
    alignItems: 'center',
  },
});
