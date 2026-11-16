import { describe, expect, it } from "vitest";
import { readableCweText, richTextToCode, richTextToText, safeHttpUrl } from "./weakness-fields";

describe("CWE field presentation", () => {
  it("turns the importer's XHTML representation into text, never markup", () => {
    const input = { "#xhtml": "<p>Hello <strong>world</strong>.</p><script>alert(1)</script>" };
    expect(readableCweText(input)).toBe("Hello world . alert(1)");
    expect(richTextToText("x &lt; y<br>then y &gt; z")).toBe("x < y then y > z");
  });

  it("keeps ordered items and attributes readable", () => {
    expect(readableCweText({
      "@Phase": "Implementation",
      "#items": [{ Body_Text: "First" }, { Example_Code: "const x = 1" }],
    })).toBe("Phase: Implementation · Body Text: First · Example Code: const x = 1");
  });

  it("preserves source line breaks in code while rendering markup as inert text", () => {
    expect(richTextToCode("<div>const x = 1;<br/>alert(x);</div><script>ignored()</script>"))
      .toBe("const x = 1;\nalert(x);\nignored()");
  });

  it("allows only HTTP and HTTPS links", () => {
    expect(safeHttpUrl("https://cwe.mitre.org/data/definitions/79.html"))
      .toBe("https://cwe.mitre.org/data/definitions/79.html");
    expect(safeHttpUrl("http://example.test/path")).toBe("http://example.test/path");
    expect(safeHttpUrl("javascript:alert(1)")).toBeUndefined();
    expect(safeHttpUrl("not a URL")).toBeUndefined();
  });
});
