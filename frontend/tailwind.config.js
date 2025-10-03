/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx,vue}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx,vue}',
    './web-app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // TigerEx Brand Colors (Binance Style)
        primary: {
          50: '#FEF7E0',
          100: '#FDECC4',
          200: '#FBD88E',
          300: '#F9C158',
          400: '#F7AA22',
          500: '#F0B90B', // Binance Yellow
          600: '#D9A441',
          700: '#B8892F',
          800: '#976E1D',
          900: '#76530B',
          DEFAULT: '#F0B90B',
        },
        success: {
          50: '#E6F9F2',
          100: '#CCF3E5',
          200: '#99E7CB',
          300: '#66DBB1',
          400: '#33CF97',
          500: '#0ECB81', // Success Green
          600: '#0BB871',
          700: '#099861',
          800: '#067851',
          900: '#045841',
          DEFAULT: '#0ECB81',
        },
        danger: {
          50: '#FEE7EA',
          100: '#FDCFD5',
          200: '#FB9FAB',
          300: '#F96F81',
          400: '#F73F57',
          500: '#F6465D', // Danger Red
          600: '#E53E3E',
          700: '#D43535',
          800: '#C32D2D',
          900: '#B22424',
          DEFAULT: '#F6465D',
        },
        // Dark Theme Colors
        dark: {
          primary: '#0B0E11',
          secondary: '#1E2329',
          tertiary: '#2B3139',
          quaternary: '#474D57',
        },
        // Text Colors
        text: {
          primary: '#EAECEF',
          secondary: '#848E9C',
          tertiary: '#5E6673',
          quaternary: '#474D57',
          light: '#1E2329',
          'light-secondary': '#707A8A',
        },
        // Border Colors
        border: {
          primary: '#2B3139',
          secondary: '#474D57',
          tertiary: '#5E6673',
          light: '#EAECEF',
        },
        // Background Colors
        bg: {
          primary: '#0B0E11',
          secondary: '#1E2329',
          tertiary: '#2B3139',
          quaternary: '#474D57',
          light: '#FFFFFF',
          'light-secondary': '#F8F9FA',
          'light-tertiary': '#EAECEF',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
      fontSize: {
        'xs': ['10px', { lineHeight: '14px' }],
        'sm': ['12px', { lineHeight: '16px' }],
        'base': ['14px', { lineHeight: '20px' }],
        'lg': ['16px', { lineHeight: '24px' }],
        'xl': ['20px', { lineHeight: '28px' }],
        '2xl': ['24px', { lineHeight: '32px' }],
        '3xl': ['30px', { lineHeight: '36px' }],
        '4xl': ['36px', { lineHeight: '40px' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
        '144': '36rem',
        '160': '40rem',
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '16px',
        '3xl': '24px',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'DEFAULT': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
        'none': 'none',
        'glow': '0 0 20px rgba(240, 185, 11, 0.3)',
        'glow-success': '0 0 20px rgba(14, 203, 129, 0.3)',
        'glow-danger': '0 0 20px rgba(246, 70, 93, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'slide-left': 'slideLeft 0.3s ease-out',
        'slide-right': 'slideRight 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'spin-slow': 'spin 3s linear infinite',
        'ping-slow': 'ping 3s cubic-bezier(0, 0, 0.2, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideLeft: {
          '0%': { transform: 'translateX(20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideRight: {
          '0%': { transform: 'translateX(-20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
      },
      screens: {
        'xs': '475px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
        '3xl': '1920px',
      },
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      },
      backdropBlur: {
        xs: '2px',
      },
      transitionProperty: {
        'height': 'height',
        'spacing': 'margin, padding',
      },
    },
  },
  plugins: [],
}