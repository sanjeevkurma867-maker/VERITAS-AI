import { defineConfig } from "vite";

const backend = "http://127.0.0.1:8000";

export default defineConfig({
  base: "/app/",
  server: {
    proxy: Object.fromEntries(
      ["/verify", "/demo", "/health", "/docs", "/openapi.json"].map((path) => [path, backend]),
    ),
  },
});
