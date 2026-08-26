/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        google: {
          blue: '#1a73e8',
          blueHover: '#1557b0',
          blueLight: '#e8f0fe',
          grayBg: '#f8fafd',
          border: '#dadce0',
          textMain: '#202124',
          textMuted: '#5f6368',
          green: '#137333',
          greenBg: '#e6f4ea',
        }
      }
    },
  },
  plugins: [],
}
