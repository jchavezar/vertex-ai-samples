import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/pwc/',
  server: {
    host: true,
    proxy: {
      '/pwc/api': {
        target: 'http://127.0.0.1:8010',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/pwc\/api/, '/api')
      }
    }
  }
})
