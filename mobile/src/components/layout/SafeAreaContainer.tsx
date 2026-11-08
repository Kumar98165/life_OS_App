import React from 'react';
import { StyleSheet, ViewProps } from 'react-native';
import { SafeAreaView, SafeAreaViewProps } from 'react-native-safe-area-context';
import { useTheme } from '../../theme';

export interface SafeAreaContainerProps extends SafeAreaViewProps {
  edges?: ('top' | 'right' | 'bottom' | 'left')[];
}

export const SafeAreaContainer: React.FC<SafeAreaContainerProps> = ({
  edges = ['top', 'bottom'],
  style,
  children,
  ...props
}) => {
  const { theme } = useTheme();

  return (
    <SafeAreaView
      edges={edges}
      style={[
        styles.safeArea,
        { backgroundColor: theme.colors.background },
        style,
      ]}
      {...props}
    >
      {children}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
});

