import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/google-api': {
        target: 'https://discoveryengine.googleapis.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/google-api/, '')
      }
    }
  }
})
