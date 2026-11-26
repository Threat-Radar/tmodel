/* Feasibility prototype UI (#14, DL-0069). Plain DOM, no build step. Reads window.Feasibility
 * and window.FEASIBILITY_EXAMPLES; changes made on the page are local and never saved. */
(function () {
  "use strict";
  var F = window.Feasibility, D = window.FEASIBILITY_EXAMPLES;
  var RATING_FILL = { high: "#8E1B1B", medium: "#D1523A", low: "#F0A58D", very_low: "#F7DDD3", not_exploitable: "#FFFFFF" };
  var SEGS = { high: 4, medium: 3, low: 2, very_low: 1, not_exploitable: 0 };
  var STATE = {
    computed: { glyph: "\u25CB", label: "Computed", dashed: false },
    reviewed: { glyph: "\u25CF", label: "Reviewed as is", dashed: false },
    changed: { glyph: "\u25B2", label: "Changed by human", dashed: false },
    overridden: { glyph: "\u25C6", label: "Overridden", dashed: false },
    stale: { glyph: "\u25CB", label: "Review stale", dashed: true },
    label: { glyph: "\u25A1", label: "Label only", dashed: true }
  };
  var DEFAULTS = {
    attack_potential: { ET: "1M", SE: "PRO", KN: "RES", WO: "MOD", EQ: "SPE" },
    cvss: { AV: "N", AC: "L", PR: "N", UI: "N" },
    attack_vector: { AV: "N" }
  };
  var params = new URLSearchParams(location.search);
  var view = params.get("view") === "mini" ? "mini" : "compact";
  var openRows = {};
  (params.get("open") || "").split(",").forEach(function (id) { if (id) openRows[id] = true; });
  var edits = {};
  var pinned = null;

  // ---- colour helpers ----
  function rgb(h) { return [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)]; }
  function hex(c) { return "#" + c.map(function (x) { return Math.round(x).toString(16).padStart(2, "0"); }).join(""); }
  function mixWhite(h, t) { var c = rgb(h); return hex([c[0] * t + 255 * (1 - t), c[1] * t + 255 * (1 - t), c[2] * t + 255 * (1 - t)]); }
  function lum(h) { var c = rgb(h).map(function (x) { var s = x / 255; return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4); }); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; }
  function ink(bg) { var l = lum(bg); return 1.05 / (l + 0.05) > (l + 0.05) / (lum("#111827") + 0.05) ? "#FFFFFF" : "#111827"; }
  function hatch(h) { return "repeating-linear-gradient(45deg," + mixWhite(h, 0.4) + " 0 4px,#FFFFFF 4px 8px)"; }
  // Shade = how much the level adds to attacker effort: light = least, full hue = most.
  function hardness(metric, lvl) {
    var vals = metric.levels.filter(function (l) { return !l.ext; });
    var i = vals.indexOf(lvl);
    if (typeof lvl.value === "number") {
      var nums = vals.map(function (l) { return l.value; });
      var lo = Math.min.apply(null, nums), hi = Math.max.apply(null, nums);
      var t = (lvl.value - lo) / (hi - lo);
      return metric.hue === "#5B6B7F" ? 1 - t : t;   // CVSS: lower weight = harder
    }
    return i / (vals.length - 1);                      // attack vector: by order
  }
  function shade(metric, lvl) { return mixWhite(metric.hue, 0.14 + 0.86 * hardness(metric, lvl)); }

  // ---- DOM helper ----
  function h(tag, attrs, kids) {
    var el = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (k === "style") Object.assign(el.style, attrs.style);
      else if (k.slice(0, 2) === "on") el.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] !== null && attrs[k] !== undefined && attrs[k] !== false) el.setAttribute(k, attrs[k]);
    }
    (kids || []).forEach(function (c) { if (c !== null && c !== undefined && c !== false) el.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return el;
  }

  // ---- pieces ----
  function methodTag(m) { return h("span", { class: "mtag", title: m.name }, [m.tag]); }
  function valueText(metric, lvl) {
    if (lvl.ext) return lvl.code + " \u2020";
    if (typeof lvl.value === "number") return lvl.code + " \u00b7 " + (metric.hue === "#5B6B7F" ? String(lvl.value).replace("0.", ".") : lvl.value);
    return lvl.code;
  }
  function chip(threat, metric, code, interactive) {
    var lvl = F.level(metric, code);
    var fill = lvl.ext ? "#FFFFFF" : shade(metric, lvl);
    var exc = threat && interactive ? F.exceptions(threat, metric.key) : null;
    var has = exc && (exc.changed || exc.disputed || exc.comments);
    var cls = "chip" + (has ? " exc " + (exc.disputed ? "exc-disputed" : exc.changed ? "exc-changed" : "exc-comment") : "");
    var el = h(has ? "button" : "span", { class: cls, type: has ? "button" : null,
      title: metric.name + ": " + lvl.label + (lvl.ext ? " (tmodel extension, not ISO/SAE 21434)" : ""),
      "aria-label": metric.name + " " + lvl.label + (has ? ", has history" : "") }, [
      h("span", { class: "ck", style: { background: metric.hue, color: ink(metric.hue), borderColor: metric.hue } }, [metric.key]),
      h("span", { class: "cv", style: { background: fill, backgroundImage: lvl.ext ? hatch(metric.hue) : "none", color: ink(fill), borderColor: metric.hue } },
        [lvl.ext ? h("span", { class: "extlbl" }, [valueText(metric, lvl)]) : valueText(metric, lvl)])
    ]);
    if (has) {
      if (exc.changed) el.appendChild(h("span", { class: "badge b-changed", "aria-hidden": "true" }, ["\u0394"]));
      if (exc.disputed) el.appendChild(h("span", { class: "badge b-disputed", "aria-hidden": "true" }, ["!"]));
      if (exc.comments) el.appendChild(h("span", { class: "badge b-comment" + (exc.changed ? " shift" : ""), "aria-hidden": "true" }, [String(exc.comments)]));
      var id = threat.id + ":" + metric.key;
      el.addEventListener("mouseenter", function () { if (!pinned) showPop(el, threat, metric, exc, false); });
      el.addEventListener("mouseleave", function () { if (!pinned) hidePop(); });
      el.addEventListener("focus", function () { if (!pinned) showPop(el, threat, metric, exc, false); });
      el.addEventListener("blur", function () { if (!pinned) hidePop(); });
      el.addEventListener("click", function (ev) {
        ev.stopPropagation();
        if (pinned === id) { pinned = null; hidePop(); } else { pinned = id; showPop(el, threat, metric, exc, true); }
      });
      el.setAttribute("data-pin", id);
    }
    return el;
  }
  function ratingChip(rating, text, small) {
    var fill = RATING_FILL[rating];
    var nex = rating === "not_exploitable";
    var meter = h("span", { class: "meter", "aria-hidden": "true" }, [0, 1, 2, 3].map(function (i) {
      return h("span", { style: { background: i < SEGS[rating] ? ink(fill) : "transparent", borderColor: nex ? "#111827" : ink(fill) } });
    }));
    return h("span", { class: "rchip" + (small ? " small" : "") + (nex ? " nex" : ""), style: { background: fill, color: nex ? "#111827" : ink(fill), backgroundImage: nex ? hatch("#5B6B7F") : "none" } },
      [meter, h("span", { class: nex ? "extlbl" : null }, [F.RATING_LABEL[rating] + (nex ? " \u2020" : "") + (text && !small ? " \u00b7 " + text : "")])]);
  }
  function stateMark(st, short) {
    var s = STATE[st.state];
    var detail = (st.by ? " " + st.by : "") + (st.stale ? ", stale" : "");
    return h("span", { class: "smark" + (s.dashed || st.stale ? " dashed" : ""), title: s.label + detail + (st.detail ? " (" + st.detail + ")" : "") },
      [h("span", { "aria-hidden": "true" }, [s.glyph]), short ? null : " " + s.label + detail]);
  }
  function mini(m, vec) {
    return h("span", { class: "mini", title: m.metrics.map(function (x) { return x.key + " " + F.level(x, vec[x.key]).label; }).join(", ") },
      m.metrics.map(function (x) {
        var l = F.level(x, vec[x.key]);
        return h("span", { style: { borderColor: x.hue, background: l.ext ? "#FFFFFF" : shade(x, l), backgroundImage: l.ext ? hatch(x.hue) : "none" } });
      }));
  }
  function ratedCell(threat, small) {
    var st = F.state(threat), eff = F.effective(threat);
    var kids = [];
    if (!threat.vector) {
      kids.push(ratingChip(threat.label, null, small));
    } else if (eff.overridden) {
      kids.push(ratingChip(eff.rating, null, small));
      if (!small) kids.push(h("span", { class: "struck" }, ["computed ", h("s", null, [F.RATING_LABEL[eff.computed.rating]])]));
    } else {
      kids.push(ratingChip(eff.rating, eff.computed.display, small));
    }
    kids.push(stateMark(st, small));
    return h("span", { class: "rated" }, kids);
  }
  function compactRow(threat) {
    var wrap = h("span", { class: "row1" }, []);
    if (!threat.vector) { wrap.appendChild(h("span", { class: "mtag none", title: "no method recorded" }, ["\u2014"])); wrap.appendChild(ratedCell(threat, view === "mini")); return wrap; }
    var p = F.parse(threat.vector), m = F.methodById(p.method);
    wrap.appendChild(methodTag(m));
    if (view === "mini") wrap.appendChild(mini(m, p.vector));
    else m.metrics.forEach(function (x) { wrap.appendChild(chip(threat, x, p.vector[x.key], true)); });
    wrap.appendChild(ratedCell(threat, view === "mini"));
    return wrap;
  }
  function riskCell(threat) {
    var eff = F.effective(threat);
    var r = F.risk(threat.impact, eff.rating);
    if (r === null) return h("span", { class: "norisk", title: "Not exploitable (tmodel extension): no risk value; Table H.8 not applied" }, ["no risk \u2020"]);
    return h("span", { class: "risk" }, [h("strong", null, [String(r)]), " ", h("span", { class: "muted" }, ["(" + threat.impact + ")"])]);
  }

  // ---- popover ----
  var pop = null;
  function showPop(anchor, threat, metric, exc, isPinned) {
    hidePop();
    var cur = F.parse(threat.vector).vector[metric.key];
    pop = h("div", { class: "pop" + (isPinned ? " pinned" : ""), role: "dialog", "aria-label": "History for " + metric.name }, [
      h("div", { class: "pop-h" }, [metric.name + ": " + F.level(metric, cur).label + " (" + metric.key + ":" + cur + ")"]),
      h("div", { class: "pop-flags" }, [
        exc.changed ? h("span", { class: "flag" }, ["\u0394 changed by a reviewer"]) : null,
        exc.disputed ? h("span", { class: "flag" }, ["! open dispute"]) : null,
        exc.comments ? h("span", { class: "flag" }, [exc.comments + " comment" + (exc.comments > 1 ? "s" : "")]) : null
      ]),
      h("ol", { class: "hist" }, histItems((threat.history || []).filter(function (ev) { return ev.factor === metric.key || (!ev.factor && ev.ref); }))),
      h("div", { class: "pop-f" }, [isPinned ? "Pinned. Click the chip again or press Esc to close." : "Click the chip to pin."])
    ]);
    document.body.appendChild(pop);
    var r = anchor.getBoundingClientRect();
    var left = Math.min(window.scrollX + r.left, window.scrollX + document.documentElement.clientWidth - pop.offsetWidth - 12);
    pop.style.left = Math.max(8, left) + "px";
    pop.style.top = (window.scrollY + r.bottom + 10) + "px";
  }
  function hidePop() { if (pop) { pop.remove(); pop = null; } }
  function histItems(events) {
    return events.map(function (ev) {
      return h("li", null, [
        h("span", { class: "kind" }, [ev.kind.replace("_", " ").toUpperCase()]), " ",
        h("code", null, [ev.at]), " ", h("span", null, [ev.by]),
        ev.from && ev.to ? h("code", { class: "delta" }, [ev.from + " \u2192 " + ev.to]) : (ev.to ? h("code", { class: "delta" }, ["= " + ev.to]) : null),
        ev.ref ? h("code", { class: "ref" }, [ev.ref]) : null,
        ev.text ? h("div", { class: "muted" }, [ev.text]) : null
      ]);
    });
  }
  document.addEventListener("click", function () { if (pinned) { pinned = null; hidePop(); } });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") { pinned = null; hidePop(); } });

  // ---- breakdown bars ----
  var SVGNS = "http://www.w3.org/2000/svg";
  function s(tag, attrs, text) { var el = document.createElementNS(SVGNS, tag); for (var k in attrs) el.setAttribute(k, attrs[k]); if (text !== undefined) el.textContent = text; return el; }
  function apBar(vec) {
    var max = 57, x0 = 10, w = 680, sc = w / max, c = F.compute("attack_potential", vec);
    var svg = s("svg", { viewBox: "0 0 700 112", width: "100%", role: "img", "aria-label": c.notExploitable ? "Not exploitable" : "Attack potential " + c.value + " of 57" });
    svg.appendChild(s("text", { x: x0, y: 9, class: "svgt" }, c.notExploitable ? "window of opportunity not exploitable (\u2020 extension): not summed; other factors shown for reference" : "contribution by factor (points of 57)"));
    var acc = 0;
    F.AP.metrics.forEach(function (x) {
      var l = F.level(x, vec[x.key]); if (l.ext || !l.value) return;
      var fill = shade(x, l);
      svg.appendChild(s("rect", { x: x0 + acc * sc, y: 14, width: l.value * sc, height: 32, fill: fill, stroke: x.hue, "stroke-width": 1.5, opacity: c.notExploitable ? 0.5 : 1 }));
      if (l.value * sc >= 44) svg.appendChild(s("text", { x: x0 + (acc + l.value / 2) * sc, y: 34, "text-anchor": "middle", class: "svgv", fill: ink(fill) }, x.key + " " + l.value));
      acc += l.value;
    });
    [[0, 14, "high"], [14, 6, "medium"], [20, 5, "low"], [25, 32, "very_low"]].forEach(function (z) {
      svg.appendChild(s("rect", { x: x0 + z[0] * sc, y: 60, width: z[1] * sc, height: 14, fill: RATING_FILL[z[2]], stroke: "#c9c3b6", "stroke-width": 0.5 }));
    });
    [0, 14, 20, 25, 57].forEach(function (t, i) { svg.appendChild(s("text", { x: x0 + t * sc, y: 90, "text-anchor": i === 0 ? "start" : i === 4 ? "end" : "middle", class: "svgt" }, String(t))); });
    [["High", 7], ["Medium", 17], ["Low", 22.5], ["Very low", 41]].forEach(function (z) { svg.appendChild(s("text", { x: x0 + z[1] * sc, y: 106, "text-anchor": "middle", class: "svgt" }, z[0])); });
    if (!c.notExploitable) svg.appendChild(s("path", { d: "M" + (x0 + Math.min(c.value, max) * sc) + " 58 l-5 -9 h10 z", class: "svgm" }));
    return svg;
  }
  function cvBar(e) {
    var max = 3.89, x0 = 10, w = 680, sc = w / max;
    var svg = s("svg", { viewBox: "0 0 700 80", width: "100%", role: "img", "aria-label": "Exploitability " + e.toFixed(2) });
    svg.appendChild(s("text", { x: x0, y: 9, class: "svgt" }, "exploitability E on the Table G.8 bands (a product, so no per-metric stack)"));
    [[0, 1.055, "very_low"], [1.055, 1.995, "low"], [1.995, 2.955, "medium"], [2.955, max, "high"]].forEach(function (z) {
      svg.appendChild(s("rect", { x: x0 + z[0] * sc, y: 28, width: (z[1] - z[0]) * sc, height: 14, fill: RATING_FILL[z[2]], stroke: "#c9c3b6", "stroke-width": 0.5 }));
      svg.appendChild(s("text", { x: x0 + ((z[0] + z[1]) / 2) * sc, y: 74, "text-anchor": "middle", class: "svgt" }, F.RATING_LABEL[z[2]]));
    });
    [0.12, 1.06, 2.0, 2.96, 3.89].forEach(function (t, i) { svg.appendChild(s("text", { x: x0 + t * sc, y: 58, "text-anchor": i === 0 ? "start" : i === 4 ? "end" : "middle", class: "svgt" }, t.toFixed(2))); });
    svg.appendChild(s("path", { d: "M" + (x0 + Math.min(e, max) * sc) + " 26 l-5 -9 h10 z", class: "svgm" }));
    return svg;
  }

  // ---- expanded view ----
  function expanded(threat) {
    var rec = threat.vector ? F.parse(threat.vector) : null;
    var ed = edits[threat.id] || (edits[threat.id] = { method: rec ? rec.method : F.DEFAULT_METHOD, vec: {} });
    if (!ed.vec[ed.method]) ed.vec[ed.method] = Object.assign({}, rec && rec.method === ed.method ? rec.vector : DEFAULTS[ed.method]);
    var m = F.methodById(ed.method), vec = ed.vec[ed.method], c = F.compute(m.id, vec);
    var box = h("div", { class: "expanded" }, []);
    box.appendChild(h("div", { class: "seg", role: "group", "aria-label": "Method" }, F.METHODS.map(function (mm) {
      return h("button", { type: "button", "aria-pressed": String(mm.id === ed.method), onclick: function () { ed.method = mm.id; render(); } }, [mm.name + (mm.id === F.DEFAULT_METHOD ? " (default)" : "")]);
    })));
    m.metrics.forEach(function (x) {
      box.appendChild(h("div", { class: "pick" }, [
        h("div", { class: "pick-name" }, [h("span", { class: "swatch", style: { background: x.hue } }), x.name]),
        h("div", { class: "pick-levels" }, x.levels.map(function (l) {
          var fill = l.ext ? "#FFFFFF" : shade(x, l), sel = vec[x.key] === l.code;
          return h("button", { type: "button", class: "lvl" + (sel ? " sel" : ""), "aria-pressed": String(sel),
            style: { background: fill, backgroundImage: l.ext ? hatch(x.hue) : "none", color: ink(fill), outlineColor: x.hue },
            onclick: function () { vec[x.key] = l.code; render(); } },
            [h("span", { class: l.ext ? "extlbl" : null }, [l.label + (l.ext ? " \u2020" : "")]), h("br"), h("small", null, [valueText(x, l)])]);
        }))
      ]));
    });
    var str = F.format(m.id, vec);
    var differs = threat.vector && str !== threat.vector;
    box.appendChild(h("div", { class: "result" }, [
      ratingChip(c.rating, c.display), " ", h("code", null, [str]),
      differs ? h("span", { class: "muted" }, [" Edited here, not saved: a human edit would mark this row \u25B2 Changed by human."]) : null
    ]));
    if (c.notExploitable) box.appendChild(h("p", { class: "muted" }, ["\u2020 tmodel extension, not ISO/SAE 21434: no total, no risk value. ISO-strict equivalent (window difficult, 10 points): " + c.isoStrict.total + " pts, " + F.RATING_LABEL[c.isoStrict.rating] + "."]));
    if (m.id === "attack_potential") box.appendChild(apBar(vec));
    if (m.id === "cvss") box.appendChild(cvBar(c.value));
    var facts = h("dl", { class: "facts" }, []);
    function fact(k, v) { facts.appendChild(h("dt", null, [k])); facts.appendChild(h("dd", null, [v])); }
    var st = F.state(threat);
    fact("State", stateMark(st, false));
    if (threat.override) fact("Override", threat.override.level + " by " + threat.override.decided_by + " at " + threat.override.decided_at + ". Rationale: " + threat.override.rationale + (st.stale ? " (stale: vector changed since; stays in force, needs re-confirmation)" : ""));
    if (threat.not_exploitable_basis) fact("Not-exploitable basis", threat.not_exploitable_basis);
    fact("Risk (Table H.8 example)", riskCell(threat));
    box.appendChild(facts);
    if ((threat.history || []).length) {
      box.appendChild(h("h4", null, ["History"]));
      box.appendChild(h("ol", { class: "hist" }, histItems(threat.history)));
    }
    return box;
  }

  // ---- main table ----
  function render() {
    var host = document.getElementById("rows");
    host.innerHTML = "";
    hidePop();
    var tbl = h("table", { class: "ft" }, [h("thead", null, [h("tr", null, ["ID", "Threat scenario", "Feasibility", "Risk", ""].map(function (t) { return h("th", null, [t]); }))])]);
    var tb = h("tbody");
    D.threats.forEach(function (t) {
      tb.appendChild(h("tr", null, [
        h("td", null, [h("code", null, [t.id])]), h("td", null, [t.title]), h("td", null, [compactRow(t)]), h("td", null, [riskCell(t)]),
        h("td", null, [h("button", { type: "button", class: "more", "aria-expanded": String(!!openRows[t.id]), onclick: function () { openRows[t.id] = !openRows[t.id]; render(); } }, [openRows[t.id] ? "Close" : "Open"])])
      ]));
      if (openRows[t.id]) tb.appendChild(h("tr", { class: "exp-row" }, [h("td", { colspan: "5" }, [expanded(t)])]));
    });
    tbl.appendChild(tb);
    host.appendChild(tbl);
    document.querySelectorAll("[data-view]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-view") === view)); });
  }

  function legend() {
    var host = document.getElementById("legend");
    var demo = { id: "LEGEND", vector: "AP:2021/ET:1M/SE:PRO/KN:RES/WO:MOD/EQ:SPE", history: [] };
    var row = function (label, el) { return h("tr", null, [h("td", null, [label]), h("td", null, [el])]); };
    var t = h("table", { class: "lg" }, [h("tbody", null, [
      row("Factor hue (attack potential)", h("span", { class: "row1" }, F.AP.metrics.map(function (x) { return h("span", { class: "sw" }, [h("span", { class: "swatch", style: { background: x.hue } }), x.key + " " + x.name.toLowerCase()]); }))),
      row("Shade: more effort for the attacker", h("span", { class: "row1" }, F.AP.metrics.concat(F.CV.metrics).map(function (x) {
        return h("span", { class: "strip", title: x.name }, x.levels.map(function (l) { return chip(null, x, l.code, false); }));
      }))),
      row("Rating", h("span", { class: "row1" }, ["high", "medium", "low", "very_low", "not_exploitable"].map(function (r) { return ratingChip(r); }))),
      row("State (shape and text, never colour)", h("span", { class: "row1" }, ["computed", "reviewed", "changed", "overridden", "stale", "label"].map(function (k) { return stateMark({ state: k }, false); }))),
      row("Exception on one item (outline and glyph)", h("span", { class: "row1" }, [
        fakeExc(F.AP.metrics[1], "EXP", "exc-changed", [["b-changed", "\u0394"]], "changed by a reviewer"),
        fakeExc(F.AP.metrics[3], "MOD", "exc-disputed", [["b-disputed", "!"]], "disputed"),
        fakeExc(F.AP.metrics[2], "RES", "exc-comment", [["b-comment", "2"]], "comments")
      ])),
      row("\u2020", "tmodel extension beyond ISO/SAE 21434 (window of opportunity: not exploitable). Never shown unmarked.")
    ])]);
    host.appendChild(t);
    void demo;
  }
  function fakeExc(metric, code, cls, badges, caption) {
    var el = chip(null, metric, code, false);
    el.className = "chip exc " + cls;
    badges.forEach(function (b) { el.appendChild(h("span", { class: "badge " + b[0], "aria-hidden": "true" }, [b[1]])); });
    return h("span", { class: "sw" }, [el, " " + caption]);
  }

  function validator() {
    var inp = document.getElementById("vin"), out = document.getElementById("vout");
    function run() {
      out.innerHTML = "";
      var p = F.parse(inp.value);
      if (!p.ok) { out.appendChild(h("p", { class: "err" }, ["Invalid: " + p.errors.join("; ")])); return; }
      var m = F.methodById(p.method), c = F.compute(p.method, p.vector);
      var r = h("span", { class: "row1" }, [methodTag(m)]);
      m.metrics.forEach(function (x) { r.appendChild(chip(null, x, p.vector[x.key], false)); });
      r.appendChild(ratingChip(c.rating, c.display));
      out.appendChild(r);
      out.appendChild(h("p", null, ["Canonical: ", h("code", null, [F.format(p.method, p.vector)])]));
      if (c.isoStrict) out.appendChild(h("p", { class: "muted" }, ["\u2020 ISO-strict equivalent: " + c.isoStrict.vector + " gives " + c.isoStrict.total + " pts, " + F.RATING_LABEL[c.isoStrict.rating] + "."]));
    }
    inp.addEventListener("input", run);
    run();
  }

  document.querySelectorAll("[data-view]").forEach(function (b) {
    b.addEventListener("click", function () { view = b.getAttribute("data-view"); render(); });
  });
  legend();
  render();
  validator();
  var pin = params.get("pin");
  if (pin) {
    var el = document.querySelector('[data-pin="' + pin + '"]');
    if (el) el.click();
  }
})();
