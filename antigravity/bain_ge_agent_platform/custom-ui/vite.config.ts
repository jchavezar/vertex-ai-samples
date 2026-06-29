import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { execSync } from 'child_process';

// Get ADC access token dynamically via gcloud CLI
function getAdcAccessToken() {
  try {
    return execSync('gcloud auth print-access-token', { encoding: 'utf-8' }).trim();
  } catch (e) {
    console.error('Failed to fetch ADC access token via gcloud:', e);
    return '';
  }
}

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5186, // Explicitly aligned with user's active browser tab (localhost:5186)
    host: true,
    proxy: {
      '/api': {
        target: 'https://us-central1-aiplatform.googleapis.com',
        changeOrigin: true,
        secure: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            const token = getAdcAccessToken();
            if (token) {
              proxyReq.setHeader('Authorization', `Bearer ${token}`);
            }
            console.log(`[Vite Proxy] Forwarding request to Vertex AI with ADC Bearer Token (${token ? 'Attached' : 'Empty'})`);
          });
        },
      },
    },
  },
});
