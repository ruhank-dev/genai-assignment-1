import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// In dev the backend runs on :8000; in Docker nginx does the same proxying.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": "http://localhost:8000", "/health": "http://localhost:8000" },
  },
});
