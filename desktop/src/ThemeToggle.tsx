/**
 * TigerEx Desktop Theme Toggle
 * @file ThemeToggle.tsx
 * @description Light/Dark theme toggle for desktop
 * @author TigerEx Development Team
 */
import React, { useState, useEffect } from 'react';
import { Switch, Typography } from 'antd';
import { SunOutlined, MoonOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';

const { Text } = Typography;

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
  setTheme: (isDark: boolean) => void;
}

const ThemeContext = React.createContext<ThemeContextType>({
  theme: darkTheme,
  isDark: true,
  toggleTheme: () => {},
  setTheme: () => {},
});

export const useTheme = () => React.useContext(ThemeContext);

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem('tigerex-theme');
    if (saved !== null) {
      setIsDark(saved === 'dark');
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = !isDark;
    localStorage.setItem('tigerex-theme', newTheme ? 'dark' : 'light');
    setIsDark(newTheme);
  };

  const setTheme = (dark: boolean) => {
    localStorage.setItem('tigerex-theme', dark ? 'dark' : 'light');
    setIsDark(dark);
  };

  const theme = isDark ? darkTheme : lightTheme;

  return (
    <ThemeContext.Provider value={{ theme, isDark, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Theme Toggle Component
interface ThemeToggleProps {
  size?: 'small' | 'default';
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ size = 'default' }) => {
  const { theme, isDark, toggleTheme } = useTheme();

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        padding: '4px 8px',
        borderRadius: 20,
        backgroundColor: theme.card,
        cursor: 'pointer',
      }}
      onClick={toggleTheme}
    >
      {isDark ? (
        <MoonOutlined style={{ color: theme.primary, fontSize: size === 'small' ? 14 : 18 }} />
      ) : (
        <SunOutlined style={{ color: '#F97316', fontSize: size === 'small' ? 14 : 18 }} />
      )}
      <Switch
        checked={isDark}
        onChange={toggleTheme}
        size={size}
        style={{ margin: 0 }}
      />
    </div>
  );
};

// Apply theme to document
export const applyTheme = (isDark: boolean) => {
  const theme = isDark ? darkTheme : lightTheme;
  document.documentElement.style.setProperty('--tigerex-primary', theme.primary);
  document.documentElement.style.setProperty('--tigerex-background', theme.background);
  document.documentElement.style.setProperty('--tigerex-card', theme.card);
  document.documentElement.style.setProperty('--tigerex-text', theme.text);
  document.documentElement.style.setProperty('--tigerex-text-secondary', theme.textSecondary);
  document.documentElement.style.setProperty('--tigerex-border', theme.border);
  document.documentElement.style.setProperty('--tigerex-green', theme.green);
  document.documentElement.style.setProperty('--tigerex-red', theme.red);
};

export default ThemeToggle;
