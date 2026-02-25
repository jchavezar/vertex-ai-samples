/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cave: {
          900: '#0a0a0a',
          800: '#141414',
          700: '#1f1f1f',
        },
        sockcop: {
          gold: '#d4af37',
          blue: '#1e3a8a',
        }
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
