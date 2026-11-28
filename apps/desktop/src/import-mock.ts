// #290's Import New Product screen: a development stand-in for POST
// /import/sbom, answering with the importer's recorded results for its alpine
// test files (fixtures/sbom-import-responses.json). Only a Vite development
// server opened with ?projectSource=mock uses it; production builds leave it out.

import responses from "./fixtures/sbom-import-responses.json";

/** Without a scan or platform it refuses as the importer does; linux/amd64 gives its warning. */
export const importMockFetch: typeof fetch = async (_input, init) => {
  const request = JSON.parse(String(init?.body ?? "{}")) as { scan?: unknown; platform?: unknown };
  const answer = request.platform === "linux/amd64" ? responses.warning
    : request.platform === null && request.scan === null ? responses.refusal
    : responses.success;
  // A short pause, so the screen's progress state can be seen.
  await new Promise((resolve) => setTimeout(resolve, 600));
  return new Response(JSON.stringify(answer.body), { status: answer.status, headers: { "Content-Type": "application/json" } });
};
