import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { AuthNavigationProp } from '../../navigation/types';
import { registerSchema, RegisterSchemaType } from '../../schemas/auth';
import { useAuthStore } from '../../store';
import {
  SafeAreaContainer,
  ScrollContainer,
  GlassInput,
  PasswordInput,
  PrimaryButton,
  Heading,
  BodyText,
  Caption,
  Toast,
} from '../../components';

export const RegisterScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<AuthNavigationProp>();
  const { register, isLoading } = useAuthStore();

  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterSchemaType>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      full_name: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
  });

  const onSubmit = async (data: RegisterSchemaType) => {
    setErrorMessage(null);
    try {
      await register({
        full_name: data.full_name,
        email: data.email,
        password: data.password,
        confirmPassword: data.confirmPassword,
      });
    } catch (err: any) {
      if (err.status === 409 || err.message?.includes('already exists')) {
        setErrorMessage('An account with this email address already exists. Please log in.');
      } else {
        setErrorMessage(err.message || 'Registration failed. Please check your information.');
      }
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
            style={[
              styles.backBtn,
              {
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.surfaceSubtle,
              },
            ]}
            onPress={() => navigation.goBack()}
            accessibilityRole="button"
            accessibilityLabel="Go back"
          >
            <Ionicons name="chevron-back" size={20} color={theme.colors.textPrimary} />
          </TouchableOpacity>

          {/* Clean Modern Branding Header */}
          <View style={styles.brandHeader}>
            <View
              style={[
                styles.logoIconCircle,
                { backgroundColor: `${theme.colors.primary}18` },
              ]}
            >
              <Ionicons name="person-add" size={32} color={theme.colors.primary} />
            </View>
            <Heading level={1} style={styles.title}>
              Create Account
            </Heading>
            <BodyText color="secondary" style={styles.subtitle}>
              Sign up to get started
            </BodyText>
          </View>

          {/* Unified Seamless Form Area */}
          <View style={styles.formArea}>
            {/* Full Name */}
            <Controller
              control={control}
              name="full_name"
              render={({ field: { onChange, onBlur, value } }) => (
                <GlassInput
                  label="Full Name"
                  required
                  placeholder="e.g. Alex Morgan"
                  autoCapitalize="words"
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                  error={errors.full_name?.message}
                  leftIcon={
                    <Ionicons name="person-outline" size={19} color={theme.colors.textMuted} />
                  }
                />
              )}
            />

            {/* Email Address */}
            <Controller
              control={control}
              name="email"
              render={({ field: { onChange, onBlur, value } }) => (
                <GlassInput
                  label="Email Address"
                  required
                  placeholder="name@example.com"
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoCorrect={false}
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                  error={errors.email?.message}
                  leftIcon={
                    <Ionicons name="mail-outline" size={19} color={theme.colors.textMuted} />
                  }
                />
              )}
            />

            {/* Password */}
            <Controller
              control={control}
              name="password"
              render={({ field: { onChange, onBlur, value } }) => (
                <PasswordInput
                  label="Password"
                  required
                  placeholder="Minimum 8 characters"
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                  error={errors.password?.message}
                  leftIcon={
                    <Ionicons
                      name="lock-closed-outline"
                      size={19}
                      color={theme.colors.textMuted}
                    />
                  }
                />
              )}
            />

            {/* Confirm Password */}
            <Controller
              control={control}
              name="confirmPassword"
              render={({ field: { onChange, onBlur, value } }) => (
                <PasswordInput
                  label="Confirm Password"
                  required
                  placeholder="Re-enter your password"
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                  error={errors.confirmPassword?.message}
                  leftIcon={
                    <Ionicons
                      name="shield-checkmark-outline"
                      size={19}
                      color={theme.colors.textMuted}
                    />
                  }
                />
              )}
            />

            {/* Password hint */}
            <Caption color="muted" style={styles.hintText}>
              At least 8 characters with letters & numbers.
            </Caption>

            {/* Submit Button */}
            <PrimaryButton
              label="Create Account"
              loading={isLoading}
              onPress={() => {
                handleSubmit(onSubmit)();
              }}
              style={styles.submitBtn}
            />
          </View>

          {/* Switch to Login */}
          <View style={styles.footerRow}>
            <BodyText color="secondary">Already have an account?</BodyText>
            <TouchableOpacity
              onPress={() => navigation.navigate('Login')}
              accessibilityRole="button"
            >
              <BodyText weight="600" style={{ color: theme.colors.primary, marginLeft: 6 }}>
                Sign In
              </BodyText>
            </TouchableOpacity>
          </View>
        </ScrollContainer>
      </KeyboardAvoidingView>

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
    paddingHorizontal: 24,
    paddingBottom: 40,
    paddingTop: 12,
  },
  backBtn: {
    width: 42,
    height: 42,
    borderRadius: 21,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
  },
  brandHeader: {
    alignItems: 'center',
    marginBottom: 28,
  },
  logoIconCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  title: {
    textAlign: 'center',
    marginBottom: 6,
  },
  subtitle: {
    textAlign: 'center',
  },
  formArea: {
    width: '100%',
    marginBottom: 24,
  },
  hintText: {
    marginTop: -4,
    marginBottom: 20,
    lineHeight: 16,
  },
  submitBtn: {
    marginTop: 4,
    borderRadius: 14,
  },
  footerRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 12,
  },
});
