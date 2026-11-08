import React from 'react';
import { View, StyleSheet, useWindowDimensions, ViewProps } from 'react-native';

export interface ResponsiveContainerProps extends ViewProps {
  maxWidth?: number;
}

export const ResponsiveContainer: React.FC<ResponsiveContainerProps> = ({
  maxWidth = 640,
  style,
  children,
  ...props
}) => {
  const { width } = useWindowDimensions();
  const isConstrained = width > maxWidth;

  return (
    <View
      style={[
        styles.container,
        isConstrained && { maxWidth, alignSelf: 'center', width: '100%' },
        style,
      ]}
      {...props}
    >
      {children}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
  },
});

