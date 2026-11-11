export type AppMode = "desktop" | "browser-preview";

/** Vite's dedicated `pages` mode is the only engine-free application mode. */
export function appMode(viteMode: string = import.meta.env.MODE): AppMode {
  return viteMode === "pages" ? "browser-preview" : "desktop";
}

export function staticDataBase(
  base: string = import.meta.env.BASE_URL,
  page: string = globalThis.location?.href ?? "https://tmodel.invalid/",
): string {
  return new URL("data/", new URL(base, page)).href;
}
