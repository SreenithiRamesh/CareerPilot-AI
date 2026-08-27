import {
  mergeConfig,
} from "vite";

import {
  defineConfig,
} from "vitest/config";

import viteConfig from "./vite.config.js";


export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment:
        "jsdom",

      setupFiles: [
        "./src/test/setup.js",
      ],

      clearMocks: true,
      restoreMocks: true,
    },
  })
);