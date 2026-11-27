// #290's Import New Product screen: the client for the engine's opt-in
// POST /import/sbom (`tmodel serve --enable-import`), which runs #257's
// importer exactly as `tmodel import-sbom` does. The request carries each
// file's name and exact bytes in base64, so the digest the model records
// matches the file; it never carries a local path. Kept in its own files
// (import-*.ts) so it can ship separately from #290.

import { DEFAULT_ENGINE_URL } from "./engine";

/** The command line's limit for each file, which the engine also applies. */
export const IMPORT_FILE_LIMIT_BYTES = 64 * 1024 * 1024;
export const IMPORT_FILE_LIMIT_TEXT = "64 MiB";

export interface ImportFileBytes {
  /** The file's own name, as the file chooser gives it: never a folder path. */
  name: string;
  base64: string;
}

/** Exactly the route's keys: sbom, scan and platform. */
export interface ImportRequest {
  sbom: ImportFileBytes;
  scan: ImportFileBytes | null;
  platform: string | null;
}

export interface ImportResult {
  model_text: string;
  report_text: string;
  warnings: string[];
  counts: Record<string, number>;
  platform: string | null;
  product: string | null;
  suggested_name: string;
}

export interface ImportFieldError {
  field: string;
  message: string;
}

export class ImportError extends Error {
  constructor(
    readonly code: string,
    message: string,
    readonly details: { notes?: readonly string[]; fields?: readonly ImportFieldError[]; status?: number } = {},
  ) {
    super(message);
    this.name = "ImportError";
  }

  get notes(): readonly string[] {
    return this.details.notes ?? [];
  }

  get fields(): readonly ImportFieldError[] {
    return this.details.fields ?? [];
  }
}

/** The counts the screen always shows, in this order; any others follow. */
export const MAIN_COUNTS = ["components", "vulnerabilities", "weaknesses", "assertions"] as const;

export function parseImportResult(value: unknown): ImportResult {
  const bad = (what: string) => new ImportError("malformed_response", `The engine's import answer could not be read: ${what}.`);
  if (!isRecord(value)) throw bad("not an object");
  if (typeof value.model_text !== "string" || !value.model_text.trim()) throw bad("it has no model");
  if (typeof value.report_text !== "string") throw bad("it has no report");
  if (!Array.isArray(value.warnings) || !value.warnings.every((item) => typeof item === "string")) throw bad("its warnings are not text");
  if (!isRecord(value.counts) || !Object.values(value.counts).every((count) => Number.isInteger(count) && Number(count) >= 0)) {
    throw bad("its counts are not whole numbers");
  }
  for (const key of ["platform", "product"] as const) {
    if (!(value[key] === null || value[key] === undefined || typeof value[key] === "string")) throw bad(`its ${key} is not text`);
  }
  if (typeof value.suggested_name !== "string") throw bad("it suggests no name");
  return {
    model_text: value.model_text,
    report_text: value.report_text,
    warnings: [...value.warnings] as string[],
    counts: { ...value.counts } as Record<string, number>,
    platform: (value.platform ?? null) as string | null,
    product: (value.product ?? null) as string | null,
    suggested_name: value.suggested_name,
  };
}

/** The route's error envelope, as #291's: code, message, and optional notes and fields. */
export function importErrorFrom(status: number, body: unknown): ImportError {
  const error = isRecord(body) && isRecord(body.error) ? body.error : undefined;
  const code = typeof error?.code === "string" ? error.code : "internal_error";
  const message = typeof error?.message === "string" && error.message.trim() ? error.message : `The engine answered HTTP ${status}.`;
  const notes = Array.isArray(error?.notes) ? error.notes.filter((note): note is string => typeof note === "string") : [];
  const fields = Array.isArray(error?.fields)
    ? error.fields.filter((item): item is ImportFieldError => isRecord(item) && typeof item.field === "string" && typeof item.message === "string")
    : [];
  return new ImportError(code, message, { notes, fields, status });
}

/**
 * Platforms the importer's own text suggests ("--platform linux/arm64/v8"), in
 * order, once each. Real platforms are lower case, which leaves out the
 * placeholder "--platform OS/ARCH[/VARIANT]".
 */
export function suggestedPlatforms(texts: readonly string[]): string[] {
  const found: string[] = [];
  for (const text of texts) {
    for (const match of text.matchAll(/--platform\s+([a-z0-9._-]+\/[a-z0-9._-]+(?:\/[a-z0-9._-]+)?)(?![\w[/])/g)) {
      if (!found.includes(match[1])) found.push(match[1]);
    }
  }
  return found;
}

/** OS/ARCH or OS/ARCH/VARIANT; the engine checks the values themselves. */
export function platformProblem(value: string): string | null {
  const text = value.trim();
  if (!text) return null;
  return /^[A-Za-z0-9._-]+\/[A-Za-z0-9._-]+(\/[A-Za-z0-9._-]+)?$/.test(text)
    ? null
    : "Write the platform as OS/ARCH or OS/ARCH/VARIANT, for example linux/arm64/v8.";
}

/**
 * A file's exact bytes in base64, read in chunks whose length is a multiple of
 * three, so the pieces join into one valid base64 text. Never file.text(),
 * which would decode and re-encode the bytes.
 */
export async function fileBase64(file: Pick<Blob, "arrayBuffer">): Promise<string> {
  const bytes = new Uint8Array(await file.arrayBuffer());
  const chunk = 3 * 0x2000;
  const parts: string[] = [];
  for (let offset = 0; offset < bytes.length; offset += chunk) {
    const piece = bytes.subarray(offset, offset + chunk);
    parts.push(btoa(String.fromCharCode.apply(null, piece as unknown as number[])));
  }
  return parts.join("");
}

export class SbomImportClient {
  constructor(
    private readonly baseUrl: string = DEFAULT_ENGINE_URL,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
  ) {}

  async importSbom(request: ImportRequest, signal?: AbortSignal): Promise<ImportResult> {
    const body: ImportRequest = {
      sbom: { name: request.sbom.name, base64: request.sbom.base64 },
      scan: request.scan ? { name: request.scan.name, base64: request.scan.base64 } : null,
      platform: request.platform?.trim() ? request.platform.trim() : null,
    };
    let response: Response;
    try {
      response = await this.fetchImpl(new URL("/import/sbom", `${this.baseUrl.replace(/\/$/, "")}/`), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal,
      });
    } catch (error) {
      if (isAbort(error)) throw error;
      // The engine refuses an oversized request before reading it, which a webview reports as this.
      throw new ImportError("network_error", "Could not reach the local engine, or it closed the connection.");
    }
    let answer: unknown;
    try {
      answer = await response.json();
    } catch (error) {
      if (isAbort(error)) throw error;
      if (!response.ok) throw importErrorFrom(response.status, undefined);
      throw new ImportError("malformed_response", "The engine's import answer could not be read: it is not JSON.");
    }
    if (!response.ok) throw importErrorFrom(response.status, answer);
    return parseImportResult(answer);
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isAbort(error: unknown): boolean {
  return typeof error === "object" && error !== null && (error as { name?: unknown }).name === "AbortError";
}
