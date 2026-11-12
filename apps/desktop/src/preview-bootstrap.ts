import { chooseModel, findModel, type ModelCatalogProvider } from "./model-catalog";
import type { ModelListResponse, ModelSummary } from "./model-types";

export const PREVIEW_MODEL_WAITING = "Loading published example models…";
export const PREVIEW_REPORT_WAITING = "Loading published example data…";

interface PreviewChrome {
  body: Pick<HTMLElement, "dataset">;
  banner: Pick<HTMLElement, "hidden">;
  enginePanel: Pick<HTMLElement, "hidden">;
  sdlTab: Pick<HTMLElement, "hidden">;
  sdlPanel: Pick<HTMLElement, "hidden">;
  proposals: Pick<HTMLElement, "hidden">;
  savedViews: Pick<HTMLElement, "hidden">;
  libraryTab: Pick<HTMLElement, "hidden">;
  modelSelect: Pick<HTMLSelectElement, "disabled" | "options">;
  modelStatus: Pick<HTMLElement, "textContent">;
  reportStatus: Pick<HTMLElement, "textContent">;
}

/** Apply the read-only preview chrome before any asynchronous data request. */
export function configurePreviewChrome(elements: PreviewChrome): void {
  elements.banner.hidden = false;
  elements.enginePanel.hidden = true;
  elements.sdlTab.hidden = true;
  elements.sdlPanel.hidden = true;
  elements.proposals.hidden = true;
  elements.savedViews.hidden = true;
  elements.libraryTab.hidden = false;
  elements.body.dataset.appMode = "browser-preview";
  elements.modelSelect.disabled = true;
  if (elements.modelSelect.options[0]) {
    elements.modelSelect.options[0].textContent = PREVIEW_MODEL_WAITING;
  }
  elements.modelStatus.textContent = PREVIEW_MODEL_WAITING;
  elements.reportStatus.textContent = PREVIEW_REPORT_WAITING;
}

interface InitialModelOptions {
  catalog: Pick<ModelCatalogProvider, "listModels">;
  requested?: string | null;
  remembered?: string | null;
  setModels(response: ModelListResponse): void;
  notice(message: string): void;
  empty(): void;
  open(model: ModelSummary): Promise<void>;
}

/**
 * Resolve the catalog and URL choice before opening any model-dependent view.
 * In preview mode `open` is the first operation allowed to construct a graph.
 */
export async function openInitialModel(options: InitialModelOptions): Promise<ModelSummary | undefined> {
  const response = await options.catalog.listModels();
  options.setModels(response);
  const model = chooseModel(response.models, {
    requested: options.requested,
    remembered: options.remembered,
  });
  if (!model) {
    options.empty();
    return undefined;
  }
  if (options.requested && !findModel(response.models, options.requested)) {
    options.notice(`Unknown example model “${options.requested}”; showing ${model.title}.`);
  }
  await options.open(model);
  return model;
}
