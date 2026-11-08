import React, { useState } from 'react';
import {
  View,
  TextInput,
  TextInputProps,
  StyleSheet,
  TouchableOpacity,
  Switch as RNSwitch,
  SwitchProps as RNSwitchProps,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { Label, BodyText, Caption } from './Typography';

export interface GlassInputProps extends TextInputProps {
  label?: string;
  error?: string;
  required?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const GlassInput: React.FC<GlassInputProps> = ({
  label,
  error,
  required,
  leftIcon,
  rightIcon,
  style,
  onFocus,
  onBlur,
  ...props
}) => {
  const { theme } = useTheme();
  const [isFocused, setIsFocused] = useState(false);

  return (
    <View style={styles.inputGroup}>
      {label ? <Label required={required}>{label}</Label> : null}
      <View
        style={[
          styles.inputContainer,
          {
            backgroundColor: theme.colors.glassBackgroundSolid,
            borderColor: error
              ? theme.colors.error
              : isFocused
              ? theme.colors.primary
              : theme.colors.glassBorder,
            borderRadius: theme.borderRadius.md,
          },
          theme.shadows.subtle,
        ]}
      >
        {leftIcon ? <View style={styles.iconSlot}>{leftIcon}</View> : null}
        <TextInput
          placeholderTextColor={theme.colors.textMuted}
          style={[
            styles.inputField,
            theme.typography.body,
            { color: theme.colors.textPrimary },
            style,
          ]}
          onFocus={(e) => {
            setIsFocused(true);
            onFocus?.(e);
          }}
          onBlur={(e) => {
            setIsFocused(false);
            onBlur?.(e);
          }}
          {...props}
        />
        {rightIcon ? <View style={styles.iconSlot}>{rightIcon}</View> : null}
      </View>
      {error ? (
        <Caption customColor={theme.colors.error} style={styles.errorText}>
          {error}
        </Caption>
      ) : null}
    </View>
  );
};

export interface PasswordInputProps extends Omit<GlassInputProps, 'rightIcon'> {}

export const PasswordInput: React.FC<PasswordInputProps> = (props) => {
  const [showPassword, setShowPassword] = useState(false);
  const { theme } = useTheme();

  return (
    <GlassInput
      secureTextEntry={!showPassword}
      autoCapitalize="none"
      autoCorrect={false}
      rightIcon={
        <TouchableOpacity
          onPress={() => setShowPassword((prev) => !prev)}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
          accessibilityRole="button"
          accessibilityLabel={showPassword ? 'Hide password' : 'Show password'}
        >
          <Ionicons
            name={showPassword ? 'eye-off-outline' : 'eye-outline'}
            size={20}
            color={theme.colors.textSecondary}
          />
        </TouchableOpacity>
      }
      {...props}
    />
  );
};

export interface SearchInputProps extends TextInputProps {
  onClear?: () => void;
}

export const SearchInput: React.FC<SearchInputProps> = ({
  value,
  onClear,
  style,
  ...props
}) => {
  const { theme } = useTheme();

  return (
    <GlassInput
      leftIcon={
        <Ionicons name="search-outline" size={18} color={theme.colors.textMuted} />
      }
      rightIcon={
        value && onClear ? (
          <TouchableOpacity onPress={onClear} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
            <Ionicons name="close-circle" size={18} color={theme.colors.textMuted} />
          </TouchableOpacity>
        ) : undefined
      }
      value={value}
      placeholder="Search..."
      style={style}
      {...props}
    />
  );
};

export interface CheckboxProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

export const Checkbox: React.FC<CheckboxProps> = ({
  label,
  checked,
  onChange,
  disabled = false,
}) => {
  const { theme } = useTheme();

  return (
    <TouchableOpacity
      activeOpacity={0.8}
      disabled={disabled}
      onPress={() => onChange(!checked)}
      style={styles.checkboxRow}
      accessibilityRole="checkbox"
      accessibilityState={{ checked, disabled }}
      accessibilityLabel={label}
    >
      <View
        style={[
          styles.checkboxBox,
          {
            borderRadius: theme.borderRadius.xs,
            borderColor: checked ? theme.colors.primary : theme.colors.border,
            backgroundColor: checked
              ? theme.colors.primary
              : theme.colors.glassBackgroundSolid,
          },
        ]}
      >
        {checked ? (
          <Ionicons name="checkmark" size={14} color="#FFFFFF" />
        ) : null}
      </View>
      <BodyText variant="small" style={styles.checkboxLabel}>
        {label}
      </BodyText>
    </TouchableOpacity>
  );
};

export interface SwitchProps extends RNSwitchProps {
  label?: string;
}

export const Switch: React.FC<SwitchProps> = ({
  label,
  value,
  onValueChange,
  ...props
}) => {
  const { theme } = useTheme();

  const switchComponent = (
    <RNSwitch
      value={value}
      onValueChange={onValueChange}
      trackColor={{
        false: theme.colors.border,
        true: theme.colors.primary,
      }}
      thumbColor="#FFFFFF"
      ios_backgroundColor={theme.colors.border}
      {...props}
    />
  );

  if (label) {
    return (
      <View style={styles.switchRow}>
        <BodyText variant="small" weight="500">
          {label}
        </BodyText>
        {switchComponent}
      </View>
    );
  }

  return switchComponent;
};

export interface SelectFieldProps {
  label?: string;
  value?: string;
  placeholder?: string;
  onPress: () => void;
  error?: string;
}

export const SelectField: React.FC<SelectFieldProps> = ({
  label,
  value,
  placeholder = 'Select option...',
  onPress,
  error,
}) => {
  const { theme } = useTheme();

  return (
    <View style={styles.inputGroup}>
      {label ? <Label>{label}</Label> : null}
      <TouchableOpacity
        onPress={onPress}
        activeOpacity={0.8}
        style={[
          styles.inputContainer,
          styles.selectContainer,
          {
            backgroundColor: theme.colors.glassBackgroundSolid,
            borderColor: error ? theme.colors.error : theme.colors.glassBorder,
            borderRadius: theme.borderRadius.md,
          },
          theme.shadows.subtle,
        ]}
        accessibilityRole="button"
        accessibilityLabel={label || placeholder}
      >
        <BodyText
          style={{
            color: value ? theme.colors.textPrimary : theme.colors.textMuted,
          }}
        >
          {value || placeholder}
        </BodyText>
        <Ionicons
          name="chevron-down"
          size={18}
          color={theme.colors.textSecondary}
        />
      </TouchableOpacity>
      {error ? (
        <Caption customColor={theme.colors.error} style={styles.errorText}>
          {error}
        </Caption>
      ) : null}
    </View>
  );
};

const styles = StyleSheet.create({
  inputGroup: {
    marginBottom: 16,
    width: '100%',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    height: 48,
    paddingHorizontal: 12,
  },
  selectContainer: {
    justifyContent: 'space-between',
  },
  inputField: {
    flex: 1,
    height: '100%',
  },
  iconSlot: {
    marginHorizontal: 4,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    marginTop: 4,
    marginLeft: 2,
  },
  checkboxRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 8,
    minHeight: 44,
  },
  checkboxBox: {
    width: 20,
    height: 20,
    borderWidth: 1.5,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  checkboxLabel: {
    flex: 1,
  },
  switchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 8,
    minHeight: 44,
  },
});

