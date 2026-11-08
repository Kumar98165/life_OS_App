import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { AuthNavigationProp } from '../../navigation/types';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  PrimaryButton,
  SecondaryButton,
  Heading,
  BodyText,
  Caption,
  IconButton,
} from '../../components';

export const WelcomeScreen: React.FC = () => {
  const { theme, isDark, toggleTheme } = useTheme();
  const navigation = useNavigation<AuthNavigationProp>();

  return (
    <SafeAreaContainer>
      <ScrollContainer contentContainerStyle={styles.scrollContent}>
        {/* Top bar with theme toggle */}
        <View style={styles.topBar}>
          <View style={styles.badge}>
            <Ionicons name="sparkles" size={14} color={theme.colors.primary} />
            <Caption weight="600" style={{ color: theme.colors.primary, marginLeft: 6 }}>
              AI Personal OS
            </Caption>
          </View>
          <IconButton
            icon={
              <Ionicons
                name={isDark ? 'sunny-outline' : 'moon-outline'}
                size={20}
                color={theme.colors.textPrimary}
              />
            }
            onPress={toggleTheme}
            variant="glass"
            size={40}
          />
        </View>

        {/* Hero Branding */}
        <View style={styles.heroSection}>
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
            <Ionicons name="infinite-outline" size={48} color={theme.colors.primary} />
          </View>
          <Heading level={1} align="center" style={styles.title}>
            LifeOS
          </Heading>
          <BodyText color="secondary" align="center" style={styles.subtitle}>
            Your intelligent personal operating system. Organize tasks, track habits, reach goals, and optimize your life with local AI.
          </BodyText>
        </View>

        {/* Feature Highlights Glass Cards */}
        <View style={styles.featuresSection}>
          <GlassCard elevation="subtle" style={styles.featureCard}>
            <View style={styles.featureRow}>
              <View
                style={[
                  styles.featureIconBox,
                  { backgroundColor: `${theme.colors.primary}15` },
                ]}
              >
                <Ionicons name="checkbox-outline" size={22} color={theme.colors.primary} />
              </View>
              <View style={styles.featureText}>
                <BodyText weight="600">Smart Tasks & Habits</BodyText>
                <Caption color="secondary">
                  Intelligent prioritization with automated streak tracking.
                </Caption>
              </View>
            </View>
          </GlassCard>

          <GlassCard elevation="subtle" style={styles.featureCard}>
            <View style={styles.featureRow}>
              <View
                style={[
                  styles.featureIconBox,
                  { backgroundColor: `${theme.colors.success}15` },
                ]}
              >
                <Ionicons name="hardware-chip-outline" size={22} color={theme.colors.success} />
              </View>
              <View style={styles.featureText}>
                <BodyText weight="600">Local Privacy-First AI</BodyText>
                <Caption color="secondary">
                  Powered by local LLMs with LangGraph context orchestration.
                </Caption>
              </View>
            </View>
          </GlassCard>

          <GlassCard elevation="subtle" style={styles.featureCard}>
            <View style={styles.featureRow}>
              <View
                style={[
                  styles.featureIconBox,
                  { backgroundColor: `${theme.colors.warning}15` },
                ]}
              >
                <Ionicons name="shield-checkmark-outline" size={22} color={theme.colors.warning} />
              </View>
              <View style={styles.featureText}>
                <BodyText weight="600">Enterprise Security</BodyText>
                <Caption color="secondary">
                  End-to-end token rotation and encrypted session isolation.
                </Caption>
              </View>
            </View>
          </GlassCard>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionsSection}>
          <PrimaryButton
            label="Get Started"
            onPress={() => navigation.navigate('Register')}
            style={styles.primaryBtn}
          />
          <SecondaryButton
            label="I already have an account"
            onPress={() => navigation.navigate('Login')}
            style={styles.secondaryBtn}
          />
        </View>

        <Caption color="muted" align="center" style={styles.footerText}>
          Version 1.0.0 • Production Ready
        </Caption>
      </ScrollContainer>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 40,
    paddingTop: 12,
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    backgroundColor: 'rgba(108, 99, 255, 0.1)',
  },
  heroSection: {
    alignItems: 'center',
    marginBottom: 32,
  },
  logoCircle: {
    width: 88,
    height: 88,
    borderRadius: 44,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 18,
  },
  title: {
    marginBottom: 8,
    fontSize: 32,
    letterSpacing: -0.5,
  },
  subtitle: {
    paddingHorizontal: 16,
    lineHeight: 22,
  },
  featuresSection: {
    gap: 12,
    marginBottom: 36,
  },
  featureCard: {
    padding: 16,
  },
  featureRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  featureIconBox: {
    width: 44,
    height: 44,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 14,
  },
  featureText: {
    flex: 1,
  },
  actionsSection: {
    gap: 12,
    marginBottom: 24,
  },
  primaryBtn: {
    marginBottom: 4,
  },
  secondaryBtn: {},
  footerText: {
    marginTop: 8,
  },
});
