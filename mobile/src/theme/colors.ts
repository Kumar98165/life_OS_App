export interface ColorPalette {
  // Base Canvas
  background: string;
  surface: string;
  surfaceSubtle: string;

  // Glassmorphic Accents
  glassBackground: string;
  glassBackgroundMuted: string;
  glassBackgroundSolid: string;
  glassBorder: string;
  glassBorderSubtle: string;

  // Brand Primaries
  primary: string;
  primaryDark: string;
  primaryHover: string;
  primaryLight: string;
  primaryGlow: string;

  // Typography
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
  textInverse: string;

  // Status & Feedback
  success: string;
  successLight: string;
  warning: string;
  warningLight: string;
  error: string;
  errorLight: string;
  info: string;
  infoLight: string;

  // Neutral Borders & Dividers
  border: string;
  divider: string;

  // Shadows
  shadowColor: string;
  blurTint: 'light' | 'dark';
}

export const lightPalette: ColorPalette = {
  background: '#F7F8FC',
  surface: '#FFFFFF',
  surfaceSubtle: '#F1F3F9',

  glassBackground: 'rgba(255, 255, 255, 0.75)',
  glassBackgroundMuted: 'rgba(255, 255, 255, 0.50)',
  glassBackgroundSolid: 'rgba(255, 255, 255, 0.92)',
  glassBorder: 'rgba(255, 255, 255, 0.85)',
  glassBorderSubtle: 'rgba(233, 234, 242, 0.80)',

  primary: '#6C63FF',
  primaryDark: '#554CE0',
  primaryHover: '#5B52E0',
  primaryLight: 'rgba(108, 99, 255, 0.12)',
  primaryGlow: 'rgba(108, 99, 255, 0.25)',

  textPrimary: '#202033',
  textSecondary: '#85859A',
  textMuted: '#A7A7BC',
  textInverse: '#FFFFFF',

  success: '#22C55E',
  successLight: 'rgba(34, 197, 94, 0.12)',
  warning: '#F59E0B',
  warningLight: 'rgba(245, 158, 11, 0.12)',
  error: '#EF4444',
  errorLight: 'rgba(239, 68, 68, 0.12)',
  info: '#3B82F6',
  infoLight: 'rgba(59, 130, 246, 0.12)',

  border: '#E9EAF2',
  divider: '#F0F1F7',

  shadowColor: '#1A1C35',
  blurTint: 'light',
};

export const darkPalette: ColorPalette = {
  background: '#0F101A',
  surface: '#1A1C2E',
  surfaceSubtle: '#22253B',

  glassBackground: 'rgba(26, 28, 46, 0.75)',
  glassBackgroundMuted: 'rgba(26, 28, 46, 0.50)',
  glassBackgroundSolid: 'rgba(26, 28, 46, 0.92)',
  glassBorder: 'rgba(255, 255, 255, 0.12)',
  glassBorderSubtle: 'rgba(255, 255, 255, 0.08)',

  primary: '#7E76FF',
  primaryDark: '#6C63FF',
  primaryHover: '#8C85FF',
  primaryLight: 'rgba(126, 118, 255, 0.18)',
  primaryGlow: 'rgba(126, 118, 255, 0.35)',

  textPrimary: '#F1F2FA',
  textSecondary: '#A0A2BA',
  textMuted: '#686A82',
  textInverse: '#10111D',

  success: '#22C55E',
  successLight: 'rgba(34, 197, 94, 0.18)',
  warning: '#F59E0B',
  warningLight: 'rgba(245, 158, 11, 0.18)',
  error: '#EF4444',
  errorLight: 'rgba(239, 68, 68, 0.18)',
  info: '#3B82F6',
  infoLight: 'rgba(59, 130, 246, 0.18)',

  border: 'rgba(255, 255, 255, 0.10)',
  divider: 'rgba(255, 255, 255, 0.06)',

  shadowColor: '#000000',
  blurTint: 'dark',
};

export const colors = lightPalette;
export type Colors = ColorPalette;
