// #290 test support: the little of the DOM the project, review and import
// screens use. The app installs no DOM library, so the tests drive these
// fakes: elements the screens create are real objects here, while markup set
// through innerHTML stays a string the tests read. Events on that markup are
// simulated with `target()`, an element-like object with attributes.

type Listener = (event: { target: unknown; preventDefault(): void }) => void;

export class FakeClassList {
  constructor(private readonly element: FakeElement) {}

  private get names(): string[] {
    return this.element.className.split(/\s+/).filter(Boolean);
  }

  add(...names: string[]): void {
    this.element.className = [...new Set([...this.names, ...names])].join(" ");
  }

  remove(...names: string[]): void {
    this.element.className = this.names.filter((name) => !names.includes(name)).join(" ");
  }

  toggle(name: string, force?: boolean): boolean {
    const on = force ?? !this.contains(name);
    if (on) this.add(name);
    else this.remove(name);
    return on;
  }

  contains(name: string): boolean {
    return this.names.includes(name);
  }
}

export class FakeElement {
  id = "";
  className = "";
  textContent = "";
  innerHTML = "";
  hidden = false;
  type = "";
  value = "";
  checked = false;
  disabled = false;
  tabIndex = 0;
  htmlFor = "";
  accept = "";
  placeholder = "";
  autocomplete = "";
  spellcheck = true;
  noValidate = false;
  files: unknown[] | null = null;
  parent?: FakeElement;
  readonly children: FakeElement[] = [];
  readonly attributes = new Map<string, string>();
  readonly classList = new FakeClassList(this);
  private readonly listeners = new Map<string, Listener[]>();

  constructor(readonly tagName: string, readonly ownerDocument: FakeDocument) {}

  setAttribute(name: string, value: string): void {
    this.attributes.set(name, value);
  }

  getAttribute(name: string): string | null {
    return this.attributes.get(name) ?? null;
  }

  removeAttribute(name: string): void {
    this.attributes.delete(name);
  }

  hasAttribute(name: string): boolean {
    return this.attributes.has(name);
  }

  addEventListener(type: string, listener: Listener): void {
    this.listeners.set(type, [...(this.listeners.get(type) ?? []), listener]);
  }

  dispatch(type: string, target: unknown = this): void {
    for (const listener of this.listeners.get(type) ?? []) listener({ target, preventDefault: () => {} });
  }

  append(...nodes: FakeElement[]): void {
    for (const node of nodes) {
      node.parent?.removeChild(node);
      node.parent = this;
      this.children.push(node);
    }
  }

  removeChild(node: FakeElement): void {
    const index = this.children.indexOf(node);
    if (index >= 0) this.children.splice(index, 1);
    node.parent = undefined;
  }

  replaceChildren(...nodes: FakeElement[]): void {
    for (const child of [...this.children]) this.removeChild(child);
    this.innerHTML = "";
    this.append(...nodes);
  }

  before(...nodes: FakeElement[]): void {
    this.insertAt(0, nodes);
  }

  after(...nodes: FakeElement[]): void {
    this.insertAt(1, nodes);
  }

  replaceWith(node: FakeElement): void {
    const parent = this.parent;
    if (!parent) return;
    const index = parent.children.indexOf(this);
    parent.removeChild(this);
    node.parent?.removeChild(node);
    node.parent = parent;
    parent.children.splice(index, 0, node);
  }

  remove(): void {
    this.parent?.removeChild(this);
  }

  focus(): void {
    this.ownerDocument.activeElement = this;
  }

  click(): void {
    this.dispatch("click");
  }

  get isConnected(): boolean {
    let node: FakeElement | undefined = this;
    while (node) {
      if (node === this.ownerDocument.body || node === this.ownerDocument.head) return true;
      node = node.parent;
    }
    return false;
  }

  /** Created descendants only: markup set through innerHTML is not searched. */
  querySelector(selector: string): FakeElement | null {
    return this.all().find((element) => matches(element, selector)) ?? null;
  }

  closest(selector: string): FakeElement | null {
    let node: FakeElement | undefined = this;
    while (node) {
      if (matches(node, selector)) return node;
      node = node.parent;
    }
    return null;
  }

  /** Every created descendant, depth first. */
  all(): FakeElement[] {
    return this.children.flatMap((child) => [child, ...child.all()]);
  }

  /** The fake as the DOM type a screen expects. */
  as<T>(): T {
    return this as unknown as T;
  }

  /** This element's text and markup and its descendants', for assertions. */
  get text(): string {
    return [this.textContent, this.innerHTML, ...this.children.map((child) => child.text)].join(" ");
  }

  private insertAt(offset: number, nodes: FakeElement[]): void {
    const parent = this.parent;
    if (!parent) return;
    let index = parent.children.indexOf(this) + offset;
    for (const node of nodes) {
      node.parent?.removeChild(node);
      node.parent = parent;
      parent.children.splice(index, 0, node);
      index += 1;
    }
  }
}

function matches(element: FakeElement, selector: string): boolean {
  if (selector.startsWith("#")) return element.id === selector.slice(1);
  const attribute = /^\[([a-z-]+)\]$/.exec(selector);
  if (attribute) return element.attributes.has(attribute[1]);
  if (selector.startsWith(".")) return element.classList.contains(selector.slice(1));
  return element.tagName === selector;
}

export class FakeDocument {
  activeElement: FakeElement | null = null;
  readonly head: FakeElement;
  readonly body: FakeElement;

  constructor() {
    this.head = new FakeElement("head", this);
    this.body = new FakeElement("body", this);
  }

  createElement(tagName: string): FakeElement {
    return new FakeElement(tagName, this);
  }

  /** The fake as the DOM type a screen expects. */
  as<T>(): T {
    return this as unknown as T;
  }
}

/** An element-like event target with attributes, for clicks and changes inside innerHTML markup. */
export function target(attributes: Record<string, string>, properties: { value?: string; checked?: boolean } = {}) {
  const element = {
    ...properties,
    getAttribute: (name: string) => attributes[name] ?? null,
    closest: (selector: string) => {
      const attribute = /^\[([a-z-]+)\]$/.exec(selector);
      return attribute && attribute[1] in attributes ? element : null;
    },
  };
  return element as unknown as Element;
}

export const tick = () => new Promise((resolve) => setTimeout(resolve, 0));
