import type { AppNavigation } from "./app-navigation";
import { requestedModel } from "./model-catalog";

interface WelcomeElements {
  welcome: HTMLElement;
  workspace: HTMLElement;
  start: HTMLButtonElement;
}

interface WelcomeEnvironment {
  isPreview: boolean;
  location: Pick<Location, "hash" | "search">;
  navigation: Pick<AppNavigation, "hasDestination">;
  events: Pick<Window, "addEventListener" | "removeEventListener">;
  reducedMotion: Pick<MediaQueryList, "matches" | "addEventListener" | "removeEventListener">;
}

export function initializeWelcome(
  { welcome, workspace, start }: WelcomeElements,
  { isPreview, location, navigation, events, reducedMotion }: WelcomeEnvironment,
): void {
  const hasDeepLink = () => navigation.hasDestination(location.hash)
    || requestedModel(new URLSearchParams(location.search)) !== undefined;
  if (isPreview || hasDeepLink()) {
    welcome.remove();
    workspace.hidden = false;
    return;
  }

  const contours = welcome.querySelectorAll<SVGAnimationElement>(".welcome-contours animate");
  const updateContourMotion = () => {
    for (const animation of contours) {
      if (reducedMotion.matches) animation.endElement();
      else animation.beginElement();
    }
  };

  const enter = () => {
    events.removeEventListener("hashchange", followLink);
    reducedMotion.removeEventListener("change", updateContourMotion);
    start.removeEventListener("click", enter);
    welcome.remove();
    workspace.classList.add("workspace-enter");
    workspace.hidden = false;
    workspace.focus({ preventScroll: true });
  };
  const followLink = () => {
    if (hasDeepLink()) enter();
  };
  events.addEventListener("hashchange", followLink);
  start.addEventListener("click", enter);
  welcome.addEventListener("keydown", (event) => {
    // The button handles its own Enter and Space through native activation.
    if (event.target === welcome && event.key === "Enter" && !event.isComposing && !event.repeat) {
      event.preventDefault();
      start.click();
    }
  });
  welcome.hidden = false;
  if (!reducedMotion.matches) updateContourMotion();
  reducedMotion.addEventListener("change", updateContourMotion);
  welcome.focus({ preventScroll: true });
}
