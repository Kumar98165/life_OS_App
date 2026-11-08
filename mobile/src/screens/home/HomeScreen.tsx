import React, { useState } from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { useAuthStore } from '../../store';
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
  ConfirmationModal,
} from '../../components';

export const HomeScreen: React.FC = () => {
  const { theme, isDark, toggleTheme } = useTheme();
  const { user, logout, isLoading, onboardingPreferences } = useAuthStore();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const handleLogout = async () => {
    setShowLogoutConfirm(false);
    await logout();
  };

  return (
    <SafeAreaContainer>
      <ScrollContainer contentContainerStyle={styles.scrollContent}>
        {/* Top App Bar */}
        <View style={styles.topBar}>
          <View>
            <Caption color="secondary">WELCOME BACK</Caption>
            <Heading level={2} style={styles.userName}>
              {user?.full_name || 'LifeOS User'}
            </Heading>
          </View>
          <View style={styles.topActions}>
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
            <IconButton
              icon={<Ionicons name="log-out-outline" size={20} color={theme.colors.error} />}
              onPress={() => setShowLogoutConfirm(true)}
              variant="glass"
              size={40}
              style={{ marginLeft: 8 }}
            />
          </View>
        </View>

        {/* Profile Card */}
        <GlassCard elevation="floating" style={styles.profileCard}>
          <View style={styles.avatarRow}>
            <View
              style={[
                styles.avatarCircle,
                {
                  backgroundColor: `${theme.colors.primary}20`,
                  borderColor: theme.colors.primary,
                },
              ]}
            >
              <Ionicons name="person" size={28} color={theme.colors.primary} />
            </View>
            <View style={styles.profileDetails}>
              <BodyText weight="600">{user?.full_name}</BodyText>
              <Caption color="secondary">{user?.email}</Caption>
              <View style={styles.statusPill}>
                <View style={[styles.activeDot, { backgroundColor: theme.colors.success }]} />
                <Caption weight="600" style={{ color: theme.colors.success, fontSize: 11 }}>
                  Authenticated & Active
                </Caption>
              </View>
            </View>
          </View>
        </GlassCard>

        {/* Security & Token Info Card */}
        <GlassCard elevation="subtle" style={styles.sectionCard}>
          <View style={styles.cardHeader}>
            <Ionicons name="shield-checkmark" size={20} color={theme.colors.primary} />
            <BodyText weight="600" style={{ marginLeft: 8 }}>
              Security Architecture
            </BodyText>
          </View>

          <View style={styles.securityItem}>
            <Caption color="secondary">Access Token Storage</Caption>
            <BodyText variant="small" weight="500">In-Memory Store (Secure)</BodyText>
          </View>

          <View style={styles.securityDivider} />

          <View style={styles.securityItem}>
            <Caption color="secondary">Refresh Token Storage</Caption>
            <BodyText variant="small" weight="500">Expo SecureStore Keychain</BodyText>
          </View>

          <View style={styles.securityDivider} />

          <View style={styles.securityItem}>
            <Caption color="secondary">Refresh Rotation (RTR)</Caption>
            <BodyText variant="small" weight="500">Single-Flight Auto-Rotation</BodyText>
          </View>
        </GlassCard>

        {/* Onboarding Summary if preferences exist */}
        {onboardingPreferences && (
          <GlassCard elevation="subtle" style={styles.sectionCard}>
            <View style={styles.cardHeader}>
              <Ionicons name="options-outline" size={20} color={theme.colors.primary} />
              <BodyText weight="600" style={{ marginLeft: 8 }}>
                Personal Preferences
              </BodyText>
            </View>

            <View style={styles.securityItem}>
              <Caption color="secondary">Focus Areas Configured</Caption>
              <BodyText variant="small" weight="500">
                {onboardingPreferences.focusAreas.join(', ')}
              </BodyText>
            </View>

            <View style={styles.securityDivider} />

            <View style={styles.securityItem}>
              <Caption color="secondary">AI Interaction Style</Caption>
              <BodyText variant="small" weight="500" style={{ textTransform: 'capitalize' }}>
                {onboardingPreferences.aiInteractionStyle}
              </BodyText>
            </View>
          </GlassCard>
        )}

        {/* Logout Button */}
        <SecondaryButton
          label="Sign Out"
          loading={isLoading}
          onPress={() => setShowLogoutConfirm(true)}
          style={styles.logoutBtn}
          icon={<Ionicons name="log-out-outline" size={18} color={theme.colors.error} />}
        />
      </ScrollContainer>

      {/* Confirmation Dialog for Logout */}
      <ConfirmationModal
        visible={showLogoutConfirm}
        title="Sign Out"
        message="Are you sure you want to end your active LifeOS session? Your refresh token will be revoked."
        confirmLabel="Sign Out"
        cancelLabel="Stay Logged In"
        isDestructive
        onConfirm={handleLogout}
        onCancel={() => setShowLogoutConfirm(false)}
      />
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 40,
    paddingTop: 8,
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  userName: {
    marginTop: 2,
  },
  topActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  profileCard: {
    padding: 18,
    marginBottom: 20,
  },
  avatarRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatarCircle: {
    width: 56,
    height: 56,
    borderRadius: 28,
    borderWidth: 1.5,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  profileDetails: {
    flex: 1,
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 6,
  },
  activeDot: {
    width: 7,
    height: 7,
    borderRadius: 3.5,
    marginRight: 6,
  },
  sectionCard: {
    padding: 18,
    marginBottom: 20,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
  },
  securityItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4,
  },
  securityDivider: {
    height: 1,
    backgroundColor: 'rgba(0,0,0,0.05)',
    marginVertical: 8,
  },
  logoutBtn: {
    marginTop: 10,
  },
});
