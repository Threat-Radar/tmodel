import { describe, expect, it, vi } from "vitest";
import type { EngineState } from "./engine";
import { GraphStartup, MAX_GRAPH_START_ATTEMPTS } from "./graph-startup";

const CONNECTED: EngineState = {
  kind: "connected",
  health: { status: "ok", engine: "tmodel", version: "0.1.0" },
};
const UNREACHABLE: EngineState = { kind: "unreachable", error: "connection refused" };

function harness(start: () => Promise<void>, requiresEngine = true) {
  const callbacks = {
    start: vi.fn(start),
    onWaiting: vi.fn(),
    onFailure: vi.fn<(error: unknown, willRetry: boolean) => void>(),
    onManualRetryAvailable: vi.fn<(available: boolean) => void>(),
  };
  return { callbacks, startup: new GraphStartup(callbacks, requiresEngine) };
}

describe("knowledge-graph startup", () => {
  it("waits without requesting the graph while the engine is unavailable at startup", async () => {
    const { callbacks, startup } = harness(async () => undefined);

    await startup.engineStateChanged(UNREACHABLE);
    await startup.engineStateChanged(UNREACHABLE);

    expect(callbacks.start).not.toHaveBeenCalled();
    expect(callbacks.onWaiting).toHaveBeenCalledTimes(2);
    expect(startup.started).toBe(false);
  });

  it("starts the graph once the engine becomes available", async () => {
    const { callbacks, startup } = harness(async () => undefined);

    await startup.engineStateChanged(UNREACHABLE);
    await startup.engineStateChanged(CONNECTED);

    expect(callbacks.start).toHaveBeenCalledTimes(1);
    expect(startup.started).toBe(true);
  });

  it("starts only once across repeated successful health checks", async () => {
    const { callbacks, startup } = harness(async () => undefined);

    for (let poll = 0; poll < 5; poll += 1) await startup.engineStateChanged(CONNECTED);
    await startup.engineStateChanged(UNREACHABLE);
    await startup.engineStateChanged(CONNECTED);

    expect(callbacks.start).toHaveBeenCalledTimes(1);
    expect(callbacks.onWaiting).not.toHaveBeenCalled();
  });

  it("shares one in-flight start between concurrent health checks", async () => {
    let finish!: () => void;
    const { callbacks, startup } = harness(() => new Promise<void>((resolve) => { finish = resolve; }));

    const first = startup.engineStateChanged(CONNECTED);
    const second = startup.engineStateChanged(CONNECTED);
    const third = startup.engineStateChanged(CONNECTED);
    finish();
    await Promise.all([first, second, third]);

    expect(callbacks.start).toHaveBeenCalledTimes(1);
    expect(startup.started).toBe(true);
  });

  it("retries after an initial graph failure and recovers on a later health check", async () => {
    let calls = 0;
    const { callbacks, startup } = harness(async () => {
      calls += 1;
      if (calls === 1) throw new Error("Engine request failed: HTTP 503");
    });

    await startup.engineStateChanged(CONNECTED);
    expect(startup.started).toBe(false);
    expect(callbacks.onFailure).toHaveBeenCalledWith(expect.any(Error), true);

    await startup.engineStateChanged(CONNECTED);
    expect(startup.started).toBe(true);
    expect(callbacks.start).toHaveBeenCalledTimes(2);
  });

  it("stops requesting after a bounded number of persistent failures", async () => {
    const { callbacks, startup } = harness(async () => {
      throw new Error("cannot read model");
    });

    for (let poll = 0; poll < MAX_GRAPH_START_ATTEMPTS + 5; poll += 1) {
      await startup.engineStateChanged(CONNECTED);
    }

    expect(callbacks.start).toHaveBeenCalledTimes(MAX_GRAPH_START_ATTEMPTS);
    expect(callbacks.onFailure).toHaveBeenLastCalledWith(expect.any(Error), false);
  });

  it("allows a fresh set of attempts after the engine restarts", async () => {
    let healthy = false;
    const { callbacks, startup } = harness(async () => {
      if (!healthy) throw new Error("transient");
    });

    for (let poll = 0; poll < MAX_GRAPH_START_ATTEMPTS; poll += 1) {
      await startup.engineStateChanged(CONNECTED);
    }
    await startup.engineStateChanged(CONNECTED);
    expect(callbacks.start).toHaveBeenCalledTimes(MAX_GRAPH_START_ATTEMPTS);

    healthy = true;
    await startup.engineStateChanged(UNREACHABLE);
    await startup.engineStateChanged(CONNECTED);

    expect(callbacks.start).toHaveBeenCalledTimes(MAX_GRAPH_START_ATTEMPTS + 1);
    expect(startup.started).toBe(true);
  });

  it("starts fixture data without consulting the engine", async () => {
    const { callbacks, startup } = harness(async () => undefined, false);

    await startup.engineStateChanged(UNREACHABLE);
    expect(callbacks.onWaiting).not.toHaveBeenCalled();
    expect(callbacks.start).not.toHaveBeenCalled();

    await startup.startNow();
    await startup.engineStateChanged(CONNECTED);

    expect(callbacks.start).toHaveBeenCalledTimes(1);
    expect(startup.started).toBe(true);
  });

  it("offers a manual retry, and makes no further requests, after three failures while connected", async () => {
    const { callbacks, startup } = harness(async () => {
      throw new Error("cannot read model");
    });

    for (let poll = 0; poll < MAX_GRAPH_START_ATTEMPTS; poll += 1) {
      await startup.engineStateChanged(CONNECTED);
    }
    expect(callbacks.onManualRetryAvailable).toHaveBeenLastCalledWith(true);
    expect(callbacks.onManualRetryAvailable.mock.calls.filter(([available]) => available))
      .toHaveLength(1);

    for (let poll = 0; poll < 10; poll += 1) await startup.engineStateChanged(CONNECTED);
    expect(callbacks.start).toHaveBeenCalledTimes(MAX_GRAPH_START_ATTEMPTS);
    expect(callbacks.onManualRetryAvailable).toHaveBeenLastCalledWith(true);
  });

  it("recovers through a manual retry without restarting automatic attempts", async () => {
    let fixed = false;
    const { callbacks, startup } = harness(async () => {
      if (!fixed) throw new Error("cannot read model");
    });
    for (let poll = 0; poll < MAX_GRAPH_START_ATTEMPTS; poll += 1) {
      await startup.engineStateChanged(CONNECTED);
    }

    fixed = true;
    await startup.retryNow();

    expect(startup.started).toBe(true);
    expect(callbacks.start).toHaveBeenCalledTimes(MAX_GRAPH_START_ATTEMPTS + 1);
    expect(callbacks.onManualRetryAvailable).toHaveBeenLastCalledWith(false);
    for (let poll = 0; poll < 5; poll += 1) await startup.engineStateChanged(CONNECTED);
    await startup.retryNow();
    expect(callbacks.start).toHaveBeenCalledTimes(MAX_GRAPH_START_ATTEMPTS + 1);
  });

  it("keeps the manual retry available after a failed manual attempt", async () => {
    let failures = MAX_GRAPH_START_ATTEMPTS + 1;
    const { callbacks, startup } = harness(async () => {
      if (failures > 0) {
        failures -= 1;
        throw new Error(`still failing (${failures})`);
      }
    });
    for (let poll = 0; poll < MAX_GRAPH_START_ATTEMPTS; poll += 1) {
      await startup.engineStateChanged(CONNECTED);
    }

    await startup.retryNow();
    expect(startup.started).toBe(false);
    expect(callbacks.onFailure).toHaveBeenLastCalledWith(expect.any(Error), false);
    expect(callbacks.onManualRetryAvailable).toHaveBeenLastCalledWith(true);
    // A failed manual attempt does not bring automatic attempts back.
    for (let poll = 0; poll < 5; poll += 1) await startup.engineStateChanged(CONNECTED);
    expect(callbacks.start).toHaveBeenCalledTimes(MAX_GRAPH_START_ATTEMPTS + 1);

    await startup.retryNow();
    expect(startup.started).toBe(true);
    expect(callbacks.onManualRetryAvailable).toHaveBeenLastCalledWith(false);
  });

  it("shares one request between repeated retry clicks", async () => {
    let finish!: () => void;
    let attempts = 0;
    const { callbacks, startup } = harness(() => {
      attempts += 1;
      if (attempts <= MAX_GRAPH_START_ATTEMPTS) return Promise.reject(new Error("down"));
      return new Promise<void>((resolve) => { finish = resolve; });
    });
    for (let poll = 0; poll < MAX_GRAPH_START_ATTEMPTS; poll += 1) {
      await startup.engineStateChanged(CONNECTED);
    }

    const clicks = [startup.retryNow(), startup.retryNow(), startup.retryNow()];
    await startup.engineStateChanged(CONNECTED);
    finish();
    await Promise.all(clicks);

    expect(callbacks.start).toHaveBeenCalledTimes(MAX_GRAPH_START_ATTEMPTS + 1);
    expect(startup.started).toBe(true);
  });

  it("withdraws the manual retry while the engine is down and retries automatically on reconnect", async () => {
    let fixed = false;
    const { callbacks, startup } = harness(async () => {
      if (!fixed) throw new Error("cannot read model");
    });
    for (let poll = 0; poll < MAX_GRAPH_START_ATTEMPTS; poll += 1) {
      await startup.engineStateChanged(CONNECTED);
    }
    expect(callbacks.onManualRetryAvailable).toHaveBeenLastCalledWith(true);

    await startup.engineStateChanged(UNREACHABLE);
    expect(callbacks.onManualRetryAvailable).toHaveBeenLastCalledWith(false);
    expect(callbacks.onWaiting).toHaveBeenCalledTimes(1);

    fixed = true;
    await startup.engineStateChanged(CONNECTED);
    expect(startup.started).toBe(true);
    expect(callbacks.start).toHaveBeenCalledTimes(MAX_GRAPH_START_ATTEMPTS + 1);
  });

  it("never offers a manual retry for fixture data", async () => {
    const { callbacks, startup } = harness(async () => {
      throw new Error("fixture bug");
    }, false);

    await startup.startNow();

    expect(callbacks.onFailure).toHaveBeenCalledWith(expect.any(Error), false);
    expect(callbacks.onManualRetryAvailable.mock.calls.some(([available]) => available)).toBe(false);
  });
});
