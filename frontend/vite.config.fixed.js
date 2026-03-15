import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  optimizeDeps: {
    exclude: ['@rollup/rollup-win32-x64-msvc']
  },
  build: {
    rollupOptions: {
      external: ['@rollup/rollup-win32-x64-msvc']
    }
  }
})
