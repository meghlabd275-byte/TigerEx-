// TigerEx Theme Manager - Shared across all platforms
// Works on: Web, Android, iOS, Desktop

const TigerExTheme = {
    // Current theme
    current: 'dark',
    
    // Initialize theme
    init() {
        // Check localStorage first
        let saved = localStorage.getItem('tigerex-theme') || localStorage.getItem('theme');
        
        // Fallback to system preference
        if (!saved) {
            saved = window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        
        this.set(saved);
        
        // Listen for system changes
        window.matchMedia?.('(prefers-color-scheme: dark)')?.addEventListener('change', (e) => {
            if (!localStorage.getItem('tigerex-theme')) {
                this.set(e.matches ? 'dark' : 'light');
            }
        });
    },
    
    // Set theme
    set(theme) {
        this.current = theme;
        document.body?.setAttribute('data-theme', theme);
        localStorage.setItem('tigerex-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update all toggles
        document.querySelectorAll('.theme-toggle').forEach(btn => {
            if (btn) btn.textContent = theme === 'dark' ? '🌙 Dark' : '☀️ Light';
        });
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
    },
    
    // Toggle theme
    toggle() {
        this.set(this.current === 'dark' ? 'light' : 'dark');
    },
    
    // Get colors
    getColors() {
        return this.current === 'dark' ? {
            bgPrimary: '#050A12',
            bgSecondary: '#0D1B2A',
            bgTertiary: '#141E2B',
            textPrimary: '#E8EEF4',
            textSecondary: 'rgba(255,255,255,0.7)',
            primary: '#F6821F',
            success: '#43A047',
            danger: '#E53935'
        } : {
            bgPrimary: '#F5F7FA',
            bgSecondary: '#FFFFFF',
            bgTertiary: '#F0F2F5',
            textPrimary: '#1A1A2E',
            textSecondary: '#666666',
            primary: '#F6821F',
            success: '#43A047',
            danger: '#E53935'
        };
    }
};

// Auto-initialize
if (typeof window !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => TigerExTheme.init());
}

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TigerExTheme;
}