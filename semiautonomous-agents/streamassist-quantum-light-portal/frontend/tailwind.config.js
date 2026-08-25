/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        quantum: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae0fd',
          300: '#7cc7fb',
          400: '#38a9f7',
          500: '#0f8ce9',
          600: '#0270c7',
          700: '#0359a1',
          800: '#074c84',
          900: '#0c406e',
          950: '#082949',
        },
      },
      boxShadow: {
        'quantum-light': '0 4px 20px -2px rgba(15, 140, 233, 0.08), 0 2px 6px -1px rgba(0, 0, 0, 0.04)',
        'quantum-glass': '0 8px 32px 0 rgba(31, 38, 135, 0.07)',
        'quantum-glow': '0 0 25px rgba(15, 140, 233, 0.25)',
      },
    },
  },
  plugins: [],
}
