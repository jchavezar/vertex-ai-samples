/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#060d1b',
          900: '#0f172a',
          800: '#1e293b',
          700: '#334155',
        },
        executive: {
          cobalt: '#1d4ed8',
          cyan: '#0284c7',
          emerald: '#059669',
          indigo: '#4338ca',
          fuchsia: '#a21caf',
          gold: '#d97706',
          bg: '#f8fafc',
          card: '#ffffff',
          glass: 'rgba(255, 255, 255, 0.85)',
          border: '#e2e8f0',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'soundwave': 'soundwave 1.2s ease-in-out infinite alternate',
      },
      keyframes: {
        soundwave: {
          '0%': { height: '15%' },
          '100%': { height: '100%' },
        }
      }
    },
  },
  plugins: [],
}
