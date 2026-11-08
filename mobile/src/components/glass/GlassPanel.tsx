import React from 'react';
import { View, StyleSheet, ViewProps, Platform } from 'react-native';
import { BlurView } from 'expo-blur';
import { useTheme } from '../../theme';

export interface GlassPanelProps extends ViewProps {
  intensity?: number;
  roundedTopOnly?: boolean;
}

export const GlassPanel: React.FC<GlassPanelProps> = ({
  intensity = 40,
  roundedTopOnly = false,
  style,
  children,
  ...props
}) => {
  const { theme, isDark } = useTheme();

  return (
    <View
      style={[
        styles.panel,
        {
          borderColor: theme.colors.glassBorder,
          backgroundColor: theme.colors.glassBackgroundSolid,
          borderRadius: roundedTopOnly ? 0 : theme.borderRadius.xl,
          borderTopLeftRadius: theme.borderRadius.xl,
          borderTopRightRadius: theme.borderRadius.xl,
        },
        theme.shadows.card,
        style,
      ]}
      {...props}
    >
      {Platform.OS === 'ios' ? (
        <BlurView
          intensity={intensity}
          tint={isDark ? 'dark' : 'light'}
          style={StyleSheet.absoluteFill}
        />
      ) : null}
      <View style={styles.content}>{children}</View>
    </View>
  );
};

const styles = StyleSheet.create({
  panel: {
    borderWidth: 1,
    overflow: 'hidden',
  },
  content: {
    padding: 20,
    zIndex: 1,
  },
});

