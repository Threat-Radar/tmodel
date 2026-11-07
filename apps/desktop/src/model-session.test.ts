import { describe, expect, it, vi } from "vitest";
import mvp01 from "./fixtures/report-input-mvp-01.json";
import mvp02 from "./fixtures/report-input-mvp-02.json";
import type { ModelReport } from "./model-report";
import { ModelSession, type ModelDataSource } from "./model-session";
import type { AttackPathResults, ModelReportInput } from "./model-types";

const [first, second] = [mvp01, mvp02] as unknown as ModelReportInput[];

// The app's model switching (main.ts wires these views to the DOM).
function harness(sources: Map<string, ModelDataSource>) {
  const shown: string[] = [];
  const failed: string[] = [];
  const pathReports: (ModelReport | undefined)[] = [];
  const changed: string[] = [];
  const remembered: string[] = [];
  const session = new ModelSession({
    views: {
      picker: { show: (model) => shown.push(`picker:${model.file}`) },
      report: {
        loading: (model) => shown.push(`loading:${model.file}`),
        show: (report) => shown.push(`report:${report.model.file}`),
        failed: (message) => failed.push(message),
      },
      paths: { setReport: (report) => pathReports.push(report) },
    },
    source: (model) => {
      const source = sources.get(model.file);
      if (!source) throw new Error(`no source for ${model.file}`);
      return source;
    },
    modelChanged: (model) => changed.push(model.file),
    remember: (file) => remembered.push(file),
  });
  return { session, shown, failed, pathReports, changed, remembered };
}

function source(input: ModelReportInput, overrides: Partial<ModelDataSource> = {}): ModelDataSource {
  return {
    getModelGraph: async () => input.graph,
    getAttackPathResults: async () => ({ responses: [...input.attackPaths], failures: [] }),
    ...overrides,
  };
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => { resolve = done; });
  return { promise, resolve };
}

describe("opening a model (#208)", () => {
  it("shows the report, the path view and a fresh Explore graph for the chosen model", async () => {
    const { session, shown, pathReports, changed, remembered } = harness(new Map([
      [first.model.file, source(first)],
    ]));
    await session.open(first.model);
    expect(shown).toEqual([
      `picker:${first.model.file}`,
      `loading:${first.model.file}`,
      `report:${first.model.file}`,
    ]);
    expect(pathReports[pathReports.length - 1]?.model.file).toBe(first.model.file);
    expect(changed).toEqual([first.model.file]);
    expect(remembered).toEqual([first.model.file]);
    expect(session.current).toBe(first.model);
  });

  it("shows only the latest choice when an earlier model answers last (rapid switching)", async () => {
    const slowGraph = deferred<ModelReportInput["graph"]>();
    const { session, shown, pathReports, changed } = harness(new Map([
      [first.model.file, source(first, { getModelGraph: () => slowGraph.promise })],
      [second.model.file, source(second)],
    ]));
    const opening = session.open(first.model);
    await session.open(second.model);
    slowGraph.resolve(first.graph);
    await opening;

    expect(shown.filter((entry) => entry.startsWith("report:"))).toEqual([`report:${second.model.file}`]);
    expect(pathReports[pathReports.length - 1]?.model.file).toBe(second.model.file);
    // Each choice replaced the Explore graph straight away.
    expect(changed).toEqual([first.model.file, second.model.file]);
    expect(session.current).toBe(second.model);
  });

  it("keeps the report usable, and says what is missing, when one threat's attack paths fail", async () => {
    const failingGoal = second.attackPaths[0].goal;
    const results: AttackPathResults = {
      responses: second.attackPaths.slice(1),
      failures: [{ goal: failingGoal, message: "Engine request failed: timed out" }],
    };
    let report: ModelReport | undefined;
    const session = new ModelSession({
      views: {
        picker: { show: () => undefined },
        report: { loading: () => undefined, show: (value) => { report = value; }, failed: vi.fn() },
        paths: { setReport: () => undefined },
      },
      source: () => source(second, { getAttackPathResults: async () => results }),
    });
    await session.open(second.model);

    expect(report?.attackPaths).toHaveLength(2);
    expect(report?.attackPathProblems).toEqual([
      { threat: { id: failingGoal, label: expect.any(String) }, message: "Engine request failed: timed out" },
    ]);
    const affected = report?.attackPaths.filter((row) => row.story.alternativesMissing) ?? [];
    expect(affected.map((row) => row.threat?.id)).toEqual([failingGoal]);
  });

  it("still shows the report when the attack-path requests fail outright", async () => {
    let report: ModelReport | undefined;
    const session = new ModelSession({
      views: {
        picker: { show: () => undefined },
        report: { loading: () => undefined, show: (value) => { report = value; }, failed: vi.fn() },
        paths: { setReport: () => undefined },
      },
      source: () => source(first, { getAttackPathResults: async () => { throw new Error("engine stopped"); } }),
    });
    await session.open(first.model);
    expect(report?.threats).toHaveLength(2);
    expect(report?.attackPathProblems).toEqual([{ threat: null, message: "engine stopped" }]);
    expect(report?.attackPaths.every((row) => row.story.alternativesMissing)).toBe(true);
  });

  it("fails clearly when the model graph itself cannot be read", async () => {
    const { session, failed, pathReports, shown } = harness(new Map([
      [first.model.file, source(first, { getModelGraph: async () => { throw new Error("Engine request failed: not YAML"); } })],
    ]));
    await session.open(first.model);
    expect(failed).toEqual([`Could not open ${first.model.title}: Engine request failed: not YAML`]);
    expect(pathReports[pathReports.length - 1]).toBeUndefined();
    expect(shown.some((entry) => entry.startsWith("report:"))).toBe(false);
  });

  it("does not report an earlier model's failure after a newer model opened", async () => {
    let rejectSlow!: (error: unknown) => void;
    const failing = new Promise<never>((_resolve, reject) => { rejectSlow = reject; });
    const { session, failed } = harness(new Map([
      [first.model.file, source(first, { getModelGraph: () => failing })],
      [second.model.file, source(second)],
    ]));
    const opening = session.open(first.model);
    await session.open(second.model);
    rejectSlow(new Error("late failure"));
    await opening;
    expect(failed).toEqual([]);
  });
});
