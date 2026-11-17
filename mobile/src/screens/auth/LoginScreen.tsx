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
import { loginSchema, LoginSchemaType } from '../../schemas/auth';
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
              <Ionicons name="shield-checkmark" size={32} color={theme.colors.primary} />
            </View>
            <Heading level={1} style={styles.title}>
              Welcome Back
            </Heading>
            <BodyText color="secondary" style={styles.subtitle}>
              Sign in to your account
            </BodyText>
          </View>

          {/* Unified Seamless Form Area */}
          <View style={styles.formArea}>
            {/* Email Field */}
            <Controller
              control={control}
              name="email"
              render={({ field: { onChange, onBlur, value } }) => (
                <GlassInput
                  label="Email"
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
                      size={19}
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
          </View>

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
        message="Self-service email password recovery is not yet configured. Please contact support or re-create your account in development."
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
    marginBottom: 32,
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
  forgotBtn: {
    alignSelf: 'flex-end',
    marginTop: 4,
    marginBottom: 22,
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
