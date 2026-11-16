import type { CweFieldValue, WeaknessEntry } from "./weakness-types";

export function fieldValues(entry: WeaknessEntry, name: string): readonly CweFieldValue[] {
  return asArray(entry.fields[name]);
}

export function fieldItems(
  entry: WeaknessEntry,
  container: string,
  item: string,
): readonly CweFieldValue[] {
  return fieldValues(entry, container).flatMap((holder) => {
    if (!isRecord(holder)) return [];
    return asArray(holder[item]);
  });
}

export function readableCweText(value: CweFieldValue): string {
  if (typeof value === "string") return normalize(value);
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (value === null) return "";
  if (Array.isArray(value)) return joinReadable(value.map(readableCweText));
  if (!isRecord(value)) return "";
  const attributes = Object.entries(value)
    .filter(([key]) => key.startsWith("@"))
    .map(([key, item]) => `${displayKey(key.slice(1))}: ${readableCweText(item)}`);
  if (typeof value["#xhtml"] === "string") {
    return joinReadable([...attributes, richTextToText(value["#xhtml"])]);
  }
  if (typeof value["#text"] === "string") {
    return joinReadable([...attributes, normalize(value["#text"])]);
  }
  if (Array.isArray(value["#items"])) {
    return joinReadable([...attributes, ...value["#items"].map(readableCweText)]);
  }
  const children = Object.entries(value)
    .filter(([key]) => !key.startsWith("@") && !key.startsWith("#"))
    .flatMap(([key, item]) => {
      const text = readableCweText(item);
      return text ? [`${displayKey(key)}: ${text}`] : [];
    });
  return joinReadable([...attributes, ...children]);
}

export function richTextToText(markup: string): string {
  if (typeof DOMParser !== "undefined") {
    const parsed = new DOMParser().parseFromString(markup, "text/html");
    for (const block of parsed.body.querySelectorAll(
      "address, article, aside, blockquote, br, dd, div, dl, dt, figcaption, figure, footer, "
      + "h1, h2, h3, h4, h5, h6, header, hr, li, main, nav, ol, p, pre, section, table, "
      + "tbody, td, tfoot, th, thead, tr, ul",
    )) block.append(parsed.createTextNode(" "));
    return normalize(parsed.body.textContent ?? "");
  }
  // Tests run without a browser DOM. This fallback only produces text; callers
  // still assign it with textContent and never interpret it as markup.
  return normalize(decodeEntities(markup.replace(/<[^>]*>/gu, " ")));
}

/** Text for source-code examples, retaining line breaks that CWE's XHTML carries. */
export function richTextToCode(markup: string): string {
  if (typeof DOMParser !== "undefined") {
    const parsed = new DOMParser().parseFromString(markup, "text/html");
    for (const lineBreak of parsed.body.querySelectorAll("br")) {
      lineBreak.replaceWith(parsed.createTextNode("\n"));
    }
    for (const block of parsed.body.querySelectorAll("div, p, pre")) {
      block.append(parsed.createTextNode("\n"));
    }
    return normalizeCode(parsed.body.textContent ?? "");
  }
  const withLines = markup
    .replace(/<br\s*\/?>/giu, "\n")
    .replace(/<\/(?:div|p|pre)>/giu, "\n")
    .replace(/<[^>]*>/gu, " ");
  return normalizeCode(decodeEntities(withLines));
}

export function safeHttpUrl(value: string | null | undefined): string | undefined {
  if (!value) return undefined;
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:" ? url.href : undefined;
  } catch {
    return undefined;
  }
}

function asArray(value: CweFieldValue | undefined): readonly CweFieldValue[] {
  if (value === undefined || value === null) return [];
  return Array.isArray(value) ? value : [value];
}

function isRecord(value: CweFieldValue): value is { readonly [key: string]: CweFieldValue } {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function joinReadable(values: readonly string[]): string {
  return values.map(normalize).filter(Boolean).join(" · ");
}

function normalize(value: string): string {
  return value.replace(/\s+/gu, " ").trim();
}

function normalizeCode(value: string): string {
  return value
    .replace(/\r\n?/gu, "\n")
    .replace(/[ \t]+\n/gu, "\n")
    .replace(/\n[ \t]+/gu, "\n")
    .replace(/\n{3,}/gu, "\n\n")
    .trim();
}

function displayKey(value: string): string {
  const words = value.replace(/_/gu, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function decodeEntities(value: string): string {
  return value
    .replace(/&lt;/gu, "<")
    .replace(/&gt;/gu, ">")
    .replace(/&quot;/gu, "\"")
    .replace(/&#39;|&apos;/gu, "'")
    .replace(/&amp;/gu, "&");
}
