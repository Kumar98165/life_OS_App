import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  RefreshControl,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import {
  useReminders,
  useDeleteReminder,
  useUpdateReminder,
} from '../../hooks/useNotifications';
import { RootNavigationProp } from '../../navigation/types';
import { Reminder, ReminderStatus } from '../../types/notification';
import {
  SafeAreaContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  EmptyState,
  SkeletonLoader,
} from '../../components';

const STATUS_FILTERS: { label: string; value: ReminderStatus | undefined }[] = [
  { label: 'Pending', value: 'pending' },
  { label: 'Triggered', value: 'triggered' },
  { label: 'All', value: undefined },
];

export const ReminderManagementScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<RootNavigationProp>();

  const [selectedStatus, setSelectedStatus] = useState<ReminderStatus | undefined>('pending');

  const {
    data: reminderData,
    isLoading,
    isRefetching,
    refetch,
  } = useReminders(selectedStatus);

  const deleteReminderMutation = useDeleteReminder();
  const updateReminderMutation = useUpdateReminder();

  const handleDelete = (item: Reminder) => {
    Alert.alert('Cancel Reminder', `Are you sure you want to cancel "${item.title}"?`, [
      { text: 'Keep', style: 'cancel' },
      {
        text: 'Cancel Reminder',
        style: 'destructive',
        onPress: () => {
          deleteReminderMutation.mutate(item.id);
        },
      },
    ]);
  };

  const formatReminderDate = (isoString: string) => {
    const dt = new Date(isoString);
    return dt.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusBadge = (status: ReminderStatus) => {
    switch (status) {
      case 'pending':
        return { label: 'Scheduled', color: theme.colors.primary, bg: theme.colors.primary + '20' };
      case 'triggered':
        return { label: 'Triggered', color: theme.colors.success, bg: theme.colors.success + '20' };
      case 'cancelled':
        return { label: 'Cancelled', color: theme.colors.textMuted, bg: theme.colors.surfaceSubtle };
      default:
        return { label: status, color: theme.colors.textMuted, bg: theme.colors.surfaceSubtle };
    }
  };

  const renderReminderItem = ({ item }: { item: Reminder }) => {
    const statusBadge = getStatusBadge(item.status);
    return (
      <GlassCard style={styles.card}>
        <View style={styles.headerRow}>
          <View style={{ flex: 1 }}>
            <View style={{ flexDirection: 'row', alignItems: 'center' }}>
              <Heading level={3} numberOfLines={1} style={{ flex: 1 }}>
                {item.title}
              </Heading>
              <View style={[styles.badge, { backgroundColor: statusBadge.bg }]}>
                <Caption weight="700" style={{ color: statusBadge.color }}>
                  {statusBadge.label}
                </Caption>
              </View>
            </View>

            {item.description ? (
              <BodyText variant="small" color="muted" style={{ marginTop: 4 }}>
                {item.description}
              </BodyText>
            ) : null}
          </View>
        </View>

        <View style={styles.metaRow}>
          <View style={styles.metaCol}>
            <Ionicons name="time-outline" size={14} color={theme.colors.primary} />
            <Caption weight="500" style={{ marginLeft: 4 }}>
              {formatReminderDate(item.reminder_time)}
            </Caption>
          </View>

          {item.is_recurring && item.recurrence_rule && (
            <View style={styles.recurrencePill}>
              <Ionicons name="repeat-outline" size={14} color={theme.colors.textMuted} />
              <Caption color="muted" style={{ marginLeft: 4, textTransform: 'capitalize' }}>
                {item.recurrence_rule}
              </Caption>
            </View>
          )}
        </View>

        <View style={[styles.divider, { backgroundColor: theme.colors.divider }]} />

        <View style={styles.cardActionsRow}>
          <TouchableOpacity
            style={styles.actionBtn}
            onPress={() => navigation.navigate('CreateEditReminder', { reminderId: item.id })}
          >
            <Ionicons name="pencil-outline" size={16} color={theme.colors.primary} />
            <BodyText variant="small" color="primary" weight="600" style={{ marginLeft: 4 }}>
              Edit
            </BodyText>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionBtn}
            onPress={() => handleDelete(item)}
          >
            <Ionicons name="trash-outline" size={16} color={theme.colors.error} />
            <BodyText variant="small" weight="600" style={{ marginLeft: 4, color: theme.colors.error }}>
              Cancel
            </BodyText>
          </TouchableOpacity>
        </View>
      </GlassCard>
    );
  };

  return (
    <SafeAreaContainer>
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.topHeader}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={[styles.iconButton, { backgroundColor: theme.colors.surfaceSubtle }]}
          >
            <Ionicons name="arrow-back" size={20} color={theme.colors.textPrimary} />
          </TouchableOpacity>

          <Heading level={2}>Reminders</Heading>

          <TouchableOpacity
            onPress={() => navigation.navigate('CreateEditReminder')}
            style={[styles.iconButton, { backgroundColor: theme.colors.primary }]}
          >
            <Ionicons name="add" size={22} color="#FFFFFF" />
          </TouchableOpacity>
        </View>

        {/* Status Filter Tabs */}
        <View style={styles.tabsRow}>
          {STATUS_FILTERS.map((f) => {
            const isSelected = selectedStatus === f.value;
            return (
              <TouchableOpacity
                key={f.label}
                onPress={() => setSelectedStatus(f.value)}
                style={[
                  styles.tabChip,
                  {
                    backgroundColor: isSelected ? theme.colors.primary : theme.colors.surface,
                    borderColor: isSelected ? theme.colors.primary : theme.colors.border,
                  },
                ]}
              >
                <BodyText
                  variant="small"
                  weight="600"
                  style={{ color: isSelected ? '#FFFFFF' : theme.colors.textPrimary }}
                >
                  {f.label}
                </BodyText>
              </TouchableOpacity>
            );
          })}
        </View>

        {isLoading ? (
          <View style={{ gap: 8, marginTop: 10 }}>
            <SkeletonLoader width="100%" height={90} borderRadius={16} />
            <SkeletonLoader width="100%" height={90} borderRadius={16} />
          </View>
        ) : (
          <FlatList
            data={reminderData?.reminders || []}
            keyExtractor={(item) => item.id}
            renderItem={renderReminderItem}
            contentContainerStyle={styles.listContent}
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
              <EmptyState
                title="No Reminders"
                description="Set a scheduled reminder for tasks, meetings, habits, or personal goals."
                actionLabel="Create Reminder"
                onActionPress={() => navigation.navigate('CreateEditReminder')}
              />
            }
          />
        )}
      </View>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 16,
  },
  topHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabsRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  tabChip: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
  },
  listContent: {
    paddingBottom: 24,
  },
  card: {
    padding: 16,
    borderRadius: 16,
    marginBottom: 12,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
    marginLeft: 8,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 10,
  },
  metaCol: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  recurrencePill: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  divider: {
    height: 1,
    marginVertical: 12,
  },
  cardActionsRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 16,
  },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
  },
});

