import React from 'react';
import { View, StyleSheet, ViewProps, StatusBar, StatusBarStyle } from 'react-native';
import { useTheme } from '../../theme';

export interface ScreenContainerProps extends ViewProps {
  statusBarStyle?: StatusBarStyle;
  padded?: boolean;
}

export const ScreenContainer: React.FC<ScreenContainerProps> = ({
  statusBarStyle,
  padded = true,
  style,
  children,
  ...props
}) => {
  const { theme, isDark } = useTheme();

  return (
    <View
      style={[
        styles.container,
        { backgroundColor: theme.colors.background },
        padded && { paddingHorizontal: theme.spacing.lg },
        style,
      ]}
      {...props}
    >
      <StatusBar
        barStyle={
          statusBarStyle || (isDark ? 'light-content' : 'dark-content')
        }
      />
      {children}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
