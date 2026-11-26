export const EMPTY_INSPECTOR = "Select a row to view its details.";

export const LIBRARY_PAGE_SIZE = 50;

export interface LibraryPagination {
  pageStatus: HTMLElement;
  previousPage: HTMLButtonElement;
  nextPage: HTMLButtonElement;
}

export function renderPagination(
  { pageStatus, previousPage, nextPage }: LibraryPagination,
  offset: number,
  count: number,
  total: number,
): void {
  const end = Math.min(offset + count, total);
  pageStatus.textContent = count ? `${offset + 1}–${end} of ${total}` : `0 of ${total}`;
  previousPage.hidden = nextPage.hidden = total <= LIBRARY_PAGE_SIZE;
  previousPage.disabled = offset === 0;
  nextPage.disabled = end >= total;
}

export function resetPagination(
  { pageStatus, previousPage, nextPage }: LibraryPagination,
): void {
  pageStatus.textContent = "";
  previousPage.hidden = nextPage.hidden = true;
  previousPage.disabled = nextPage.disabled = true;
}

export function bindClearFilters(
  button: HTMLButtonElement,
  search: HTMLInputElement,
  filters: readonly HTMLSelectElement[],
  apply: () => void,
): () => void {
  const controls = [search, ...filters];
  const update = () => {
    button.hidden = !controls.some((control) => !control.disabled && control.value.trim());
  };
  search.addEventListener("input", update);
  search.addEventListener("search", update);
  for (const filter of filters) filter.addEventListener("change", update);
  button.addEventListener("click", () => {
    for (const control of controls) control.value = "";
    search.focus();
    update();
    apply();
  });
  update();
  return update;
}

/** Keep native activation and dismiss on outside focus, outside clicks, or Escape. */
export function bindInfoDisclosures(root: Document): void {
  const openDisclosures = () => root.querySelectorAll<HTMLDetailsElement>(".info-disclosure[open]");

  const dismissOutside = (event: Event) => {
    if (!(event.target instanceof Node)) return;
    for (const disclosure of openDisclosures()) {
      if (!disclosure.contains(event.target)) disclosure.open = false;
    }
  };
  root.addEventListener("click", dismissOutside);
  root.addEventListener("focusin", dismissOutside);

  root.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || !(event.target instanceof Node)) return;
    for (const disclosure of openDisclosures()) {
      const hadFocus = disclosure.contains(event.target);
      disclosure.open = false;
      if (hadFocus) {
        disclosure.querySelector("summary")?.focus();
        event.preventDefault();
      }
    }
  });
}
