// Escaping HTML builder shared by the app and the static Pages renderer (#208).
//
// Every interpolated value is escaped unless it is already SafeHtml, so model
// text (names, descriptions, justifications) can never become markup. This file
// imports nothing, so Node can run it directly with type stripping.

export class SafeHtml {
  readonly value: string;

  constructor(value: string) {
    this.value = value;
  }

  toString(): string {
    return this.value;
  }
}

const ESCAPES: Readonly<Record<string, string>> = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
};

/** Escapes text for use in element content or a quoted attribute value. */
export function escapeHtml(text: string): string {
  return text.replace(/[&<>"']/g, (character) => ESCAPES[character] ?? character);
}

/** Marks trusted markup (produced by this module or a caller's own template). */
export function trusted(markup: string): SafeHtml {
  return new SafeHtml(markup);
}

/**
 * Tagged template: `html\`<td>${name}</td>\``. Values are escaped; SafeHtml and
 * arrays of SafeHtml pass through; null, undefined and false render nothing.
 */
export function html(strings: TemplateStringsArray, ...values: readonly unknown[]): SafeHtml {
  let out = strings[0] ?? "";
  values.forEach((value, index) => {
    out += fragment(value) + (strings[index + 1] ?? "");
  });
  return new SafeHtml(out);
}

/** Joins fragments, escaping any plain strings among them. */
export function join(values: readonly unknown[], separator = ""): SafeHtml {
  return new SafeHtml(values.map(fragment).join(fragment(separator)));
}

function fragment(value: unknown): string {
  if (value === null || value === undefined || value === false) return "";
  if (value instanceof SafeHtml) return value.value;
  if (Array.isArray(value)) return value.map(fragment).join("");
  return escapeHtml(String(value));
}
