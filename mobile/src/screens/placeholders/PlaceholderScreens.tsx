import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
} from '../../components';

interface PlaceholderProps {
  title: string;
  subtitle: string;
  icon: keyof typeof Ionicons.glyphMap;
  description: string;
  upcomingStep: string;
}

const GenericPlaceholder: React.FC<PlaceholderProps> = ({
  title,
  subtitle,
  icon,
  description,
  upcomingStep,
}) => {
  const { theme } = useTheme();

  return (
    <SafeAreaContainer edges={['top']}>
      <ScrollContainer contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Heading level={1}>{title}</Heading>
          <Caption color="secondary">{subtitle}</Caption>
        </View>

        <GlassCard elevation="floating" style={styles.card}>
          <View
            style={[
              styles.iconCircle,
              { backgroundColor: `${theme.colors.primary}15` },
            ]}
          >
            <Ionicons name={icon} size={36} color={theme.colors.primary} />
          </View>
          <Heading level={2} align="center" style={styles.cardTitle}>
            {title} Engine
          </Heading>
          <BodyText color="secondary" align="center" style={styles.cardDesc}>
            {description}
          </BodyText>
          <View
            style={[
              styles.stepBadge,
              { backgroundColor: theme.colors.surfaceSubtle },
            ]}
          >
            <Caption weight="600" style={{ color: theme.colors.primary }}>
              {upcomingStep}
            </Caption>
          </View>
        </GlassCard>
      </ScrollContainer>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 100,
  },
  header: {
    marginBottom: 24,
  },
  card: {
    padding: 24,
    alignItems: 'center',
  },
  iconCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  cardTitle: {
    marginBottom: 8,
  },
  cardDesc: {
    lineHeight: 22,
    marginBottom: 20,
  },
  stepBadge: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 12,
  },
});

