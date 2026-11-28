import { describe, expect, it, vi } from "vitest";
import responses from "./fixtures/sbom-import-responses.json";
import { FakeDocument, target, tick, type FakeElement } from "./fake-dom.test-support";
import { IMPORT_FILE_LIMIT_BYTES, ImportError, importErrorFrom, parseImportResult, type ImportRequest } from "./import-client";
import { ImportScreen } from "./import-screen";

function screen({ importSbom, available = true }: {
  importSbom?: (request: ImportRequest, signal?: AbortSignal) => Promise<ReturnType<typeof parseImportResult>>;
  available?: boolean;
} = {}) {
  const doc = new FakeDocument();
  const home = doc.createElement("main");
  const opener = doc.createElement("button");
  doc.body.append(home);
  const requests: ImportRequest[] = [];
  const client = {
    importSbom: vi.fn(async (request: ImportRequest, signal?: AbortSignal) => {
      requests.push(request);
      return importSbom ? importSbom(request, signal) : parseImportResult(responses.success.body);
    }),
  };
  const createProject = vi.fn(async () => true);
  const view = new ImportScreen({
    documentRoot: doc.as(),
    client,
    createProject,
    projects: () => available ? { available: true, reason: "" } : { available: false, reason: "Local projects are not connected in this build yet." },
  });
  const element = view.element as unknown as FakeElement;
  doc.body.append(element);
  const find = (id: string) => element.querySelector(`#${id}`)!;
  const byClass = (name: string) => element.all().find((child) => child.classList.contains(name))!;
  return {
    doc, home, opener, view, element, client, requests, createProject,
    sbom: find("import-sbom"), scan: find("import-scan"), platform: find("import-platform"),
    alert: () => byClass("import-alert"),
    result: () => byClass("import-result"),
    status: () => byClass("import-status").textContent,
    button: () => element.all().find((child) => child.type === "submit")!,
    progress: () => byClass("import-progress"),
  };
}

const sbomFile = () => new File(['{"bomFormat":"CycloneDX"}'], "alpine-3.24.2.cdx.json", { type: "application/json" });
const scanFile = () => new File(['{"matches":[]}'], "alpine-3.24.2.grype.json", { type: "application/json" });

describe("Import New Product screen", () => {
  it("replaces the home screen and returns to it, focus and all", () => {
    const s = screen();
    s.view.open(s.home.as(), s.opener.as());
    expect(s.home.hidden).toBe(true);
    expect(s.element.hidden).toBe(false);
    expect(s.doc.activeElement?.id).toBe("import-title");
    s.view.close();
    expect(s.home.hidden).toBe(false);
    expect(s.element.hidden).toBe(true);
    expect(s.doc.activeElement).toBe(s.opener);
  });

  it("labels every field and says what the platform is for, in one line", () => {
    const s = screen();
    expect(s.element.all().filter((child) => child.tagName === "label").map((label) => [label.htmlFor, label.textContent])).toEqual([
      ["import-sbom", "SBOM file (required)"],
      ["import-scan", "Vulnerability scan (optional)"],
      ["import-platform", "Platform (optional)"],
    ]);
    expect(s.element.text).toContain("Needed when neither the SBOM nor the scan records the platform.");
    expect(s.platform.getAttribute("aria-describedby")).toBe("import-platform-help import-platform-error");
    expect(s.sbom.getAttribute("aria-required")).toBe("true");
  });

  it("shows a chosen file's name and size, never a path, and refuses a file over the limit before reading it", async () => {
    const s = screen();
    s.view.chooseFile("sbom", sbomFile());
    expect(s.element.text).toContain("Chosen: alpine-3.24.2.cdx.json (25 bytes)");
    const huge = { name: "huge.cdx.json", size: IMPORT_FILE_LIMIT_BYTES + 1, arrayBuffer: vi.fn() } as unknown as File;
    s.view.chooseFile("sbom", huge);
    expect(s.element.text).toContain("each file can be at most 64 MiB");
    expect(s.sbom.getAttribute("aria-invalid")).toBe("true");
    await s.view.submit();
    expect(s.client.importSbom).not.toHaveBeenCalled();
    expect((huge as unknown as { arrayBuffer: ReturnType<typeof vi.fn> }).arrayBuffer).not.toHaveBeenCalled();
    expect(s.alert().hidden).toBe(false);
  });

  it("needs an SBOM and a well-formed platform before it sends anything", async () => {
    const s = screen();
    await s.view.submit();
    expect(s.alert().innerHTML).toContain("Choose the SBOM file to import.");
    s.view.chooseFile("sbom", sbomFile());
    s.platform.value = "arm64";
    await s.view.submit();
    expect(s.alert().innerHTML).toContain("Write the platform as OS/ARCH or OS/ARCH/VARIANT");
    expect(s.client.importSbom).not.toHaveBeenCalled();
  });

  it("imports, shows the product, platform, counts and every warning in full, and offers the suggested platform", async () => {
    const s = screen({ importSbom: async () => parseImportResult(responses.warning.body) });
    s.view.chooseFile("sbom", sbomFile());
    s.view.chooseFile("scan", scanFile());
    s.platform.value = "linux/amd64";
    await s.view.submit();
    expect(s.requests[0]).toEqual({
      sbom: { name: "alpine-3.24.2.cdx.json", base64: btoa('{"bomFormat":"CycloneDX"}') },
      scan: { name: "alpine-3.24.2.grype.json", base64: btoa('{"matches":[]}') },
      platform: "linux/amd64",
    });
    const html = s.result().innerHTML;
    expect(html).toContain("Imported index.docker.io/library/alpine");
    expect(html).toContain("<dd>linux/amd64</dd>");
    for (const count of ["<strong>17</strong> components", "<strong>15</strong> vulnerabilities", "<strong>9</strong> weaknesses", "<strong>45</strong> assertions"]) {
      expect(html).toContain(count);
    }
    expect(html).toContain("16 of the SBOM&#39;s packages are built for arm64 (arch=aarch64) and none for amd64 or the 386 it also runs, though the platform is linux/amd64 (from --platform). Every package is kept as a Component; if the SBOM is of another build, pass its platform, for example --platform linux/arm64/v8");
    expect(html).toContain('data-import-action="use-platform" data-platform="linux/arm64/v8"');
    s.view.handleClick(target({ "data-import-action": "use-platform", "data-platform": "linux/arm64/v8" }));
    expect(s.platform.value).toBe("linux/arm64/v8");
    expect(s.doc.activeElement).toBe(s.platform);
    expect(s.status()).toContain("Import again to use it.");
  });

  it("allows one import at a time and shows progress while it runs", async () => {
    let finish!: () => void;
    const s = screen({ importSbom: () => new Promise((resolve) => { finish = () => resolve(parseImportResult(responses.success.body)); }) });
    s.view.chooseFile("sbom", sbomFile());
    const running = s.view.submit();
    await tick();
    expect(s.button().disabled).toBe(true);
    expect(s.button().textContent).toBe("Importing…");
    expect(s.progress().hidden).toBe(false);
    await s.view.submit();
    expect(s.client.importSbom).toHaveBeenCalledOnce();
    finish();
    await running;
    expect(s.button().disabled).toBe(false);
    expect(s.progress().hidden).toBe(true);
  });

  it("shows a refusal exactly as the importer words it, with its notes, and keeps the choices for a retry", async () => {
    const refusal = importErrorFrom(422, { error: { ...responses.refusal.body.error, notes: ["alpine-3.24.2.cdx.json: the file --force was replacing is kept as MODEL.yaml.bak"] } });
    const s = screen({ importSbom: async () => { throw refusal; } });
    s.view.chooseFile("sbom", sbomFile());
    await s.view.submit();
    const html = s.alert().innerHTML;
    expect(html).toContain("The importer refused the files:");
    expect(html).toContain("alpine-3.24.2.cdx.json: the SBOM does not record which platform its digest names (an index&#39;s digest names every platform of a release). Pass --platform OS/ARCH[/VARIANT], for example --platform linux/arm64/v8");
    expect(html).toContain("the file --force was replacing is kept as MODEL.yaml.bak");
    expect(html).toContain('data-import-action="focus-platform"');
    expect(html).toContain('data-platform="linux/arm64/v8"');
    // The placeholder in "--platform OS/ARCH[/VARIANT]" is not offered as a platform.
    expect(html).not.toContain('data-platform="OS/ARCH"');
    expect(s.doc.activeElement).toBe(s.alert());
    expect(s.element.text).toContain("Chosen: alpine-3.24.2.cdx.json");
    s.view.handleClick(target({ "data-import-action": "use-platform", "data-platform": "linux/arm64/v8" }));
    s.client.importSbom.mockImplementationOnce(async (request) => {
      s.requests.push(request);
      return parseImportResult(responses.success.body);
    });
    await s.view.submit();
    expect(s.requests.pop()?.platform).toBe("linux/arm64/v8");
    expect(s.result().hidden).toBe(false);
  });

  it("marks the fields a validation error names", async () => {
    const s = screen({ importSbom: async () => { throw importErrorFrom(422, { error: { code: "validation_error", message: "Bad request.", fields: [{ field: "scan", message: "The scan is empty." }] } }); } });
    s.view.chooseFile("sbom", sbomFile());
    s.view.chooseFile("scan", scanFile());
    await s.view.submit();
    expect(s.scan.getAttribute("aria-invalid")).toBe("true");
    expect(s.element.text).toContain("The scan is empty.");
    expect(s.alert().innerHTML).toContain("Vulnerability scan: The scan is empty.");
  });

  it("says when importing is not available and keeps the screen disabled", async () => {
    const s = screen({ importSbom: async () => { throw importErrorFrom(503, { error: { code: "not_enabled", message: "This engine was started without importing." } }); } });
    s.view.chooseFile("sbom", sbomFile());
    await s.view.submit();
    expect(s.alert().innerHTML).toContain("Importing is not available in this app:");
    expect(s.alert().innerHTML).toContain("tmodel serve --enable-import");
    expect(s.button().disabled).toBe(true);
    await s.view.submit();
    expect(s.client.importSbom).toHaveBeenCalledOnce();
  });

  it.each([
    [new ImportError("busy", "Another import is still running."), "Another import is still running."],
    [new ImportError("request_timeout", "The body did not arrive within 30 s."), "did not reach the engine in time"],
    [new ImportError("network_error", "Could not reach the local engine, or it closed the connection."), "the engine may have refused it before reading it"],
  ])("offers a retry after %s", async (error, text) => {
    const s = screen({ importSbom: async () => { throw error; } });
    s.view.chooseFile("sbom", sbomFile());
    await s.view.submit();
    expect(s.alert().innerHTML).toContain(text);
    expect(s.alert().innerHTML).toContain('data-import-action="retry"');
    expect(s.button().disabled).toBe(false);
  });

  it("creates a project from the imported model text under the name the user gives", async () => {
    const s = screen();
    s.view.chooseFile("sbom", sbomFile());
    await s.view.submit();
    expect(s.result().innerHTML).toContain('id="import-project-name" class="import-platform" type="text" value="alpine"');
    expect(s.doc.activeElement).toBeNull();
    await s.view.create();
    expect(s.createProject).toHaveBeenCalledWith("alpine", responses.success.body.model_text);
    expect(s.status()).toBe("Created the project alpine.");
  });

  it("says why a project cannot be created when projects are unavailable", async () => {
    const s = screen({ available: false });
    s.view.chooseFile("sbom", sbomFile());
    await s.view.submit();
    expect(s.result().innerHTML).toContain('data-import-action="create" aria-disabled="true"');
    expect(s.result().innerHTML).toContain("Creating a project is not available: Local projects are not connected in this build yet.");
    await s.view.create();
    expect(s.createProject).not.toHaveBeenCalled();
  });

  it("cancels a running import on Back, and never shows its late answer", async () => {
    let finish!: () => void;
    const s = screen({ importSbom: (_request, signal) => new Promise((resolve, reject) => {
      finish = () => signal?.aborted ? reject(new DOMException("aborted", "AbortError")) : resolve(parseImportResult(responses.success.body));
    }) });
    s.view.open(s.home.as(), s.opener.as());
    s.view.chooseFile("sbom", sbomFile());
    const running = s.view.submit();
    await tick();
    s.view.close();
    finish();
    await running;
    expect(s.result().hidden).toBe(true);
    expect(s.alert().hidden).toBe(true);
  });
});
