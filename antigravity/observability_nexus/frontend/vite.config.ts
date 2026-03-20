import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5179, // Dedicated port for tracing system
    host: '0.0.0.0',
    proxy: {
      '/ws': {
        target: 'http://127.0.0.1:8145',
        ws: true,
        changeOrigin: true
      }
    }
  }
})
