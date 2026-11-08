import React from 'react';
import { View, StyleSheet, TouchableOpacity, ViewProps } from 'react-native';
import { useTheme } from '../../theme';
import { Heading, BodyText } from '../common/Typography';

export interface SectionHeaderProps extends ViewProps {
  title: string;
  subtitle?: string;
  actionText?: string;
  onActionPress?: () => void;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  subtitle,
  actionText,
  onActionPress,
  style,
  ...props
}) => {
  const { theme } = useTheme();

  return (
    <View style={[styles.container, style]} {...props}>
      <View style={styles.textContainer}>
        <Heading level={2} style={styles.title}>
          {title}
        </Heading>
        {subtitle ? (
          <BodyText variant="small" color="secondary" style={styles.subtitle}>
            {subtitle}
          </BodyText>
        ) : null}
      </View>
      {actionText && onActionPress ? (
        <TouchableOpacity
          onPress={onActionPress}
          hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
          accessibilityRole="button"
          accessibilityLabel={actionText}
        >
          <BodyText
            variant="small"
            weight="600"
            customColor={theme.colors.primary}
          >
            {actionText}
          </BodyText>
        </TouchableOpacity>
      ) : null}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  textContainer: {
    flex: 1,
    marginRight: 8,
  },
  title: {
    letterSpacing: -0.2,
  },
  subtitle: {
    marginTop: 2,
  },
});

