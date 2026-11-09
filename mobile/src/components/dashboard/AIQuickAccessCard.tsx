import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { GlassCard } from '../glass/GlassCard';
import { Heading, BodyText, Caption } from '../common/Typography';
import { PrimaryButton } from '../common/Buttons';
import { useAIProactiveInsights, useAIDailyBriefing } from '../../hooks/useAI';

export interface AIQuickAccessCardProps {
  onTalkToAI: () => void;
  onNavigateScreen?: (screen: string) => void;
}

export const AIQuickAccessCard: React.FC<AIQuickAccessCardProps> = ({
  onTalkToAI,
  onNavigateScreen,
}) => {
  const { theme } = useTheme();
  const { data: insights = [] } = useAIProactiveInsights();
  const { data: briefing } = useAIDailyBriefing();

  const topInsight = insights.length > 0 ? insights[0] : null;

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
                PERSONAL INTELLIGENCE
              </Caption>
            </View>
            <Heading level={2} style={styles.title}>
              {briefing?.greeting || 'LifeOS Intelligence'}
            </Heading>
          </View>
        </View>

        {topInsight ? (
          <TouchableOpacity
            style={[
              styles.insightBox,
              {
                backgroundColor:
                  topInsight.severity === 'warning'
                    ? '#EF444415'
                    : topInsight.severity === 'celebration'
                    ? '#10B98115'
                    : `${theme.colors.primary}12`,
                borderColor:
                  topInsight.severity === 'warning'
                    ? '#EF444440'
                    : topInsight.severity === 'celebration'
                    ? '#10B98140'
                    : `${theme.colors.primary}30`,
              },
            ]}
            onPress={() => {
              if (topInsight.target_screen && onNavigateScreen) {
                onNavigateScreen(topInsight.target_screen);
              } else {
                onTalkToAI();
              }
            }}
            accessibilityLabel={topInsight.title}
          >
            <View style={styles.insightHeader}>
              <Ionicons
                name={
                  topInsight.severity === 'warning'
                    ? 'alert-circle'
                    : topInsight.severity === 'celebration'
                    ? 'ribbon'
                    : 'bulb-outline'
                }
                size={16}
                color={
                  topInsight.severity === 'warning'
                    ? '#EF4444'
                    : topInsight.severity === 'celebration'
                    ? '#10B981'
                    : theme.colors.primary
                }
                style={{ marginRight: 6 }}
              />
              <Caption
                weight="700"
                style={{
                  color:
                    topInsight.severity === 'warning'
                      ? '#EF4444'
                      : topInsight.severity === 'celebration'
                      ? '#10B981'
                      : theme.colors.primary,
                  flex: 1,
                }}
                numberOfLines={1}
              >
                {topInsight.title}
              </Caption>
            </View>
            <BodyText
              color="secondary"
              style={styles.insightMessage}
              numberOfLines={2}
            >
              {topInsight.message}
            </BodyText>
          </TouchableOpacity>
        ) : (
          <BodyText color="secondary" style={styles.description}>
            {briefing?.priority_suggestions && briefing.priority_suggestions.length > 0
              ? briefing.priority_suggestions[0]
              : 'Ask LifeOS to organize your day, review habit streaks, or analyze active goal milestones.'}
          </BodyText>
        )}

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
  insightBox: {
    borderWidth: 1,
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
  },
  insightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  insightMessage: {
    fontSize: 13,
    lineHeight: 18,
  },
  button: {},
});


