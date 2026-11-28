import { describe, expect, it, vi } from "vitest";
import html from "../index.html?raw";
import { AppNavigation } from "./app-navigation";
import { initializeWelcome } from "./welcome";
// @ts-expect-error The app deliberately does not install @types/node; Vitest runs this in Node.
import { readFileSync } from "node:fs";

const css = readFileSync(new URL("./welcome.css", import.meta.url), "utf8");

function launch(location = { hash: "", search: "" }, isPreview = false, reduceMotion = false) {
  const surface = () => Object.assign(new EventTarget(), {
    hidden: true,
    classList: { add: vi.fn() },
    setAttribute: vi.fn(),
    focus: vi.fn(),
    remove: vi.fn(),
  });
  const contour = { beginElement: vi.fn(), endElement: vi.fn() };
  const welcome = Object.assign(surface(), { querySelectorAll: vi.fn(() => [contour]) });
  const reducedMotion = Object.assign(new EventTarget(), { matches: reduceMotion });
  const workspace = surface();
  const start = Object.assign(new EventTarget(), {
    click: () => start.dispatchEvent(new Event("click")),
  });
  const events = new EventTarget();
  const navigation = new AppNavigation(
    (["report", "paths", "graph", "library"] as const).map((view) => ({
      view,
      button: surface() as unknown as HTMLButtonElement,
      panel: surface() as unknown as HTMLElement,
      activated: vi.fn(),
    })),
    location,
    events,
  );
  initializeWelcome({
    welcome: welcome as unknown as HTMLElement,
    workspace: workspace as unknown as HTMLElement,
    start: start as unknown as HTMLButtonElement,
  }, {
    isPreview,
    location,
    navigation,
    events,
    reducedMotion,
  });
  return { welcome, workspace, start, events, reducedMotion, contour };
}

describe("desktop welcome and direct navigation", () => {
  it("keeps the workspace inaccessible until the native button is activated", () => {
    const { welcome, workspace, start } = launch();
    expect(welcome.hidden).toBe(false);
    expect(welcome.focus).toHaveBeenCalledOnce();
    expect(workspace.hidden).toBe(true);
    start.click();
    start.click();
    expect(welcome.remove).toHaveBeenCalledOnce();
    expect(workspace.hidden).toBe(false);
    expect(workspace.focus).toHaveBeenCalledExactlyOnceWith({ preventScroll: true });
    expect(workspace.classList.add).toHaveBeenCalledExactlyOnceWith("workspace-enter");
  });

  it("shows welcome on the next fresh launch after entering the workspace", () => {
    const first = launch();
    first.start.click();
    expect(first.workspace.hidden).toBe(false);

    const reopened = launch();
    expect(reopened.welcome.hidden).toBe(false);
    expect(reopened.welcome.focus).toHaveBeenCalledOnce();
    expect(reopened.workspace.hidden).toBe(true);
  });

  it("keeps welcome dismissed while navigating the workspace and changing models", () => {
    const location = { hash: "", search: "" };
    const { events, start, welcome, workspace } = launch(location);
    start.click();

    location.hash = "#graph";
    events.dispatchEvent(new Event("hashchange"));
    location.search = "?model=another-example";
    location.hash = "#library";
    events.dispatchEvent(new Event("hashchange"));
    location.hash = "";
    events.dispatchEvent(new Event("hashchange"));

    expect(welcome.remove).toHaveBeenCalledOnce();
    expect(workspace.hidden).toBe(false);
    expect(workspace.focus).toHaveBeenCalledOnce();
  });

  it.each([
    { search: "?file=example.yaml", hash: "" },
    { search: "?model=example", hash: "#graph" },
    { search: "?model=example", hash: "#unknown" },
    { search: "?model=&file=example.yaml", hash: "" },
    ...["report", "paths", "graph", "library", "weaknesses", "attack-patterns", "requirements", "sdl"]
      .map((view) => ({ search: "", hash: `#${view}` })),
  ])("opens the workspace directly at %o", (location) => {
    const initialLocation = { ...location };
    const { welcome, workspace } = launch(location);
    expect(welcome.remove).toHaveBeenCalledOnce();
    expect(welcome.focus).not.toHaveBeenCalled();
    expect(workspace.hidden).toBe(false);
    expect(location).toEqual(initialLocation);
  });

  it.each([
    { search: "", hash: "#unknown" },
    { search: "", hash: "#" },
    { search: "?model=", hash: "" },
    { search: "?file=", hash: "" },
    { search: "?model=%20%09&file=%20", hash: "#unknown" },
    { search: "?graphSource=fixture", hash: "" },
  ])("keeps welcome visible for %o", (location) => {
    const { welcome, workspace } = launch(location);
    expect(welcome.remove).not.toHaveBeenCalled();
    expect(welcome.hidden).toBe(false);
    expect(workspace.hidden).toBe(true);
  });

  it("lets history open a recognized view while welcome is visible", () => {
    const location = { hash: "", search: "" };
    const { events, start, welcome, workspace } = launch(location);
    location.hash = "#unknown";
    events.dispatchEvent(new Event("hashchange"));
    expect(workspace.hidden).toBe(true);
    location.hash = "#sdl";
    events.dispatchEvent(new Event("hashchange"));
    expect(workspace.hidden).toBe(false);
    start.click();
    expect(workspace.hidden).toBe(false);
    expect(welcome.remove).toHaveBeenCalledOnce();
    expect(location.hash).toBe("#sdl");
  });

  it.each([
    { search: "", hash: "" },
    { search: "?model=example", hash: "#sdl" },
    { search: "?model=", hash: "#unknown" },
  ])("opens preview directly at %o", (location) => {
    const initialLocation = { ...location };
    const { welcome, workspace } = launch(location, true);
    expect(welcome.remove).toHaveBeenCalledOnce();
    expect(welcome.focus).not.toHaveBeenCalled();
    expect(workspace.hidden).toBe(false);
    expect(location).toEqual(initialLocation);
  });

  it("handles Enter on the welcome landmark without intercepting native button events", () => {
    const { welcome, workspace } = launch();
    const repeated = Object.assign(new Event("keydown", { cancelable: true }), { key: "Enter", repeat: true });
    const enter = Object.assign(new Event("keydown", { cancelable: true }), { key: "Enter" });
    welcome.dispatchEvent(repeated);
    expect(workspace.hidden).toBe(true);
    welcome.dispatchEvent(enter);
    expect(enter.defaultPrevented).toBe(true);
    expect(workspace.hidden).toBe(false);
  });

  it("loops the radar rotation and returns both SVG contours to their original shapes", () => {
    expect(css).toContain("animation: welcome-sweep 54s linear infinite;");
    const contours = html.split('<g class="welcome-contours"')[1].split("</g>")[0];
    const paths = [...contours.matchAll(/<path d="([^"]+)"[^>]*>\s*<animate([^>]*)>/g)];
    expect(paths).toHaveLength(2);
    for (const [, base, animation] of paths) {
      expect(animation).toContain('attributeName="d" begin="indefinite"');
      expect(animation).toContain('repeatCount="indefinite" calcMode="spline"');
      const poses = animation.match(/values="([^"]+)"/)?.[1].split(";").map((pose) => pose.trim());
      expect(poses?.[0]).toBe(base);
      expect(poses?.[poses.length - 1]).toBe(base);
      expect(poses?.slice(1, -1).every((pose) => pose !== base)).toBe(true);
    }
  });

  it("starts the contours only when motion is allowed and releases the listener on entry", () => {
    const { contour, reducedMotion, start } = launch(undefined, false, true);
    expect(contour.beginElement).not.toHaveBeenCalled();

    reducedMotion.matches = false;
    reducedMotion.dispatchEvent(new Event("change"));
    expect(contour.beginElement).toHaveBeenCalledOnce();

    reducedMotion.matches = true;
    reducedMotion.dispatchEvent(new Event("change"));
    expect(contour.endElement).toHaveBeenCalledOnce();

    start.click();
    reducedMotion.matches = false;
    reducedMotion.dispatchEvent(new Event("change"));
    expect(contour.beginElement).toHaveBeenCalledOnce();
  });

  it("gives both entry states a main landmark and hides the decorative artwork", () => {
    expect(html).toMatch(/<main id="welcome"[^>]+aria-labelledby="welcome-title"[^>]+hidden>/);
    expect(html).toMatch(/<main id="workspace"[^>]+tabindex="-1" hidden>/);
    expect(html).toMatch(/<svg class="welcome-art"[^>]+aria-hidden="true">/);
    expect(html).toMatch(/<button id="get-started"[^>]+type="button">\s*Get started/);
    expect(css).toMatch(/prefers-reduced-motion: reduce[^}]+\.welcome-sweep, \.welcome-node, \.workspace-enter\s*\{ animation: none/);
  });
});
