# LifeOS – Component Guidelines & API Reference

## 1. Overview
All LifeOS components are organized by functional domain under `mobile/src/components/` and re-exported via `mobile/src/components/index.ts`. Components consume semantic tokens through the `useTheme()` hook.

---

## 2. Component Catalog

### 2.1 Layout Components (`components/layout/`)
- **`ScreenContainer`**: Root screen wrapper applying theme background and status bar configuration.
  - Props: `statusBarStyle?: StatusBarStyle`, `padded?: boolean`.
- **`SafeAreaContainer`**: Safe area insets container utilizing `react-native-safe-area-context`.
  - Props: `edges?: ('top' | 'right' | 'bottom' | 'left')[]`.
- **`ScrollContainer`**: Vertical scroll container with optional `KeyboardAvoidingView` behavior.
  - Props: `avoidKeyboard?: boolean`, `padded?: boolean`.
- **`SectionHeader`**: Clean header row for content groupings with optional right-aligned action button.
  - Props: `title: string`, `subtitle?: string`, `actionText?: string`, `onActionPress?: () => void`.
- **`ResponsiveContainer`**: Responsive layout constraint centering content on larger tablet screens.
  - Props: `maxWidth?: number` (default: 640).

### 2.2 Glass Components (`components/glass/`)
- **`GlassCard`**: Frosted glass card with sub-pixel border and soft elevation shadow.
  - Props: `elevation?: 'subtle' | 'card' | 'floating' | 'none'`, `intensity?: number`, `variant?: 'frosted' | 'solid'`, `onPress?: () => void`.
- **`GlassPanel`**: Translucent container for sheets or bottom drawers with optional top-only border radii.
  - Props: `roundedTopOnly?: boolean`, `intensity?: number`.
- **`GlassHeader`**: Top application bar with back navigation chevron, centered heading, and right action slot.
  - Props: `title: string`, `onBackPress?: () => void`, `rightAction?: ReactNode`, `showBorder?: boolean`.
- **`GlassBottomNavigation`**: Bottom tab bar with active indicator pills and safe area padding.
  - Props: `tabs: TabItem[]`, `activeTab: string`, `onTabPress: (key: string) => void`.

### 2.3 Buttons (`components/common/Buttons.tsx`)
- **`PrimaryButton`**: Gradient iris button with touch opacity and loading spinner.
  - Props: `label: string`, `loading?: boolean`, `disabled?: boolean`, `icon?: ReactNode`, `fullWidth?: boolean`.
- **`SecondaryButton`**: Frosted glass button with light border and theme text.
  - Props: `label: string`, `loading?: boolean`, `disabled?: boolean`, `icon?: ReactNode`, `fullWidth?: boolean`.
- **`IconButton`**: Circular glass or primary button for icon actions (>= 44x44pt).
  - Props: `icon: ReactNode`, `size?: number`, `variant?: 'glass' | 'solid' | 'primary'`.
- **`FloatingActionButton`**: Primary elevated button positioned above content.
  - Props: `icon: ReactNode`, `label?: string`, `onPress: () => void`.

### 2.4 Form Inputs (`components/common/FormInputs.tsx`)
- **`GlassInput`**: Accessible text input with label, error caption, and icon slots.
  - Props: `label?: string`, `error?: string`, `required?: boolean`, `leftIcon?: ReactNode`, `rightIcon?: ReactNode`.
- **`PasswordInput`**: Secure password field with show/hide password toggle.
- **`SearchInput`**: Search bar with search icon and clear button.
  - Props: `onClear?: () => void`.
- **`Checkbox`**: Accessible checkmark box with label and touch feedback.
  - Props: `label: string`, `checked: boolean`, `onChange: (checked: boolean) => void`.
- **`Switch`**: Accessible toggle switch with optional leading label.
  - Props: `label?: string`, `value: boolean`, `onValueChange: (val: boolean) => void`.
- **`SelectField`**: Dropdown trigger displaying chosen value with chevron indicator.
  - Props: `label?: string`, `value?: string`, `placeholder?: string`, `onPress: () => void`.

### 2.5 Feedback (`components/feedback/FeedbackComponents.tsx`)
- **`Toast`**: Floating notification banner with auto-dismiss icon styling.
  - Props: `visible: boolean`, `message: string`, `type?: 'success' | 'warning' | 'error' | 'info'`.
- **`AlertDialog`**: Glass modal displaying title, message, and single dismiss button.
  - Props: `visible: boolean`, `title: string`, `message: string`, `onDismiss: () => void`.
- **`ConfirmationModal`**: Dual-action dialog for confirming irreversible or critical operations.
  - Props: `visible: boolean`, `title: string`, `message: string`, `onConfirm: () => void`, `onCancel: () => void`.
- **`LoadingIndicator`**: Centered activity spinner with optional status text.
  - Props: `message?: string`, `size?: 'small' | 'large'`.
- **`SkeletonLoader`**: Placeholder block with subtle fill for content loading states.
- **`EmptyState`**: Centered icon, title, description, and action button for zero-item states.
- **`ErrorState`**: Centered error illustration and retry button for network or processing failures.

### 2.6 Typography (`components/common/Typography.tsx`)
- **`Heading`**: Accessible header text (`accessibilityRole="header"`). `level: 1 | 2 | 3`.
- **`BodyText`**: Standard body paragraph text. `variant: 'large' | 'regular' | 'small'`.
- **`Caption`**: Fine-print caption text for timestamps and helper hints.
- **`Label`**: Bold field descriptor with optional red asterisk (`required: boolean`).

