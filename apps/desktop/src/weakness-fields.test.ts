import { afterEach, describe, expect, it, vi } from "vitest";
import { readableCweText, richTextToCode, richTextToText, safeHttpUrl } from "./weakness-fields";

// CWE 4.20, CWE-1229 Demonstrative Example DX-193, after the engine removes
// the xhtml namespace prefix and preserves the element's inner markup.
const CWE_1229_PYTHON = `<div>def validate_password(actual_pw, typed_pw):
\t\t <div style="margin-left:1em;">
                   <div>if len(actual_pw) &lt;&gt; len(typed_pw):
\t\t   <div style="margin-left:1em;">return 0</div>
                   <br/>for i in len(actual_pw):
\t\t   <div style="margin-left:1em;">if actual_pw[i] &lt;&gt; typed_pw[i]:
\t\t   <div style="margin-left:1em;">return 0</div>
                   </div>
                   <br/>return 1</div>
                 </div>
                 </div>`;

const CWE_1229_RENDERED = `def validate_password(actual_pw, typed_pw):
    if len(actual_pw) <> len(typed_pw):
        return 0
    for i in len(actual_pw):
        if actual_pw[i] <> typed_pw[i]:
            return 0
    return 1`;

// CWE 4.20, CWE-1389's first Python example, after the engine removes the
// xhtml namespace prefix. The tabs align the XML source and must not become
// code indentation; the styled divs carry the actual Python block structure.
const CWE_1389_PYTHON = `<div>
\t\t\t\t\t  import subprocess<br/>
\t\t\t\t\t  <br/>
\t\t\t\t\t  def validate_ip(ip: str):<br/>
\t\t\t\t\t  <div style="margin-left:1em;">
\t\t\t\t\t    split_ip = ip.split('.')<br/>
\t\t\t\t\t\tif len(split_ip) &gt; 4 or len(split_ip) == 0:<br/>
\t\t\t\t\t\t<div style="margin-left:1em;">
\t\t\t\t\t\t  raise ValueError("Invalid IP length")<br/>
\t\t\t\t\t\t</div>
\t\t\t\t\t\t<br/>
\t\t\t\t\t\tfor octet in split_ip:<br/>
\t\t\t\t\t\t<div style="margin-left:1em;">
\t\t\t\t\t\t  try:<br/>
\t\t\t\t\t\t  <div style="margin-left:1em;">
\t\t\t\t\t\t    int(octet, 10)<br/>
\t\t\t\t\t\t  </div>
\t\t\t\t\t\t  except ValueError as e:<br/>
\t\t\t\t\t\t  <div style="margin-left:1em;">
\t\t\t\t\t\t    raise ValueError(f"Cannot convert IP octet to int - {e}")<br/>
\t\t\t\t\t\t  </div>
\t\t\t\t\t\t</div>
\t\t\t\t\t\t<br/>
\t\t\t\t\t\t<i># Returns original IP after ensuring no exceptions are raised</i><br/>
\t\t\t\t\t\treturn ip<br/>

\t\t\t\t\t  </div>
\t\t\t\t\t  <br/>
\t\t\t\t\t  def run_ping(ip: str):<br/>
\t\t\t\t\t  <div style="margin-left:1em;">
\t\t\t\t\t    validated = validate_ip(ip)<br/>
\t\t\t\t\t\t<i># The ping command treats zero-prepended IP addresses as octal</i><br/>
\t\t\t\t\t\tresult = subprocess.call(["ping", validated])<br/>
\t\t\t\t\t\tprint(result)<br/>
\t\t\t\t\t  </div>
\t\t\t\t\t</div>`;

const CWE_1389_RENDERED = `import subprocess

def validate_ip(ip: str):
    split_ip = ip.split('.')
    if len(split_ip) > 4 or len(split_ip) == 0:
        raise ValueError("Invalid IP length")

    for octet in split_ip:
        try:
            int(octet, 10)
        except ValueError as e:
            raise ValueError(f"Cannot convert IP octet to int - {e}")

    # Returns original IP after ensuring no exceptions are raised
    return ip

def run_ping(ip: str):
    validated = validate_ip(ip)
    # The ping command treats zero-prepended IP addresses as octal
    result = subprocess.call(["ping", validated])
    print(result)`;

afterEach(() => vi.unstubAllGlobals());

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

  it("reconstructs the nested Python blocks in CWE-1229's actual markup", () => {
    expect(richTextToCode(CWE_1229_PYTHON)).toBe(CWE_1229_RENDERED);
  });

  it("removes CWE-1389's XML formatting tabs before reconstructing Python blocks", () => {
    expect(richTextToCode(CWE_1389_PYTHON)).toBe(CWE_1389_RENDERED);
  });

  it("preserves literal indentation, tabs, blank lines, entities, and line breaks", () => {
    expect(richTextToCode(`<pre>
    if x &lt; y:
        return &quot;yes&quot;

    return &amp;mask
</pre>`)).toBe(`if x < y:
    return "yes"

return &mask`);
    expect(richTextToCode("root\n\tchild<br/>  sibling")).toBe("root\n\tchild\n  sibling");
    expect(richTextToCode("<div>\n\t\tbase\n\t\t    child\n</div>"))
      .toBe("base\n    child");
    expect(richTextToCode("one<br/><br/>two")).toBe("one\n\ntwo");
    expect(richTextToCode("return value &amp; mask")).toBe("return value & mask");
  });

  it("uses each nested margin-left block as one relative indentation level", () => {
    expect(richTextToCode(
      `<div>outer<div style="margin-left: 1em">middle`
      + `<div style="margin-left: 1em">inner</div></div></div>`,
    )).toBe("outer\n    middle\n        inner");
  });

  it("walks parsed browser DOM blocks without flattening their styled indentation", () => {
    const body = {
      childNodes: [domElement("div", [
        domText("outer"),
        domElement("div", [
          domText("\n  "),
          domElement("div", [
            domText("middle"),
            domElement("br"),
            domText("next"),
            domElement("div", [domText("inner")], "margin-left:1em"),
          ]),
        ], "margin-left:1em"),
      ])],
    };
    vi.stubGlobal("DOMParser", class {
      parseFromString(): { body: typeof body } {
        return { body };
      }
    });

    expect(richTextToCode("browser parser supplies the DOM"))
      .toBe("outer\n    middle\n    next\n        inner");
  });

  it("allows HTTP and HTTPS links", () => {
    expect(safeHttpUrl("https://cwe.mitre.org/data/definitions/79.html"))
      .toBe("https://cwe.mitre.org/data/definitions/79.html");
    expect(safeHttpUrl("http://example.test/path")).toBe("http://example.test/path");
  });

  it.each([
    "javascript:alert(1)",
    "data:text/html,<script>alert(1)</script>",
    "vbscript:msgbox(1)",
    "file:///etc/passwd",
    "blob:https://example.test/identifier",
    "custom-scheme://example.test/path",
    "JaVaScRiPt:alert(1)",
    " \t\r\nJaVaScRiPt:alert(1)",
    "java\tscript:alert(1)",
    "java\nscript:alert(1)",
  ])("rejects a non-HTTP URL: %s", (value) => {
    expect(safeHttpUrl(value)).toBeUndefined();
  });

  it("rejects malformed URLs", () => {
    expect(safeHttpUrl("not a URL")).toBeUndefined();
    expect(safeHttpUrl(null)).toBeUndefined();
  });
});

function domText(textContent: string) {
  return { nodeType: 3, textContent };
}

function domElement(name: string, childNodes: object[] = [], style: string | null = null) {
  return {
    nodeType: 1,
    localName: name,
    tagName: name.toUpperCase(),
    childNodes,
    textContent: "",
    getAttribute(attribute: string): string | null {
      return attribute === "style" ? style : null;
    },
  };
}
