// #290: the home page entry points of the team's design, added to #278's
// welcome screen in the desktop app only (the browser preview removes the
// welcome screen and never loads this module). Three large options, each with
// one line of explanation, sit under the welcome text; "Get started" still
// opens the example models.
//
// An option that cannot work in this build says so and stays unavailable,
// rather than pretending to work.

import { html } from "./safe-html";

export interface HomeActions {
  /** Opens the Import New Product screen; absent when the import screen is not part of the build. */
  importProduct?(opener: HTMLElement): void;
  openThreatModel(): Promise<boolean>;
  openProject(): Promise<boolean>;
}

export interface HomeAvailability {
  /** Projects need the workspace (#288) and a verified review session (#289). */
  projects: boolean;
  reason: string;
}

type HomeAction = "import" | "threat-model" | "project";

interface HomeOption {
  action: HomeAction;
  title: string;
  help: string;
  available: boolean;
  unavailable: string;
}

export function homeOptions(actions: HomeActions, availability: HomeAvailability): HomeOption[] {
  return [
    {
      action: "import",
      title: "Import New Product",
      help: "Create a threat model from an SBOM and a vulnerability scan.",
      available: Boolean(actions.importProduct),
      unavailable: "Coming soon to the app. For now, import from a terminal with tmodel import-sbom.",
    },
    {
      action: "threat-model",
      title: "Open Existing Threat Model",
      help: "Open a previously saved YAML file.",
      available: availability.projects,
      unavailable: availability.reason,
    },
    {
      action: "project",
      title: "Open Existing Project",
      help: "Continue a project and its version history.",
      available: availability.projects,
      unavailable: availability.reason,
    },
  ];
}

export function renderHomeOptions(options: readonly HomeOption[]): string {
  return html`<ul class="welcome-options">${options.map((option) => html`<li>
<button type="button" class="welcome-option" data-home-action="${option.action}" aria-labelledby="home-${option.action}-title" aria-describedby="home-${option.action}-help"${option.available ? "" : html` aria-disabled="true"`}>
<span id="home-${option.action}-title" class="welcome-option-title">${option.title}</span>
<span id="home-${option.action}-help" class="welcome-option-help">${option.help}${option.available ? "" : html` <span class="welcome-option-unavailable">${option.unavailable}</span>`}</span>
</button></li>`)}</ul>`.value;
}

/**
 * Adds the options to the welcome screen. `enter` leaves the welcome screen
 * for the workspace the same way "Get started" does.
 */
export class HomeEntryPoints {
  readonly element: HTMLElement;
  private readonly status: HTMLElement;
  private busy = false;

  constructor(
    private readonly actions: HomeActions,
    private readonly availability: () => HomeAvailability,
    documentRoot: Pick<Document, "createElement"> = document,
  ) {
    this.element = documentRoot.createElement("nav");
    this.element.className = "welcome-entry";
    this.element.setAttribute("aria-label", "Start working");
    this.status = documentRoot.createElement("p");
    this.status.className = "welcome-entry-status";
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    this.element.addEventListener("click", (event) => void this.handleClick(event.target as Element | null));
    this.render();
  }

  render(): void {
    this.element.innerHTML = renderHomeOptions(homeOptions(this.actions, this.availability()));
    this.element.append(this.status);
  }

  async handleClick(target: Element | null): Promise<void> {
    const button = target?.closest?.("[data-home-action]");
    const action = button?.getAttribute("data-home-action") as HomeAction | null | undefined;
    if (!button || !action || this.busy) return;
    const option = homeOptions(this.actions, this.availability()).find((candidate) => candidate.action === action);
    if (!option) return;
    if (!option.available) {
      this.status.textContent = `${option.title}: ${option.unavailable}`;
      return;
    }
    if (action === "import") {
      this.status.textContent = "";
      this.actions.importProduct?.(button as HTMLElement);
      return;
    }
    this.busy = true;
    this.status.textContent = action === "project" ? "Choose a project folder…" : "Choose a saved threat model file…";
    try {
      const opened = action === "project" ? await this.actions.openProject() : await this.actions.openThreatModel();
      this.status.textContent = opened ? "" : "Nothing was opened.";
    } catch (error) {
      this.status.textContent = error instanceof Error ? error.message : String(error);
    } finally {
      this.busy = false;
    }
  }

  get statusText(): string {
    return this.status.textContent ?? "";
  }
}
