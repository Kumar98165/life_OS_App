import React, { useState, useMemo } from 'react';
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
  useNotifications,
  useMarkAsRead,
  useMarkAllAsRead,
  useDeleteNotification,
  useScanContext,
} from '../../hooks/useNotifications';
import { pushNotificationService } from '../../services/pushNotificationService';
import { RootNavigationProp } from '../../navigation/types';
import { Notification, NotificationCategory } from '../../types/notification';
import {
  SafeAreaContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  EmptyState,
  SkeletonLoader,
} from '../../components';

const CATEGORY_FILTERS: { label: string; value: string }[] = [
  { label: 'All', value: 'all' },
  { label: 'Unread', value: 'unread' },
  { label: 'Tasks', value: 'task' },
  { label: 'Planner', value: 'planner' },
  { label: 'Habits', value: 'habit' },
  { label: 'Finance', value: 'finance' },
  { label: 'Reminders', value: 'reminder' },
];

export const NotificationCenterScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<RootNavigationProp>();

  const [activeFilter, setActiveFilter] = useState<string>('all');

  const isUnreadFilter = activeFilter === 'unread';
  const categoryFilter =
    activeFilter !== 'all' && activeFilter !== 'unread'
      ? (activeFilter as NotificationCategory)
      : undefined;

  const {
    data: notifData,
    isLoading,
    isRefetching,
    refetch,
  } = useNotifications({
    unread_only: isUnreadFilter ? true : undefined,
    notification_type: categoryFilter,
    limit: 100,
  });

  const markReadMutation = useMarkAsRead();
  const markAllReadMutation = useMarkAllAsRead();
  const deleteNotifMutation = useDeleteNotification();
  const scanContextMutation = useScanContext();

  const handleNotificationPress = async (item: Notification) => {
    // 1. Mark as read
    if (!item.is_read) {
      markReadMutation.mutate(item.id);
    }

    // 2. Resolve deep link target
    const deepLink = pushNotificationService.parseNotificationDeepLink(item.data_payload);
    if (deepLink && deepLink.route) {
      try {
        (navigation as any).navigate(deepLink.route, deepLink.params);
      } catch {
        // Fallback if route does not match stack
      }
    }
  };

  const handleMarkAllRead = () => {
    markAllReadMutation.mutate();
  };

  const handleDelete = (item: Notification) => {
    deleteNotifMutation.mutate(item.id);
  };

  const handleScan = () => {
    scanContextMutation.mutate(undefined, {
      onSuccess: (data) => {
        Alert.alert(
          'Smart Context Scan Complete',
          `Generated ${data.total_generated} notifications (${data.task_notifications} tasks, ${data.habit_notifications} habits, ${data.finance_notifications} finance).`
        );
      },
    });
  };

  const getCategoryIcon = (cat: NotificationCategory) => {
    switch (cat) {
      case 'task':
        return { name: 'checkbox-outline' as const, color: '#48BB78' };
      case 'planner':
        return { name: 'calendar-outline' as const, color: '#4299E1' };
      case 'habit':
        return { name: 'flame-outline' as const, color: '#ED8936' };
      case 'goal':
        return { name: 'trophy-outline' as const, color: '#ECC94B' };
      case 'finance':
        return { name: 'wallet-outline' as const, color: '#38B2AC' };
      case 'reminder':
        return { name: 'alarm-outline' as const, color: '#9F7AEA' };
      default:
        return { name: 'notifications-outline' as const, color: theme.colors.primary };
    }
  };

  const formatRelativeTime = (isoString?: string) => {
    if (!isoString) return '';
    const now = new Date();
    const dt = new Date(isoString);
    const diffMs = now.getTime() - dt.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHrs = Math.floor(diffMin / 60);
    const diffDays = Math.floor(diffHrs / 24);

    if (diffMin < 1) return 'Just now';
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHrs < 24) return `${diffHrs}h ago`;
    if (diffDays === 1) return 'Yesterday';
    return dt.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  const renderNotificationItem = ({ item }: { item: Notification }) => {
    const iconMeta = getCategoryIcon(item.notification_type);
    return (
      <TouchableOpacity
        onPress={() => handleNotificationPress(item)}
        activeOpacity={0.7}
      >
        <GlassCard
          style={[
            styles.notifCard,
            !item.is_read && { borderLeftWidth: 4, borderLeftColor: theme.colors.primary },
          ]}
        >
          <View style={styles.cardRow}>
            <View style={[styles.iconBox, { backgroundColor: iconMeta.color + '20' }]}>
              <Ionicons name={iconMeta.name} size={20} color={iconMeta.color} />
            </View>

            <View style={styles.cardMain}>
              <View style={styles.titleRow}>
                <BodyText weight={item.is_read ? '500' : '700'} numberOfLines={1} style={{ flex: 1 }}>
                  {item.title}
                </BodyText>
                <Caption color="muted" style={{ marginLeft: 8 }}>
                  {formatRelativeTime(item.created_at)}
                </Caption>
              </View>

              <BodyText
                variant="small"
                color={item.is_read ? 'muted' : 'primary'}
                style={{ marginTop: 2 }}
                numberOfLines={2}
              >
                {item.body}
              </BodyText>
            </View>

            <TouchableOpacity
              onPress={() => handleDelete(item)}
              hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
              style={{ marginLeft: 8 }}
            >
              <Ionicons name="close" size={16} color={theme.colors.textMuted} />
            </TouchableOpacity>
          </View>
        </GlassCard>
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaContainer>
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.headerRow}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={[styles.iconButton, { backgroundColor: theme.colors.surfaceSubtle }]}
          >
            <Ionicons name="arrow-back" size={20} color={theme.colors.textPrimary} />
          </TouchableOpacity>

          <Heading level={2}>Notifications</Heading>

          <View style={styles.headerActions}>
            <TouchableOpacity
              onPress={handleScan}
              style={[styles.actionIconBtn, { backgroundColor: theme.colors.surfaceSubtle }]}
              accessibilityLabel="Scan Context"
            >
              <Ionicons name="scan-outline" size={18} color={theme.colors.primary} />
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => navigation.navigate('ReminderManagement')}
              style={[styles.actionIconBtn, { backgroundColor: theme.colors.surfaceSubtle }]}
            >
              <Ionicons name="alarm-outline" size={18} color={theme.colors.primary} />
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => navigation.navigate('NotificationSettings')}
              style={[styles.actionIconBtn, { backgroundColor: theme.colors.surfaceSubtle }]}
            >
              <Ionicons name="settings-outline" size={18} color={theme.colors.textPrimary} />
            </TouchableOpacity>
          </View>
        </View>

        {/* Filter Chips Row */}
        <View style={styles.filterRow}>
          <FlatList
            horizontal
            showsHorizontalScrollIndicator={false}
            data={CATEGORY_FILTERS}
            keyExtractor={(item) => item.value}
            contentContainerStyle={{ gap: 6, paddingVertical: 4 }}
            renderItem={({ item }) => {
              const isSelected = activeFilter === item.value;
              return (
                <TouchableOpacity
                  onPress={() => setActiveFilter(item.value)}
                  style={[
                    styles.filterChip,
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
                    {item.label}
                  </BodyText>
                </TouchableOpacity>
              );
            }}
          />
        </View>

        {/* Mark All Read Link */}
        <View style={styles.subHeaderRow}>
          <Caption color="muted">
            {notifData?.total || 0} Total Notifications
          </Caption>
          <TouchableOpacity onPress={handleMarkAllRead}>
            <BodyText variant="small" color="primary" weight="600">
              Mark all as read
            </BodyText>
          </TouchableOpacity>
        </View>

        {/* Notification List */}
        {isLoading ? (
          <View style={{ gap: 8, marginTop: 10 }}>
            <SkeletonLoader width="100%" height={74} borderRadius={14} />
            <SkeletonLoader width="100%" height={74} borderRadius={14} />
            <SkeletonLoader width="100%" height={74} borderRadius={14} />
          </View>
        ) : (
          <FlatList
            data={notifData?.notifications || []}
            keyExtractor={(item) => item.id}
            renderItem={renderNotificationItem}
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
                title="All Caught Up!"
                description="No notifications in this category. You're completely up to date."
                actionLabel="Schedule Reminder"
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
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerActions: {
    flexDirection: 'row',
    gap: 8,
  },
  actionIconBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  filterRow: {
    marginBottom: 10,
  },
  filterChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
  },
  subHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
    paddingHorizontal: 2,
  },
  listContent: {
    paddingBottom: 24,
  },
  notifCard: {
    padding: 14,
    borderRadius: 16,
    marginBottom: 8,
  },
  cardRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconBox: {
    width: 38,
    height: 38,
    borderRadius: 19,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  cardMain: {
    flex: 1,
  },
  titleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
});

