# LifeOS – Theme Architecture

## 1. Overview
The LifeOS theme architecture separates raw color definitions from semantic component consumption. All styling is dynamically derived via the `useTheme()` hook, establishing full preparation for dark mode toggling without requiring code refactoring across individual components.

```
+----------------------------------------------------------------+
|                         ThemeProvider                          |
|  - Tracks `isDark` boolean state                               |
|  - Injects `theme` context object                              |
|  - Exposes `toggleTheme()` and `setScheme('light' | 'dark')`   |
+----------------------------------------------------------------+
                               |
                        React Context
                               v
+----------------------------------------------------------------+
|                           useTheme()                           |
|  - `theme.colors`: Light or Dark Palette                       |
|  - `theme.spacing`: Spacing scale (4pt - 48pt)                 |
|  - `theme.borderRadius`: Corner radii (6pt - 9999pt)           |
|  - `theme.shadows`: Subtle, Card, Floating                     |
|  - `theme.typography`: h1, h2, h3, body, caption, button       |
|  - `theme.opacity`: Glass and overlay opacity values           |
|  - `theme.zIndex`: Header, modal, toast layers                 |
+----------------------------------------------------------------+
```

## 2. Palette Definitions

### 2.1 Light Palette (Active Default)
- `background`: `#F7F8FC`
- `surface`: `#FFFFFF`
- `glassBackground`: `rgba(255, 255, 255, 0.75)`
- `glassBorder`: `rgba(255, 255, 255, 0.85)`
- `textPrimary`: `#202033`
- `textSecondary`: `#85859A`

### 2.2 Dark Palette (Foundation Ready)
- `background`: `#0F101A`
- `surface`: `#1A1C2E`
- `glassBackground`: `rgba(26, 28, 46, 0.75)`
- `glassBorder`: `rgba(255, 255, 255, 0.12)`
- `textPrimary`: `#F1F2FA`
- `textSecondary`: `#A0A2BA`

## 3. Usage Pattern in Components
```typescript
import React from 'react';
import { View, StyleSheet } from 'react-native';
import { useTheme } from '../theme';

export const ExampleCard = () => {
  const { theme } = useTheme();

  return (
    <View
      style={[
        styles.card,
        {
          backgroundColor: theme.colors.glassBackgroundSolid,
          borderColor: theme.colors.glassBorder,
          borderRadius: theme.borderRadius.lg,
        },
        theme.shadows.card,
      ]}
    />
  );
};

const styles = StyleSheet.create({
  card: {
    borderWidth: 1,
    padding: 16,
  },
});
```

