import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Built files go to frontend/dist, which FastAPI serves at "/".
// During development (npm run dev), /api calls are sent to the Python app on port 8000.
export default defineConfig({
  plugins: [react()],
  build: { outDir: "dist", emptyOutDir: true, chunkSizeWarningLimit: 900 },
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
});
