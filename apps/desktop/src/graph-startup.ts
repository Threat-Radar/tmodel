import type { EngineState } from "./engine";

// Attempts allowed while the engine stays connected. The engine health poll
// spaces them out; the count resets once the engine is seen down and back up,
// so a persistent `/graph` error cannot turn into an unbounded request loop.
export const MAX_GRAPH_START_ATTEMPTS = 3;

export interface GraphStartupCallbacks {
  start(): Promise<void>;
  onWaiting(): void;
  onFailure(error: unknown, willRetry: boolean): void;
  /** Whether a manual retry is useful: automatic attempts are used up. */
  onManualRetryAvailable?(available: boolean): void;
}

/**
 * Starts the knowledge graph once its data source is reachable and retries a
 * failed start on later engine health checks. A started graph is never started
 * again, so repeated polls cannot recreate the Cytoscape view or its elements.
 * Once automatic attempts are used up while the engine stays connected, only
 * a manual retry (or the engine going down and coming back) tries again.
 */
export class GraphStartup {
  private status: "idle" | "starting" | "started" = "idle";
  private attempts = 0;
  private inFlight?: Promise<void>;

  constructor(
    private readonly callbacks: GraphStartupCallbacks,
    private readonly requiresEngine = true,
    private readonly maxAttempts = MAX_GRAPH_START_ATTEMPTS,
  ) {}

  get started(): boolean {
    return this.status === "started";
  }

  /** Starts a graph that does not depend on the engine, such as fixture data. */
  startNow(): Promise<void> {
    return this.attempt();
  }

  /**
   * One user-requested attempt. It shares an in-flight start and does not
   * reset the automatic attempt count, so it cannot restart automatic retries.
   */
  retryNow(): Promise<void> {
    return this.attempt();
  }

  engineStateChanged(state: EngineState): Promise<void> {
    if (!this.requiresEngine || this.status === "started") return Promise.resolve();
    if (state.kind !== "connected") {
      // Automatic attempts resume once the engine is back, so a manual retry
      // against an engine that is down is not offered.
      this.attempts = 0;
      this.callbacks.onManualRetryAvailable?.(false);
      if (this.status === "idle") this.callbacks.onWaiting();
      return this.inFlight ?? Promise.resolve();
    }
    if (this.attempts >= this.maxAttempts) return Promise.resolve();
    return this.attempt();
  }

  private attempt(): Promise<void> {
    if (this.status === "started") return Promise.resolve();
    if (this.inFlight) return this.inFlight;
    this.status = "starting";
    this.attempts += 1;
    this.callbacks.onManualRetryAvailable?.(false);
    const pending = this.callbacks.start().then(
      () => {
        this.status = "started";
      },
      (error: unknown) => {
        this.status = "idle";
        const willRetry = this.requiresEngine && this.attempts < this.maxAttempts;
        this.callbacks.onFailure(error, willRetry);
        if (this.requiresEngine && !willRetry) this.callbacks.onManualRetryAvailable?.(true);
      },
    ).finally(() => {
      this.inFlight = undefined;
    });
    this.inFlight = pending;
    return pending;
  }
}

export interface GraphStartupControls {
  notice: HTMLElement | null;
  retryButton: HTMLButtonElement | null;
}

/**
 * Wires a startup to the source notice and the "Retry graph" button. The
 * button is shown only after automatic attempts are used up while the engine
 * stays connected, and is hidden again as soon as any attempt starts.
 */
export function connectGraphStartup(
  start: () => Promise<void>,
  usesEngine: boolean,
  { notice, retryButton }: GraphStartupControls,
  report: (error: unknown) => void = (error) => console.error("Unable to start the knowledge graph", error),
): GraphStartup {
  const setNotice = (message: string, isError = false) => {
    if (!notice) return;
    notice.textContent = message;
    notice.classList.toggle("is-error", isError);
  };
  const startup = new GraphStartup({
    start,
    onWaiting: () => setNotice(
      "Waiting for the local engine. The graph loads automatically once it is running.",
    ),
    onFailure: (error, willRetry) => {
      report(error);
      const detail = error instanceof Error ? error.message : "unexpected error";
      const next = willRetry
        ? "Retrying automatically."
        : usesEngine
          ? "Use Retry graph to try again."
          : "Check the developer console for details.";
      setNotice(`Unable to load the knowledge graph: ${detail}. ${next}`, true);
    },
    onManualRetryAvailable: (available) => {
      if (!retryButton) return;
      retryButton.hidden = !available;
      retryButton.disabled = !available;
    },
  }, usesEngine);
  if (retryButton) {
    retryButton.onclick = () => {
      setNotice("Retrying the knowledge graph…");
      void startup.retryNow();
    };
  }
  return startup;
}
