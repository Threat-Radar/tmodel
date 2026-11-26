#!/usr/bin/env node
/* Lightweight checks of the feasibility prototype (#14, DL-0069). Not wired into CI.
 *   node docs/feasibility/test-feasibility.js
 * Expected values: ISO/SAE 21434:2021 Tables G.6 to G.9 as carried by the library record, the
 * library's hand-worked fixtures (distilled/examples/expected.yaml, incl. the Table H.7 paths), and
 * FIRST CVSS v3.1 Table 16 weights. */
"use strict";
const assert = require("node:assert/strict");
const F = require("./feasibility.js");
const D = require("./examples.js");
let n = 0;
function check(name, fn) { fn(); n++; }

const AP = (v) => F.compute("attack_potential", F.parse(v).vector);
const CVE = (v) => F.compute("cvss", F.parse("CV:3.1/" + v).vector);

check("Table G.6 point values", () => {
  const want = { ET: [0, 1, 4, 17, 19], SE: [0, 3, 6, 8], KN: [0, 3, 7, 11], WO: [0, 1, 4, 10], EQ: [0, 4, 7, 9] };
  F.AP.metrics.forEach((m) => assert.deepEqual(m.levels.filter((l) => !l.ext).map((l) => l.value), want[m.key], m.key));
});
check("Table G.7 bands (library expected.yaml cases)", () => {
  [[0, "high"], [9, "high"], [10, "high"], [13, "high"], [14, "medium"], [19, "medium"], [20, "low"], [24, "low"], [25, "very_low"], [57, "very_low"]]
    .forEach(([s, r]) => assert.equal(F.rateAttackPotential(s), r, String(s)));
});
check("largest sum is 57", () => assert.equal(AP("AP:2021/ET:GT6M/SE:MEX/KN:SCO/WO:DIF/EQ:MBE").value, 57));
check("Table H.7 stated paths AP-4 and AP-5", () => {
  assert.deepEqual([AP("AP:2021/ET:1W/SE:MEX/KN:CON/WO:UNL/EQ:SPE").value, AP("AP:2021/ET:1W/SE:MEX/KN:CON/WO:UNL/EQ:SPE").rating], [20, "low"]);
  assert.deepEqual([AP("AP:2021/ET:1W/SE:MEX/KN:CON/WO:MOD/EQ:SPE").value, AP("AP:2021/ET:1W/SE:MEX/KN:CON/WO:MOD/EQ:SPE").rating], [24, "low"]);
});
check("CVSS exploitability cases (library expected.yaml)", () => {
  [["AV:N/AC:L/PR:N/UI:N", 3.89, "high"], ["AV:A/AC:L/PR:N/UI:N", 2.84, "medium"], ["AV:N/AC:L/PR:L/UI:N", 2.84, "medium"],
   ["AV:L/AC:L/PR:N/UI:N", 2.52, "medium"], ["AV:N/AC:H/PR:N/UI:N", 2.22, "medium"], ["AV:L/AC:H/PR:N/UI:N", 1.44, "low"],
   ["AV:A/AC:H/PR:L/UI:R", 0.86, "very_low"], ["AV:P/AC:L/PR:N/UI:N", 0.91, "very_low"], ["AV:P/AC:H/PR:H/UI:R", 0.12, "very_low"]]
    .forEach(([v, e, r]) => { const c = CVE(v); assert.equal(c.value, e, v); assert.equal(c.rating, r, v); });
});
check("all 48 CVSS combinations: 1 / 8 / 12 / 27, E within 0.12..3.89", () => {
  const count = { high: 0, medium: 0, low: 0, very_low: 0 };
  const M = F.CV.metrics;
  M[0].levels.forEach((a) => M[1].levels.forEach((b) => M[2].levels.forEach((c) => M[3].levels.forEach((d) => {
    const r = CVE(`AV:${a.code}/AC:${b.code}/PR:${c.code}/UI:${d.code}`);
    assert.ok(r.value >= 0.12 && r.value <= 3.89);
    count[r.rating]++;
  }))));
  assert.deepEqual(count, { high: 1, medium: 8, low: 12, very_low: 27 });
});
check("Table G.8 band edges", () => {
  [[3.89, "high"], [2.96, "high"], [2.95, "medium"], [2.0, "medium"], [1.99, "low"], [1.06, "low"], [1.05, "very_low"], [0.12, "very_low"]]
    .forEach(([e, r]) => assert.equal(F.rateExploitability(e), r, String(e)));
});
check("Table G.9 attack vector", () => {
  [["N", "high"], ["A", "medium"], ["L", "low"], ["P", "very_low"]]
    .forEach(([v, r]) => assert.equal(F.compute("attack_vector", F.parse("AX:2021/AV:" + v).vector).rating, r));
});
check("NEX extension: not summed, no rating level, no risk, ISO-strict equivalent", () => {
  const c = AP("AP:2021/ET:1M/SE:EXP/KN:RES/WO:NEX/EQ:SPE");
  assert.equal(c.rating, "not_exploitable");
  assert.equal(c.value, null);
  assert.equal(c.feasibility, null);
  assert.deepEqual([c.isoStrict.total, c.isoStrict.rating], [27, "very_low"]);
  assert.equal(F.risk("severe", c.rating), null);
});
check("Table H.8 example matrix (engine annex-h-table-h8)", () => {
  assert.equal(F.risk("severe", "high"), 5);
  assert.equal(F.risk("severe", "very_low"), 2);
  assert.equal(F.risk("moderate", "medium"), 2);
  assert.equal(F.risk("negligible", "high"), 1);
});
check("parse: canonical round trip and any order", () => {
  const p = F.parse("AP:2021/EQ:SPE/ET:1M/SE:PRO/WO:MOD/KN:RES");
  assert.ok(p.ok);
  assert.equal(F.format(p.method, p.vector), "AP:2021/ET:1M/SE:PRO/KN:RES/WO:MOD/EQ:SPE");
});
check("parse: rejects", () => {
  const bad = {
    "AP:2022/ET:1M/SE:PRO/KN:RES/WO:MOD/EQ:SPE": "unknown version",
    "XX:1/ET:1M": "must start with",
    "AP:2021/ET:1M/SE:PRO/KN:RES/WO:MOD": "missing EQ",
    "AP:2021/ET:1M/ET:1W/SE:PRO/KN:RES/WO:MOD/EQ:SPE": "duplicate metric ET",
    "AP:2021/ET:2M/SE:PRO/KN:RES/WO:MOD/EQ:SPE": "ET has no level 2M",
    "AP:2021/AV:N/ET:1M/SE:PRO/KN:RES/WO:MOD/EQ:SPE": "unknown metric AV",
    "CV:3.1/AV:N/AC:L/PR:N/ui:n": "malformed token",
    "CV:4.0/AV:N/AC:L/AT:N/PR:N/UI:N": "unknown version",
    "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H": "must start with"
  };
  Object.entries(bad).forEach(([v, msg]) => { const p = F.parse(v); assert.equal(p.ok, false, v); assert.ok(p.errors.join("; ").includes(msg), v + " -> " + p.errors); });
});
check("example states", () => {
  const want = { "EX-01": "reviewed", "EX-02": "changed", "EX-03": "overridden", "EX-04": "changed", "EX-05": "changed",
    "EX-06": "stale", "EX-07": "computed", "EX-08": "label", "EX-09": "reviewed", "EX-10": "overridden" };
  D.threats.forEach((t) => assert.equal(F.state(t).state, want[t.id], t.id));
  assert.equal(F.state(D.threats.find((t) => t.id === "EX-10")).stale, true);
  assert.equal(F.state(D.threats.find((t) => t.id === "EX-03")).stale, false);
  assert.equal(D.example_data, true);
});
check("exception flags from history", () => {
  const t2 = D.threats.find((t) => t.id === "EX-02"), t9 = D.threats.find((t) => t.id === "EX-09");
  assert.deepEqual([F.exceptions(t2, "SE").changed, F.exceptions(t2, "SE").comments], [true, 1]);
  assert.equal(F.exceptions(t9, "WO").disputed, true);
  assert.equal(F.exceptions(t9, "KN").comments, 1);
  assert.equal(F.exceptions(t9, "ET").changed || F.exceptions(t9, "ET").disputed || F.exceptions(t9, "ET").comments > 0, false);
});
check("override needs level, rationale, author, date", () => {
  D.threats.filter((t) => t.override).forEach((t) =>
    ["level", "rationale", "decided_by", "decided_at", "vector_at_decision"].forEach((k) => assert.ok(t.override[k], t.id + " " + k)));
});
check("NEX rows carry a basis", () => {
  D.threats.filter((t) => t.vector && t.vector.includes("WO:NEX")).forEach((t) => assert.ok(t.not_exploitable_basis, t.id));
});
console.log(`ok - ${n} checks passed`);
