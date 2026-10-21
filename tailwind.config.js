/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        indigo: { 50: 'rgb(var(--ix-50) / <alpha-value>)', 100: 'rgb(var(--ix-100) / <alpha-value>)', 200: 'rgb(var(--ix-200) / <alpha-value>)', 300: 'rgb(var(--ix-300) / <alpha-value>)', 400: 'rgb(var(--ix-400) / <alpha-value>)', 500: 'rgb(var(--ix-500) / <alpha-value>)', 600: 'rgb(var(--ix-600) / <alpha-value>)', 700: 'rgb(var(--ix-700) / <alpha-value>)', 800: 'rgb(var(--ix-800) / <alpha-value>)', 900: 'rgb(var(--ix-900) / <alpha-value>)', 950: 'rgb(var(--ix-950) / <alpha-value>)' },
        purple: { 50: 'rgb(var(--px-50) / <alpha-value>)', 100: 'rgb(var(--px-100) / <alpha-value>)', 200: 'rgb(var(--px-200) / <alpha-value>)', 300: 'rgb(var(--px-300) / <alpha-value>)', 400: 'rgb(var(--px-400) / <alpha-value>)', 500: 'rgb(var(--px-500) / <alpha-value>)', 600: 'rgb(var(--px-600) / <alpha-value>)', 700: 'rgb(var(--px-700) / <alpha-value>)', 800: 'rgb(var(--px-800) / <alpha-value>)', 900: 'rgb(var(--px-900) / <alpha-value>)', 950: 'rgb(var(--px-950) / <alpha-value>)' },
        gold: { 400:'#e3c25a', 500:'#d4af37', 600:'#b58a2c' },
        brand: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
        accent: {
          50: '#ecfdf5',
          100: '#d1fae5',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
        },
        warning: '#f59e0b',
        danger: '#ef4444',
      },
      fontFamily: {
        sans: ['Hanken Grotesk', 'Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      animation: {
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.2s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        }
      }
    },
  },
  plugins: [],
}
