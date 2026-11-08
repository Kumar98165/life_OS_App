import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
  TouchableOpacityProps,
  View,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../theme';

export interface ButtonProps extends TouchableOpacityProps {
  label: string;
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  fullWidth?: boolean;
}

export const PrimaryButton: React.FC<ButtonProps> = ({
  label,
  loading = false,
  disabled = false,
  icon,
  fullWidth = true,
  style,
  ...props
}) => {
  const { theme } = useTheme();

  return (
    <TouchableOpacity
      activeOpacity={0.85}
      disabled={disabled || loading}
      style={[
        styles.base,
        fullWidth && styles.fullWidth,
        disabled && styles.disabled,
        theme.shadows.floating,
        style,
      ]}
      accessibilityRole="button"
      accessibilityLabel={label}
      {...props}
    >
      <LinearGradient
        colors={[theme.colors.primary, theme.colors.primaryDark]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={[styles.gradient, { borderRadius: theme.borderRadius.md }]}
      >
        {loading ? (
          <ActivityIndicator color="#FFFFFF" size="small" />
        ) : (
          <View style={styles.contentRow}>
            {icon ? <View style={styles.iconMargin}>{icon}</View> : null}
            <Text style={[theme.typography.button, styles.primaryText]}>
              {label}
            </Text>
          </View>
        )}
      </LinearGradient>
    </TouchableOpacity>
  );
};

export const SecondaryButton: React.FC<ButtonProps> = ({
  label,
  loading = false,
  disabled = false,
  icon,
  fullWidth = true,
  style,
  ...props
}) => {
  const { theme } = useTheme();

  return (
    <TouchableOpacity
      activeOpacity={0.8}
      disabled={disabled || loading}
      style={[
        styles.base,
        styles.secondaryBase,
        fullWidth && styles.fullWidth,
        {
          borderRadius: theme.borderRadius.md,
          borderColor: theme.colors.glassBorder,
          backgroundColor: theme.colors.glassBackgroundSolid,
        },
        theme.shadows.subtle,
        disabled && styles.disabled,
        style,
      ]}
      accessibilityRole="button"
      accessibilityLabel={label}
      {...props}
    >
      {loading ? (
        <ActivityIndicator color={theme.colors.primary} size="small" />
      ) : (
        <View style={styles.contentRow}>
          {icon ? <View style={styles.iconMargin}>{icon}</View> : null}
          <Text
            style={[
              theme.typography.button,
              { color: theme.colors.textPrimary },
            ]}
          >
            {label}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );
};

export interface IconButtonProps extends TouchableOpacityProps {
  icon: React.ReactNode;
  size?: number;
  variant?: 'glass' | 'solid' | 'primary';
}

export const IconButton: React.FC<IconButtonProps> = ({
  icon,
  size = 44,
  variant = 'glass',
  style,
  ...props
}) => {
  const { theme } = useTheme();

  const bg =
    variant === 'primary'
      ? theme.colors.primary
      : variant === 'solid'
      ? theme.colors.surface
      : theme.colors.glassBackgroundSolid;

  return (
    <TouchableOpacity
      activeOpacity={0.75}
      style={[
        styles.iconButtonBase,
        {
          width: size,
          height: size,
          borderRadius: size / 2,
          backgroundColor: bg,
          borderColor: theme.colors.glassBorder,
        },
        theme.shadows.subtle,
        style,
      ]}
      accessibilityRole="button"
      {...props}
    >
      {icon}
    </TouchableOpacity>
  );
};

export interface FloatingActionButtonProps extends TouchableOpacityProps {
  icon: React.ReactNode;
  onPress: () => void;
  label?: string;
}

export const FloatingActionButton: React.FC<FloatingActionButtonProps> = ({
  icon,
  onPress,
  label,
  style,
  ...props
}) => {
  const { theme } = useTheme();

  return (
    <TouchableOpacity
      activeOpacity={0.85}
      onPress={onPress}
      style={[
        styles.fabBase,
        {
          backgroundColor: theme.colors.primary,
          borderRadius: theme.borderRadius.pill,
        },
        theme.shadows.floating,
        style,
      ]}
      accessibilityRole="button"
      accessibilityLabel={label || 'Action'}
      {...props}
    >
      {icon}
      {label ? (
        <Text style={[theme.typography.button, styles.fabText]}>{label}</Text>
      ) : null}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  base: {
    height: 50,
    minHeight: 44,
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 6,
  },
  fullWidth: {
    width: '100%',
  },
  gradient: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  secondaryBase: {
    borderWidth: 1,
    paddingHorizontal: 20,
  },
  contentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconMargin: {
    marginRight: 8,
  },
  primaryText: {
    color: '#FFFFFF',
  },
  disabled: {
    opacity: 0.5,
  },
  iconButtonBase: {
    borderWidth: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  fabBase: {
    position: 'absolute',
    bottom: 24,
    right: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    paddingHorizontal: 20,
    minWidth: 54,
    minHeight: 54,
    zIndex: 90,
  },
  fabText: {
    color: '#FFFFFF',
    marginLeft: 8,
  },
});

