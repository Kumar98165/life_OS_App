import React from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  ViewProps,
  Platform,
} from 'react-native';
import { BlurView } from 'expo-blur';
import { useTheme } from '../../theme';

export interface GlassCardProps extends ViewProps {
  onPress?: () => void;
  intensity?: number;
  elevation?: 'subtle' | 'card' | 'floating' | 'elevated' | 'none';
  variant?: 'frosted' | 'solid' | 'elevated';
}

export const GlassCard: React.FC<GlassCardProps> = ({
  onPress,
  intensity = 50,
  elevation = 'card',
  variant = 'frosted',
  style,
  children,
  ...props
}) => {
  const { theme, isDark } = useTheme();

  const effectiveElevation = elevation === 'elevated' ? 'floating' : elevation;
  const effectiveVariant = variant === 'elevated' ? 'frosted' : variant;

  const shadowStyle =
    effectiveElevation === 'subtle'
      ? theme.shadows.subtle
      : effectiveElevation === 'floating'
      ? theme.shadows.floating
      : effectiveElevation === 'card'
      ? theme.shadows.card
      : null;

  const cardContent = (
    <View
      style={[
        styles.base,
        {
          borderRadius: theme.borderRadius.xl,
          borderColor: theme.colors.glassBorder,
          backgroundColor:
            effectiveVariant === 'solid'
              ? theme.colors.glassBackgroundSolid
              : theme.colors.glassBackground,
        },
        shadowStyle,
        style,
      ]}
      {...props}
    >
      {/* Platform-aware frosted glass effect */}
      {Platform.OS === 'ios' && effectiveVariant === 'frosted' ? (
        <BlurView
          intensity={intensity}
          tint={isDark ? 'dark' : 'light'}
          style={StyleSheet.absoluteFill}
        />
      ) : null}
      <View style={styles.contentWrapper}>{children}</View>
    </View>
  );

  if (onPress) {
    return (
      <TouchableOpacity
        activeOpacity={0.85}
        onPress={onPress}
        accessibilityRole="button"
      >
        {cardContent}
      </TouchableOpacity>
    );
  }

  return cardContent;
};

const styles = StyleSheet.create({
  base: {
    borderWidth: 1,
    overflow: 'hidden',
    position: 'relative',
  },
  contentWrapper: {
    padding: 16,
    zIndex: 1,
  },
});

