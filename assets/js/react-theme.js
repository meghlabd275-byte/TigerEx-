/**
 * TigerEx Theme Hook for React/Next.js
 * Use this hook in React components for theme management
 */

import { useState, useEffect, useCallback } from 'react';

const THEME_KEY = 'tigerex_theme';
const THEME_CLASS = 'light-mode';

export function useTheme() {
    const [theme, setTheme] = useState('dark');
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        const savedTheme = localStorage.getItem(THEME_KEY);
        
        if (!savedTheme) {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
                setTheme('light');
            } else {
                setTheme('dark');
            }
        } else {
            setTheme(savedTheme);
        }
    }, []);

    useEffect(() => {
        if (!mounted) return;
        
        if (theme === 'light') {
            document.body.classList.add(THEME_CLASS);
        } else {
            document.body.classList.remove(THEME_CLASS);
        }
        localStorage.setItem(THEME_KEY, theme);
        document.documentElement.setAttribute('data-theme', theme);
    }, [theme, mounted]);

    const toggleTheme = useCallback(() => {
        setTheme(prev => prev === 'light' ? 'dark' : 'light');
    }, []);

    const setLightTheme = useCallback(() => {
        setTheme('light');
    }, []);

    const setDarkTheme = useCallback(() => {
        setTheme('dark');
    }, []);

    return {
        theme,
        isLight: theme === 'light',
        isDark: theme === 'dark',
        mounted,
        toggleTheme,
        setLightTheme,
        setDarkTheme
    };
}

// Theme Provider for Next.js _app.js
export function ThemeProvider({ children }) {
    useEffect(() => {
        const savedTheme = localStorage.getItem(THEME_KEY);
        
        if (!savedTheme) {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
                document.body.classList.add(THEME_CLASS);
            }
        } else if (savedTheme === 'light') {
            document.body.classList.add(THEME_CLASS);
        }
    }, []);

    return children;
}

// Theme Toggle Component
export function ThemeToggle({ className = '' }) {
    const { theme, toggleTheme } = useTheme();
    
    return (
        <button 
            className={`theme-toggle ${className}`}
            onClick={toggleTheme}
            title="Toggle Theme"
            type="button"
        >
            <span>{theme === 'light' ? '🌙' : '☀️'}</span>
        </button>
    );
}

export default useTheme;export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
