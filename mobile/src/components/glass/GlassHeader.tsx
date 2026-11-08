import React from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  Platform,
  ViewProps,
} from 'react-native';
import { BlurView } from 'expo-blur';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTheme } from '../../theme';
import { Heading } from '../common/Typography';

export interface GlassHeaderProps extends ViewProps {
  title: string;
  onBackPress?: () => void;
  rightAction?: React.ReactNode;
  showBorder?: boolean;
}

export const GlassHeader: React.FC<GlassHeaderProps> = ({
  title,
  onBackPress,
  rightAction,
  showBorder = true,
  style,
  ...props
}) => {
  const insets = useSafeAreaInsets();
  const { theme, isDark } = useTheme();

  return (
    <View
      style={[
        styles.container,
        {
          paddingTop: Math.max(insets.top, 12),
          borderBottomColor: theme.colors.glassBorderSubtle,
          borderBottomWidth: showBorder ? 1 : 0,
          backgroundColor:
            Platform.OS === 'ios'
              ? theme.colors.glassBackgroundMuted
              : theme.colors.glassBackgroundSolid,
        },
        style,
      ]}
      {...props}
    >
      {Platform.OS === 'ios' ? (
        <BlurView
          intensity={60}
          tint={isDark ? 'dark' : 'light'}
          style={StyleSheet.absoluteFill}
        />
      ) : null}

      <View style={styles.contentRow}>
        <View style={styles.leftSlot}>
          {onBackPress ? (
            <TouchableOpacity
              onPress={onBackPress}
              hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
              style={styles.iconButton}
              accessibilityRole="button"
              accessibilityLabel="Go back"
            >
              <Ionicons
                name="chevron-back"
                size={24}
                color={theme.colors.textPrimary}
              />
            </TouchableOpacity>
          ) : null}
        </View>

        <Heading level={3} style={styles.title} numberOfLines={1}>
          {title}
        </Heading>

        <View style={styles.rightSlot}>{rightAction || null}</View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
    paddingBottom: 12,
    zIndex: 50,
  },
  contentRow: {
    height: 44,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
  },
  leftSlot: {
    width: 44,
    alignItems: 'flex-start',
    justifyContent: 'center',
  },
  rightSlot: {
    width: 44,
    alignItems: 'flex-end',
    justifyContent: 'center',
  },
  title: {
    flex: 1,
    textAlign: 'center',
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

