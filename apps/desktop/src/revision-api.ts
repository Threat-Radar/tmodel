// #290: one project version's views behind the engine's GET routes, so the
// existing providers (report source, Explore graph, risk panel, requirements
// coverage) show a saved version without touching the approved-vector routes.
// HUMAN_REVIEW.md: a project's `file` labels are opaque and must never be sent
// to the legacy GET routes; this adapter answers in memory instead, like the
// browser preview's StaticPreviewApi. Each version gets its own instance, so a
// view built for one version can never read another's data.

import type { RevisionViews } from "./review-contract";
import { REVIEW_MATRIX } from "./review-contract";

const API_ORIGIN = "https://project-version.invalid/";
const LABEL_PREFIX = "project:";

/** The app's own label for one project version. It is never sent to the engine. */
export function projectVersionLabel(projectId: string, versionId: string): string {
  return `${LABEL_PREFIX}${encodeURIComponent(projectId)}@${encodeURIComponent(versionId)}`;
}

export function isProjectVersionLabel(file: string | undefined): boolean {
  return typeof file === "string" && file.startsWith(LABEL_PREFIX);
}

/** What the existing providers take in place of the engine: a base URL and a fetch. */
export interface VersionApi {
  readonly engineBase: string;
  readonly fetch: typeof fetch;
}

/** For a version that is no longer shown: every request fails, none reaches the engine. */
export const CLOSED_VERSION_API: VersionApi = {
  engineBase: API_ORIGIN,
  fetch: () => Promise.resolve(json(404, { error: "This project version is no longer open." })),
};

export class RevisionApi implements VersionApi {
  readonly engineBase = API_ORIGIN;
  readonly fetch: typeof fetch;

  constructor(readonly label: string, readonly views: RevisionViews) {
    this.fetch = (input, init) => Promise.resolve(this.answer(input, init));
  }

  private answer(input: RequestInfo | URL, init?: RequestInit): Response {
    const method = (init?.method ?? (input instanceof Request ? input.method : "GET")).toUpperCase();
    if (method !== "GET") return json(405, { error: "project version views are read-only here" });
    const url = new URL(typeof input === "string" ? input : input instanceof URL ? input.href : input.url);
    if (url.origin !== new URL(API_ORIGIN).origin) return json(400, { error: "unexpected project version origin" });
    if (url.searchParams.get("file") !== this.label) return json(404, { error: "this project version is not open" });
    const { views } = this;
    if (url.pathname === "/graph") return json(200, { ...views.graph, file: this.label });
    if (url.pathname === "/risk") {
      if (url.searchParams.get("matrix") !== REVIEW_MATRIX || url.searchParams.has("goal")) {
        return json(400, { error: "project versions are calculated with the Annex H Table H.8 example profile" });
      }
      return json(200, { ...views.risk, file: this.label });
    }
    if (url.pathname === "/attack-paths") {
      const goal = url.searchParams.get("goal");
      // Only the threat list: the per-goal answers carry everything the views read.
      if (goal === null) return json(200, { file: this.label, threats: views.attackPaths.map((response) => response.goal) });
      const response = views.attackPaths.find((candidate) => candidate.goal === goal);
      return response ? json(200, { ...response, file: this.label }) : json(404, { error: `unknown goal: ${goal}` });
    }
    // Coverage and every other route are not part of a saved version's views.
    return json(404, { error: "not available for project versions" });
  }
}

function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}
