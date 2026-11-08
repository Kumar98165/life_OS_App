import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Switch,
  ActivityIndicator,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import {
  useVoiceSettings,
  useUpdateVoiceSettings,
  useVoiceList,
} from '../../hooks/useVoice';

interface VoiceSettingsScreenProps {
  navigation: any;
}

export function VoiceSettingsScreen({ navigation }: VoiceSettingsScreenProps) {
  const { theme } = useTheme();
  const insets = useSafeAreaInsets();

  const { data: settings, isLoading } = useVoiceSettings();
  const { data: voices } = useVoiceList();
  const updateSettingsMutation = useUpdateVoiceSettings();

  const [savingField, setSavingField] = useState<string | null>(null);

  if (isLoading || !settings) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  const handleUpdate = (updates: any, fieldName: string) => {
    setSavingField(fieldName);
    updateSettingsMutation.mutate(updates, {
      onSettled: () => setSavingField(null),
    });
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
        <Text style={[styles.headerTitle, { color: theme.colors.textPrimary }]}>Voice & Speech Settings</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Language Selection */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>Primary Language</Text>
          <Text style={[styles.sectionSubtitle, { color: theme.colors.textSecondary }]}>
            Choose your preferred speech recognition and synthesis language mode.
          </Text>

          <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            {(['en', 'hi', 'hinglish'] as const).map((lang) => (
              <TouchableOpacity
                key={lang}
                onPress={() => handleUpdate({ language: lang }, 'language')}
                style={[
                  styles.optionRow,
                  { borderBottomColor: theme.colors.border },
                  lang === 'hinglish' && { borderBottomWidth: 0 },
                ]}
              >
                <View style={styles.optionInfo}>
                  <Text style={[styles.optionTitle, { color: theme.colors.textPrimary }]}>
                    {lang === 'en' ? 'English (Global)' : lang === 'hi' ? 'Hindi (हिंदी)' : 'Hinglish (Code-Switching)'}
                  </Text>
                  <Text style={[styles.optionDesc, { color: theme.colors.textSecondary }]}>
                    {lang === 'en'
                      ? 'Optimal for English-only voice interaction'
                      : lang === 'hi'
                      ? 'Full Hindi speech processing & vernacular replies'
                      : 'Mixed Hindi-English voice recognition support'}
                  </Text>
                </View>
                {settings.language === lang && (
                  <Ionicons name="checkmark-circle" size={22} color={theme.colors.primary} />
                )}
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Speech Rate (Speed) */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>Speaking Rate</Text>
          <Text style={[styles.sectionSubtitle, { color: theme.colors.textSecondary }]}>
            Current speed: {settings.speech_rate}x
          </Text>

          <View style={[styles.card, styles.speedRow, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            {[0.75, 1.0, 1.25, 1.5].map((rate) => (
              <TouchableOpacity
                key={rate}
                onPress={() => handleUpdate({ speech_rate: rate }, 'speech_rate')}
                style={[
                  styles.speedChip,
                  {
                    backgroundColor:
                      settings.speech_rate === rate ? theme.colors.primary : `${theme.colors.primary}15`,
                  },
                ]}
              >
                <Text
                  style={[
                    styles.speedChipText,
                    { color: settings.speech_rate === rate ? '#FFFFFF' : theme.colors.primary },
                  ]}
                >
                  {rate}x
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Toggles */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>Playback & Security</Text>

          <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            {/* Auto Play Response */}
            <View style={[styles.switchRow, { borderBottomColor: theme.colors.border, borderBottomWidth: StyleSheet.hairlineWidth }]}>
              <View style={styles.switchTextContainer}>
                <Text style={[styles.optionTitle, { color: theme.colors.textPrimary }]}>Auto-Play Spoken Response</Text>
                <Text style={[styles.optionDesc, { color: theme.colors.textSecondary }]}>
                  Automatically speak replies through device speaker
                </Text>
              </View>
              <Switch
                value={settings.auto_play_response}
                onValueChange={(val) => handleUpdate({ auto_play_response: val }, 'auto_play')}
                trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
              />
            </View>

            {/* Zero Audio Retention (Audio Privacy) */}
            <View style={[styles.switchRow, { borderBottomColor: theme.colors.border, borderBottomWidth: StyleSheet.hairlineWidth }]}>
              <View style={styles.switchTextContainer}>
                <View style={styles.privacyBadgeRow}>
                  <Text style={[styles.optionTitle, { color: theme.colors.textPrimary }]}>Zero Audio Retention</Text>
                  <View style={[styles.privacyPill, { backgroundColor: '#10B98120' }]}>
                    <Text style={styles.privacyPillText}>Strict Privacy</Text>
                  </View>
                </View>
                <Text style={[styles.optionDesc, { color: theme.colors.textSecondary }]}>
                  Delete temporary audio files immediately after processing
                </Text>
              </View>
              <Switch
                value={settings.audio_privacy_enabled}
                onValueChange={(val) => handleUpdate({ audio_privacy_enabled: val }, 'audio_privacy')}
                trackColor={{ false: theme.colors.border, true: '#10B981' }}
              />
            </View>

            {/* Confirm Actions via Voice */}
            <View style={styles.switchRow}>
              <View style={styles.switchTextContainer}>
                <Text style={[styles.optionTitle, { color: theme.colors.textPrimary }]}>Voice Action Confirmation</Text>
                <Text style={[styles.optionDesc, { color: theme.colors.textSecondary }]}>
                  Require explicit vocal confirmation before executing medium/high risk tasks
                </Text>
              </View>
              <Switch
                value={settings.confirm_actions_via_voice}
                onValueChange={(val) => handleUpdate({ confirm_actions_via_voice: val }, 'confirm_voice')}
                trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
              />
            </View>
          </View>
        </View>

        {/* Architecture Note */}
        <View style={[styles.infoBox, { backgroundColor: `${theme.colors.primary}10`, borderColor: `${theme.colors.primary}30` }]}>
          <Ionicons name="information-circle-outline" size={20} color={theme.colors.primary} />
          <Text style={[styles.infoText, { color: theme.colors.textSecondary }]}>
            Speech processing executes entirely through your local machine via Whisper and native speech synthesizers.
            Zero audio samples are sent to cloud APIs or stored permanently.
          </Text>
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
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
  },
  content: {
    padding: 16,
    paddingBottom: 40,
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
  optionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  optionInfo: {
    flex: 1,
    marginRight: 10,
  },
  optionTitle: {
    fontSize: 15,
    fontWeight: '600',
    marginBottom: 2,
  },
  optionDesc: {
    fontSize: 12,
    lineHeight: 16,
  },
  speedRow: {
    flexDirection: 'row',
    padding: 12,
    justifyContent: 'space-around',
  },
  speedChip: {
    paddingHorizontal: 18,
    paddingVertical: 10,
    borderRadius: 20,
    minWidth: 64,
    alignItems: 'center',
  },
  speedChipText: {
    fontSize: 14,
    fontWeight: '700',
  },
  switchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
  },
  switchTextContainer: {
    flex: 1,
    marginRight: 12,
  },
  privacyBadgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 2,
  },
  privacyPill: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
  },
  privacyPillText: {
    color: '#10B981',
    fontSize: 10,
    fontWeight: '700',
  },
  infoBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 10,
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
  },
  infoText: {
    flex: 1,
    fontSize: 12,
    lineHeight: 18,
  },
});
