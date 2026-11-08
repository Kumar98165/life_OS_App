import React from 'react';
import { Text, TextProps, StyleSheet, TextStyle } from 'react-native';
import { useTheme } from '../../theme';

export interface HeadingProps extends TextProps {
  level?: 1 | 2 | 3;
  color?: string;
  align?: 'left' | 'center' | 'right';
}

export const Heading: React.FC<HeadingProps> = ({
  level = 1,
  color,
  align = 'left',
  style,
  children,
  ...props
}) => {
  const { theme } = useTheme();

  const baseStyle: TextStyle =
    level === 1
      ? theme.typography.h1
      : level === 2
      ? theme.typography.h2
      : theme.typography.h3;

  return (
    <Text
      accessibilityRole="header"
      style={[
        baseStyle,
        { textAlign: align },
        color ? { color } : undefined,
        style,
      ]}
      {...props}
    >
      {children}
    </Text>
  );
};

export interface BodyTextProps extends TextProps {
  variant?: 'large' | 'regular' | 'small' | 'lg' | 'sm' | 'xs';
  size?: 'large' | 'regular' | 'small' | 'lg' | 'sm' | 'xs' | 'md';
  color?: 'primary' | 'secondary' | 'muted' | 'inverse' | string;
  customColor?: string;
  weight?: TextStyle['fontWeight'] | 'bold' | 'semiBold' | 'medium' | 'normal';
  align?: 'left' | 'center' | 'right';
}

function resolveFontWeight(w?: any): TextStyle['fontWeight'] | undefined {
  if (!w) return undefined;
  if (w === 'bold') return '700';
  if (w === 'semiBold') return '600';
  if (w === 'medium') return '500';
  if (w === 'normal') return '400';
  return w;
}

export const BodyText: React.FC<BodyTextProps> = ({
  variant = 'regular',
  size,
  color = 'primary',
  customColor,
  weight,
  align = 'left',
  style,
  children,
  ...props
}) => {
  const { theme } = useTheme();

  const sizeKey = size || variant;
  const sizeStyle: TextStyle =
    sizeKey === 'large' || sizeKey === 'lg'
      ? theme.typography.bodyLarge
      : sizeKey === 'small' || sizeKey === 'sm' || sizeKey === 'xs'
      ? theme.typography.bodySmall
      : theme.typography.body;

  let resolvedColor = customColor;
  if (!resolvedColor) {
    if (color === 'secondary') resolvedColor = theme.colors.textSecondary;
    else if (color === 'muted') resolvedColor = theme.colors.textMuted;
    else if (color === 'inverse') resolvedColor = theme.colors.textInverse;
    else if (color === 'primary') resolvedColor = theme.colors.textPrimary;
    else resolvedColor = color || theme.colors.textPrimary;
  }

  const resolvedWeight = resolveFontWeight(weight);

  return (
    <Text
      style={[
        sizeStyle,
        { color: resolvedColor, textAlign: align },
        resolvedWeight ? { fontWeight: resolvedWeight } : undefined,
        style,
      ]}
      {...props}
    >
      {children}
    </Text>
  );
};

export interface CaptionProps extends TextProps {
  color?: 'primary' | 'secondary' | 'muted' | string;
  customColor?: string;
  weight?: TextStyle['fontWeight'] | 'bold' | 'semiBold' | 'medium' | 'normal';
  align?: 'left' | 'center' | 'right';
}

export const Caption: React.FC<CaptionProps> = ({
  color = 'muted',
  customColor,
  weight,
  align = 'left',
  style,
  children,
  ...props
}) => {
  const { theme } = useTheme();

  let resolvedColor = customColor;
  if (!resolvedColor) {
    if (color === 'secondary') resolvedColor = theme.colors.textSecondary;
    else if (color === 'primary') resolvedColor = theme.colors.textPrimary;
    else if (color === 'muted') resolvedColor = theme.colors.textMuted;
    else resolvedColor = color || theme.colors.textMuted;
  }

  const resolvedWeight = resolveFontWeight(weight);

  return (
    <Text
      style={[
        theme.typography.caption,
        { color: resolvedColor, textAlign: align },
        resolvedWeight ? { fontWeight: resolvedWeight } : undefined,
        style,
      ]}
      {...props}
    >
      {children}
    </Text>
  );
};

export interface LabelProps extends TextProps {
  required?: boolean;
}

export const Label: React.FC<LabelProps> = ({
  required = false,
  style,
  children,
  ...props
}) => {
  const { theme } = useTheme();

  return (
    <Text
      style={[
        theme.typography.bodySmall,
        styles.label,
        { color: theme.colors.textPrimary },
        style,
      ]}
      {...props}
    >
      {children}
      {required && <Text style={{ color: theme.colors.error }}> *</Text>}
    </Text>
  );
};

const styles = StyleSheet.create({
  label: {
    fontWeight: '600',
    marginBottom: 6,
    letterSpacing: 0.2,
  },
});
