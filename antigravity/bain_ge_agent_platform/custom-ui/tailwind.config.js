/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Space Grotesk"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        canvas: '#faf9f6',
        panel: '#f4f3ef',
        primary: '#1a1a19',
        muted: '#7c7a75',
        borderTech: '#d8d6d0',
        void: '#111111',
      },
      scale: {
        '102': '1.02',
      },
    },
  },
  plugins: [],
};
