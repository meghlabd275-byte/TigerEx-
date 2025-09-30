import { MD3LightTheme as DefaultTheme } from 'react-native-paper';

export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#FF6B00',
    secondary: '#1E1E1E',
    background: '#FFFFFF',
    surface: '#F5F5F5',
    error: '#FF3B30',
    success: '#34C759',
    warning: '#FF9500',
    text: '#000000',
    textSecondary: '#8E8E93',
    border: '#E5E5EA',
    card: '#FFFFFF',
  },
  roundness: 8,
};

export const darkTheme = {
  ...DefaultTheme,
  dark: true,
  colors: {
    ...DefaultTheme.colors,
    primary: '#FF6B00',
    secondary: '#FFFFFF',
    background: '#000000',
    surface: '#1C1C1E',
    error: '#FF453A',
    success: '#32D74B',
    warning: '#FF9F0A',
    text: '#FFFFFF',
    textSecondary: '#8E8E93',
    border: '#38383A',
    card: '#1C1C1E',
  },
  roundness: 8,
};