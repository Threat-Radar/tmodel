// Engine transport types shared by the app and the static Pages renderer (#208).
// Types only: Node's type stripping erases this module's imports entirely.

import type { AttackPathResponse, GraphProperties } from "./graph-types";

/** One entry of the engine's `/models` list (engine/core.py `list_models`). */
export interface ModelSummary {
  id: string;
  /** What `/graph?file=` accepts: a file name inside the approved model directory. */
  file: string;
  title: string;
  description: string | null;
  kind: string;
  kind_label: string;
  counts: Readonly<Record<string, number>>;
  reviewed_threats: number;
}

export interface ModelListProblem {
  file: string;
  error: string;
}

export interface ModelListResponse {
  count: number;
  models: readonly ModelSummary[];
  problems: readonly ModelListProblem[];
}

/** The engine's storage-neutral `/graph` DTO (engine/model_graph.py). */
export interface EngineGraphNode {
  id: string;
  domain_type: string;
  label: string;
  properties: GraphProperties;
}

export interface EngineGraphEdge {
  id: string;
  source: string;
  target: string;
  relationship_type: string;
  properties: GraphProperties;
}

export interface EngineGraphResponse {
  file: string;
  nodes: readonly EngineGraphNode[];
  edges: readonly EngineGraphEdge[];
}

/** One threat whose attack paths the engine could not compute; `goal` is null when the threat list itself failed. */
export interface AttackPathFailure {
  goal: string | null;
  message: string;
}

/** Attack paths per threat, with the threats that failed kept apart rather than failing them all. */
export interface AttackPathResults {
  responses: AttackPathResponse[];
  failures: AttackPathFailure[];
}

/** Everything one model report is built from: the same engine responses in the app and on Pages. */
export interface ModelReportInput {
  model: ModelSummary;
  graph: EngineGraphResponse;
  attackPaths: readonly AttackPathResponse[];
  /**
   * Threats whose `/attack-paths` answer failed (app only; the Pages build
   * stops instead). The report says what is missing rather than looking complete.
   */
  attackPathFailures?: readonly AttackPathFailure[];
}
