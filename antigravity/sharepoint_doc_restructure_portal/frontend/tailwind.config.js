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
        yazdani: {
          canvas: '#faf9f6',     // Alabaster white
          panel: '#f4f3ef',      // Warm sand
          charcoal: '#1a1a19',   // Primary text
          muted: '#7c7a75',      // Muted gray
          border: '#d8d6d0',     // Technical border
          void: '#111111',       // Black placeholders
        }
      }
    },
  },
  plugins: [],
}
