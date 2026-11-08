import React, { useState } from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { useAuthStore } from '../../store';
import { OnboardingPreferences } from '../../types';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  PrimaryButton,
  SecondaryButton,
  Heading,
  BodyText,
  Caption,
} from '../../components';

const FOCUS_AREAS = [
  { id: 'health', label: 'Health & Fitness', icon: 'fitness-outline' },
  { id: 'career', label: 'Career & Ambition', icon: 'briefcase-outline' },
  { id: 'finance', label: 'Financial Freedom', icon: 'wallet-outline' },
  { id: 'knowledge', label: 'Deep Knowledge', icon: 'book-outline' },
  { id: 'productivity', label: 'Daily Organization', icon: 'time-outline' },
  { id: 'mindfulness', label: 'Mental Clarity', icon: 'leaf-outline' },
];

const INITIAL_GOALS = [
  { id: 'routine', label: 'Establish a morning & evening routine', category: 'productivity' },
  { id: 'deep_work', label: 'Execute 4 hours of distraction-free deep work', category: 'career' },
  { id: 'budget', label: 'Track daily personal & business expenses', category: 'finance' },
  { id: 'workout', label: 'Exercise 4 times per week consistently', category: 'health' },
  { id: 'reading', label: 'Read 20 pages of non-fiction daily', category: 'knowledge' },
  { id: 'meditate', label: 'Practice 10 minutes of daily mindfulness', category: 'mindfulness' },
];

export const OnboardingScreen: React.FC = () => {
  const { theme, isDark, toggleTheme } = useTheme();
  const { user, completeOnboarding } = useAuthStore();

  const [step, setStep] = useState<number>(1);
  const [selectedFocus, setSelectedFocus] = useState<string[]>(['productivity', 'health']);
  const [selectedGoals, setSelectedGoals] = useState<string[]>(['routine', 'deep_work']);
  const [themePref, setThemePref] = useState<'light' | 'dark' | 'system'>('system');
  const [notificationPref, setNotificationPref] = useState<'realtime' | 'daily_summary' | 'quiet'>('daily_summary');
  const [aiStyle, setAiStyle] = useState<'concise' | 'balanced' | 'comprehensive'>('balanced');

  const toggleFocus = (id: string) => {
    setSelectedFocus((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const toggleGoal = (id: string) => {
    setSelectedGoals((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleFinish = async () => {
    const preferences: OnboardingPreferences = {
      focusAreas: selectedFocus,
      initialGoals: selectedGoals,
      themePreference: themePref,
      notificationFrequency: notificationPref,
      aiInteractionStyle: aiStyle,
    };
    await completeOnboarding(preferences);
  };

  return (
    <SafeAreaContainer>
      <ScrollContainer contentContainerStyle={styles.scrollContent}>
        {/* Progress Header */}
        <View style={styles.progressRow}>
          <Caption weight="600" style={{ color: theme.colors.primary }}>
            STEP {step} OF 5
          </Caption>
          <View style={styles.progressBarBackground}>
            <View
              style={[
                styles.progressBarFill,
                {
                  backgroundColor: theme.colors.primary,
                  width: `${(step / 5) * 100}%`,
                },
              ]}
            />
          </View>
        </View>

        {/* Step 1: Welcome */}
        {step === 1 && (
          <View style={styles.stepContainer}>
            <View style={styles.iconCircle}>
              <Ionicons name="sparkles" size={40} color={theme.colors.primary} />
            </View>
            <Heading level={1} align="center" style={styles.title}>
              Welcome, {user?.full_name?.split(' ')[0] || 'Friend'}!
            </Heading>
            <BodyText color="secondary" align="center" style={styles.description}>
              LifeOS brings all dimensions of your daily life together—tasks, habits, schedules, goals, and finances—assisted by local artificial intelligence.
            </BodyText>

            <GlassCard elevation="subtle" style={styles.infoCard}>
              <View style={styles.bulletRow}>
                <Ionicons name="checkmark-circle" size={18} color={theme.colors.success} />
                <BodyText variant="small" style={styles.bulletText}>
                  Your data stays strictly private and secure on your device.
                </BodyText>
              </View>
              <View style={styles.bulletRow}>
                <Ionicons name="checkmark-circle" size={18} color={theme.colors.success} />
                <BodyText variant="small" style={styles.bulletText}>
                  Intelligent recommendations adapt to your personal lifestyle.
                </BodyText>
              </View>
            </GlassCard>
          </View>
        )}

        {/* Step 2: Focus Areas */}
        {step === 2 && (
          <View style={styles.stepContainer}>
            <Heading level={1}>Core Focus Areas</Heading>
            <BodyText color="secondary" style={styles.stepSubtitle}>
              Select the pillars of your life you want LifeOS to optimize first.
            </BodyText>

            <View style={styles.gridContainer}>
              {FOCUS_AREAS.map((area) => {
                const isSelected = selectedFocus.includes(area.id);
                return (
                  <TouchableOpacity
                    key={area.id}
                    onPress={() => toggleFocus(area.id)}
                    activeOpacity={0.8}
                    style={[
                      styles.choiceCard,
                      {
                        backgroundColor: isSelected
                          ? 'rgba(108, 99, 255, 0.12)'
                          : theme.colors.glassBackgroundSolid,
                        borderColor: isSelected
                          ? theme.colors.primary
                          : theme.colors.glassBorder,
                      },
                    ]}
                  >
                    <Ionicons
                      name={area.icon as any}
                      size={24}
                      color={isSelected ? theme.colors.primary : theme.colors.textSecondary}
                    />
                    <BodyText
                      weight={isSelected ? '600' : '400'}
                      style={{
                        marginTop: 8,
                        color: isSelected ? theme.colors.primary : theme.colors.textPrimary,
                        fontSize: 13,
                        textAlign: 'center',
                      }}
                    >
                      {area.label}
                    </BodyText>
                  </TouchableOpacity>
                );
              })}
            </View>
          </View>
        )}

        {/* Step 3: Initial Goals */}
        {step === 3 && (
          <View style={styles.stepContainer}>
            <Heading level={1}>Initial Goals</Heading>
            <BodyText color="secondary" style={styles.stepSubtitle}>
              Choose 1 or more initial targets you'd like to achieve this month.
            </BodyText>

            <View style={styles.listContainer}>
              {INITIAL_GOALS.map((goal) => {
                const isSelected = selectedGoals.includes(goal.id);
                return (
                  <TouchableOpacity
                    key={goal.id}
                    onPress={() => toggleGoal(goal.id)}
                    activeOpacity={0.8}
                    style={[
                      styles.goalCard,
                      {
                        backgroundColor: isSelected
                          ? 'rgba(108, 99, 255, 0.1)'
                          : theme.colors.glassBackgroundSolid,
                        borderColor: isSelected
                          ? theme.colors.primary
                          : theme.colors.glassBorder,
                      },
                    ]}
                  >
                    <Ionicons
                      name={isSelected ? 'checkbox' : 'square-outline'}
                      size={22}
                      color={isSelected ? theme.colors.primary : theme.colors.textMuted}
                    />
                    <BodyText
                      weight={isSelected ? '600' : '400'}
                      style={[
                        styles.goalLabel,
                        {
                          color: isSelected
                            ? theme.colors.textPrimary
                            : theme.colors.textSecondary,
                        },
                      ]}
                    >
                      {goal.label}
                    </BodyText>
                  </TouchableOpacity>
                );
              })}
            </View>
          </View>
        )}

        {/* Step 4: Preferences */}
        {step === 4 && (
          <View style={styles.stepContainer}>
            <Heading level={1}>Preferences</Heading>
            <BodyText color="secondary" style={styles.stepSubtitle}>
              Configure notifications and AI interaction style.
            </BodyText>

            {/* AI Style */}
            <BodyText weight="600" style={styles.sectionLabel}>
              AI Communication Style
            </BodyText>
            <View style={styles.segmentRow}>
              {(['concise', 'balanced', 'comprehensive'] as const).map((styleOpt) => (
                <TouchableOpacity
                  key={styleOpt}
                  onPress={() => setAiStyle(styleOpt)}
                  style={[
                    styles.segmentBtn,
                    aiStyle === styleOpt && {
                      backgroundColor: theme.colors.primary,
                      borderColor: theme.colors.primary,
                    },
                    { borderColor: theme.colors.glassBorder },
                  ]}
                >
                  <Caption
                    weight="600"
                    style={{
                      color: aiStyle === styleOpt ? '#FFFFFF' : theme.colors.textSecondary,
                      textTransform: 'capitalize',
                    }}
                  >
                    {styleOpt}
                  </Caption>
                </TouchableOpacity>
              ))}
            </View>

            {/* Notification Frequency */}
            <BodyText weight="600" style={[styles.sectionLabel, { marginTop: 20 }]}>
              Notification Cadence
            </BodyText>
            <View style={styles.segmentRow}>
              {(
                [
                  { id: 'daily_summary', label: 'Daily Brief' },
                  { id: 'realtime', label: 'Realtime' },
                  { id: 'quiet', label: 'Quiet Mode' },
                ] as const
              ).map((notifOpt) => (
                <TouchableOpacity
                  key={notifOpt.id}
                  onPress={() => setNotificationPref(notifOpt.id)}
                  style={[
                    styles.segmentBtn,
                    notificationPref === notifOpt.id && {
                      backgroundColor: theme.colors.primary,
                      borderColor: theme.colors.primary,
                    },
                    { borderColor: theme.colors.glassBorder },
                  ]}
                >
                  <Caption
                    weight="600"
                    style={{
                      color:
                        notificationPref === notifOpt.id ? '#FFFFFF' : theme.colors.textSecondary,
                    }}
                  >
                    {notifOpt.label}
                  </Caption>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {/* Step 5: Summary */}
        {step === 5 && (
          <View style={styles.stepContainer}>
            <View style={styles.iconCircle}>
              <Ionicons name="rocket-outline" size={40} color={theme.colors.primary} />
            </View>
            <Heading level={1} align="center" style={styles.title}>
              You're All Set!
            </Heading>
            <BodyText color="secondary" align="center" style={styles.description}>
              LifeOS has configured your workspace based on your selections. You are ready to start organizing your life.
            </BodyText>

            <GlassCard elevation="floating" style={styles.summaryCard}>
              <View style={styles.summaryItem}>
                <Caption color="secondary">Selected Focus Areas</Caption>
                <BodyText weight="600">{selectedFocus.length} Pillars Chosen</BodyText>
              </View>
              <View style={styles.summaryDivider} />
              <View style={styles.summaryItem}>
                <Caption color="secondary">Initial Targets</Caption>
                <BodyText weight="600">{selectedGoals.length} Goals Active</BodyText>
              </View>
              <View style={styles.summaryDivider} />
              <View style={styles.summaryItem}>
                <Caption color="secondary">AI Assistant Mode</Caption>
                <BodyText weight="600" style={{ textTransform: 'capitalize' }}>
                  {aiStyle}
                </BodyText>
              </View>
            </GlassCard>
          </View>
        )}

        {/* Navigation Controls */}
        <View style={styles.buttonRow}>
          {step > 1 && (
            <SecondaryButton
              label="Back"
              onPress={() => setStep((s) => s - 1)}
              style={styles.backButton}
              fullWidth={false}
            />
          )}
          {step < 5 ? (
            <PrimaryButton
              label="Continue"
              onPress={() => setStep((s) => s + 1)}
              style={styles.continueButton}
              fullWidth={step === 1}
            />
          ) : (
            <PrimaryButton
              label="Enter LifeOS"
              onPress={handleFinish}
              style={styles.continueButton}
              fullWidth
            />
          )}
        </View>
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
  progressRow: {
    marginBottom: 28,
  },
  progressBarBackground: {
    height: 6,
    borderRadius: 3,
    backgroundColor: 'rgba(0,0,0,0.06)',
    marginTop: 8,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 3,
  },
  stepContainer: {
    marginBottom: 32,
  },
  iconCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(108, 99, 255, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    alignSelf: 'center',
    marginBottom: 20,
  },
  title: {
    marginBottom: 10,
  },
  description: {
    paddingHorizontal: 16,
    lineHeight: 22,
    marginBottom: 24,
  },
  stepSubtitle: {
    marginTop: 6,
    marginBottom: 20,
  },
  infoCard: {
    padding: 16,
    gap: 12,
  },
  bulletRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  bulletText: {
    marginLeft: 10,
    flex: 1,
  },
  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  choiceCard: {
    width: '48%',
    padding: 16,
    borderRadius: 16,
    borderWidth: 1.5,
    alignItems: 'center',
    justifyContent: 'center',
  },
  listContainer: {
    gap: 10,
  },
  goalCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 14,
    borderWidth: 1.5,
  },
  goalLabel: {
    marginLeft: 12,
    flex: 1,
  },
  sectionLabel: {
    marginBottom: 10,
  },
  segmentRow: {
    flexDirection: 'row',
    gap: 8,
  },
  segmentBtn: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.7)',
  },
  summaryCard: {
    padding: 20,
    gap: 14,
  },
  summaryItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  summaryDivider: {
    height: 1,
    backgroundColor: 'rgba(0,0,0,0.06)',
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
    alignItems: 'center',
  },
  backButton: {
    flex: 1,
  },
  continueButton: {
    flex: 2,
  },
});

