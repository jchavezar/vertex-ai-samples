import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Listen on all local IPs
    port: 5180,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8012',
        changeOrigin: true
      }
    }
  }
})
