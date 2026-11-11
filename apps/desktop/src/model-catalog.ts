// The example models a reader can open (#208): the engine's `/models` list,
// which model to open first, and the model picker <select>.

import { DEFAULT_ENGINE_URL } from "./engine";
import { requestEngineJson } from "./engine-graph-provider";
import type { ModelListResponse, ModelSummary } from "./model-types";

/** Where the last model a reader opened is remembered (a per-window convenience only). */
export const MODEL_STORAGE_KEY = "tmodel.selected-model";

export interface ModelCatalogProvider {
  listModels(): Promise<ModelListResponse>;
}

export class EngineModelCatalogProvider implements ModelCatalogProvider {
  constructor(
    private readonly baseUrl = DEFAULT_ENGINE_URL,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
  ) {}

  listModels(): Promise<ModelListResponse> {
    return requestEngineJson<ModelListResponse>(this.baseUrl, "/models", {}, this.fetchImpl);
  }
}

/**
 * The model to open: the one the URL asks for (`?model=` id or `?file=` file
 * name, a developer switch), else the one last opened, else the first listed.
 * A request for a model that is not listed is ignored, never guessed at.
 */
export function chooseModel(
  models: readonly ModelSummary[],
  { requested, remembered }: { requested?: string | null; remembered?: string | null } = {},
): ModelSummary | undefined {
  return findModel(models, requested) ?? findModel(models, remembered) ?? models[0];
}

export function findModel(models: readonly ModelSummary[], key: string | null | undefined): ModelSummary | undefined {
  if (!key) return undefined;
  const wanted = key.trim();
  return models.find((model) => model.file === wanted || model.id === wanted);
}

export interface ModelOptionGroup {
  label: string;
  options: { value: string; label: string }[];
}

/** Picker options, grouped by the engine's model family, in the engine's order. */
export function modelOptionGroups(models: readonly ModelSummary[]): ModelOptionGroup[] {
  const groups: ModelOptionGroup[] = [];
  for (const model of models) {
    let group = groups.find((candidate) => candidate.label === model.kind_label);
    if (!group) {
      group = { label: model.kind_label, options: [] };
      groups.push(group);
    }
    group.options.push({ value: model.file, label: model.title });
  }
  return groups;
}

/** A one-line description of a model for the picker's status line. */
export function modelSummaryLine(model: ModelSummary): string {
  const threats = model.counts.threats ?? 0;
  const paths = model.counts.attack_paths ?? 0;
  return `${model.kind_label} · ${threats} ${threats === 1 ? "threat" : "threats"}, `
    + `${model.reviewed_threats} with an accepted review · ${paths} attack ${paths === 1 ? "path" : "paths"}`;
}

export function readRememberedModel(storage: Pick<Storage, "getItem"> | undefined = browserStorage()): string | null {
  try {
    return storage?.getItem(MODEL_STORAGE_KEY) ?? null;
  } catch {
    return null;
  }
}

export function rememberModel(file: string, storage: Pick<Storage, "setItem"> | undefined = browserStorage()): void {
  try {
    storage?.setItem(MODEL_STORAGE_KEY, file);
  } catch {
    // Storage can be unavailable (private window, blocked site data); the picker still works.
  }
}

/** Keep the selected example shareable without reloading the application. */
export function syncModelUrl(
  model: ModelSummary,
  href: string = globalThis.location?.href ?? "https://tmodel.invalid/",
  history: Pick<History, "replaceState"> | undefined = globalThis.history,
): string {
  const url = new URL(href);
  url.searchParams.set("model", model.id);
  url.searchParams.delete("file");
  history?.replaceState(null, "", url);
  return url.href;
}

function browserStorage(): Storage | undefined {
  try {
    return globalThis.localStorage;
  } catch {
    return undefined;
  }
}

/** Fills the model <select> and reports changes. Text only: model titles never become markup. */
export class ModelPicker {
  private models: readonly ModelSummary[] = [];
  // Files the engine could not load. Kept on the status line after a model
  // opens, so the reader still learns that some examples are missing.
  private problemNote = "";
  private externalNote = "";

  constructor(
    private readonly select: HTMLSelectElement,
    private readonly status: HTMLElement,
    private readonly onChange: (model: ModelSummary) => void,
    private readonly documentRoot: Pick<Document, "createElement"> = document,
  ) {
    select.addEventListener("change", () => {
      const model = findModel(this.models, select.value);
      if (model) this.onChange(model);
    });
  }

  setModels(response: ModelListResponse): void {
    this.models = response.models;
    const children: HTMLElement[] = [];
    for (const group of modelOptionGroups(response.models)) {
      const optgroup = this.documentRoot.createElement("optgroup") as HTMLOptGroupElement;
      optgroup.label = group.label;
      for (const entry of group.options) {
        const option = this.documentRoot.createElement("option") as HTMLOptionElement;
        option.value = entry.value;
        option.textContent = entry.label;
        optgroup.append(option);
      }
      children.push(optgroup);
    }
    this.select.replaceChildren(...children);
    this.select.disabled = response.models.length === 0;
    this.problemNote = response.problems.length > 0
      ? `Could not load: ${response.problems.map((problem) => `${problem.file} (${problem.error})`).join("; ")}`
      : "";
    const empty = response.models.length === 0 ? "The engine lists no example models." : "";
    this.status.textContent = [empty, this.problemNote, this.externalNote].filter(Boolean).join(" · ");
  }

  show(model: ModelSummary): void {
    this.select.value = model.file;
    this.status.textContent = [modelSummaryLine(model), this.problemNote, this.externalNote].filter(Boolean).join(" · ");
  }

  notice(message: string): void {
    this.externalNote = message;
    this.status.textContent = [this.status.textContent, message].filter(Boolean).join(" · ");
  }

  waiting(message: string): void {
    this.select.disabled = true;
    this.status.textContent = message;
  }
}
