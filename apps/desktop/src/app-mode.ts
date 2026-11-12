export type AppMode = "desktop" | "browser-preview";

/** Vite's dedicated `pages` mode is the only engine-free application mode. */
export function appMode(viteMode: string = import.meta.env.MODE): AppMode {
  return viteMode === "pages" ? "browser-preview" : "desktop";
}

/** A standalone Pages build is scratch output; render_app owns docs/app/. */
export function pagesBuildOutDir(configured?: string): string {
  return configured || "dist/pages";
}

export function staticDataBase(
  base: string = import.meta.env.BASE_URL,
  page: string = globalThis.location?.href ?? "https://tmodel.invalid/",
): string {
  return new URL("data/", new URL(base, page)).href;
}
