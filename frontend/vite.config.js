import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

// Single-bundle build into the Frappe app's public/ folder (served at
// /assets/ops_dashboard/...), matching the other Justyol portals. Dev serves the
// SPA standalone on :8082 and proxies API calls to a running bench when present;
// with no bench, the resource shim answers from the live snapshot (lib/demo.js).
export default defineConfig({
  plugins: [vue()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  build: {
    outDir: "../ops_dashboard/public",
    emptyOutDir: false,
    target: "es2018",
    cssCodeSplit: false,
    rollupOptions: {
      input: path.resolve(__dirname, "src/main.js"),
      output: {
        entryFileNames: "ops_dashboard.bundle.js",
        assetFileNames: "ops_dashboard.bundle.css",
        inlineDynamicImports: true,
      },
    },
  },
  server: {
    port: 8082,
    proxy: {
      "^/(api|login|app)": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
