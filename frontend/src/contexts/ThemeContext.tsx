/**
 * TigerEx Theme Context - Light/Dark Mode Toggle
 * @file ThemeContext.tsx
 * @description Global theme system for light/dark mode
 * @author TigerEx Development Team
 */
import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

export interface ThemeColors {
  // Primary colors
  primary: string;
  primaryDark: string;
  primaryLight: string;
  
  // Background colors
  background: string;
  backgroundSecondary: string;
  card: string;
  cardHover: string;
  cardActive: string;
  
  // Text colors
  text: string;
  textSecondary: string;
  textMuted: string;
  
  // Accent colors
  green: string;
  greenLight: string;
  red: string;
  redLight: string;
  
  // Border colors
  border: string;
  borderLight: string;
  
  // Utility
  white: string;
  black: string;
  transparent: string;
  
  // Status
  success: string;
  warning: string;
  error: string;
  info: string;
}

// Dark Theme (Default - Exchange Style)
export const darkTheme: ThemeColors = {
  primary: '#F0B90B',
  primaryDark: '#E5A809',
  primaryLight: '#FFD54F',
  background: '#0B0E14',
  backgroundSecondary: '#151A21',
  card: '#1C2128',
  cardHover: '#252D38',
  cardActive: '#2D3540',
  text: '#EAECE4',
  textSecondary: '#8B929E',
  textMuted: '#5C6370',
  green: '#00C087',
  greenLight: '#00E5A8',
  red: '#F6465D',
  redLight: '#FF6B7A',
  border: '#2A303C',
  borderLight: '#3A4250',
  white: '#FFFFFF',
  black: '#000000',
  transparent: 'transparent',
  success: '#00C087',
  warning: '#F0B90B',
  error: '#F6465D',
  info: '#3B82F6',
};

// Light Theme
export const lightTheme: ThemeColors = {
  primary: '#F0B90B',
  primaryDark: '#E5A809',
  primaryLight: '#6D4C00',
  background: '#FFFFFF',
  backgroundSecondary: '#F8FAFC',
  card: '#FFFFFF',
  cardHover: '#F1F5F9',
  cardActive: '#E2E8F0',
  text: '#1E293B',
  textSecondary: '#64748B',
  textMuted: '#94A3B8',
  green: '#059669',
  greenLight: '#10B981',
  red: '#DC2626',
  redLight: '#EF4444',
  border: '#E2E8F0',
  borderLight: '#CBD5E1',
  white: '#FFFFFF',
  black: '#000000',
  transparent: 'transparent',
  success: '#059669',
  warning: '#D97706',
  error: '#DC2626',
  info: '#2563EB',
};

interface ThemeContextType {
  theme: 'light' | 'dark';
  colors: ThemeColors;
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setThemeState] = useState<'light' | 'dark'>('dark');
  const [colors, setColors] = useState<ThemeColors>(darkTheme);

  // Initialize from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('tigerex-theme') as 'light' | 'dark' | null;
    if (savedTheme) {
      setThemeState(savedTheme);
      setColors(savedTheme === 'dark' ? darkTheme : lightTheme);
    }
  }, []);

  // Update colors when theme changes
  useEffect(() => {
    setColors(theme === 'dark' ? darkTheme : lightTheme);
    localStorage.setItem('tigerex-theme', theme);
    
    // Update document class for global styles
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.classList.add(theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setThemeState(prev => prev === 'dark' ? 'light' : 'dark');
  }, []);

  const setTheme = useCallback((newTheme: 'light' | 'dark') => {
    setThemeState(newTheme);
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, colors, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Utility hook for theme-based styles
export const useThemeStyles = () => {
  const { colors } = useTheme();
  
  return {
    // Common container styles
    container: {
      backgroundColor: colors.background,
      color: colors.text,
    },
    containerSecondary: {
      backgroundColor: colors.backgroundSecondary,
      color: colors.text,
    },
    card: {
      backgroundColor: colors.card,
      color: colors.text,
      borderColor: colors.border,
    },
    cardHover: {
      backgroundColor: colors.cardHover,
      color: colors.text,
    },
    
    // Button styles
    buttonPrimary: {
      backgroundColor: colors.primary,
      color: colors.black,
    },
    buttonSuccess: {
      backgroundColor: colors.green,
      color: colors.white,
    },
    buttonDanger: {
      backgroundColor: colors.red,
      color: colors.white,
    },
    
    // Text styles
    textPrimary: {
      color: colors.text,
    },
    textSecondary: {
      color: colors.textSecondary,
    },
    textMuted: {
      color: colors.textMuted,
    },
    
    // Border styles
    border: {
      borderColor: colors.border,
    },
    borderLight: {
      borderColor: colors.borderLight,
    },
    
    // Status colors
    success: {
      color: colors.green,
    },
    error: {
      color: colors.red,
    },
    warning: {
      color: colors.warning,
    },
  };
};

export default ThemeProvider;
