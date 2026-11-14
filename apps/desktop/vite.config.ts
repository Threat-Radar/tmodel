import { defineConfig } from "vite";
// @ts-expect-error type error without @types/node package
import process from "node:process";
import { pagesBuildOutDir } from "./src/app-mode.ts";
const host = process.env.TAURI_DEV_HOST;

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({

  // GitHub Pages serves this repository below /tmodel/. Tauri and local Vite
  // development retain their existing root base and output directory.
  base: mode === "pages" ? "/tmodel/app/" : "/",
  build: mode === "pages"
    ? {
        outDir: pagesBuildOutDir(process.env.TMODEL_APP_OUT_DIR),
        emptyOutDir: true,
      }
    : undefined,

  // Vite options tailored for Tauri development and only applied in `tauri dev` or `tauri build`
  //
  // 1. prevent Vite from obscuring rust errors
  clearScreen: false,
  // 2. tauri expects a fixed port, fail if that port is not available
  server: {
    port: 1420,
    strictPort: true,
    host: host || false,
    hmr: host
      ? {
          protocol: "ws",
          host,
          port: 1421,
        }
      : undefined,
    watch: {
      // 3. tell Vite to ignore watching `src-tauri`
      ignored: ["**/src-tauri/**"],
    },
  },
}));
