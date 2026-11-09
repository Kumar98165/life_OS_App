import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { Heading, BodyText, Caption } from '../common/Typography';
import { IconButton } from '../common/Buttons';
import { getGreeting, formatDashboardDate } from '../../utils/dashboardUtils';

export interface DashboardHeaderProps {
  userName?: string | null;
  onProfilePress?: () => void;
  onNotificationPress?: () => void;
  onCustomizePress?: () => void;
  hasUnreadNotifications?: boolean;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  userName,
  onProfilePress,
  onNotificationPress,
  onCustomizePress,
  hasUnreadNotifications = false,
}) => {
  const { theme, isDark, toggleTheme } = useTheme();
  const greeting = getGreeting();
  const dateFormatted = formatDashboardDate();
  const displayName = userName?.split(' ')[0] || 'Friend';

  return (
    <View style={styles.container}>
      <View style={styles.textContainer}>
        <Caption color="secondary" style={styles.dateText}>
          {dateFormatted.toUpperCase()}
        </Caption>
        <Heading level={2} style={styles.greetingTitle}>
          {greeting},{'\n'}
          <Heading level={2} style={{ color: theme.colors.primary }}>
            {displayName} 👋
          </Heading>
        </Heading>
      </View>

      <View style={styles.actionButtons}>
        {/* Theme Toggle */}
        <IconButton
          icon={
            <Ionicons
              name={isDark ? 'sunny-outline' : 'moon-outline'}
              size={20}
              color={theme.colors.textPrimary}
            />
          }
          onPress={toggleTheme}
          variant="glass"
          size={40}
          accessibilityLabel="Toggle Dark Mode"
        />

        {/* Notifications Icon Button */}
        <View style={styles.notifWrapper}>
          <IconButton
            icon={
              <Ionicons
                name="notifications-outline"
                size={20}
                color={theme.colors.textPrimary}
              />
            }
            onPress={onNotificationPress}
            variant="glass"
            size={40}
            accessibilityLabel="Notifications"
          />
          {hasUnreadNotifications && (
            <View
              style={[
                styles.notifBadge,
                { backgroundColor: theme.colors.primary },
              ]}
            />
          )}
        </View>

        {/* Customize Dashboard Button */}
        {onCustomizePress && (
          <IconButton
            icon={
              <Ionicons
                name="options-outline"
                size={20}
                color={theme.colors.textPrimary}
              />
            }
            onPress={onCustomizePress}
            variant="glass"
            size={40}
            accessibilityLabel="Customize Dashboard Layout"
          />
        )}

        {/* Profile Avatar Button */}
        {onProfilePress && (
          <TouchableOpacity
            onPress={onProfilePress}
            style={[
              styles.avatarButton,
              {
                backgroundColor: theme.colors.glassBackgroundSolid,
                borderColor: theme.colors.glassBorder,
              },
              theme.shadows.subtle,
            ]}
            accessibilityRole="button"
            accessibilityLabel="View Profile"
          >
            <Ionicons name="person" size={18} color={theme.colors.primary} />
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 20,
    paddingTop: 8,
  },
  textContainer: {
    flex: 1,
    paddingRight: 12,
  },
  dateText: {
    letterSpacing: 0.8,
    marginBottom: 4,
    fontWeight: '600',
  },
  greetingTitle: {
    lineHeight: 28,
  },
  actionButtons: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  notifWrapper: {
    position: 'relative',
  },
  notifBadge: {
    position: 'absolute',
    top: 3,
    right: 3,
    width: 8,
    height: 8,
    borderRadius: 4,
    borderWidth: 1.5,
    borderColor: '#FFFFFF',
  },
  avatarButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
});

