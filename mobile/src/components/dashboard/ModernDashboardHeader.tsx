import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { Heading, Caption } from '../common/Typography';

export interface ModernDashboardHeaderProps {
  userName?: string | null;
  onProfilePress?: () => void;
  onNotificationPress?: () => void;
  onSearchPress?: () => void;
  hasUnreadNotifications?: boolean;
}

export const ModernDashboardHeader: React.FC<ModernDashboardHeaderProps> = ({
  userName,
  onProfilePress,
  onNotificationPress,
  onSearchPress,
  hasUnreadNotifications = false,
}) => {
  const { theme } = useTheme();
  const displayName = userName?.split(' ')[0] || 'Friend';

  return (
    <View style={styles.header}>
      {/* Left: Avatar + Greeting */}
      <TouchableOpacity
        style={styles.profileSection}
        activeOpacity={0.8}
        onPress={onProfilePress}
      >
        <View style={[styles.avatarCircle, { backgroundColor: `${theme.colors.primary}20`, borderColor: theme.colors.border }]}>
          <Ionicons name="person" size={20} color={theme.colors.primary} />
          <View style={[styles.activeDot, { backgroundColor: theme.colors.success }]} />
        </View>
        <View style={styles.nameCol}>
          <Caption color="secondary">Welcome back,</Caption>
          <Heading level={2} style={styles.userNameText}>
            {displayName}
          </Heading>
        </View>
      </TouchableOpacity>

      {/* Right Action Icons: Search, Notifications */}
      <View style={styles.iconsRow}>
        {onSearchPress && (
          <TouchableOpacity
            style={[styles.iconBtn, { backgroundColor: theme.colors.surfaceSubtle }]}
            onPress={onSearchPress}
          >
            <Ionicons name="search-outline" size={20} color={theme.colors.textPrimary} />
          </TouchableOpacity>
        )}

        <TouchableOpacity
          style={[styles.iconBtn, { backgroundColor: theme.colors.surfaceSubtle }]}
          onPress={onNotificationPress}
        >
          <Ionicons name="notifications-outline" size={20} color={theme.colors.textPrimary} />
          {hasUnreadNotifications && (
            <View style={[styles.badgeDot, { backgroundColor: theme.colors.error }]} />
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    marginBottom: 12,
  },
  profileSection: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  avatarCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    position: 'relative',
  },
  activeDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    position: 'absolute',
    bottom: 0,
    right: 0,
    borderWidth: 1.5,
    borderColor: '#fff',
  },
  nameCol: {
    justifyContent: 'center',
  },
  userNameText: {
    fontSize: 18,
    fontWeight: '700',
  },
  iconsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  iconBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  badgeDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    position: 'absolute',
    top: 9,
    right: 10,
  },
});
