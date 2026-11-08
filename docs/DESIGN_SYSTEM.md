# LifeOS – Premium White Glassmorphism Design System

## 1. Design Direction
LifeOS adopts a **Premium White Glassmorphism** design language characterized by:
- Clean white and soft lavender-tinted background (`#F7F8FC`).
- Frosted glass cards and panels with sub-pixel borders (`rgba(255, 255, 255, 0.85)`).
- Vibrant primary iris accents (`#6C63FF`).
- High-contrast, WCAG AAA-compliant typography (`#202033`).
- Soft multi-stop shadows (`shadowColor: #1A1C35`, low opacity) avoiding heavy visual clutter.

## 2. Centralized Design Tokens

### 2.1 Color Palette
| Token | Hex / RGBA Value | Purpose |
| :--- | :--- | :--- |
| `background` | `#F7F8FC` | Base light canvas background |
| `surface` | `#FFFFFF` | Solid opaque card/container background |
| `surfaceSubtle` | `#F1F3F9` | Skeleton loaders, subtle divider fills |
| `glassBackground` | `rgba(255, 255, 255, 0.75)` | Translucent frosted glass card body |
| `glassBackgroundSolid`| `rgba(255, 255, 255, 0.92)` | High-contrast glass fallback for inputs & dialogs |
| `glassBorder` | `rgba(255, 255, 255, 0.85)` | Primary sub-pixel border outline |
| `primary` | `#6C63FF` | Primary action buttons, active pills, indicators |
| `primaryDark` | `#554CE0` | Button gradient end stop |
| `textPrimary` | `#202033` | Headings, labels, body text (> 11:1 contrast) |
| `textSecondary`| `#85859A` | Subtitles, helper text (> 4.5:1 contrast) |
| `textMuted` | `#A7A7BC` | Input placeholders, captions |
| `success` | `#22C55E` | Habit streaks, completed tasks, success badges |
| `warning` | `#F59E0B` | Deadlines nearing, caution alerts |
| `error` | `#EF4444` | Form validation errors, destructive actions |

### 2.2 Spacing & Radii
```typescript
spacing = { xs: 4, sm: 8, md: 12, lg: 16, xl: 20, xxl: 24, xxxl: 32, huge: 48 };
borderRadius = { xs: 6, sm: 10, md: 14, lg: 18, xl: 24, pill: 9999 };
```

### 2.3 Shadows & Elevation
- **`subtle`**: Elevation 2, `shadowOpacity: 0.05`, `shadowRadius: 12`. Used on inputs, buttons, and badges.
- **`card`**: Elevation 4, `shadowOpacity: 0.07`, `shadowRadius: 20`. Used on `GlassCard` and `GlassPanel`.
- **`floating`**: Elevation 6, `shadowOpacity: 0.18`, `shadowRadius: 24`, iris tint. Used on FABs and active modals.

## 3. Glassmorphism Performance & Accessibility Rules
1. **Platform-Aware Blur**:
   - iOS utilizes `expo-blur` (`BlurView`) with hardware-accelerated translucent filters.
   - Android utilizes high-opacity static glass surfaces (`rgba(255, 255, 255, 0.92)`) with sub-pixel borders to guarantee 60 FPS scrolling and avoid GPU thermal throttling.
2. **Text Contrast**: Text is never rendered directly over raw photographic or variable content without an intervening glass or solid layer with opacity `>= 0.75`.
3. **Minimum Touch Targets**: All interactive buttons, switches, checkboxes, and tabs enforce a minimum touch target of `44x44` points.

