import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Switch,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import {
  usePersonalization,
  useUpdatePersonalization,
  useResetPreferences,
} from '../../hooks/usePersonalization';

interface PersonalizationSettingsScreenProps {
  navigation: any;
}

export function PersonalizationSettingsScreen({ navigation }: PersonalizationSettingsScreenProps) {
  const { theme } = useTheme();
  const insets = useSafeAreaInsets();

  const { data, isLoading } = usePersonalization();
  const updateMutation = useUpdatePersonalization();
  const resetMutation = useResetPreferences();

  const [preferredName, setPreferredName] = useState('');
  const [hasInitialized, setHasInitialized] = useState(false);

  const p = data?.personalization;

  if (p && !hasInitialized) {
    setPreferredName(p.preferred_name || '');
    setHasInitialized(true);
  }

  if (isLoading || !p) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  const handleUpdate = (fieldUpdates: any) => {
    updateMutation.mutate(fieldUpdates);
  };

  const handleSaveName = () => {
    updateMutation.mutate(
      { preferred_name: preferredName.trim() || null },
      {
        onSuccess: () => {
          Alert.alert('Saved', 'Preferred name updated.');
        },
      }
    );
  };

  const handleResetTarget = (target: 'all' | 'identity' | 'ai_style') => {
    Alert.alert(
      'Reset Preferences',
      `Restore default settings for ${target}? Your tasks, habits, and confirmed AI memories will remain intact.`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          style: 'destructive',
          onPress: () => {
            resetMutation.mutate(target, {
              onSuccess: () => setHasInitialized(false),
            });
          },
        },
      ]
    );
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background, paddingTop: insets.top }]}>
      {/* Header */}
      <View style={[styles.header, { borderBottomColor: theme.colors.border }]}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          <Ionicons name="arrow-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <View style={styles.headerTitleContainer}>
          <Text style={[styles.headerTitle, { color: theme.colors.textPrimary }]}>Personalization Hub</Text>
          <Text style={[styles.headerSubtitle, { color: theme.colors.textSecondary }]}>
            Identity, productivity, AI styles, and layouts
          </Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Navigation Quick Links to Sub-Modules */}
        <View style={styles.quickLinksRow}>
          <TouchableOpacity
            onPress={() => navigation.navigate('DashboardCustomization')}
            style={[styles.quickLinkCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}
          >
            <Ionicons name="grid-outline" size={24} color={theme.colors.primary} />
            <Text style={[styles.quickLinkTitle, { color: theme.colors.textPrimary }]}>Dashboard Cards</Text>
            <Text style={[styles.quickLinkDesc, { color: theme.colors.textSecondary }]}>Order & visibility</Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => navigation.navigate('DailyRoutine')}
            style={[styles.quickLinkCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}
          >
            <Ionicons name="time-outline" size={24} color={theme.colors.primary} />
            <Text style={[styles.quickLinkTitle, { color: theme.colors.textPrimary }]}>Daily Rhythm</Text>
            <Text style={[styles.quickLinkDesc, { color: theme.colors.textSecondary }]}>Work & sleep hours</Text>
          </TouchableOpacity>
        </View>

        {/* 1. Identity & Name */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>Personal Profile & Identity</Text>
          <Text style={[styles.sectionSubtitle, { color: theme.colors.textSecondary }]}>
            How LifeOS addresses you across notifications and the AI Assistant.
          </Text>

          <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            <View style={styles.inputRow}>
              <View style={styles.inputFlex}>
                <Text style={[styles.fieldLabel, { color: theme.colors.textSecondary }]}>Preferred Display Name</Text>
                <TextInput
                  style={[styles.textInput, { color: theme.colors.textPrimary, borderColor: theme.colors.border }]}
                  value={preferredName}
                  onChangeText={setPreferredName}
                  placeholder="e.g. Alex"
                  placeholderTextColor={theme.colors.textSecondary}
                  maxLength={50}
                />
              </View>
              <TouchableOpacity
                onPress={handleSaveName}
                style={[styles.saveInlineBtn, { backgroundColor: theme.colors.primary }]}
              >
                <Text style={styles.saveInlineText}>Save</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        {/* 2. Productivity & Priority Strategy */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>Productivity & Task Strategy</Text>
          <Text style={[styles.sectionSubtitle, { color: theme.colors.textSecondary }]}>
            Determines how tasks and planner suggestions are prioritized for you.
          </Text>

          <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            <View style={styles.optionGroup}>
              <Text style={[styles.fieldLabel, { color: theme.colors.textSecondary }]}>Productivity Style</Text>
              <View style={styles.chipRow}>
                {(['structured', 'flexible', 'pomodoro', 'deep_work'] as const).map((style) => (
                  <TouchableOpacity
                    key={style}
                    onPress={() => handleUpdate({ productivity_style: style })}
                    style={[
                      styles.chip,
                      {
                        backgroundColor:
                          p.productivity_style === style ? theme.colors.primary : `${theme.colors.primary}15`,
                      },
                    ]}
                  >
                    <Text
                      style={[
                        styles.chipText,
                        { color: p.productivity_style === style ? '#FFFFFF' : theme.colors.primary },
                      ]}
                    >
                      {style.replace('_', ' ').toUpperCase()}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <View style={[styles.optionGroup, { borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: theme.colors.border }]}>
              <Text style={[styles.fieldLabel, { color: theme.colors.textSecondary }]}>Task Prioritization Strategy</Text>
              <View style={styles.chipRow}>
                {(['eisenhower', 'deadline_first', 'impact_first', 'quick_wins'] as const).map((strat) => (
                  <TouchableOpacity
                    key={strat}
                    onPress={() => handleUpdate({ task_priority_strategy: strat })}
                    style={[
                      styles.chip,
                      {
                        backgroundColor:
                          p.task_priority_strategy === strat ? theme.colors.primary : `${theme.colors.primary}15`,
                      },
                    ]}
                  >
                    <Text
                      style={[
                        styles.chipText,
                        { color: p.task_priority_strategy === strat ? '#FFFFFF' : theme.colors.primary },
                      ]}
                    >
                      {strat.replace('_', ' ').toUpperCase()}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </View>
        </View>

        {/* 3. AI Assistant Response Style */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>AI Assistant Response Style</Text>
          <Text style={[styles.sectionSubtitle, { color: theme.colors.textSecondary }]}>
            Configure the tone and verbosity of AI chat responses.
          </Text>

          <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            <View style={styles.optionGroup}>
              <Text style={[styles.fieldLabel, { color: theme.colors.textSecondary }]}>Tone of Voice</Text>
              <View style={styles.chipRow}>
                {(['concise', 'detailed', 'motivational', 'formal'] as const).map((tone) => (
                  <TouchableOpacity
                    key={tone}
                    onPress={() => handleUpdate({ ai_response_style: tone })}
                    style={[
                      styles.chip,
                      {
                        backgroundColor:
                          p.ai_response_style === tone ? theme.colors.primary : `${theme.colors.primary}15`,
                      },
                    ]}
                  >
                    <Text
                      style={[
                        styles.chipText,
                        { color: p.ai_response_style === tone ? '#FFFFFF' : theme.colors.primary },
                      ]}
                    >
                      {tone.toUpperCase()}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <View style={[styles.optionGroup, { borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: theme.colors.border }]}>
              <Text style={[styles.fieldLabel, { color: theme.colors.textSecondary }]}>Response Length</Text>
              <View style={styles.chipRow}>
                {(['short', 'medium', 'comprehensive'] as const).map((len) => (
                  <TouchableOpacity
                    key={len}
                    onPress={() => handleUpdate({ ai_response_length: len })}
                    style={[
                      styles.chip,
                      {
                        backgroundColor:
                          p.ai_response_length === len ? theme.colors.primary : `${theme.colors.primary}15`,
                      },
                    ]}
                  >
                    <Text
                      style={[
                        styles.chipText,
                        { color: p.ai_response_length === len ? '#FFFFFF' : theme.colors.primary },
                      ]}
                    >
                      {len.toUpperCase()}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </View>
        </View>

        {/* 4. Privacy & Personalization Controls */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>Privacy & Control</Text>

          <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            <View style={styles.switchRow}>
              <View style={styles.switchInfo}>
                <Text style={[styles.optionTitle, { color: theme.colors.textPrimary }]}>Personalization Engine</Text>
                <Text style={[styles.optionDesc, { color: theme.colors.textSecondary }]}>
                  Allow LifeOS to adapt suggestions using your configured preferences
                </Text>
              </View>
              <Switch
                value={p.personalization_enabled}
                onValueChange={(val) => handleUpdate({ personalization_enabled: val })}
                trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
              />
            </View>
          </View>
        </View>

        {/* Reset Actions */}
        <View style={styles.resetRow}>
          <TouchableOpacity
            onPress={() => handleResetTarget('identity')}
            style={[styles.resetButtonOutline, { borderColor: theme.colors.border }]}
          >
            <Text style={[styles.resetButtonText, { color: theme.colors.textSecondary }]}>Reset Identity</Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => handleResetTarget('ai_style')}
            style={[styles.resetButtonOutline, { borderColor: theme.colors.border }]}
          >
            <Text style={[styles.resetButtonText, { color: theme.colors.textSecondary }]}>Reset AI Style</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  backButton: {
    marginRight: 12,
  },
  headerTitleContainer: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
  },
  headerSubtitle: {
    fontSize: 12,
    marginTop: 2,
  },
  content: {
    padding: 16,
    paddingBottom: 40,
  },
  quickLinksRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  quickLinkCard: {
    flex: 1,
    padding: 16,
    borderRadius: 14,
    borderWidth: StyleSheet.hairlineWidth,
    alignItems: 'center',
  },
  quickLinkTitle: {
    fontSize: 14,
    fontWeight: '700',
    marginTop: 8,
    marginBottom: 2,
  },
  quickLinkDesc: {
    fontSize: 11,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 4,
  },
  sectionSubtitle: {
    fontSize: 13,
    marginBottom: 12,
  },
  card: {
    borderRadius: 14,
    borderWidth: StyleSheet.hairlineWidth,
    overflow: 'hidden',
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: 14,
    gap: 12,
  },
  inputFlex: {
    flex: 1,
  },
  fieldLabel: {
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 8,
  },
  textInput: {
    height: 44,
    borderRadius: 10,
    borderWidth: 1,
    paddingHorizontal: 12,
    fontSize: 15,
  },
  saveInlineBtn: {
    height: 44,
    paddingHorizontal: 16,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  saveInlineText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 14,
  },
  optionGroup: {
    padding: 14,
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 14,
  },
  chipText: {
    fontSize: 11,
    fontWeight: '700',
  },
  switchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
  },
  switchInfo: {
    flex: 1,
    marginRight: 12,
  },
  optionTitle: {
    fontSize: 15,
    fontWeight: '600',
    marginBottom: 2,
  },
  optionDesc: {
    fontSize: 12,
  },
  resetRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 8,
    marginBottom: 24,
  },
  resetButtonOutline: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 10,
    borderWidth: 1,
    alignItems: 'center',
  },
  resetButtonText: {
    fontSize: 13,
    fontWeight: '600',
  },
});
