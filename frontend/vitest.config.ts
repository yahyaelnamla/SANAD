import path from "path";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
    include: ["../tests/frontend/**/*.test.{ts,tsx}"],
    server: {
      deps: {
        inline: ["@testing-library/react", "@testing-library/jest-dom"],
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@testing-library/react": path.resolve(
        __dirname,
        "node_modules/@testing-library/react",
      ),
    },
  },
  server: {
    fs: {
      allow: [".."],
    },
  },
});
