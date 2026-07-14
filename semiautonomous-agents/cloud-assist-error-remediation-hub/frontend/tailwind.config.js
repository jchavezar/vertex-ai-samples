/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0a0d14',
        card: '#131824',
        cardHover: '#1c2333',
        borderGlow: '#2e3952',
        accentBlue: '#3b82f6',
        accentCyan: '#06b6d4',
        accentPurple: '#8b5cf6'
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
