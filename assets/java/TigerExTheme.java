/**
 * TigerEx Theme Manager for Java/Kotlin/JVM
 * Include in your backend services
 */

package com.tigerex.theme;

public class TigerExTheme {
    public static final String THEME_KEY = "tigerex_theme";
    public static final String THEME_LIGHT = "light";
    public static final String THEME_DARK = "dark";
    
    // Theme colors
    public static class Colors {
        // Dark Mode
        public static final String DARK_BG = "#0B0E11";
        public static final String DARK_BG_SECONDARY = "#1C2128";
        public static final String DARK_CARD = "#1E2329";
        public static final String DARK_TEXT_PRIMARY = "#EAECEF";
        public static final String DARK_TEXT_SECONDARY = "#848E9C";
        public static final String DARK_BORDER = "#2B3139";
        
        // Light Mode
        public static final String LIGHT_BG = "#F5F5F5";
        public static final String LIGHT_BG_SECONDARY = "#FFFFFF";
        public static final String LIGHT_CARD = "#FFFFFF";
        public static final String LIGHT_TEXT_PRIMARY = "#1A1A1A";
        public static final String LIGHT_TEXT_SECONDARY = "#666666";
        public static final String LIGHT_BORDER = "#E0E0E0";
        
        // Brand Colors
        public static final String PRIMARY = "#F0B90B";
        public static final String ACCENT_GREEN = "#00C087";
        public static final String ACCENT_RED = "#F6465D";
    }
    
    /**
     * Get CSS variables for current theme
     */
    public static String getCssVariables(boolean isLight) {
        if (isLight) {
            return getLightModeCss();
        } else {
            return getDarkModeCss();
        }
    }
    
    public static String getDarkModeCss() {
        return """
            :root {
                --bg-dark: #0B0E11;
                --bg-dark-secondary: #1C2128;
                --bg-card: #1E2329;
                --bg-card-hover: #252A32;
                --text-primary: #EAECEF;
                --text-secondary: #848E9C;
                --border: #2B3139;
                --primary: #F0B90B;
                --primary-hover: #FFD84D;
                --accent-green: #00C087;
                --accent-red: #F6465D;
            }
            """;
    }
    
    public static String getLightModeCss() {
        return """
            :root {
                --bg-dark: #F5F5F5;
                --bg-dark-secondary: #FFFFFF;
                --bg-card: #FFFFFF;
                --bg-card-hover: #F0F0F0;
                --text-primary: #1A1A1A;
                --text-secondary: #666666;
                --border: #E0E0E0;
                --primary: #F0B90B;
                --primary-hover: #E5A809;
                --accent-green: #00C087;
                --accent-red: #F6465D;
            }
            """;
    }
    
    /**
     * Get HTML style tag with theme
     */
    public static String getThemeStyleTag(boolean isLight) {
        return "<style>:root{" + (isLight ? getLightModeCss() : getDarkModeCss()) + "}</style>";
    }
}