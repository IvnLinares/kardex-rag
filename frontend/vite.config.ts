import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    watch: {
      // Los volumenes montados de Docker Desktop en Windows no siempre
      // propagan eventos nativos del sistema de archivos al contenedor;
      // sin polling, Vite no detecta los cambios y no dispara HMR.
      usePolling: true,
      interval: 300,
    },
  },
})
