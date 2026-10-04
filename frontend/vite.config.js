import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/chat": "http://localhost:8080",
      "/conversations": "http://localhost:8080",
      "/history": "http://localhost:8080",
      "/upload": "http://localhost:8080",
    },
  },
});
