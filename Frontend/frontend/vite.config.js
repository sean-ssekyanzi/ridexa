import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    // Render.com (and some other hosts) provide the port in `PORT`.
    // We also support `VITE_PORT` for local overrides.
    port: process.env.PORT
      ? parseInt(process.env.PORT)
      : process.env.VITE_PORT
      ? parseInt(process.env.VITE_PORT)
      : 5173
  }
})
