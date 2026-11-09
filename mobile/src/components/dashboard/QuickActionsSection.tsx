import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { BodyText, Caption } from '../common/Typography';

export type QuickActionType = 'add_task' | 'plan_day' | 'create_goal' | 'focus';

export interface QuickActionsSectionProps {
  onActionPress: (action: QuickActionType) => void;
}

interface ActionItem {
  type: QuickActionType;
  label: string;
  icon: keyof typeof Ionicons.glyphMap;
  colorKey: 'primary' | 'success' | 'warning' | 'info';
}

const ACTIONS: ActionItem[] = [
  { type: 'add_task', label: 'Add Task', icon: 'add-circle-outline', colorKey: 'primary' },
  { type: 'plan_day', label: 'Plan Day', icon: 'calendar-outline', colorKey: 'info' },
  { type: 'create_goal', label: 'Create Goal', icon: 'flag-outline', colorKey: 'warning' },
  { type: 'focus', label: 'Focus Mode', icon: 'timer-outline', colorKey: 'success' },
];

export const QuickActionsSection: React.FC<QuickActionsSectionProps> = ({ onActionPress }) => {
  const { theme } = useTheme();

  return (
    <View style={styles.container}>
      <Caption color="secondary" style={styles.sectionTitle}>
        QUICK ACTIONS
      </Caption>

      <View style={styles.actionsRow}>
        {ACTIONS.map((action) => {
          const accentColor =
            action.colorKey === 'primary'
              ? theme.colors.primary
              : action.colorKey === 'success'
              ? theme.colors.success
              : action.colorKey === 'warning'
              ? theme.colors.warning
              : theme.colors.info;

          return (
            <TouchableOpacity
              key={action.type}
              onPress={() => onActionPress(action.type)}
              activeOpacity={0.8}
              style={[
                styles.actionCard,
                {
                  backgroundColor: theme.colors.glassBackgroundSolid,
                  borderColor: theme.colors.glassBorder,
                },
                theme.shadows.subtle,
              ]}
              accessibilityRole="button"
              accessibilityLabel={action.label}
            >
              <View
                style={[
                  styles.iconCircle,
                  { backgroundColor: `${accentColor}15` },
                ]}
              >
                <Ionicons name={action.icon} size={22} color={accentColor} />
              </View>
              <BodyText
                variant="small"
                weight="600"
                align="center"
                style={styles.actionLabel}
              >
                {action.label}
              </BodyText>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 24,
  },
  sectionTitle: {
    letterSpacing: 0.8,
    fontWeight: '600',
    marginBottom: 10,
  },
  actionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 8,
  },
  actionCard: {
    flex: 1,
    paddingVertical: 14,
    paddingHorizontal: 6,
    borderRadius: 14,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 88,
  },
  iconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  actionLabel: {
    fontSize: 12,
  },
});

