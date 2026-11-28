// Cytoscape renders into a canvas and needs resolved CSS values.
export function canvasTheme(documentRoot?: Document): (token: string) => string {
  const styles = documentRoot?.defaultView?.getComputedStyle(documentRoot.documentElement);
  return (token) => styles?.getPropertyValue(`--${token}`).trim() ?? "";
}
