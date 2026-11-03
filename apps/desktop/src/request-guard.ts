export interface RequestHandle {
  token: number;
  signal: AbortSignal;
}

/** Coordinates a latest-request-wins asynchronous UI operation. */
export class LatestRequestGuard {
  private generation = 0;
  private controller?: AbortController;

  begin(): RequestHandle {
    this.controller?.abort();
    this.generation += 1;
    this.controller = new AbortController();
    return { token: this.generation, signal: this.controller.signal };
  }

  cancel(): void {
    this.generation += 1;
    this.controller?.abort();
    this.controller = undefined;
  }

  isCurrent(request: RequestHandle): boolean {
    return request.token === this.generation && !request.signal.aborted;
  }

  complete(request: RequestHandle): void {
    if (this.isCurrent(request)) this.controller = undefined;
  }
}
