import React from 'react';
import {
  ScrollView,
  ScrollViewProps,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useTheme } from '../../theme';

export interface ScrollContainerProps extends ScrollViewProps {
  avoidKeyboard?: boolean;
  padded?: boolean;
}

export const ScrollContainer: React.FC<ScrollContainerProps> = ({
  avoidKeyboard = true,
  padded = true,
  contentContainerStyle,
  children,
  ...props
}) => {
  const { theme } = useTheme();

  const content = (
    <ScrollView
      showsVerticalScrollIndicator={false}
      keyboardShouldPersistTaps="handled"
      contentContainerStyle={[
        padded && { padding: theme.spacing.lg },
        styles.content,
        contentContainerStyle,
      ]}
      {...props}
    >
      {children}
    </ScrollView>
  );

  if (avoidKeyboard) {
    return (
      <KeyboardAvoidingView
        style={styles.keyboardContainer}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        {content}
      </KeyboardAvoidingView>
    );
  }

  return content;
};

const styles = StyleSheet.create({
  keyboardContainer: {
    flex: 1,
  },
  content: {
    flexGrow: 1,
  },
});

