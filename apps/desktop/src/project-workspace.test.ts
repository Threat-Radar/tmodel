// #288's workspace, as the app reads it: contract tests against #288's own
// examples (fixtures/model-workspace-contract.json), and the provider that
// joins the host's step to the webview's routes.
import { describe, expect, it } from "vitest";
import contract from "../../../engine/examples/human-review/contract.json";
import workspace from "./fixtures/model-workspace-contract.json";
import revisions from "./fixtures/human-review-revisions.json";
import { NO_HOST_REASON, NO_PROJECT_HOST, type HostProjectStep, type ProjectHost } from "./project-host";
import {
  checkProjectVersions,
  currentVersion,
  EngineProjectWorkspace,
  parseWorkspaceModels,
  parseWorkspaceVersions,
  riskSummaryFromMetadata,
  riskSummaryOf,
  riskSummaryText,
  toProjectVersions,
  versionLabel,
  versionOptionLabel,
  WorkspaceClient,
  type ProjectVersion,
} from "./project-workspace";
import { parseRevisionViews } from "./review-contract";

const TOKEN = "host-token-of-at-least-thirty-two-characters";
const PROJECT = workspace.openModel.response.model_id;
const FILE = workspace.openFile.response.model_id;
const version = (id: string, number: number | null, current: boolean): ProjectVersion => ({
  id, number, description: null, date: null, riskSummary: null, current,
});

/** An engine answering #288's contract examples for the webview's GET routes. */
function engine(statusFor?: (path: string) => number) {
  const calls: { url: URL; init?: RequestInit }[] = [];
  const fetchImpl = (async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(String(input));
    calls.push({ url, init });
    const status = statusFor?.(url.pathname) ?? 200;
    if (status !== 200) {
      const example = workspace.errors.find((item) => item.status === status && item.operation === "listOpenModels");
      return new Response(JSON.stringify(example?.response), { status });
    }
    const body = url.pathname === "/workspace/models" ? workspace.listOpenModels.response
      : url.searchParams.get("model_id") === FILE ? { model_id: FILE, revision: workspace.openFile.response.revision, current_revision: workspace.openFile.response.revision, versions: [workspace.openFile.response.version] }
      : workspace.listVersions.response;
    return new Response(JSON.stringify(body), { status: 200 });
  }) as typeof fetch;
  return { calls, fetchImpl };
}

function host(answer: string | null): ProjectHost & { steps: HostProjectStep[] } {
  const steps: HostProjectStep[] = [];
  return { steps, session: () => TOKEN, hostProjectStep: async (step) => { steps.push(step); return answer; } };
}

describe("#288 workspace contract (the team's design)", () => {
  it("reads the open models and a project's versions as #288 answers them", () => {
    const models = parseWorkspaceModels(workspace.listOpenModels.response);
    expect(models.map((model) => [model.model_id, model.kind, model.editable])).toEqual([
      [PROJECT, "project", true],
      [FILE, "file", false],
      ["project:b3277bb3d6a9ee865f98b7fc0747fb93", "project", true],
    ]);
    const versions = toProjectVersions(models[0], parseWorkspaceVersions(workspace.listVersions.response, PROJECT));
    expect(versions.project).toEqual({ id: PROJECT, name: "Example Threat Model", kind: "project", editable: true });
    expect(versions.versions.map((entry) => [versionOptionLabel(entry), entry.description, entry.date]))
      .toEqual([
        ["Version 1", "Initial model, copied from workspace-example.yaml", "2026-11-27T12:00:00Z"],
        ["Version 2 (Current)", "Reviewed the example path and rated it high", "2026-11-27T12:01:00Z"],
      ]);
    // The summary a version recorded, in the categories it recorded.
    expect(riskSummaryText(versions.versions[1].riskSummary)).toBe("Safety 3 · Financial 4 · Operational 3 · Privacy 1 (recorded with the version)");
    expect(versions.versions[0].riskSummary).toBeNull();
    expect(() => parseWorkspaceVersions(workspace.listVersions.response, FILE)).toThrow(/another model/);
  });

  it("shows a file opened read-only as one opened revision", () => {
    const file = parseWorkspaceModels(workspace.listOpenModels.response)[1];
    const versions = toProjectVersions(file, parseWorkspaceVersions(
      { model_id: FILE, current_revision: file.current_revision, versions: [workspace.openFile.response.version] }, FILE,
    ));
    expect(versions.project.editable).toBe(false);
    expect(versionOptionLabel(currentVersion(versions))).toBe("Opened file");
  });

  it("asks the host for the folder or file, then reads the model by id with the host's token", async () => {
    const { calls, fetchImpl } = engine();
    const projectHost = host(PROJECT);
    const provider = new EngineProjectWorkspace(projectHost, new WorkspaceClient({ current: () => ({ token: TOKEN }) }, "http://127.0.0.1:47811", fetchImpl));
    expect(provider.status()).toEqual({ available: true });
    const opened = await provider.openProject();
    expect(projectHost.steps).toEqual([{ kind: "open-project" }]);
    expect(opened?.project.id).toBe(PROJECT);
    expect(calls.map((call) => `${call.url.pathname}${call.url.search}`)).toEqual(["/workspace/models", `/workspace/versions?model_id=${encodeURIComponent(PROJECT)}`]);
    for (const call of calls) {
      expect(call.init?.headers).toEqual({ Authorization: `Bearer ${TOKEN}` });
      expect(call.init?.method ?? "GET").toBe("GET");
      expect(String(call.url)).not.toContain(TOKEN);
    }
    await provider.createProject({ kind: "example", file: "mvp-01-software-doc-service.yaml", title: "Doc service" });
    await provider.createProject({ kind: "file", modelId: FILE });
    await provider.createProject({ kind: "model-text", name: "alpine", text: "# STARTER MODEL" });
    await provider.openThreatModel();
    expect(projectHost.steps.slice(1)).toEqual([
      { kind: "create-project", from: { source_file: "mvp-01-software-doc-service.yaml" } },
      { kind: "create-project", from: { model_id: FILE } },
      { kind: "create-project", from: { model_text: "# STARTER MODEL", name: "alpine" } },
      { kind: "open-file" },
    ]);
  });

  it("opens nothing when the picker is cancelled, and nothing at all without the host", async () => {
    const { calls, fetchImpl } = engine();
    const client = new WorkspaceClient({ current: () => ({ token: TOKEN }) }, "http://127.0.0.1:47811", fetchImpl);
    expect(await new EngineProjectWorkspace(host(null), client).openProject()).toBeNull();
    expect(calls).toEqual([]);
    const none = new EngineProjectWorkspace(NO_PROJECT_HOST, client);
    expect(none.status()).toEqual({ available: false, reason: NO_HOST_REASON });
    await expect(none.openProject()).rejects.toThrow(NO_HOST_REASON);
  });

  it("reads #288's error envelope: no token, projects off, or an unexpected failure", async () => {
    for (const [status, kind] of [[403, "permission"], [503, "unavailable"], [500, "unexpected"]] as const) {
      const { fetchImpl } = engine(() => status);
      const client = new WorkspaceClient({ current: () => ({ token: TOKEN }) }, "http://127.0.0.1:47811", fetchImpl);
      await expect(client.listModels()).rejects.toMatchObject({ kind });
    }
    const noToken = new WorkspaceClient({ current: () => undefined }, "http://127.0.0.1:47811", engine().fetchImpl);
    await expect(noToken.listModels()).rejects.toMatchObject({ kind: "permission" });
  });
});

describe("versions and risk summaries", () => {
  it("names versions as the team's design does, from the workspace's number", () => {
    expect(versionLabel(version("v004", 4, true))).toBe("Version 4");
    expect(versionOptionLabel(version("v004", 4, true))).toBe("Version 4 (Current)");
    expect(versionOptionLabel(version("v003", 3, false))).toBe("Version 3");
    // An opaque id is shown as it is, never parsed for a number.
    expect(versionLabel(version("v005", null, true))).toBe("Version v005");
  });

  it("refuses a version list without exactly one current version or with repeated ids", () => {
    const project = { id: "p", name: "Project", kind: "project" as const, editable: true };
    expect(() => checkProjectVersions({ project, versions: [] })).toThrow();
    expect(() => checkProjectVersions({ project, versions: [version("v001", 1, false)] })).toThrow();
    expect(() => checkProjectVersions({ project, versions: [version("v001", 1, true), version("v001", 2, true)] })).toThrow();
    expect(currentVersion(checkProjectVersions({ project, versions: [version("v001", 1, false), version("v002", 2, true)] })).id).toBe("v002");
  });

  it("summarises a version's risk in the engine's own impact categories", () => {
    const before = riskSummaryOf(parseRevisionViews(revisions.refresh_r1.response, { model_id: "local:one" }).risk);
    const after = riskSummaryOf(parseRevisionViews(contract.save.response, { model_id: "local:one" }).risk);
    expect(before.categories.map((entry) => entry.category)).toEqual(["safety", "financial", "operational", "privacy"]);
    expect(riskSummaryText(before)).toBe("Safety 3 · Financial 2 · Operational 2 · Privacy 1 (highest of 1 assessment)");
    expect(riskSummaryText(after)).toBe("Safety 5 · Financial 4 · Operational 3 · Privacy 4 (highest of 1 assessment)");
    expect(riskSummaryText(null)).toBe("Not recorded");
    expect(riskSummaryText({ categories: [], assessments: 0, incomplete: 0 })).toBe("No risk assessments");
    // A recorded summary in any other shape is not shown as one.
    expect(riskSummaryFromMetadata({ matrix: "annex-h-table-h8" })).toBeNull();
    expect(riskSummaryFromMetadata({ derived_risk: { safety: "high" } })).toBeNull();
  });
});
