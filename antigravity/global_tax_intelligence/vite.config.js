import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/kpmg/',
  server: {
    host: true, // Listen on all local IPs
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8009',
        changeOrigin: true
      }
    }
  }
})
