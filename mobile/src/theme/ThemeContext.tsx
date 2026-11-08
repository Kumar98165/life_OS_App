import React, { createContext, useContext, useState, useMemo } from 'react';
import { lightPalette, darkPalette, ColorPalette } from './colors';
import { spacing, borderRadius, shadows } from './spacing';
import { typography } from './typography';
import { opacity, animation, zIndex } from './tokens';

export interface Theme {
  isDark: boolean;
  colors: ColorPalette;
  spacing: typeof spacing;
  borderRadius: typeof borderRadius;
  shadows: typeof shadows;
  typography: typeof typography;
  opacity: typeof opacity;
  animation: typeof animation;
  zIndex: typeof zIndex;
}

const defaultTheme: Theme = {
  isDark: false,
  colors: lightPalette,
  spacing,
  borderRadius,
  shadows,
  typography,
  opacity,
  animation,
  zIndex,
};

interface ThemeContextType {
  theme: Theme;
  isDark: boolean;
  setScheme: (scheme: 'light' | 'dark') => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  theme: defaultTheme,
  isDark: false,
  setScheme: () => {},
  toggleTheme: () => {},
});

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isDark, setIsDark] = useState<boolean>(false);

  const theme = useMemo<Theme>(() => ({
    isDark,
    colors: isDark ? darkPalette : lightPalette,
    spacing,
    borderRadius,
    shadows,
    typography,
    opacity,
    animation,
    zIndex,
  }), [isDark]);

  const setScheme = (scheme: 'light' | 'dark') => {
    setIsDark(scheme === 'dark');
  };

  const toggleTheme = () => {
    setIsDark((prev) => !prev);
  };

  return (
    <ThemeContext.Provider value={{ theme, isDark, setScheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);
