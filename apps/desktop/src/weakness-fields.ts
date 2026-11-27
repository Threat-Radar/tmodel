import type { CweFieldValue } from "./weakness-types";

/** A CWE or CAPEC entry's preserved fields; the CAPEC reader keeps them by CWE's rules (DL-0056). */
export interface CatalogFields {
  readonly fields: Readonly<Record<string, CweFieldValue>>;
}

export function fieldValues(entry: CatalogFields, name: string): readonly CweFieldValue[] {
  return asArray(entry.fields[name]);
}

export function fieldItems(
  entry: CatalogFields,
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
    return normalizeCode(codeFromDom(parsed.body));
  }
  return normalizeCode(codeFromMarkup(markup));
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
  const lines = value.replace(/\r\n?/gu, "\n").split("\n");
  while (lines.length && !lines[0].trim()) lines.shift();
  while (lines.length && !lines[lines.length - 1].trim()) lines.pop();
  const content = lines.filter((line) => line.trim());
  if (content.length > 1) {
    const common = commonIndent(content.map((line) => line.match(/^[ \t]*/u)?.[0] ?? ""));
    if (common) {
      for (let index = 0; index < lines.length; index += 1) {
        if (lines[index].startsWith(common)) lines[index] = lines[index].slice(common.length);
      }
    }
  }
  return lines.map((line) => line.trim() ? line : "").join("\n");
}

const CODE_BLOCK_ELEMENTS = new Set(["address", "article", "aside", "blockquote", "dd", "div",
  "dl", "dt", "figcaption", "figure", "footer", "header", "li", "main", "nav", "ol", "p",
  "pre", "section", "table", "tbody", "td", "tfoot", "th", "thead", "tr", "ul"]);
const CODE_INDENT_SPACES = 4;

class CodeText {
  private readonly lines = [""];
  private pendingWhitespace = "";
  private pendingBlockBreak = false;

  text(value: string, indent: number): void {
    const normalized = value.replace(/\r\n?/gu, "\n");
    if (!normalized.trim()) {
      if (!normalized.includes("\n")) this.pendingWhitespace += normalized;
      return;
    }
    const parts = normalized.split("\n");
    let first = 0;
    let last = parts.length - 1;
    while (first <= last && !parts[first].trim()) first += 1;
    while (last >= first && !parts[last].trim()) last -= 1;
    const xmlLinePadding = first > 0 ? commonIndent(
      parts.slice(first, last + 1)
        .filter((part) => part.trim())
        .map((part) => part.match(/^[ \t]*/u)?.[0] ?? ""),
    ) : "";
    const hasXmlLinePadding = xmlLinePadding.includes("\t");
    for (let index = first; index <= last; index += 1) {
      if (index > first) this.breakLine(true);
      // CWE's formatted XML puts tabs before code that shares a source line
      // with a tag. Those tabs describe the XML document, not the example.
      // Strip them before adding margin-left indentation. Text that starts on
      // the first line (and literal space indentation, such as <pre> content)
      // remains unchanged.
      const text = hasXmlLinePadding && parts[index].startsWith(xmlLinePadding)
        ? parts[index].slice(xmlLinePadding.length) : parts[index];
      this.write(text, indent);
    }
  }

  breakLine(force = false): void {
    this.pendingWhitespace = "";
    const lineHasContent = this.lines[this.lines.length - 1] !== "";
    if (force || lineHasContent) this.lines.push("");
    this.pendingBlockBreak = false;
  }

  explicitBreak(): void {
    this.pendingWhitespace = "";
    this.lines.push("");
    this.pendingBlockBreak = false;
  }

  endBlock(): void {
    if (this.lines[this.lines.length - 1] !== "") this.pendingBlockBreak = true;
  }

  value(): string {
    return this.lines.join("\n");
  }

  private write(value: string, indent: number): void {
    if (!value) return;
    if (this.pendingBlockBreak) this.breakLine();
    const text = this.pendingWhitespace + value;
    this.pendingWhitespace = "";
    const line = this.lines.length - 1;
    if (!this.lines[line] && text.trim()) this.lines[line] = " ".repeat(indent);
    this.lines[line] += text;
  }
}

function codeFromDom(root: ParentNode): string {
  const output = new CodeText();
  for (const child of Array.from(root.childNodes)) renderCodeNode(child, output, 0);
  return output.value();
}

function renderCodeNode(node: Node, output: CodeText, indent: number): void {
  if (node.nodeType === 3) {
    output.text(node.textContent ?? "", indent);
    return;
  }
  if (node.nodeType !== 1) return;
  const element = node as Element;
  const name = (element.localName || element.tagName).toLowerCase();
  if (name === "br") {
    output.explicitBreak();
    return;
  }
  if (CODE_BLOCK_ELEMENTS.has(name)) output.breakLine();
  const childIndent = indent + indentationFromStyle(element.getAttribute("style"));
  for (const child of Array.from(element.childNodes)) renderCodeNode(child, output, childIndent);
  if (CODE_BLOCK_ELEMENTS.has(name)) output.endBlock();
}

function codeFromMarkup(markup: string): string {
  const output = new CodeText();
  const stack: Array<{ name: string; indent: number }> = [];
  let indent = 0;
  const tokens = markup.match(/<!--[\s\S]*?-->|<\/?[^>]+>|[^<]+/gu) ?? [];
  for (const token of tokens) {
    if (token.startsWith("<!--")) continue;
    if (!token.startsWith("<")) {
      output.text(decodeEntities(token), indent);
      continue;
    }
    const tag = token.match(/^<\s*(\/?)\s*([a-zA-Z0-9:-]+)/u);
    if (!tag) continue;
    const closing = Boolean(tag[1]);
    const name = tag[2].split(":").pop()!.toLowerCase();
    if (closing) {
      for (let index = stack.length - 1; index >= 0; index -= 1) {
        const removed = stack.pop()!;
        indent -= removed.indent;
        if (CODE_BLOCK_ELEMENTS.has(removed.name)) output.endBlock();
        if (removed.name === name) break;
      }
      continue;
    }
    if (name === "br") {
      output.explicitBreak();
      continue;
    }
    if (CODE_BLOCK_ELEMENTS.has(name)) output.breakLine();
    const addedIndent = indentationFromStyle(attributeValue(token, "style"));
    indent += addedIndent;
    if (!/\/\s*>$/u.test(token)) stack.push({ name, indent: addedIndent });
    else if (CODE_BLOCK_ELEMENTS.has(name)) output.endBlock();
  }
  return output.value();
}

function indentationFromStyle(style: string | null): number {
  const match = style?.match(/(?:^|;)\s*margin-left\s*:\s*([0-9]*\.?[0-9]+)\s*(em|rem|px|%)?/iu);
  if (!match) return 0;
  const amount = Number(match[1]);
  if (!Number.isFinite(amount) || amount <= 0) return 0;
  const levels = match[2]?.toLowerCase() === "px" ? amount / 16
    : match[2] === "%" ? amount / 100 : amount;
  return Math.max(1, Math.round(levels)) * CODE_INDENT_SPACES;
}

function attributeValue(tag: string, name: string): string | null {
  const match = tag.match(new RegExp(`\\s${name}\\s*=\\s*(?:"([^"]*)"|'([^']*)')`, "iu"));
  return match?.[1] ?? match?.[2] ?? null;
}

function commonIndent(indents: readonly string[]): string {
  if (!indents.length) return "";
  let prefix = indents[0];
  for (const indent of indents.slice(1)) {
    while (prefix && !indent.startsWith(prefix)) prefix = prefix.slice(0, -1);
  }
  return prefix;
}

function displayKey(value: string): string {
  const words = value.replace(/_/gu, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function decodeEntities(value: string): string {
  return value
    .replace(/&#(x[0-9a-f]+|[0-9]+);/giu, (entity, encoded: string) => {
      const codePoint = encoded[0].toLowerCase() === "x"
        ? Number.parseInt(encoded.slice(1), 16) : Number.parseInt(encoded, 10);
      try {
        return String.fromCodePoint(codePoint);
      } catch {
        return entity;
      }
    })
    .replace(/&lt;/giu, "<")
    .replace(/&gt;/giu, ">")
    .replace(/&quot;/giu, "\"")
    .replace(/&#39;|&apos;/giu, "'")
    .replace(/&nbsp;/giu, " ")
    .replace(/&amp;/giu, "&");
}
