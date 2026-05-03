/**
 * TigerEx Theme System
 * Works on all platforms: Android, iOS, Desktop, Web App
 * Compatible with all browsers and devices
 */

(function() {
    'use strict';
    
    // Theme configuration
    var THEME_KEY = 'tigerex_theme';
    var THEME_CLASS = 'light-mode';
    
    // Initialize theme on page load
    function initTheme() {
        // Check localStorage first
        var savedTheme = localStorage.getItem(THEME_KEY);
        
        // Check system preference if no saved preference
        if (!savedTheme) {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
                setLightMode();
            } else {
                setDarkMode();
            }
        } else if (savedTheme === 'light') {
            setLightMode();
        } else {
            setDarkMode();
        }
        
        // Listen for system theme changes
        if (window.matchMedia) {
            var mediaQuery = window.matchMedia('(prefers-color-scheme: light)');
            mediaQuery.addEventListener('change', function(e) {
                if (!localStorage.getItem(THEME_KEY)) {
                    if (e.matches) {
                        setLightMode();
                    } else {
                        setDarkMode();
                    }
                }
            });
        }
    }
    
    // Set light mode
    function setLightMode() {
        document.body.classList.add(THEME_CLASS);
        localStorage.setItem(THEME_KEY, 'light');
        updateThemeIcon(true);
        document.documentElement.setAttribute('data-theme', 'light');
    }
    
    // Set dark mode
    function setDarkMode() {
        document.body.classList.remove(THEME_CLASS);
        localStorage.setItem(THEME_KEY, 'dark');
        updateThemeIcon(false);
        document.documentElement.setAttribute('data-theme', 'dark');
    }
    
    // Toggle theme
    function toggleTheme() {
        if (document.body.classList.contains(THEME_CLASS)) {
            setDarkMode();
        } else {
            setLightMode();
        }
    }
    
    // Update theme icon
    function updateThemeIcon(isLight) {
        var icons = document.querySelectorAll('.theme-toggle span');
        for (var i = 0; i < icons.length; i++) {
            icons[i].textContent = isLight ? '\u2600\uFE0F' : '\uD83C\uDF19';
        }
    }
    
    // Get current theme
    function getTheme() {
        return localStorage.getItem(THEME_KEY) || 'dark';
    }
    
    // Set specific theme
    function setTheme(theme) {
        if (theme === 'light') {
            setLightMode();
        } else {
            setDarkMode();
        }
    }
    
    // Make functions globally available
    window.TigerExTheme = {
        init: initTheme,
        toggle: toggleTheme,
        setLight: setLightMode,
        setDark: setDarkMode,
        getTheme: getTheme,
        setTheme: setTheme
    };
    
    window.toggleTheme = toggleTheme;
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }
})();export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
