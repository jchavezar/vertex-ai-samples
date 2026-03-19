import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5179,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8010',
        changeOrigin: true,
      },
      '/google-api': {
        target: 'https://discoveryengine.googleapis.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/google-api/, ''),
      },
      '/sts': {
        target: 'https://sts.googleapis.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/sts/, ''),
      },
    },
  }
})
