import { describe, expect, it } from "vitest";
import { appMode, pagesBuildOutDir, staticDataBase } from "./app-mode";

describe("application mode", () => {
  it("uses static preview data only for the dedicated Pages build", () => {
    expect(appMode("pages")).toBe("browser-preview");
    expect(appMode("production")).toBe("desktop");
    expect(appMode("development")).toBe("desktop");
  });

  it("resolves data below the GitHub Pages application base", () => {
    expect(staticDataBase("/tmodel/app/", "https://threat-radar.github.io/tmodel/app/?model=x"))
      .toBe("https://threat-radar.github.io/tmodel/app/data/");
  });

  it("keeps standalone Pages builds away from the committed preview", () => {
    expect(pagesBuildOutDir()).toBe("dist/pages");
    expect(pagesBuildOutDir("custom/pages")).toBe("custom/pages");
  });
});
