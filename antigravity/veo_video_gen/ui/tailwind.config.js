/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'mono': ['"JetBrains Mono"', 'monospace'],
        'sans': ['"Inter"', 'sans-serif'],
      },
      colors: {
        cave: {
          50: '#f8fafc',
          900: '#0f172a', /* Slate 900 */
          950: '#020617', /* Slate 950 */
        },
        stone: {
          800: '#292524',
          900: '#1c1917',
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
