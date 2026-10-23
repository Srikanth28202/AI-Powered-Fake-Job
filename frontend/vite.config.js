import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': import.meta.dirname + '/src',
      '@components': import.meta.dirname + '/src/components',
      '@pages': import.meta.dirname + '/src/pages',
      '@hooks': import.meta.dirname + '/src/hooks',
      '@services': import.meta.dirname + '/src/services',
      '@store': import.meta.dirname + '/src/store',
      '@utils': import.meta.dirname + '/src/utils',
      '@types': import.meta.dirname + '/src/types',
      '@assets': import.meta.dirname + '/src/assets',
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
