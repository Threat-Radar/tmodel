/* tmodel attack-feasibility vectors: standalone prototype core (#14, DL-0069).
 * Pure functions, no DOM. Works as a browser script (window.Feasibility) and in node (require).
 * Values: ISO/SAE 21434:2021 Annex G (Tables G.6, G.7, G.8, G.9) as carried by the library record
 * records/iso/iso-sae-21434-2021/distilled/examples/annex-g-feasibility.yaml; CVSS v3.1 metric
 * weights from FIRST CVSS v3.1 Table 16. Level names and numbers only; no standard text.
 * Items marked ext are tmodel extensions beyond ISO/SAE 21434 (WO:NEX). */
(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.Feasibility = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  var RATINGS = ["high", "medium", "low", "very_low"];
  var RATING_LABEL = { high: "High", medium: "Medium", low: "Low", very_low: "Very low", not_exploitable: "Not exploitable" };

  function lv(code, label, value, extra) {
    var o = { code: code, label: label, value: value };
    if (extra) for (var k in extra) o[k] = extra[k];
    return o;
  }

  // Attack potential, Table G.6 (factor tables G.1 to G.5). WO:NEX is a tmodel extension.
  var AP = {
    id: "attack_potential", tag: "AP", prefix: "AP:2021", name: "Attack potential",
    source: "ISO/SAE 21434:2021 G.2, Tables G.1 to G.7",
    metrics: [
      { key: "ET", name: "Elapsed time", table: "G.1", hue: "#0072B2", levels: [
        lv("1D", "up to 1 day", 0), lv("1W", "up to 1 week", 1), lv("1M", "up to 1 month", 4),
        lv("6M", "up to 6 months", 17), lv("GT6M", "more than 6 months", 19)] },
      { key: "SE", name: "Specialist expertise", table: "G.2", hue: "#CC79A7", levels: [
        lv("LAY", "layman", 0), lv("PRO", "proficient", 3), lv("EXP", "expert", 6), lv("MEX", "multiple experts", 8)] },
      { key: "KN", name: "Knowledge of the item or component", table: "G.3", hue: "#009E73", levels: [
        lv("PUB", "public", 0), lv("RES", "restricted", 3), lv("CON", "confidential", 7), lv("SCO", "strictly confidential", 11)] },
      { key: "WO", name: "Window of opportunity", table: "G.4", hue: "#56B4E9", levels: [
        lv("UNL", "unlimited", 0), lv("EAS", "easy", 1), lv("MOD", "moderate", 4), lv("DIF", "difficult", 10),
        lv("NEX", "not exploitable", null, { ext: true })] },
      { key: "EQ", name: "Equipment", table: "G.5", hue: "#E69F00", levels: [
        lv("STD", "standard", 0), lv("SPE", "specialized", 4), lv("BES", "bespoke", 7), lv("MBE", "multiple bespoke", 9)] }
    ]
  };
  // CVSS exploitability, G.3 / Table G.8. Weights: FIRST CVSS v3.1 Table 16 (scope unchanged).
  var SLATE = "#5B6B7F";
  var CV = {
    id: "cvss", tag: "CVSS", prefix: "CV:3.1", name: "CVSS exploitability",
    source: "ISO/SAE 21434:2021 G.3, Table G.8; weights FIRST CVSS v3.1 Table 16",
    metrics: [
      { key: "AV", name: "Attack vector", hue: SLATE, levels: [lv("N", "network", 0.85), lv("A", "adjacent", 0.62), lv("L", "local", 0.55), lv("P", "physical", 0.2)] },
      { key: "AC", name: "Attack complexity", hue: SLATE, levels: [lv("L", "low", 0.77), lv("H", "high", 0.44)] },
      { key: "PR", name: "Privileges required", hue: SLATE, levels: [lv("N", "none", 0.85), lv("L", "low", 0.62), lv("H", "high", 0.27)] },
      { key: "UI", name: "User interaction", hue: SLATE, levels: [lv("N", "none", 0.85), lv("R", "required", 0.62)] }
    ]
  };
  // Attack vector, G.4 / Table G.9.
  var AX = {
    id: "attack_vector", tag: "AV", prefix: "AX:2021", name: "Attack vector",
    source: "ISO/SAE 21434:2021 G.4, Table G.9",
    metrics: [
      { key: "AV", name: "Attack vector (predominant)", hue: SLATE, levels: [
        lv("N", "network", "high"), lv("A", "adjacent", "medium"), lv("L", "local", "low"), lv("P", "physical", "very_low")] }
    ]
  };
  var METHODS = [AP, CV, AX];
  var DEFAULT_METHOD = "attack_potential";

  function methodById(id) { for (var i = 0; i < METHODS.length; i++) if (METHODS[i].id === id) return METHODS[i]; return null; }
  function level(metric, code) { for (var i = 0; i < metric.levels.length; i++) if (metric.levels[i].code === code) return metric.levels[i]; return null; }

  // Table G.7: 0-9 and 10-13 High, 14-19 Medium, 20-24 Low, 25+ Very low.
  function rateAttackPotential(total) { return total <= 13 ? "high" : total <= 19 ? "medium" : total <= 24 ? "low" : "very_low"; }
  // Table G.8 bands on E rounded to two decimals (rounding is a tmodel reading; it changes no rating).
  function rateExploitability(e) { return e >= 2.96 ? "high" : e >= 2.0 ? "medium" : e >= 1.06 ? "low" : "very_low"; }
  function round2(x) { return Math.round(x * 100 + 1e-9) / 100; }

  function parse(text) {
    var errors = [];
    var s = String(text == null ? "" : text).trim();
    var parts = s.split("/");
    var m = null;
    for (var i = 0; i < METHODS.length; i++) if (METHODS[i].prefix === parts[0]) m = METHODS[i];
    if (!m) {
      errors.push(/^(AP|CV|AX):/.test(parts[0] || "") ? "unknown version " + parts[0] : "must start with AP:2021, CV:3.1 or AX:2021");
      return { ok: false, errors: errors };
    }
    var vec = {};
    parts.slice(1).forEach(function (p) {
      var mm = /^([A-Z]{2}):([A-Z0-9]+)$/.exec(p);
      if (!mm) { errors.push("malformed token " + (p === "" ? "(empty)" : p)); return; }
      var metric = null;
      m.metrics.forEach(function (x) { if (x.key === mm[1]) metric = x; });
      if (!metric) { errors.push("unknown metric " + mm[1] + " for " + m.tag); return; }
      if (vec[mm[1]] !== undefined) { errors.push("duplicate metric " + mm[1]); return; }
      if (!level(metric, mm[2])) { errors.push(mm[1] + " has no level " + mm[2]); return; }
      vec[mm[1]] = mm[2];
    });
    var missing = m.metrics.filter(function (x) { return vec[x.key] === undefined; }).map(function (x) { return x.key; });
    if (missing.length) errors.push("missing " + missing.join(", "));
    return errors.length ? { ok: false, errors: errors, method: m.id } : { ok: true, errors: [], method: m.id, vector: vec };
  }

  function format(methodId, vec) {
    var m = methodById(methodId);
    return m.prefix + "/" + m.metrics.map(function (x) { return x.key + ":" + vec[x.key]; }).join("/");
  }

  // Returns rating (a Table 1 level, or "not_exploitable" for the extension), value and display text.
  function compute(methodId, vec) {
    var m = methodById(methodId);
    if (m.id === "attack_potential") {
      var nex = vec.WO === "NEX";
      var sum = 0;
      m.metrics.forEach(function (x) { if (!(nex && x.key === "WO")) sum += level(x, vec[x.key]).value; });
      if (nex) {
        return { method: m.id, notExploitable: true, rating: "not_exploitable", feasibility: null, value: null,
          display: "not summed", isoStrict: { vector: format(m.id, Object.assign({}, vec, { WO: "DIF" })), total: sum + 10, rating: rateAttackPotential(sum + 10) } };
      }
      return { method: m.id, notExploitable: false, rating: rateAttackPotential(sum), feasibility: rateAttackPotential(sum), value: sum, display: sum + " pts", isoStrict: null };
    }
    if (m.id === "cvss") {
      var prod = 8.22;
      m.metrics.forEach(function (x) { prod *= level(x, vec[x.key]).value; });
      var e = round2(prod);
      return { method: m.id, notExploitable: false, rating: rateExploitability(e), feasibility: rateExploitability(e), value: e, display: "E " + e.toFixed(2), isoStrict: null };
    }
    var r = level(m.metrics[0], vec.AV).value;
    return { method: m.id, notExploitable: false, rating: r, feasibility: r, value: null, display: level(m.metrics[0], vec.AV).label, isoStrict: null };
  }

  // Informative Annex H example matrix, as engine/engine/risk.py (annex-h-table-h8).
  var H8 = { negligible: [1, 1, 1, 1], moderate: [1, 2, 2, 3], major: [1, 2, 3, 4], severe: [2, 3, 4, 5] };
  var H8_COLS = ["very_low", "low", "medium", "high"];
  // Not exploitable gives no risk value (sponsor decision); it does not feed Table H.8.
  function risk(impact, feasibility) {
    if (!feasibility || feasibility === "not_exploitable") return null;
    return H8[impact][H8_COLS.indexOf(feasibility)];
  }

  function isHuman(by) { return typeof by === "string" && by.charAt(0) === "@"; }

  // Rating state from a threat's recorded history. Every row starts with the default method;
  // a human then approves it as it stands (reviewed) or changes method or values (changed).
  function state(threat) {
    if (!threat.vector) return { state: "label", label: "Label only" };
    var current = threat.vector;
    var hist = threat.history || [];
    var lastHuman = null, humanChanged = false;
    hist.forEach(function (ev) {
      if (!isHuman(ev.by)) return;
      if (ev.kind === "changed" || ev.kind === "method_changed") { humanChanged = true; lastHuman = ev; }
      if (ev.kind === "reviewed") lastHuman = ev;
    });
    var ov = threat.override;
    if (ov) {
      var fresh = ov.vector_at_decision === current;
      return { state: "overridden", label: "Overridden", by: ov.decided_by, at: ov.decided_at, stale: !fresh,
        detail: fresh ? null : "vector changed since override" };
    }
    if (!lastHuman) return { state: "computed", label: "Computed" };
    if (lastHuman.vector_after !== current) return { state: "stale", label: "Review stale", by: lastHuman.by, at: lastHuman.at, detail: "vector changed since review" };
    if (humanChanged) return { state: "changed", label: "Changed by human", by: lastHuman.by, at: lastHuman.at };
    return { state: "reviewed", label: "Reviewed as is", by: lastHuman.by, at: lastHuman.at };
  }

  // Exception flags for one vector item, derived from history.
  function exceptions(threat, key) {
    var hist = (threat.history || []).filter(function (ev) { return ev.factor === key; });
    var changed = hist.some(function (ev) { return ev.kind === "changed" && isHuman(ev.by) && ev.from !== ev.to; });
    var open = 0;
    hist.forEach(function (ev) { if (ev.kind === "disputed") open++; if (ev.kind === "resolved" && open > 0) open--; });
    var comments = hist.filter(function (ev) { return ev.kind === "commented" || ev.kind === "disputed"; }).length;
    return { changed: changed, disputed: open > 0, comments: comments, events: hist };
  }

  function effective(threat) {
    if (!threat.vector) return { rating: threat.label || null, computed: null, overridden: false };
    var p = parse(threat.vector);
    var c = compute(p.method, p.vector);
    if (threat.override) return { rating: threat.override.level, computed: c, overridden: true };
    return { rating: c.rating, computed: c, overridden: false };
  }

  return {
    METHODS: METHODS, AP: AP, CV: CV, AX: AX, DEFAULT_METHOD: DEFAULT_METHOD, RATINGS: RATINGS, RATING_LABEL: RATING_LABEL,
    H8: H8, methodById: methodById, level: level, parse: parse, format: format, compute: compute,
    rateAttackPotential: rateAttackPotential, rateExploitability: rateExploitability, risk: risk,
    state: state, exceptions: exceptions, effective: effective
  };
});
