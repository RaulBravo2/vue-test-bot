import path from "path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src")
    }
  },
  server: { port: 5050 },
  // Preview/producción (Railway): bind 0.0.0.0 y puerto desde $PORT. Leerlo acá (JS) es
  // portable; no depende de expansión del shell (que en Windows con yarn no funciona).
  preview: {
    host: true,
    port: Number(process.env.PORT) || 4173,
    strictPort: true
  },
  build: { chunkSizeWarningLimit: 1600 }
});
