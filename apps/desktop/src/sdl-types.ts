// The engine's GET /sdl payload (engine/engine/sdl.py, DL-0043). Read-only: the app
// never writes SDL data; selections are decided by a human Review (PROC-0002).

export interface SdlDecision {
  state: string;
  label: string;
  by?: string;
  why?: string;
}

export interface SdlLink {
  name: string;
  href: string;
  kind?: string | null;
}

export interface SdlPracticeItem {
  id: string;
  name: string;
  description: string;
  row: string;
  row_n: number | string;
  status: string;
  owner: string;
  evidence: SdlLink[];
  requirements: SdlLink[];
  due: string[];
  covered: number;
  total: number;
  decision: SdlDecision;
}

export interface SdlPhase {
  code: string;
  name: string;
  items: SdlPracticeItem[];
}

export interface SdlRequirementSource {
  id: string;
  name: string;
  proposal: string;
  rationale: string;
  link: string;
  decision: SdlDecision;
}

export interface SdlProgramNode {
  order: number | null;
  name: string;
  kind: string;
  planned: string;
  actual: string;
  status: string;
  owner: string;
  description: string;
  practices: number;
  name_decision: SdlDecision | null;
}

export interface SdlView {
  file: string;
  proposal: string;
  product: { name: string; description: string };
  program: { name: string; revision?: number | string | null; owner: string; description: string };
  sets: SdlRequirementSource[];
  phases: SdlPhase[];
  nodes: SdlProgramNode[];
  gaps: string[];
  uncovered: string[];
  awaiting_review: { id: string; predicate: string; name: string }[];
}

export interface SdlModel {
  file: string;
  programs?: { id: string; name: string }[];
  error?: string;
}

export interface SdlDataProvider {
  listModels(signal?: AbortSignal): Promise<SdlModel[]>;
  getView(file: string, program?: string, signal?: AbortSignal): Promise<SdlView>;
}
