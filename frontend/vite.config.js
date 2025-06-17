import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Assuming backend runs on port 8000
        changeOrigin: true, // Recommended for virtual hosted sites
        // You might not need rewrite if your backend paths are already /api/...
        // rewrite: (path) => path.replace(/^\/api/, ''), // Use if backend doesn't expect /api prefix
      }
    }
  }
});
