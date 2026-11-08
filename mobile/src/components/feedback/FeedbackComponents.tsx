import React from 'react';
import {
  View,
  StyleSheet,
  ActivityIndicator,
  Modal,
  ViewProps,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { GlassCard } from '../glass/GlassCard';
import { Heading, BodyText, Caption } from '../common/Typography';
import { PrimaryButton, SecondaryButton } from '../common/Buttons';

export interface ToastProps {
  visible: boolean;
  message: string;
  type?: 'success' | 'warning' | 'error' | 'info';
}

export const Toast: React.FC<ToastProps> = ({
  visible,
  message,
  type = 'info',
}) => {
  const { theme } = useTheme();

  if (!visible) return null;

  const iconName =
    type === 'success'
      ? 'checkmark-circle'
      : type === 'warning'
      ? 'alert-circle'
      : type === 'error'
      ? 'close-circle'
      : 'information-circle';

  const typeColor =
    type === 'success'
      ? theme.colors.success
      : type === 'warning'
      ? theme.colors.warning
      : type === 'error'
      ? theme.colors.error
      : theme.colors.info;

  return (
    <View style={styles.toastContainer} pointerEvents="none">
      <GlassCard elevation="floating" style={styles.toastCard}>
        <Ionicons name={iconName} size={22} color={typeColor} style={styles.toastIcon} />
        <BodyText variant="small" weight="600" style={styles.toastMessage}>
          {message}
        </BodyText>
      </GlassCard>
    </View>
  );
};

export interface AlertDialogProps {
  visible: boolean;
  title: string;
  message: string;
  onDismiss: () => void;
  buttonLabel?: string;
}

export const AlertDialog: React.FC<AlertDialogProps> = ({
  visible,
  title,
  message,
  onDismiss,
  buttonLabel = 'OK',
}) => {
  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={styles.modalOverlay}>
        <GlassCard elevation="floating" style={styles.dialogCard}>
          <Heading level={2} style={styles.dialogTitle}>
            {title}
          </Heading>
          <BodyText color="secondary" style={styles.dialogMessage}>
            {message}
          </BodyText>
          <PrimaryButton label={buttonLabel} onPress={onDismiss} />
        </GlassCard>
      </View>
    </Modal>
  );
};

export interface ConfirmationModalProps {
  visible: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  confirmLabel?: string;
  cancelLabel?: string;
  isDestructive?: boolean;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  visible,
  title,
  message,
  onConfirm,
  onCancel,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
}) => {
  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={styles.modalOverlay}>
        <GlassCard elevation="floating" style={styles.dialogCard}>
          <Heading level={2} style={styles.dialogTitle}>
            {title}
          </Heading>
          <BodyText color="secondary" style={styles.dialogMessage}>
            {message}
          </BodyText>
          <View style={styles.modalActions}>
            <SecondaryButton
              label={cancelLabel}
              onPress={onCancel}
              style={{ flex: 1, marginRight: 8 }}
            />
            <PrimaryButton
              label={confirmLabel}
              onPress={onConfirm}
              style={{ flex: 1, marginLeft: 8 }}
            />
          </View>
        </GlassCard>
      </View>
    </Modal>
  );
};

export interface LoadingIndicatorProps {
  message?: string;
  size?: 'small' | 'large';
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  message,
  size = 'large',
}) => {
  const { theme } = useTheme();

  return (
    <View style={styles.centerContainer}>
      <ActivityIndicator size={size} color={theme.colors.primary} />
      {message ? (
        <Caption style={{ marginTop: 12 }}>{message}</Caption>
      ) : null}
    </View>
  );
};

export interface SkeletonLoaderProps extends ViewProps {
  width?: number | string;
  height?: number;
  borderRadius?: number;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  width = '100%',
  height = 20,
  borderRadius = 8,
  style,
  ...props
}) => {
  const { theme } = useTheme();

  return (
    <View
      style={[
        {
          width: width as any,
          height,
          borderRadius,
          backgroundColor: theme.colors.surfaceSubtle,
        },
        style,
      ]}
      {...props}
    />
  );
};

export interface EmptyStateProps {
  icon?: keyof typeof Ionicons.glyphMap;
  title: string;
  description: string;
  actionLabel?: string;
  onActionPress?: () => void;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon = 'file-tray-outline',
  title,
  description,
  actionLabel,
  onActionPress,
  onAction,
}) => {
  const { theme } = useTheme();
  const handleAction = onActionPress || onAction;

  return (
    <View style={styles.emptyContainer}>
      <View
        style={[
          styles.emptyIconCircle,
          { backgroundColor: theme.colors.primaryLight },
        ]}
      >
        <Ionicons name={icon} size={36} color={theme.colors.primary} />
      </View>
      <Heading level={3} align="center" style={styles.emptyTitle}>
        {title}
      </Heading>
      <BodyText color="secondary" align="center" style={styles.emptyDesc}>
        {description}
      </BodyText>
      {actionLabel && handleAction ? (
        <PrimaryButton
          label={actionLabel}
          onPress={handleAction}
          fullWidth={false}
          style={styles.emptyAction}
        />
      ) : null}
    </View>
  );
};

export interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message = 'An unexpected error occurred. Please try again.',
  onRetry,
}) => {
  const { theme } = useTheme();

  return (
    <View style={styles.emptyContainer}>
      <View
        style={[
          styles.emptyIconCircle,
          { backgroundColor: theme.colors.errorLight },
        ]}
      >
        <Ionicons name="alert-circle-outline" size={36} color={theme.colors.error} />
      </View>
      <Heading level={3} align="center" style={styles.emptyTitle}>
        {title}
      </Heading>
      <BodyText color="secondary" align="center" style={styles.emptyDesc}>
        {message}
      </BodyText>
      {onRetry ? (
        <PrimaryButton
          label="Try Again"
          onPress={onRetry}
          fullWidth={false}
          style={styles.emptyAction}
        />
      ) : null}
    </View>
  );
};

const styles = StyleSheet.create({
  toastContainer: {
    position: 'absolute',
    top: 50,
    left: 20,
    right: 20,
    zIndex: 200,
    alignItems: 'center',
  },
  toastCard: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    width: '100%',
  },
  toastIcon: {
    marginRight: 10,
  },
  toastMessage: {
    flex: 1,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  dialogCard: {
    width: '100%',
    maxWidth: 400,
    padding: 24,
  },
  dialogTitle: {
    marginBottom: 8,
  },
  dialogMessage: {
    marginBottom: 20,
  },
  modalActions: {
    flexDirection: 'row',
  },
  centerContainer: {
    padding: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    padding: 32,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyIconCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  emptyTitle: {
    marginBottom: 8,
  },
  emptyDesc: {
    maxWidth: 280,
    marginBottom: 20,
  },
  emptyAction: {
    paddingHorizontal: 24,
  },
});

