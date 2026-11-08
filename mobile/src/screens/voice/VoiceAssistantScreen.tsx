import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  TextInput,
  ActivityIndicator,
  Animated,
  Platform,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Audio } from 'expo-av';
import { useTheme } from '../../theme';
import {
  useVoiceAssistantTurn,
  useVoiceSettings,
} from '../../hooks/useVoice';
import { VoiceConversationTurn } from '../../types/voice';

interface VoiceAssistantScreenProps {
  navigation: any;
}

export function VoiceAssistantScreen({ navigation }: VoiceAssistantScreenProps) {
  const { theme } = useTheme();
  const insets = useSafeAreaInsets();

  const { data: voiceSettings } = useVoiceSettings();
  const assistantTurnMutation = useVoiceAssistantTurn();

  const [conversation, setConversation] = useState<VoiceConversationTurn[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [isRecording, setIsRecording] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [textInputFallback, setTextInputFallback] = useState('');
  const [statusMessage, setStatusMessage] = useState('Tap mic to start speaking');

  // Animation values
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const waveAnim1 = useRef(new Animated.Value(0.4)).current;
  const waveAnim2 = useRef(new Animated.Value(0.8)).current;
  const waveAnim3 = useRef(new Animated.Value(0.5)).current;

  // Audio recording ref
  const recordingRef = useRef<Audio.Recording | null>(null);
  const soundRef = useRef<Audio.Sound | null>(null);

  useEffect(() => {
    return () => {
      // Unload audio on unmount
      if (soundRef.current) {
        soundRef.current.unloadAsync().catch(() => {});
      }
      if (recordingRef.current) {
        recordingRef.current.stopAndUnloadAsync().catch(() => {});
      }
    };
  }, []);

  // Pulsing animation when recording
  useEffect(() => {
    let loop: Animated.CompositeAnimation | null = null;
    if (isRecording) {
      loop = Animated.loop(
        Animated.parallel([
          Animated.sequence([
            Animated.timing(pulseAnim, {
              toValue: 1.25,
              duration: 700,
              useNativeDriver: true,
            }),
            Animated.timing(pulseAnim, {
              toValue: 1.0,
              duration: 700,
              useNativeDriver: true,
            }),
          ]),
          Animated.sequence([
            Animated.timing(waveAnim1, {
              toValue: 1.0,
              duration: 350,
              useNativeDriver: true,
            }),
            Animated.timing(waveAnim1, {
              toValue: 0.3,
              duration: 350,
              useNativeDriver: true,
            }),
          ]),
          Animated.sequence([
            Animated.timing(waveAnim2, {
              toValue: 0.3,
              duration: 400,
              useNativeDriver: true,
            }),
            Animated.timing(waveAnim2, {
              toValue: 1.0,
              duration: 400,
              useNativeDriver: true,
            }),
          ]),
          Animated.sequence([
            Animated.timing(waveAnim3, {
              toValue: 0.9,
              duration: 500,
              useNativeDriver: true,
            }),
            Animated.timing(waveAnim3, {
              toValue: 0.4,
              duration: 500,
              useNativeDriver: true,
            }),
          ]),
        ])
      );
      loop.start();
    } else {
      pulseAnim.setValue(1);
      waveAnim1.setValue(0.4);
      waveAnim2.setValue(0.8);
      waveAnim3.setValue(0.5);
    }
    return () => {
      if (loop) loop.stop();
    };
  }, [isRecording]);

  const startRecording = async () => {
    try {
      const perm = await Audio.requestPermissionsAsync();
      if (!perm.granted) {
        setStatusMessage('Microphone permission denied.');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      recordingRef.current = recording;
      setIsRecording(true);
      setStatusMessage('Listening... (Tap to finish)');
    } catch (err: any) {
      setStatusMessage(`Microphone error: ${err.message || 'Unable to record'}`);
      setIsRecording(false);
    }
  };

  const stopRecordingAndSend = async () => {
    if (!recordingRef.current) {
      setIsRecording(false);
      return;
    }

    try {
      setIsRecording(false);
      setStatusMessage('Processing your voice offline...');

      await recordingRef.current.stopAndUnloadAsync();
      const uri = recordingRef.current.getURI();
      recordingRef.current = null;

      if (!uri) {
        setStatusMessage('No audio recorded.');
        return;
      }

      // Prepare multipart form data
      const formData = new FormData();
      formData.append('audio', {
        uri,
        name: 'voice.wav',
        type: 'audio/wav',
      } as any);

      if (conversationId) {
        formData.append('conversation_id', conversationId);
      }
      formData.append('return_audio', voiceSettings?.auto_play_response !== false ? 'true' : 'false');

      executeAssistantTurn(formData);
    } catch (err: any) {
      setStatusMessage(`Recording error: ${err.message || 'Failed'}`);
    }
  };

  const sendTextTurn = () => {
    if (!textInputFallback.trim()) return;
    const text = textInputFallback.trim();
    setTextInputFallback('');
    setStatusMessage('Consulting LifeOS...');

    executeAssistantTurn({
      text_input: text,
      conversation_id: conversationId,
      return_audio: voiceSettings?.auto_play_response !== false,
    });
  };

  const executeAssistantTurn = (payload: any) => {
    assistantTurnMutation.mutate(payload, {
      onSuccess: async (data) => {
        if (data.conversation_id) {
          setConversationId(data.conversation_id);
        }

        const newTurn: VoiceConversationTurn = {
          id: Date.now().toString(),
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          user_transcript: data.transcript,
          assistant_reply: data.response_text,
          detected_language: data.detected_language,
          action_proposals: data.action_proposals,
          audio_base64: data.audio_base64,
        };

        setConversation((prev) => [...prev, newTurn]);
        setStatusMessage('Tap mic to start speaking');

        // Auto-play synthesized voice response if available
        if (data.audio_base64 && voiceSettings?.auto_play_response !== false) {
          playAudioBase64(data.audio_base64);
        }
      },
      onError: (error: any) => {
        setStatusMessage(`Error: ${error.response?.data?.message || error.message || 'Request failed'}`);
      },
    });
  };

  const playAudioBase64 = async (b64Data: string) => {
    try {
      if (soundRef.current) {
        await soundRef.current.unloadAsync();
      }

      setIsPlayingAudio(true);
      const uri = `data:audio/wav;base64,${b64Data}`;
      const { sound } = await Audio.Sound.createAsync(
        { uri },
        { shouldPlay: true }
      );
      soundRef.current = sound;

      sound.setOnPlaybackStatusUpdate((status) => {
        if (!status.isLoaded || status.didJustFinish) {
          setIsPlayingAudio(false);
        }
      });
    } catch (err) {
      setIsPlayingAudio(false);
    }
  };

  const stopAudioPlayback = async () => {
    if (soundRef.current) {
      await soundRef.current.stopAsync();
      setIsPlayingAudio(false);
    }
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
          <Text style={[styles.headerTitle, { color: theme.colors.textPrimary }]}>Voice Assistant</Text>
          <Text style={[styles.headerSubtitle, { color: theme.colors.textSecondary }]}>
            Local Whisper + TTS • Private
          </Text>
        </View>
        <TouchableOpacity
          onPress={() => navigation.navigate('VoiceSettings')}
          style={styles.settingsButton}
        >
          <Ionicons name="settings-outline" size={22} color={theme.colors.textPrimary} />
        </TouchableOpacity>
      </View>

      {/* Conversation Scroll */}
      <ScrollView
        style={styles.dialogueList}
        contentContainerStyle={styles.dialogueListContent}
        keyboardShouldPersistTaps="handled"
      >
        {conversation.length === 0 ? (
          <View style={styles.emptyState}>
            <View style={[styles.iconCircle, { backgroundColor: `${theme.colors.primary}15` }]}>
              <Ionicons name="mic-outline" size={48} color={theme.colors.primary} />
            </View>
            <Text style={[styles.emptyTitle, { color: theme.colors.textPrimary }]}>How can I help you today?</Text>
            <Text style={[styles.emptySubtitle, { color: theme.colors.textSecondary }]}>
              Try saying "Plan my afternoon", "Show pending tasks", or "Create a reminder for 6 PM".
            </Text>
            <View style={styles.badgeRow}>
              <View style={[styles.badge, { backgroundColor: `${theme.colors.primary}20` }]}>
                <Ionicons name="shield-checkmark-outline" size={14} color={theme.colors.primary} />
                <Text style={[styles.badgeText, { color: theme.colors.primary }]}>Zero Cloud Upload</Text>
              </View>
              <View style={[styles.badge, { backgroundColor: `${theme.colors.primary}20` }]}>
                <Ionicons name="language-outline" size={14} color={theme.colors.primary} />
                <Text style={[styles.badgeText, { color: theme.colors.primary }]}>English & Hindi</Text>
              </View>
            </View>
          </View>
        ) : (
          conversation.map((turn) => (
            <View key={turn.id} style={styles.turnCard}>
              {/* User Voice Bubble */}
              <View style={[styles.userBubble, { backgroundColor: theme.colors.primary }]}>
                <View style={styles.bubbleHeader}>
                  <Ionicons name="person-circle-outline" size={16} color="#FFFFFF" />
                  <Text style={styles.userBubbleName}>You</Text>
                  <Text style={styles.bubbleTime}>{turn.timestamp}</Text>
                </View>
                <Text style={styles.userBubbleText}>{turn.user_transcript}</Text>
              </View>

              {/* Assistant Speech Bubble */}
              <View style={[styles.assistantBubble, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
                <View style={styles.bubbleHeader}>
                  <Ionicons name="sparkles" size={16} color={theme.colors.primary} />
                  <Text style={[styles.assistantBubbleName, { color: theme.colors.primary }]}>LifeOS</Text>
                  {turn.audio_base64 && (
                    <TouchableOpacity
                      onPress={() => playAudioBase64(turn.audio_base64!)}
                      style={styles.replayButton}
                    >
                      <Ionicons name="volume-medium-outline" size={18} color={theme.colors.primary} />
                      <Text style={[styles.replayText, { color: theme.colors.primary }]}>Replay</Text>
                    </TouchableOpacity>
                  )}
                </View>
                <Text style={[styles.assistantBubbleText, { color: theme.colors.textPrimary }]}>
                  {turn.assistant_reply}
                </Text>

                {/* Action Proposals requiring confirmation */}
                {turn.action_proposals && turn.action_proposals.length > 0 && (
                  <View style={[styles.actionBanner, { backgroundColor: `${theme.colors.primary}10`, borderColor: theme.colors.primary }]}>
                    <View style={styles.actionHeader}>
                      <Ionicons name="alert-circle-outline" size={18} color={theme.colors.primary} />
                      <Text style={[styles.actionTitle, { color: theme.colors.primary }]}>Action Proposal</Text>
                    </View>
                    <Text style={[styles.actionSummary, { color: theme.colors.textPrimary }]}>
                      {turn.action_proposals[0].summary}
                    </Text>
                  </View>
                )}
              </View>
            </View>
          ))
        )}
      </ScrollView>

      {/* Voice Control & Status Panel */}
      <View style={[styles.bottomControlPanel, { backgroundColor: theme.colors.surface, borderTopColor: theme.colors.border }]}>
        {/* Status text */}
        <Text style={[styles.statusText, { color: theme.colors.textSecondary }]}>{statusMessage}</Text>

        {/* Audio playback indicator */}
        {isPlayingAudio && (
          <View style={styles.playbackBar}>
            <Ionicons name="volume-high" size={18} color={theme.colors.primary} />
            <Text style={[styles.playbackText, { color: theme.colors.primary }]}>Playing audio response...</Text>
            <TouchableOpacity onPress={stopAudioPlayback} style={styles.stopButton}>
              <Ionicons name="stop-circle" size={20} color={theme.colors.primary} />
            </TouchableOpacity>
          </View>
        )}

        {/* Mic Button & Waveform Container */}
        <View style={styles.micSection}>
          {isRecording && (
            <View style={styles.waveformContainer}>
              <Animated.View style={[styles.waveBar, { height: 35, transform: [{ scaleY: waveAnim1 }], backgroundColor: theme.colors.primary }]} />
              <Animated.View style={[styles.waveBar, { height: 50, transform: [{ scaleY: waveAnim2 }], backgroundColor: theme.colors.primary }]} />
              <Animated.View style={[styles.waveBar, { height: 40, transform: [{ scaleY: waveAnim3 }], backgroundColor: theme.colors.primary }]} />
              <Animated.View style={[styles.waveBar, { height: 55, transform: [{ scaleY: waveAnim1 }], backgroundColor: theme.colors.primary }]} />
              <Animated.View style={[styles.waveBar, { height: 30, transform: [{ scaleY: waveAnim2 }], backgroundColor: theme.colors.primary }]} />
            </View>
          )}

          <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
            <TouchableOpacity
              onPress={isRecording ? stopRecordingAndSend : startRecording}
              disabled={assistantTurnMutation.isPending}
              style={[
                styles.micButton,
                {
                  backgroundColor: isRecording ? '#EF4444' : theme.colors.primary,
                  shadowColor: isRecording ? '#EF4444' : theme.colors.primary,
                },
              ]}
              accessibilityRole="button"
              accessibilityLabel={isRecording ? 'Stop Recording' : 'Start Recording'}
            >
              {assistantTurnMutation.isPending ? (
                <ActivityIndicator color="#FFFFFF" size="large" />
              ) : (
                <Ionicons
                  name={isRecording ? 'stop' : 'mic'}
                  size={36}
                  color="#FFFFFF"
                />
              )}
            </TouchableOpacity>
          </Animated.View>
        </View>

        {/* Text Fallback Input Bar */}
        <View style={[styles.textInputRow, { backgroundColor: theme.colors.background, borderColor: theme.colors.border }]}>
          <TextInput
            style={[styles.textInput, { color: theme.colors.textPrimary }]}
            placeholder="Or type voice command..."
            placeholderTextColor={theme.colors.textSecondary}
            value={textInputFallback}
            onChangeText={setTextInputFallback}
            onSubmitEditing={sendTextTurn}
            returnKeyType="send"
          />
          {textInputFallback.trim().length > 0 && (
            <TouchableOpacity onPress={sendTextTurn} style={styles.sendButton}>
              <Ionicons name="arrow-up-circle" size={32} color={theme.colors.primary} />
            </TouchableOpacity>
          )}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
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
  settingsButton: {
    padding: 6,
  },
  dialogueList: {
    flex: 1,
  },
  dialogueListContent: {
    padding: 16,
    paddingBottom: 24,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 48,
    paddingHorizontal: 24,
  },
  iconCircle: {
    width: 96,
    height: 96,
    borderRadius: 48,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 14,
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 24,
  },
  badgeRow: {
    flexDirection: 'row',
    gap: 8,
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 16,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  turnCard: {
    marginBottom: 20,
  },
  userBubble: {
    alignSelf: 'flex-end',
    maxWidth: '85%',
    padding: 14,
    borderRadius: 18,
    borderBottomRightRadius: 4,
    marginBottom: 10,
  },
  assistantBubble: {
    alignSelf: 'flex-start',
    maxWidth: '90%',
    padding: 14,
    borderRadius: 18,
    borderBottomLeftRadius: 4,
    borderWidth: StyleSheet.hairlineWidth,
  },
  bubbleHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 6,
  },
  userBubbleName: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  bubbleTime: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: 10,
    marginLeft: 'auto',
  },
  userBubbleText: {
    color: '#FFFFFF',
    fontSize: 15,
    lineHeight: 21,
  },
  assistantBubbleName: {
    fontSize: 12,
    fontWeight: '700',
  },
  assistantBubbleText: {
    fontSize: 15,
    lineHeight: 22,
  },
  replayButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginLeft: 'auto',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  replayText: {
    fontSize: 12,
    fontWeight: '600',
  },
  actionBanner: {
    marginTop: 12,
    padding: 10,
    borderRadius: 10,
    borderWidth: 1,
  },
  actionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 4,
  },
  actionTitle: {
    fontSize: 13,
    fontWeight: '700',
  },
  actionSummary: {
    fontSize: 13,
    lineHeight: 18,
  },
  bottomControlPanel: {
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 24,
    borderTopWidth: StyleSheet.hairlineWidth,
    alignItems: 'center',
  },
  statusText: {
    fontSize: 13,
    marginBottom: 8,
  },
  playbackBar: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 10,
  },
  playbackText: {
    fontSize: 13,
    fontWeight: '600',
  },
  stopButton: {
    padding: 2,
  },
  micSection: {
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 10,
    height: 90,
  },
  waveformContainer: {
    position: 'absolute',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  waveBar: {
    width: 4,
    borderRadius: 2,
  },
  micButton: {
    width: 76,
    height: 76,
    borderRadius: 38,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 8,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.35,
    shadowRadius: 8,
  },
  textInputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
    borderRadius: 24,
    borderWidth: StyleSheet.hairlineWidth,
    paddingHorizontal: 14,
    paddingVertical: 4,
    marginTop: 8,
  },
  textInput: {
    flex: 1,
    height: 40,
    fontSize: 14,
  },
  sendButton: {
    padding: 2,
  },
});
