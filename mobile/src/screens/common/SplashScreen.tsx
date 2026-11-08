import React from 'react';
import { View, StyleSheet, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { SafeAreaContainer, Heading, BodyText } from '../../components';

export const SplashScreen: React.FC = () => {
  const { theme } = useTheme();

  return (
    <SafeAreaContainer>
      <View style={styles.container}>
        <View
          style={[
            styles.logoCircle,
            {
              backgroundColor: theme.colors.glassBackgroundSolid,
              borderColor: theme.colors.glassBorder,
            },
            theme.shadows.floating,
          ]}
        >
          <Ionicons name="infinite-outline" size={44} color={theme.colors.primary} />
        </View>
        <Heading level={2} style={styles.title}>
          LifeOS
        </Heading>
        <BodyText color="secondary" style={styles.subtitle}>
          Restoring your secure session...
        </BodyText>
        <ActivityIndicator
          size="small"
          color={theme.colors.primary}
          style={styles.spinner}
        />
      </View>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  logoCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  title: {
    marginBottom: 6,
  },
  subtitle: {
    marginBottom: 24,
  },
  spinner: {
    marginTop: 8,
  },
});

