/**
 * TigerEx Theme Toggle Component
 * @file ThemeToggle.tsx
 * @description Light/Dark theme toggle switch
 * @author TigerEx Development Team
 */
import React from 'react';
import { useTheme, ThemeColors } from '../contexts/ThemeContext';
import { Sun, Moon } from 'lucide-react';

interface ThemeToggleProps {
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ 
  size = 'md', 
  showLabel = false 
}) => {
  const { theme, toggleTheme, colors } = useTheme();

  const sizes = {
    sm: { button: 'w-8 h-8', icon: 'w-4 h-4' },
    md: { button: 'w-10 h-10', icon: 'w-5 h-5' },
    lg: { button: 'w-12 h-12', icon: 'w-6 h-6' },
  };

  const iconSizes = {
    sm: 14,
    md: 18,
    lg: 22,
  };

  return (
    <button
      onClick={toggleTheme}
      className={`
        ${sizes[size].button} 
        rounded-full 
        flex items-center justify-center 
        transition-all duration-200 
        hover:scale-110 
        focus:outline-none focus:ring-2 focus:ring-offset-2
        ${theme === 'dark' 
          ? 'bg-[#1C2128] hover:bg-[#252D38]' 
          : 'bg-gray-100 hover:bg-gray-200'
        }
      `}
      style={{
        backgroundColor: theme === 'dark' ? colors.card : '#F3F4F6',
        borderColor: colors.border,
      }}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      {theme === 'dark' ? (
        <Moon 
          size={iconSizes[size]} 
          className="text-[#F0B90B]"
          style={{ color: colors.primary }}
        />
      ) : (
        <Sun 
          size={iconSizes[size]} 
          className="text-orange-500"
          style={{ color: '#F97316' }}
        />
      )}
    </button>
  );
};

export default ThemeToggle;
