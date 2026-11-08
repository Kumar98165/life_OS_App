import React, { useState } from 'react';
import { View, StyleSheet, TouchableOpacity, KeyboardAvoidingView, Platform } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { AuthNavigationProp } from '../../navigation/types';
import { loginSchema, LoginSchemaType } from '../../schemas/auth';
import { useAuthStore } from '../../store';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassCard,
  GlassInput,
  PasswordInput,
  PrimaryButton,
  Heading,
  BodyText,
  Caption,
  AlertDialog,
  Toast,
} from '../../components';

export const LoginScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<AuthNavigationProp>();
  const { login, isLoading } = useAuthStore();

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showForgotDialog, setShowForgotDialog] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginSchemaType>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginSchemaType) => {
    setErrorMessage(null);
    try {
      await login(data);
    } catch (err: any) {
      setErrorMessage(err.message || 'Login failed. Please check your credentials.');
    }
  };

  return (
    <SafeAreaContainer>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.keyboardContainer}
      >
        <ScrollContainer contentContainerStyle={styles.scrollContent}>
          {/* Back Button */}
          <TouchableOpacity
            style={[styles.backBtn, { borderColor: theme.colors.glassBorder }]}
            onPress={() => navigation.goBack()}
            accessibilityRole="button"
            accessibilityLabel="Go back"
          >
            <Ionicons name="chevron-back" size={20} color={theme.colors.textPrimary} />
          </TouchableOpacity>

          {/* Header */}
          <View style={styles.header}>
            <Heading level={1}>Welcome Back</Heading>
            <BodyText color="secondary" style={styles.subtitle}>
              Sign in to access your LifeOS dashboard and personal AI.
            </BodyText>
          </View>

          {/* Form Card */}
          <GlassCard elevation="floating" style={styles.formCard}>
            {/* Email Field */}
            <Controller
              control={control}
              name="email"
              render={({ field: { onChange, onBlur, value } }) => (
                <GlassInput
                  label="Email Address"
                  required
                  placeholder="alex@example.com"
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoCorrect={false}
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                  error={errors.email?.message}
                  leftIcon={
                    <Ionicons name="mail-outline" size={18} color={theme.colors.textMuted} />
                  }
                />
              )}
            />

            {/* Password Field */}
            <Controller
              control={control}
              name="password"
              render={({ field: { onChange, onBlur, value } }) => (
                <PasswordInput
                  label="Password"
                  required
                  placeholder="Enter your password"
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                  error={errors.password?.message}
                  leftIcon={
                    <Ionicons
                      name="lock-closed-outline"
                      size={18}
                      color={theme.colors.textMuted}
                    />
                  }
                />
              )}
            />

            {/* Forgot Password Link */}
            <TouchableOpacity
              onPress={() => setShowForgotDialog(true)}
              style={styles.forgotBtn}
              accessibilityRole="button"
            >
              <Caption weight="600" style={{ color: theme.colors.primary }}>
                Forgot Password?
              </Caption>
            </TouchableOpacity>

            {/* Submit Button */}
            <PrimaryButton
              label="Sign In"
              loading={isLoading}
              onPress={() => {
                handleSubmit(onSubmit)();
              }}
              style={styles.submitBtn}
            />
          </GlassCard>

          {/* Switch to Register */}
          <View style={styles.footerRow}>
            <BodyText color="secondary">Don't have an account?</BodyText>
            <TouchableOpacity
              onPress={() => navigation.navigate('Register')}
              accessibilityRole="button"
            >
              <BodyText weight="600" style={{ color: theme.colors.primary, marginLeft: 6 }}>
                Create Account
              </BodyText>
            </TouchableOpacity>
          </View>
        </ScrollContainer>
      </KeyboardAvoidingView>

      {/* Forgot Password Explanation Dialog */}
      <AlertDialog
        visible={showForgotDialog}
        title="Password Reset Notice"
        message="Self-service email password recovery is not yet configured on this backend instance. Please contact your system administrator or re-create your account if running in development mode."
        onDismiss={() => setShowForgotDialog(false)}
        buttonLabel="Understood"
      />

      {/* Error Toast */}
      <Toast
        visible={!!errorMessage}
        message={errorMessage || ''}
        type="error"
      />
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  keyboardContainer: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 40,
    paddingTop: 8,
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.7)',
  },
  header: {
    marginBottom: 28,
  },
  subtitle: {
    marginTop: 6,
    lineHeight: 20,
  },
  formCard: {
    padding: 20,
    marginBottom: 24,
  },
  forgotBtn: {
    alignSelf: 'flex-end',
    marginTop: 4,
    marginBottom: 20,
  },
  submitBtn: {
    marginTop: 8,
  },
  footerRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 8,
  },
});
