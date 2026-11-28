// #290's Import New Product screen, the home page entry point of the team's
// design: choose a Syft CycloneDX SBOM and, optionally, a Grype scan of the
// same image and a platform; the engine's /import/sbom runs #257's importer;
// the screen shows the product, platform, counts, every warning and any
// refusal exactly as the engine words it; "Create project" starts a project
// from the imported model through the workspace provider (#288).
//
// The form is built once and never re-rendered, so the chosen files and the
// platform survive a refusal or a failure and can be fixed and retried. Only
// the result and the alert regions are redrawn. Desktop only.

import {
  fileBase64,
  IMPORT_FILE_LIMIT_BYTES,
  IMPORT_FILE_LIMIT_TEXT,
  ImportError,
  MAIN_COUNTS,
  platformProblem,
  SbomImportClient,
  suggestedPlatforms,
  type ImportResult,
} from "./import-client";
import importStyles from "./import-screen.css?inline";
import { importMockFetch } from "./import-mock";
import type { ProjectSource } from "./project-workspace";
import { html, type SafeHtml } from "./safe-html";

export interface ImportScreenOptions {
  documentRoot: Document;
  client: Pick<SbomImportClient, "importSbom">;
  /** Starts a project from the model text and opens it at v001; false when nothing opened. */
  createProject(name: string, modelText: string): Promise<boolean>;
  projects(): { available: boolean; reason: string };
  mock?: boolean;
}

type FileKind = "sbom" | "scan";

interface FileField {
  input: HTMLInputElement;
  chosen: HTMLElement;
  error: HTMLElement;
  clear?: HTMLButtonElement;
  file?: File;
}

export class ImportScreen {
  readonly element: HTMLElement;
  private readonly title: HTMLElement;
  private readonly fields: Record<FileKind, FileField>;
  private readonly platform: HTMLInputElement;
  private readonly platformError: HTMLElement;
  private readonly importButton: HTMLButtonElement;
  private readonly progress: HTMLElement;
  private readonly status: HTMLElement;
  private readonly alert: HTMLElement;
  private readonly result: HTMLElement;
  private busy?: "import" | "create";
  private unavailable?: string;
  private imported?: ImportResult;
  private request?: AbortController;
  private from?: HTMLElement;
  private returnFocus?: HTMLElement;

  constructor(private readonly options: ImportScreenOptions) {
    const doc = options.documentRoot;
    const style = doc.createElement("style");
    style.textContent = importStyles;
    doc.head.append(style);
    const make = <K extends keyof HTMLElementTagNameMap>(tag: K, className = "", text = ""): HTMLElementTagNameMap[K] => {
      const element = doc.createElement(tag);
      if (className) element.className = className;
      if (text) element.textContent = text;
      return element;
    };
    this.element = make("main", "import-screen");
    this.element.id = "import-screen";
    this.element.setAttribute("aria-labelledby", "import-title");
    this.element.hidden = true;
    const card = make("div", "import-card");
    const eyebrow = make("p", "eyebrow", "Import New Product");
    this.title = make("h1", "import-title", "Import a product from its SBOM");
    this.title.id = "import-title";
    this.title.tabIndex = -1;
    const intro = make("p", "import-intro", "Create a threat model from an SBOM and a vulnerability scan. The app reads the files in this window and sends their bytes to tmodel's local engine, which runs the same import as tmodel import-sbom. No folder path is sent or shown.");
    card.append(eyebrow, this.title, intro);
    // A development server's mock only: builds leave the notice out with the mock.
    if (import.meta.env.DEV && options.mock) card.append(make("p", "import-mock", "Development mock: the import answers with the importer's recorded results for its alpine test files, whatever files you choose."));

    const form = make("form", "import-form");
    form.noValidate = true;
    form.setAttribute("aria-describedby", "import-limit");
    const fileField = (kind: FileKind, label: string, help: string, required: boolean): FileField => {
      const wrapper = make("div", "import-field");
      const id = `import-${kind}`;
      const labelElement = make("label", "import-label", label);
      labelElement.htmlFor = id;
      const input = make("input", "import-file");
      input.type = "file";
      input.id = id;
      input.accept = ".json,application/json";
      input.setAttribute("aria-describedby", `${id}-help ${id}-chosen ${id}-error`);
      if (required) input.setAttribute("aria-required", "true");
      const helpElement = make("p", "import-help", help);
      helpElement.id = `${id}-help`;
      const chosen = make("p", "import-chosen");
      chosen.id = `${id}-chosen`;
      const error = make("p", "field-error");
      error.id = `${id}-error`;
      error.hidden = true;
      wrapper.append(labelElement, input, helpElement, chosen, error);
      const field: FileField = { input, chosen, error };
      if (!required) {
        const clear = make("button", "review-secondary", "Remove the scan");
        clear.type = "button";
        clear.hidden = true;
        clear.addEventListener("click", () => this.chooseFile(kind, undefined, true));
        wrapper.append(clear);
        field.clear = clear;
      }
      input.addEventListener("change", () => this.chooseFile(kind, input.files?.[0]));
      form.append(wrapper);
      return field;
    };
    this.fields = {
      sbom: fileField("sbom", "SBOM file (required)", "Syft's CycloneDX JSON SBOM of a container image.", true),
      scan: fileField("scan", "Vulnerability scan (optional)", "Grype's JSON scan of the same image.", false),
    };
    const platformField = make("div", "import-field");
    const platformLabel = make("label", "import-label", "Platform (optional)");
    platformLabel.htmlFor = "import-platform";
    this.platform = make("input", "import-platform");
    this.platform.type = "text";
    this.platform.id = "import-platform";
    this.platform.autocomplete = "off";
    this.platform.spellcheck = false;
    this.platform.placeholder = "linux/arm64/v8";
    this.platform.setAttribute("aria-describedby", "import-platform-help import-platform-error");
    this.platform.addEventListener("input", () => this.clearError(this.platform, this.platformError));
    const platformHelp = make("p", "import-help", "OS/ARCH[/VARIANT], for example linux/arm64/v8. Needed when neither the SBOM nor the scan records the platform.");
    platformHelp.id = "import-platform-help";
    this.platformError = make("p", "field-error");
    this.platformError.id = "import-platform-error";
    this.platformError.hidden = true;
    platformField.append(platformLabel, this.platform, platformHelp, this.platformError);
    const limit = make("p", "import-help", `Each file can be at most ${IMPORT_FILE_LIMIT_TEXT}.`);
    limit.id = "import-limit";
    const actions = make("div", "import-actions");
    this.importButton = make("button", "primary-button", "Import");
    this.importButton.type = "submit";
    const back = make("button", "review-secondary", "Back");
    back.type = "button";
    back.addEventListener("click", () => this.close());
    actions.append(this.importButton, back);
    this.progress = make("div", "import-progress");
    this.progress.hidden = true;
    this.progress.tabIndex = -1;
    const bar = make("progress");
    bar.setAttribute("aria-label", "Importing");
    this.progress.append(bar, make("span", "", "Importing… This can take a few seconds."));
    this.status = make("p", "import-status");
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    form.append(platformField, limit, actions, this.progress, this.status);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      void this.submit();
    });
    this.alert = make("div", "import-alert");
    this.alert.setAttribute("role", "alert");
    this.alert.tabIndex = -1;
    this.alert.hidden = true;
    this.result = make("section", "import-result");
    this.result.setAttribute("aria-labelledby", "import-result-heading");
    this.result.hidden = true;
    const regions = (event: Event) => this.handleClick(event.target as Element | null);
    this.alert.addEventListener("click", regions);
    this.result.addEventListener("click", regions);
    card.append(form, this.alert, this.result);
    this.element.append(card);
  }

  /** Shows the screen in place of `from` (the home screen), keeping what was chosen before. */
  open(from: HTMLElement, returnFocus?: HTMLElement): void {
    this.from = from;
    this.returnFocus = returnFocus;
    from.hidden = true;
    this.element.hidden = false;
    this.title.focus();
  }

  /** Back to the screen it was opened from; a running import is cancelled. */
  close(): void {
    this.request?.abort();
    this.element.hidden = true;
    if (this.from) this.from.hidden = false;
    this.returnFocus?.focus();
  }

  /** Leaves for the workspace, which the project now shows. */
  hide(): void {
    this.request?.abort();
    this.element.hidden = true;
  }

  chooseFile(kind: FileKind, file: File | undefined, clearInput = false): void {
    const field = this.fields[kind];
    if (clearInput) field.input.value = "";
    field.file = file;
    field.chosen.textContent = file ? `Chosen: ${file.name} (${sizeText(file.size)})` : "";
    if (field.clear) field.clear.hidden = !file;
    this.clearError(field.input, field.error);
    if (file && file.size > IMPORT_FILE_LIMIT_BYTES) {
      this.showFieldError(field.input, field.error, `${file.name} is ${sizeText(file.size)}; each file can be at most ${IMPORT_FILE_LIMIT_TEXT}.`);
    }
  }

  usePlatform(value: string): void {
    this.platform.value = value;
    this.clearError(this.platform, this.platformError);
    this.platform.focus();
    this.status.textContent = `The platform is set to ${value}. Import again to use it.`;
  }

  async submit(): Promise<void> {
    if (this.busy || this.unavailable) return;
    const sbom = this.fields.sbom.file;
    const scan = this.fields.scan.file;
    const problems: string[] = [];
    if (!sbom) problems.push(this.showFieldError(this.fields.sbom.input, this.fields.sbom.error, "Choose the SBOM file to import."));
    for (const kind of ["sbom", "scan"] as const) {
      const file = this.fields[kind].file;
      if (file && file.size > IMPORT_FILE_LIMIT_BYTES) {
        problems.push(this.showFieldError(this.fields[kind].input, this.fields[kind].error, `${file.name} is ${sizeText(file.size)}; each file can be at most ${IMPORT_FILE_LIMIT_TEXT}.`));
      }
    }
    const platformError = platformProblem(this.platform.value);
    if (platformError) problems.push(this.showFieldError(this.platform, this.platformError, platformError));
    if (problems.length || !sbom) {
      this.showAlert(html`<p>Fix ${problems.length === 1 ? "this" : "these"} before importing:</p><ul>${problems.map((problem) => html`<li>${problem}</li>`)}</ul>`);
      return;
    }
    this.setBusy("import");
    this.clearAlert();
    this.result.hidden = true;
    this.imported = undefined;
    const controller = new AbortController();
    this.request = controller;
    try {
      const [sbomBytes, scanBytes] = await Promise.all([fileBase64(sbom), scan ? fileBase64(scan) : Promise.resolve(null)]);
      const result = await this.options.client.importSbom({
        sbom: { name: sbom.name, base64: sbomBytes },
        scan: scan && scanBytes !== null ? { name: scan.name, base64: scanBytes } : null,
        platform: this.platform.value.trim() || null,
      }, controller.signal);
      if (controller.signal.aborted) return;
      this.imported = result;
      this.renderResult(result);
      this.status.textContent = `Imported ${result.product ?? "the product"}${result.warnings.length ? ` with ${result.warnings.length} ${result.warnings.length === 1 ? "warning" : "warnings"}` : ""}.`;
    } catch (error) {
      if (controller.signal.aborted) return;
      this.importFailed(error);
    } finally {
      if (this.request === controller) this.request = undefined;
      this.setBusy(undefined);
    }
    if (this.imported) this.focusResult();
    else if (!this.alert.hidden) this.alert.focus();
  }

  async create(): Promise<void> {
    const result = this.imported;
    if (!result || this.busy) return;
    const availability = this.options.projects();
    if (!availability.available) {
      this.status.textContent = `Creating a project is not available: ${availability.reason}`;
      return;
    }
    const nameInput = (this.result as HTMLElement & ParentNode).querySelector?.<HTMLInputElement>("#import-project-name");
    const name = nameInput?.value.trim() || result.suggested_name || "Imported product";
    this.setBusy("create");
    this.clearAlert();
    this.status.textContent = `Creating the project ${name}…`;
    try {
      const opened = await this.options.createProject(name, result.model_text);
      this.status.textContent = opened ? `Created the project ${name}.` : "No project was created.";
    } catch (error) {
      this.showAlert(html`<p>${error instanceof Error ? error.message : String(error)} The imported model is kept on this screen; try again.</p>`);
      this.alert.focus();
    } finally {
      this.setBusy(undefined);
    }
  }

  handleClick(target: Element | null): void {
    const button = target?.closest?.("[data-import-action]");
    const action = button?.getAttribute("data-import-action");
    if (!button || !action) return;
    if (action === "retry") void this.submit();
    else if (action === "create") void this.create();
    else if (action === "use-platform") this.usePlatform(button.getAttribute("data-platform") ?? "");
    else if (action === "focus-platform") this.platform.focus();
  }

  private importFailed(error: unknown): void {
    if (!(error instanceof ImportError)) {
      this.showAlert(html`<p>The import failed unexpectedly: ${error instanceof Error ? error.message : String(error)}. Your files are still chosen.</p>${retry()}`);
      return;
    }
    const kept = "Your files and platform are still chosen.";
    switch (error.code) {
      case "import_refused": {
        const platforms = suggestedPlatforms([error.message, ...error.notes]);
        this.showAlert(html`<p><strong>The importer refused the files:</strong> ${error.message}</p>
${error.notes.length ? html`<ul class="import-notes">${error.notes.map((note) => html`<li>${note}</li>`)}</ul>` : ""}
<p>${kept} Fix them, or the platform field, and import again.</p>${platformButtons(platforms)}
<button type="button" class="review-secondary" data-import-action="focus-platform">Go to the platform field</button>`);
        return;
      }
      case "validation_error": {
        for (const field of error.fields) {
          if (field.field === "platform") this.showFieldError(this.platform, this.platformError, field.message);
          else if (field.field === "sbom" || field.field === "scan") this.showFieldError(this.fields[field.field].input, this.fields[field.field].error, field.message);
        }
        this.showAlert(html`<p>The engine could not read the request: ${error.message}</p>${error.fields.length ? html`<ul>${error.fields.map((field) => html`<li>${fieldLabel(field.field)}: ${field.message}</li>`)}</ul>` : ""}<p>${kept}</p>`);
        return;
      }
      case "not_enabled":
      case "not_found":
        this.unavailable = error.message;
        this.setBusy(undefined);
        this.showAlert(html`<p><strong>Importing is not available in this app:</strong> ${error.message}</p>
<p>The engine must be started with importing turned on (tmodel serve --enable-import). For now, import from a terminal with tmodel import-sbom SBOM --scan SCAN --platform OS/ARCH -o MODEL.yaml.</p>`);
        return;
      case "busy":
        this.showAlert(html`<p>${error.message} Another import is still running. ${kept} Try again in a moment.</p>${retry()}`);
        return;
      case "request_timeout":
        this.showAlert(html`<p>${error.message} The files did not reach the engine in time. ${kept}</p>${retry()}`);
        return;
      case "network_error":
        this.showAlert(html`<p>${error.message} If a file is very large, the engine may have refused it before reading it. ${kept}</p>${retry()}`);
        return;
      case "permission_denied":
        this.showAlert(html`<p>The engine refused the import: ${error.message} ${kept}</p>`);
        return;
      default:
        this.showAlert(html`<p>The import failed: ${error.message} ${kept}</p>${retry()}`);
    }
  }

  private renderResult(result: ImportResult): void {
    const extra = Object.entries(result.counts).filter(([name]) => !(MAIN_COUNTS as readonly string[]).includes(name));
    const platforms = suggestedPlatforms(result.warnings);
    const availability = this.options.projects();
    this.result.innerHTML = html`<h2 id="import-result-heading" tabindex="-1">Imported ${result.product ?? "a product"}</h2>
<dl class="import-facts"><div><dt>Product</dt><dd>${result.product ?? "Not recorded"}</dd></div><div><dt>Platform</dt><dd>${result.platform ?? "Not recorded"}</dd></div></dl>
<ul class="import-counts">${MAIN_COUNTS.map((name) => html`<li><strong>${result.counts[name] ?? "Not reported"}</strong> ${name}</li>`)}</ul>
${extra.length ? html`<p class="import-help">Also: ${extra.map(([name, count]) => `${count} ${name.replace(/_/g, " ")}`).join(", ")}.</p>` : ""}
${result.warnings.length ? html`<section class="import-warnings" aria-labelledby="import-warnings-heading"><h3 id="import-warnings-heading">${result.warnings.length} ${result.warnings.length === 1 ? "warning" : "warnings"}</h3>
<ul>${result.warnings.map((warning) => html`<li>${warning}</li>`)}</ul>${platformButtons(platforms)}</section>` : html`<p class="import-help">The importer reported no warnings.</p>`}
<details class="import-report"><summary>Import report</summary><pre>${result.report_text}</pre></details>
<div class="import-create">
<label class="import-label" for="import-project-name">Project name</label>
<input id="import-project-name" class="import-platform" type="text" value="${result.suggested_name}" autocomplete="off">
<button type="button" class="primary-button" data-import-action="create"${availability.available ? "" : html` aria-disabled="true" aria-describedby="import-create-help"`}>Create project</button>
<p id="import-create-help" class="import-help">${availability.available
    ? "Starts a project whose original.yaml is this imported model, and opens it at Version 1."
    : `Creating a project is not available: ${availability.reason}`}</p>
</div>`.value;
    this.result.hidden = false;
  }

  private focusResult(): void {
    (this.result as HTMLElement & ParentNode).querySelector?.<HTMLElement>("#import-result-heading")?.focus();
  }

  private setBusy(busy: "import" | "create" | undefined): void {
    const wasFocused = (this.importButton.ownerDocument?.activeElement ?? null) === this.importButton;
    this.busy = busy;
    this.progress.hidden = busy !== "import";
    // The engine runs one import at a time: no second request while one runs.
    this.importButton.disabled = busy !== undefined || this.unavailable !== undefined;
    this.importButton.textContent = busy === "import" ? "Importing…" : "Import";
    this.element.setAttribute("aria-busy", String(busy !== undefined));
    if (busy === "import" && wasFocused) this.progress.focus();
  }

  private showFieldError(input: HTMLElement, error: HTMLElement, message: string): string {
    error.textContent = message;
    error.hidden = false;
    input.setAttribute("aria-invalid", "true");
    return message;
  }

  private clearError(input: HTMLElement, error: HTMLElement): void {
    error.textContent = "";
    error.hidden = true;
    input.removeAttribute("aria-invalid");
  }

  private showAlert(markup: SafeHtml): void {
    this.alert.innerHTML = markup.value;
    this.alert.hidden = false;
  }

  private clearAlert(): void {
    this.alert.innerHTML = "";
    this.alert.hidden = true;
  }
}

function retry(): SafeHtml {
  return html`<button type="button" class="review-secondary" data-import-action="retry">Try the import again</button>`;
}

function platformButtons(platforms: readonly string[]): SafeHtml | string {
  return platforms.length
    ? html`<p class="import-suggestions">${platforms.map((platform) => html`<button type="button" class="review-secondary" data-import-action="use-platform" data-platform="${platform}">Use ${platform}</button> `)}</p>`
    : "";
}

function fieldLabel(field: string): string {
  return field === "sbom" ? "SBOM file" : field === "scan" ? "Vulnerability scan" : field === "platform" ? "Platform" : field;
}

export function sizeText(bytes: number): string {
  if (bytes < 1024) return `${bytes} bytes`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KiB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MiB`;
}

/** The screen as the desktop app builds it: the real engine route, or in a Vite dev server the recorded mock. */
export function createImportScreen(
  documentRoot: Document,
  parameters: URLSearchParams,
  projects: {
    createProject(source: ProjectSource): Promise<boolean>;
    projectsAvailable(): boolean;
    unavailableReason(): string;
  },
): ImportScreen {
  const mock = import.meta.env.DEV && parameters.get("projectSource") === "mock";
  return new ImportScreen({
    documentRoot,
    client: new SbomImportClient(undefined, mock ? importMockFetch : undefined),
    createProject: (name, text) => projects.createProject({ kind: "model-text", name, text }),
    projects: () => ({ available: projects.projectsAvailable(), reason: projects.unavailableReason() }),
    mock,
  });
}
