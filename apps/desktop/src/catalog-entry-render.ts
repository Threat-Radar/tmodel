import {
  fieldItems, fieldValues, readableCweText, richTextToCode, safeHttpUrl, type CatalogFields,
} from "./weakness-fields";
import type { CweFieldValue } from "./weakness-types";

export interface DisclosureOptions {
  count?: number;
  open?: boolean;
}

/** An Assertion the CWE or CAPEC import makes; it stays proposed until a human accepts it. */
export interface CatalogAssertion {
  id: string;
  name: string;
  subject: string;
  predicate: string;
  object: string;
  assertion_status: string;
  asserted_by: string;
  generated_by: string;
  description?: string;
  evidence?: readonly string[];
}

/** Each inspector keeps its own class names; styles.css styles the two alike. */
export type CatalogClassPrefix = "weakness" | "attack-pattern";

export const PROPOSED_LABEL = "Proposed, not human-reviewed";

/**
 * Inspector sections for one MITRE catalog entry. The CWE and CAPEC readers keep every
 * field by the same rules (DL-0050, DL-0056), so the Weaknesses and Attack Patterns
 * inspectors render them with this one class. A value only ever reaches the page as
 * text (textContent), and a link only when its URL is HTTP or HTTPS.
 */
export class CatalogEntryRenderer {
  constructor(
    private readonly documentRoot: Document,
    private readonly prefix: CatalogClassPrefix,
  ) {}

  fieldSection(
    entry: CatalogFields,
    title: string,
    field: string,
    options: DisclosureOptions = {},
  ): HTMLElement[] {
    return this.valuesSection(title, fieldValues(entry, field), options);
  }

  itemSection(
    entry: CatalogFields,
    title: string,
    container: string,
    itemNames: readonly string[],
    options: DisclosureOptions = {},
  ): HTMLElement[] {
    const items = itemNames.flatMap((item) => fieldItems(entry, container, item));
    return this.valuesSection(title, items.length ? items : fieldValues(entry, container), {
      count: items.length || undefined,
      ...options,
    });
  }

  alternateTerms(entry: CatalogFields & { readonly alternate_terms: readonly string[] }): HTMLElement[] {
    const terms = fieldItems(entry, "Alternate_Terms", "Alternate_Term");
    return this.valuesSection("Alternate Terms", terms.length ? terms : entry.alternate_terms, {
      count: terms.length || entry.alternate_terms.length,
    });
  }

  valuesSection(
    title: string,
    values: readonly CweFieldValue[],
    options: DisclosureOptions = {},
  ): HTMLElement[] {
    const items = values.filter((value) => readableCweText(value));
    if (!items.length) return [];
    const list = this.valueList(items);
    return [this.detailSection(title, list, { count: options.count ?? items.length, ...options })];
  }

  valueGroup(title: string, values: readonly CweFieldValue[]): HTMLElement | undefined {
    const items = values.filter((value) => readableCweText(value));
    if (!items.length) return undefined;
    const group = this.documentRoot.createElement("section");
    group.className = this.className("detail-group");
    const heading = this.documentRoot.createElement("h4");
    heading.textContent = `${title} (${items.length})`;
    group.append(heading, this.valueList(items));
    return group;
  }

  /** Several value groups under one section body. */
  groups(groups: readonly HTMLElement[]): HTMLElement {
    const wrapper = this.documentRoot.createElement("div");
    wrapper.className = this.className("detail-groups");
    wrapper.append(...groups);
    return wrapper;
  }

  valueList(values: readonly CweFieldValue[]): HTMLUListElement {
    const list = this.documentRoot.createElement("ul");
    list.className = this.className("detail-items");
    list.append(...values.map((value) => {
      const item = this.documentRoot.createElement("li");
      item.append(this.fieldValue(value));
      return item;
    }));
    return list;
  }

  fieldValue(value: CweFieldValue, name?: string): HTMLElement {
    if (name === "Example_Code") return this.codeValue(value);
    const wrapper = this.documentRoot.createElement("div");
    wrapper.className = this.className("field-value");
    if (value === null) return wrapper;
    if (typeof value !== "object") {
      wrapper.textContent = String(value);
      return wrapper;
    }
    if (Array.isArray(value)) {
      if (value.every((item) => item === null || typeof item !== "object")) {
        wrapper.textContent = value.map(readableCweText).filter(Boolean).join(" · ");
      } else {
        wrapper.className = `${this.className("field-value")} ${this.className("field-collection")}`;
        wrapper.append(...value
          .filter((item) => readableCweText(item))
          .map((item) => this.fieldValue(item)));
      }
      return wrapper;
    }
    for (const [key, child] of Object.entries(value)) {
      if (key === "#xhtml" || key === "#text") {
        const text = this.documentRoot.createElement("p");
        text.className = this.className("field-text");
        text.textContent = key === "#xhtml" && typeof child === "string"
          ? readableCweText({ "#xhtml": child })
          : readableCweText(child);
        if (text.textContent) wrapper.append(text);
      } else if (key === "#items" && Array.isArray(child)) {
        for (const ordered of child) wrapper.append(this.fieldValue(ordered));
      } else {
        const row = this.documentRoot.createElement("div");
        row.className = this.className(key.startsWith("@") ? "field-attribute" : "field-row");
        const label = this.documentRoot.createElement("span");
        label.className = this.className("field-label");
        label.textContent = displayValue(key.replace(/^@/, ""));
        row.append(label, this.fieldValue(child, key));
        wrapper.append(row);
      }
    }
    return wrapper;
  }

  /** Identifiers such as CWE or CAPEC ids, each linked when `linkFor` gives an HTTP(S) URL. */
  identifierList(
    title: string,
    items: readonly string[],
    linkFor?: (identifier: string) => string | undefined,
  ): HTMLElement[] {
    if (!items.length) return [];
    const list = this.documentRoot.createElement("ul");
    list.className = `${this.className("detail-items")} ${this.className("identifier-items")}`;
    list.append(...items.map((text) => {
      const item = this.documentRoot.createElement("li");
      const link = safeHttpUrl(linkFor?.(text));
      if (link) item.append(externalLink(this.documentRoot, text, link, this.className("identifier-link")));
      else item.textContent = text;
      return item;
    }));
    return [this.detailSection(title, list, { count: items.length })];
  }

  /** An identifier shown without a link, in the identifier style. */
  identifier(value: string): HTMLElement {
    const identifier = this.documentRoot.createElement("span");
    identifier.className = this.className("identifier-link");
    identifier.textContent = value;
    return identifier;
  }

  assertions(assertions: readonly CatalogAssertion[]): HTMLElement[] {
    if (!assertions.length) return [];
    const list = this.documentRoot.createElement("ul");
    list.className = this.className("assertions");
    list.append(...assertions.map((assertion) => {
      const item = this.documentRoot.createElement("li");
      const heading = this.documentRoot.createElement("div");
      const status = assertion.assertion_status.toLocaleLowerCase("und") === "proposed"
        ? PROPOSED_LABEL
        : displayValue(assertion.assertion_status);
      heading.textContent = `${assertion.name} · ${status}`;
      const relation = this.documentRoot.createElement("code");
      relation.textContent = `${assertion.subject} ${assertion.predicate} ${assertion.object}`;
      const provenance = this.documentRoot.createElement("dl");
      provenance.className = this.className("assertion-provenance");
      provenance.append(
        this.assertionProvenanceRow("Assertion ID", assertion.id, true),
        this.assertionProvenanceRow("Asserted by", assertion.asserted_by, true),
        this.assertionProvenanceRow("Generated by", assertion.generated_by),
      );
      item.append(heading, relation, provenance);
      if (assertion.description) {
        const description = this.documentRoot.createElement("p");
        description.textContent = assertion.description;
        item.append(description);
      }
      const evidence = assertion.evidence?.flatMap((url) => {
        const safe = safeHttpUrl(url);
        return safe ? [externalLink(this.documentRoot, "Evidence", safe)] : [];
      }) ?? [];
      if (evidence.length) item.append(...evidence);
      return item;
    }));
    const note = this.documentRoot.createElement("p");
    note.className = this.className("proposal-note");
    note.textContent = "Imported relationships are proposals until a human accepts them through the review workflow.";
    const wrapper = this.documentRoot.createElement("div");
    wrapper.append(note, list);
    return [this.detailSection("Proposed Relationships", wrapper, { count: assertions.length })];
  }

  /** Every field with text that no named section shows, so nothing is silently hidden. */
  additionalFields(entry: CatalogFields, alreadyShown: ReadonlySet<string>): HTMLElement[] {
    const groups = Object.entries(entry.fields).flatMap(([name, value]) => {
      if (alreadyShown.has(name)) return [];
      if (!readableCweText(value)) return [];
      const group = this.valueGroup(
        displayValue(name.replace(/^@/, "")),
        fieldValues(entry, name),
      );
      return group ? [group] : [];
    });
    if (!groups.length) return [];
    return [this.detailSection("Additional Catalog Fields", this.groups(groups), { count: groups.length })];
  }

  contentHistory(entry: CatalogFields): HTMLElement[] {
    const values = fieldValues(entry, "Content_History");
    if (!values.length) return [];
    const eventCount = ["Submission", "Modification", "Contribution", "Previous_Entry_Name"]
      .reduce((count, item) => count + fieldItems(entry, "Content_History", item).length, 0);
    return this.valuesSection("Content History", values, { count: eventCount || undefined });
  }

  detailSection(
    title: string,
    content: HTMLElement,
    options: DisclosureOptions = {},
  ): HTMLElement {
    const details = this.documentRoot.createElement("details");
    details.className = this.className("detail-section");
    details.open = options.open ?? false;
    const summary = this.documentRoot.createElement("summary");
    const label = this.documentRoot.createElement("span");
    label.textContent = title;
    summary.append(label);
    if (options.count !== undefined) {
      const count = this.documentRoot.createElement("span");
      count.className = this.className("section-count");
      count.textContent = String(options.count);
      count.setAttribute("aria-label", `${options.count} ${options.count === 1 ? "item" : "items"}`);
      summary.append(count);
    }
    const body = this.documentRoot.createElement("div");
    body.className = this.className("detail-section-body");
    body.append(content);
    details.append(summary, body);
    return details;
  }

  detailRow(label: string, value: string | HTMLElement): HTMLElement {
    const wrapper = this.documentRoot.createElement("div");
    wrapper.className = "detail-row";
    const term = this.documentRoot.createElement("dt");
    term.textContent = label;
    const description = this.documentRoot.createElement("dd");
    if (typeof value === "string") description.textContent = value;
    else description.append(value);
    wrapper.append(term, description);
    return wrapper;
  }

  badge(value: string): HTMLElement {
    const badge = this.documentRoot.createElement("span");
    badge.className = "status-chip";
    badge.textContent = value;
    return badge;
  }

  private codeValue(value: CweFieldValue): HTMLElement {
    const wrapper = this.documentRoot.createElement("div");
    wrapper.className = this.className("code-value");
    const values = Array.isArray(value) ? value : [value];
    for (const codeValue of values) {
      if (typeof codeValue === "object" && codeValue !== null && !Array.isArray(codeValue)) {
        const attributes = (Object.entries(codeValue) as Array<[string, CweFieldValue]>)
          .filter(([key]) => key.startsWith("@"));
        if (attributes.length) {
          const meta = this.documentRoot.createElement("div");
          meta.className = this.className("code-meta");
          meta.textContent = attributes
            .map(([key, item]) => `${displayValue(key.slice(1))}: ${readableCweText(item)}`)
            .join(" · ");
          wrapper.append(meta);
        }
      }
      const markup = typeof codeValue === "object" && codeValue !== null && !Array.isArray(codeValue)
        ? codeValue["#xhtml"]
        : undefined;
      const code = this.documentRoot.createElement("code");
      code.textContent = typeof markup === "string" ? richTextToCode(markup) : readableCweText(codeValue);
      const pre = this.documentRoot.createElement("pre");
      pre.append(code);
      wrapper.append(pre);
    }
    return wrapper;
  }

  private assertionProvenanceRow(label: string, value: string, stableId = false): HTMLElement {
    const row = this.documentRoot.createElement("div");
    const term = this.documentRoot.createElement("dt");
    term.textContent = label;
    const description = this.documentRoot.createElement("dd");
    if (stableId) {
      const code = this.documentRoot.createElement("code");
      code.textContent = value;
      description.append(code);
    } else description.textContent = value;
    row.append(term, description);
    return row;
  }

  private className(name: string): string {
    return `${this.prefix}-${name}`;
  }
}

/** A definition-list row with an external link, or nothing when the URL is not HTTP(S). */
export function safeLinkRows(
  root: Document,
  label: string,
  value: string | null | undefined,
  linkLabel: string,
): HTMLElement[] {
  const url = safeHttpUrl(value);
  if (!url) return [];
  const wrapper = root.createElement("div");
  wrapper.className = "detail-row";
  const term = root.createElement("dt");
  term.textContent = label;
  const description = root.createElement("dd");
  description.append(externalLink(root, linkLabel, url));
  wrapper.append(term, description);
  return [wrapper];
}

export function externalLink(root: Document, label: string, url: string, className = ""): HTMLAnchorElement {
  const link = root.createElement("a");
  link.textContent = label;
  link.className = className;
  link.href = url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  return link;
}

/** A catalog field name for display: underscores become spaces, the first letter a capital. */
export function displayValue(value: string): string {
  const words = value.replace(/_/gu, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

/** capec.mitre.org's page for CAPEC-N; undefined for anything that is not a CAPEC id. */
export function capecDefinitionUrl(id: string): string | undefined {
  const number = /^CAPEC-([0-9]+)$/i.exec(id)?.[1];
  return number ? `https://capec.mitre.org/data/definitions/${Number(number)}.html` : undefined;
}

/** cwe.mitre.org's page for CWE-N; undefined for anything that is not a CWE id. */
export function cweDefinitionUrl(id: string): string | undefined {
  const number = /^CWE-([0-9]+)$/i.exec(id)?.[1];
  return number ? `https://cwe.mitre.org/data/definitions/${Number(number)}.html` : undefined;
}

/** attack.mitre.org's page for an ATT&CK technique (T1083) or sub-technique (T1574.011). */
export function attackTechniqueUrl(id: string): string | undefined {
  const match = /^T([0-9]{4})(?:\.([0-9]{3}))?$/.exec(id);
  if (!match) return undefined;
  return `https://attack.mitre.org/techniques/T${match[1]}/${match[2] ? `${match[2]}/` : ""}`;
}
