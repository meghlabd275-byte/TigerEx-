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
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

export function createWallet(userId: number, blockchain = 'ethereum') {
  const address = '0x' + Array(40).fill().map(() => Math.random().toString(16)[2]).join('');
  const words = 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork'; return { address, seedPhrase: words.split(' ').slice(0,24).join(' '), blockchain, ownership: 'USER_OWNS', userId }; }
