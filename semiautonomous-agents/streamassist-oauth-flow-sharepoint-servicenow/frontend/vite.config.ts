import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5177,
    proxy: {
      '/api': {
        target: 'http://localhost:8004',
        changeOrigin: true,
      }
    }
  }
})
