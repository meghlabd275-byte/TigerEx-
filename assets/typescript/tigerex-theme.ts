/**
 * TigerEx Theme Manager for TypeScript/Node.js
 * Works with React, Next.js, Vue, and Node.js backends
 */

// Theme type
export type Theme = 'light' | 'dark';

// Theme configuration
export const THEME_KEY = 'tigerex_theme';
export const THEME_CLASS = 'light-mode';

// Theme colors interface
export interface ThemeColors {
    bgDark: string;
    bgDarkSecondary: string;
    bgCard: string;
    bgCardHover: string;
    textPrimary: string;
    textSecondary: string;
    border: string;
    primary: string;
    primaryHover: string;
    accentGreen: string;
    accentRed: string;
}

// Dark mode colors
export const darkColors: ThemeColors = {
    bgDark: '#0B0E11',
    bgDarkSecondary: '#1C2128',
    bgCard: '#1E2329',
    bgCardHover: '#252A32',
    textPrimary: '#EAECEF',
    textSecondary: '#848E9C',
    border: '#2B3139',
    primary: '#F0B90B',
    primaryHover: '#FFD84D',
    accentGreen: '#00C087',
    accentRed: '#F6465D'
};

// Light mode colors
export const lightColors: ThemeColors = {
    bgDark: '#F5F5F5',
    bgDarkSecondary: '#FFFFFF',
    bgCard: '#FFFFFF',
    bgCardHover: '#F0F0F0',
    textPrimary: '#1A1A1A',
    textSecondary: '#666666',
    border: '#E0E0E0',
    primary: '#F0B90B',
    primaryHover: '#E5A809',
    accentGreen: '#00C087',
    accentRed: '#F6465D'
};

// Get colors for theme
export function getThemeColors(theme: Theme): ThemeColors {
    return theme === 'light' ? lightColors : darkColors;
}

// Generate CSS variables
export function getCssVariables(theme: Theme): string {
    const colors = getThemeColors(theme);
    return `
        :root {
            --bg-dark: ${colors.bgDark};
            --bg-dark-secondary: ${colors.bgDarkSecondary};
            --bg-card: ${colors.bgCard};
            --bg-card-hover: ${colors.bgCardHover};
            --text-primary: ${colors.textPrimary};
            --text-secondary: ${colors.textSecondary};
            --border: ${colors.border};
            --primary: ${colors.primary};
            --primary-hover: ${colors.primaryHover};
            --accent-green: ${colors.accentGreen};
            --accent-red: ${colors.accentRed};
        }
    `;
}

// Generate full CSS
export function getThemeCss(): string {
    return `
        :root {
            --bg-dark: ${darkColors.bgDark};
            --bg-dark-secondary: ${darkColors.bgDarkSecondary};
            --bg-card: ${darkColors.bgCard};
            --bg-card-hover: ${darkColors.bgCardHover};
            --text-primary: ${darkColors.textPrimary};
            --text-secondary: ${darkColors.textSecondary};
            --border: ${darkColors.border};
            --primary: ${darkColors.primary};
            --primary-hover: ${darkColors.primaryHover};
            --accent-green: ${darkColors.accentGreen};
            --accent-red: ${darkColors.accentRed};
        }
        body.light-mode {
            --bg-dark: ${lightColors.bgDark};
            --bg-dark-secondary: ${lightColors.bgDarkSecondary};
            --bg-card: ${lightColors.bgCard};
            --bg-card-hover: ${lightColors.bgCardHover};
            --text-primary: ${lightColors.textPrimary};
            --text-secondary: ${lightColors.textSecondary};
            --border: ${lightColors.border};
            --primary: ${lightColors.primary};
            --primary-hover: ${lightColors.primaryHover};
            --accent-green: ${lightColors.accentGreen};
            --accent-red: ${lightColors.accentRed};
        }
    `;
}

// Theme hook for React
export function useTheme() {
    if (typeof window === 'undefined') {
        return { theme: 'dark' as Theme, toggleTheme: () => {} };
    }
    
    const savedTheme = localStorage.getItem(THEME_KEY) as Theme | null;
    const systemPrefersLight = window.matchMedia?.('(prefers-color-scheme: light)').matches;
    
    const theme: Theme = savedTheme || (systemPrefersLight ? 'light' : 'dark');
    
    const toggleTheme = () => {
        const newTheme = localStorage.getItem(THEME_KEY) === 'light' ? 'dark' : 'light';
        localStorage.setItem(THEME_KEY, newTheme);
        
        if (newTheme === 'light') {
            document.body.classList.add(THEME_CLASS);
        } else {
            document.body.classList.remove(THEME_CLASS);
        }
    };
    
    return { theme, toggleTheme };
}

// Export for Node.js
export default {
    THEME_KEY,
    THEME_CLASS,
    darkColors,
    lightColors,
    getThemeColors,
    getCssVariables,
    getThemeCss,
    useTheme
};