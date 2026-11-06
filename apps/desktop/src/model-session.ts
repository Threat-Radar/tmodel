// Opening an example model in the app (#208). The picker, the model report,
// the attack-path view and the Explore graph follow one choice, and only the
// latest choice is ever shown: a slower answer for an earlier model is dropped.
//
// The report needs the model graph. Attack paths are fetched per threat; one
// that fails leaves the rest of the report usable, and the report says what is
// missing rather than looking complete.

import { buildModelReport, type ModelReport } from "./model-report";
import type { AttackPathResults, EngineGraphResponse, ModelSummary } from "./model-types";

/** Where one model's engine answers come from (EngineGraphDataProvider in the app). */
export interface ModelDataSource {
  getModelGraph(): Promise<EngineGraphResponse>;
  getAttackPathResults(): Promise<AttackPathResults>;
}

export interface ModelSessionViews {
  picker: { show(model: ModelSummary): void };
  report: {
    loading(model: ModelSummary): void;
    show(report: ModelReport): void;
    failed(message: string): void;
  };
  paths: { setReport(report: ModelReport | undefined, message?: string): void };
}

export interface ModelSessionOptions {
  views: ModelSessionViews;
  /** A data source for one model. */
  source(model: ModelSummary): ModelDataSource;
  /** Called as soon as a model is chosen: replace the Explore graph, reset scrolling. */
  modelChanged?(model: ModelSummary): void;
  /** Remembers the choice for the next start (a per-window convenience only). */
  remember?(file: string): void;
}

export class ModelSession {
  private token?: symbol;
  private model?: ModelSummary;

  constructor(private readonly options: ModelSessionOptions) {}

  get current(): ModelSummary | undefined {
    return this.model;
  }

  /** Opens a model; resolves once it is shown, failed, or replaced by a newer choice. */
  async open(model: ModelSummary): Promise<void> {
    const token = Symbol(model.file);
    this.token = token;
    this.model = model;
    const { views } = this.options;
    this.options.remember?.(model.file);
    views.picker.show(model);
    views.report.loading(model);
    views.paths.setReport(undefined, `Loading ${model.title}…`);
    this.options.modelChanged?.(model);

    const source = this.options.source(model);
    const graphRequest = source.getModelGraph();
    const pathRequest = source.getAttackPathResults().catch((error: unknown): AttackPathResults => ({
      responses: [],
      failures: [{ goal: null, message: errorMessage(error) }],
    }));
    let report: ModelReport;
    try {
      const graph = await graphRequest;
      const paths = await pathRequest;
      if (this.token !== token) return; // a newer choice won
      report = buildModelReport({
        model,
        graph,
        attackPaths: paths.responses,
        attackPathFailures: paths.failures,
      });
    } catch (error) {
      if (this.token !== token) return;
      views.report.failed(`Could not open ${model.title}: ${errorMessage(error)}`);
      views.paths.setReport(undefined, `Could not open ${model.title}.`);
      return;
    }
    views.report.show(report);
    views.paths.setReport(report);
  }
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}
