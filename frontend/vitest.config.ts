import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vitest/config";

export default defineConfig({
  // Mesmo atalho "@" do vite.config.ts, usado pelos componentes da interface.
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
  test: {
    environment: "node",
    include: ["../tests/frontend/**/*.test.ts"],
  },
});
