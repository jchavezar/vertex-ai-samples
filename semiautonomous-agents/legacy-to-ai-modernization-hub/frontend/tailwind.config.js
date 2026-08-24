/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        legacy: {
          bg: '#e4e7ea',
          panel: '#f0f3f6',
          header: '#3b4b5a',
          accent: '#1e5f8a',
          border: '#b8c3cd',
          text: '#222f3e',
        },
        cyber: {
          bg: '#090d16',
          surface: '#0f172a',
          card: '#1e293b',
          neonCyan: '#06b6d4',
          neonEmerald: '#10b981',
          neonViolet: '#8b5cf6',
          neonAmber: '#f59e0b',
          neonRose: '#f43f5e',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-fast': 'pulse 1.2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow-cyan': 'glowCyan 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glowCyan: {
          '0%': { boxShadow: '0 0 10px rgba(6, 182, 212, 0.2)' },
          '100%': { boxShadow: '0 0 25px rgba(6, 182, 212, 0.6)' },
        }
      }
    },
  },
  plugins: [],
}
