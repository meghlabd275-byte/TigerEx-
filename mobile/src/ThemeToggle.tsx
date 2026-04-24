/**
 * TigerEx Mobile Theme Toggle
 * @file ThemeToggle.tsx
 * @description Light/Dark theme toggle for mobile
 * @author TigerEx Development Team
 */
import React, { useState, useEffect } from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Theme configuration
export const lightTheme = {
  primary: '#F0B90B',
  background: '#FFFFFF',
  backgroundSecondary: '#F8FAFC',
  card: '#FFFFFF',
  cardHover: '#F1F5F9',
  text: '#1E293B',
  textSecondary: '#64748B',
  textMuted: '#94A3B8',
  green: '#059669',
  red: '#DC2626',
  border: '#E2E8F0',
};

export const darkTheme = {
  primary: '#F0B90B',
  background: '#0B0E14',
  backgroundSecondary: '#151A21',
  card: '#1C2128',
  cardHover: '#252D38',
  text: '#EAECE4',
  textSecondary: '#8B929E',
  textMuted: '#5C6370',
  green: '#00C087',
  red: '#F6465D',
  border: '#2A303C',
};

type Theme = typeof lightTheme;

interface ThemeContextType {
  theme: Theme;
  isDark: boolean;
  toggleTheme: () => void;
}

const ThemeContext = React.createContext<ThemeContextType>({
  theme: darkTheme,
  isDark: true,
  toggleTheme: () => {},
});

export const useTheme = () => React.useContext(ThemeContext);

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    loadTheme();
  }, []);

  const loadTheme = async () => {
    try {
      const saved = await AsyncStorage.getItem('tigerex-theme');
      if (saved !== null) {
        setIsDark(saved === 'dark');
      }
    } catch (e) {
      console.log('Error loading theme:', e);
    }
  };

  const toggleTheme = async () => {
    try {
      const newTheme = isDark ? 'light' : 'dark';
      await AsyncStorage.setItem('tigerex-theme', newTheme);
      setIsDark(!isDark);
    } catch (e) {
      console.log('Error saving theme:', e);
    }
  };

  const theme = isDark ? darkTheme : lightTheme;

  return (
    <ThemeContext.Provider value={{ theme, isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Theme Toggle Button Component
interface ThemeToggleProps {
  size?: number;
  showLabel?: boolean;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ size = 24, showLabel = false }) => {
  const { theme, isDark, toggleTheme } = useTheme();

  return (
    <TouchableOpacity
      onPress={toggleTheme}
      style={[
        styles.container,
        {
          backgroundColor: theme.card,
          width: size + 16,
          height: size + 16,
          borderRadius: (size + 16) / 2,
        },
      ]}
    >
      <Ionicons
        name={isDark ? 'moon' : 'sunny'}
        size={size}
        color={isDark ? theme.primary : '#F97316'}
      />
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
  },
});

export default ThemeToggle;
