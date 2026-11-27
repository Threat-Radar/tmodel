// #290: the desktop client for #289's opt-in review operations. Every request
// is a JSON POST with the host-issued bearer session (engine/HUMAN_REVIEW.md).
// The token is only ever sent in the Authorization header: never logged, never
// put in a URL, an error message or the page.

import { DEFAULT_ENGINE_URL } from "./engine";
import {
  malformed,
  parseReviewContext,
  parseRevisionViews,
  ReviewApiError,
  reviewErrorFromResponse,
  type ContextRequest,
  type RefreshRequest,
  type ReviewContext,
  type RevisionViews,
  type SaveRequest,
} from "./review-contract";

/** A session the trusted desktop host issued for one verified reviewer. */
export interface ReviewSession {
  readonly token: string;
}

/** Where the client finds the host's session; none means the app stays read-only. */
export interface ReviewSessionSource {
  current(): ReviewSession | undefined;
}

/**
 * The host does not deliver a review session yet (HUMAN_REVIEW.md, integration
 * step 2), so the normal desktop launch has none and shows no review controls.
 */
export const NO_REVIEW_SESSION: ReviewSessionSource = { current: () => undefined };

export class ReviewApiClient {
  constructor(
    private readonly session: ReviewSessionSource,
    private readonly baseUrl: string = DEFAULT_ENGINE_URL,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
  ) {}

  get hasSession(): boolean {
    return this.session.current() !== undefined;
  }

  async getReviewContext(request: ContextRequest, signal?: AbortSignal): Promise<ReviewContext> {
    return parseReviewContext(await this.post("/reviews/context", request, signal), request);
  }

  /** Every view of exactly `request.revision`, never silently the latest. */
  async refreshModel(request: RefreshRequest, signal?: AbortSignal): Promise<RevisionViews> {
    const body = await this.post("/reviews/refresh", request, signal);
    return parseRevisionViews(body, { model_id: request.model_id, revision: request.revision });
  }

  /**
   * The one atomic save: reviews, annotations and ratings together. It is never
   * aborted, because its outcome decides whether the input is still unsaved.
   */
  async saveModelChanges(request: SaveRequest): Promise<RevisionViews> {
    const body = await this.post("/reviews/changes", request);
    return parseRevisionViews(body, { model_id: request.model_id, notRevision: request.expected_revision });
  }

  private async post(path: string, payload: object, signal?: AbortSignal): Promise<unknown> {
    const session = this.session.current();
    if (!session) {
      throw new ReviewApiError("permission_denied", "This app has no verified review session, so the model stays read-only.");
    }
    let response: Response;
    try {
      response = await this.fetchImpl(new URL(path, `${this.baseUrl.replace(/\/$/, "")}/`), {
        method: "POST",
        headers: { Authorization: `Bearer ${session.token}`, "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal,
      });
    } catch (error) {
      if (isAbort(error)) throw error;
      throw new ReviewApiError("network_error", "Could not reach the local engine.");
    }
    let body: unknown;
    try {
      body = await response.json();
    } catch (error) {
      if (isAbort(error)) throw error;
      if (!response.ok) throw reviewErrorFromResponse(response.status, undefined);
      throw malformed("it is not JSON");
    }
    if (!response.ok) throw reviewErrorFromResponse(response.status, body);
    return body;
  }
}

export function isAbort(error: unknown): boolean {
  return typeof error === "object" && error !== null && (error as { name?: unknown }).name === "AbortError";
}
