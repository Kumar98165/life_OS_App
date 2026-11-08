import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../theme';
import { GlassCard } from '../glass/GlassCard';
import { Heading, BodyText, Caption } from '../common/Typography';
import { PrimaryButton } from '../common/Buttons';

export interface AIQuickAccessCardProps {
  onTalkToAI: () => void;
}
export const AIQuickAccessCard: React.FC<AIQuickAccessCardProps> = ({ onTalkToAI }) => {
  const { theme } = useTheme();

  return (
    <GlassCard elevation="floating" style={styles.card}>
      <View style={styles.content}>
        <View style={styles.headerRow}>
          <View
            style={[
              styles.sparkleCircle,
              { backgroundColor: `${theme.colors.primary}18` },
            ]}
          >
            <Ionicons name="sparkles" size={24} color={theme.colors.primary} />
          </View>
          <View style={styles.titleCol}>
            <View style={styles.badgeRow}>
              <Caption
                weight="700"
                style={{ color: theme.colors.primary, letterSpacing: 0.8 }}
              >
                LOCAL AI ASSISTANT
              </Caption>
            </View>
            <Heading level={2} style={styles.title}>
              LifeOS Intelligence
            </Heading>
          </View>
        </View>

        <BodyText color="secondary" style={styles.description}>
          Ask LifeOS to help organize your schedule, synthesize notes, or reflect on goal progress with local privacy-first AI.
        </BodyText>

        <PrimaryButton
          label="Talk to LifeOS"
          icon={<Ionicons name="chatbubble-ellipses-outline" size={18} color="#FFFFFF" />}
          onPress={onTalkToAI}
          style={styles.button}
        />
      </View>
    </GlassCard>
  );
};

const styles = StyleSheet.create({
  card: {
    padding: 20,
    marginBottom: 28,
  },
  content: {},
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  sparkleCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 14,
  },
  titleCol: {
    flex: 1,
  },
  badgeRow: {
    marginBottom: 2,
  },
  title: {
    fontSize: 18,
  },
  description: {
    lineHeight: 20,
    marginBottom: 18,
  },
  button: {},
});

