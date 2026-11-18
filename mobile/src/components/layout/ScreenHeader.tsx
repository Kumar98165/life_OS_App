import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import { Heading, Caption } from '../common/Typography';

export interface ScreenHeaderProps {
  title: string;
  subtitle?: string;
  onBack?: () => void;
  rightAction?: React.ReactNode;
}

export const ScreenHeader: React.FC<ScreenHeaderProps> = ({
  title,
  subtitle,
  onBack,
  rightAction,
}) => {
  const { theme } = useTheme();
  const navigation = useNavigation();

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      navigation.goBack();
    }
  };

  return (
    <View style={styles.header}>
      {/* Back Button on Left */}
      <TouchableOpacity
        style={[
          styles.backBtn,
          {
            backgroundColor: theme.colors.surfaceSubtle,
            borderColor: theme.colors.border,
          },
        ]}
        onPress={handleBack}
        accessibilityRole="button"
        accessibilityLabel="Go back"
      >
        <Ionicons name="chevron-back" size={20} color={theme.colors.textPrimary} />
      </TouchableOpacity>

      {/* Center/Left Title Column */}
      <View style={styles.titleCol}>
        <Heading level={2} style={styles.title} numberOfLines={1}>
          {title}
        </Heading>
        {subtitle ? (
          <Caption color="secondary" numberOfLines={1}>
            {subtitle}
          </Caption>
        ) : null}
      </View>

      {/* Right Slot */}
      <View style={styles.rightSlot}>
        {rightAction || null}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    paddingTop: 8,
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 14,
  },
  titleCol: {
    flex: 1,
    justifyContent: 'center',
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
  },
  rightSlot: {
    alignItems: 'flex-end',
    justifyContent: 'center',
  },
});
