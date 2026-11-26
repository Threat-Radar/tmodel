/* EXAMPLE DATA: invented threat scenarios for the feasibility prototype (#14, DL-0069).
 * Not a real model, not read from or written to any model file. Handles are placeholders.
 * JSON-shaped; loaded as a script so the page also works when opened from disk. */
(function (root) {
  var data = {
    schema: "tmodel-feasibility-prototype-examples/v1",
    example_data: true,
    note: "Invented examples for layout and behaviour only. Not a threat model.",
    threats: [
      { id: "EX-01", title: "Remote command injection over the cellular link", impact: "severe",
        vector: "AP:2021/ET:1W/SE:PRO/KN:PUB/WO:EAS/EQ:STD",
        history: [
          { at: "2026-11-20 09:00", by: "tmodel", kind: "default_method", to: "attack_potential" },
          { at: "2026-11-20 09:02", by: "AI hook", kind: "proposed", to: "AP:2021/ET:1W/SE:PRO/KN:PUB/WO:EAS/EQ:STD", ref: "proposal P-EX01" },
          { at: "2026-11-21 10:15", by: "@analyst-a", kind: "reviewed", vector_after: "AP:2021/ET:1W/SE:PRO/KN:PUB/WO:EAS/EQ:STD", ref: "accept A-EX01", text: "Approved as proposed." }
        ] },
      { id: "EX-02", title: "Tamper with ECU flash through the diagnostic port", impact: "major",
        vector: "AP:2021/ET:1M/SE:EXP/KN:RES/WO:MOD/EQ:SPE",
        history: [
          { at: "2026-11-20 09:00", by: "tmodel", kind: "default_method", to: "attack_potential" },
          { at: "2026-11-20 09:03", by: "AI hook", kind: "proposed", to: "AP:2021/ET:1M/SE:PRO/KN:RES/WO:MOD/EQ:SPE", ref: "proposal P-EX02" },
          { at: "2026-11-21 11:40", by: "@reviewer-b", kind: "changed", factor: "SE", from: "PRO", to: "EXP", vector_after: "AP:2021/ET:1M/SE:EXP/KN:RES/WO:MOD/EQ:SPE", ref: "accept A-EX02",
            text: "Public write-up covers only the first step; the rest needs bench and firmware skill." },
          { at: "2026-11-21 15:05", by: "@analyst-a", kind: "commented", factor: "SE", text: "Agreed after reading the write-up again." }
        ] },
      { id: "EX-03", title: "Extract a key by fault injection", impact: "severe",
        vector: "AP:2021/ET:1M/SE:EXP/KN:RES/WO:MOD/EQ:SPE",
        override: { level: "medium", rationale: "Fault-injection kits are now sold ready-made; the equipment factor understates how easy this has become.",
          decided_by: "@reviewer-b", decided_at: "2026-11-22 14:30", vector_at_decision: "AP:2021/ET:1M/SE:EXP/KN:RES/WO:MOD/EQ:SPE" },
        history: [
          { at: "2026-11-20 09:00", by: "tmodel", kind: "default_method", to: "attack_potential" },
          { at: "2026-11-20 09:04", by: "AI hook", kind: "proposed", to: "AP:2021/ET:1M/SE:EXP/KN:RES/WO:MOD/EQ:SPE", ref: "proposal P-EX03" },
          { at: "2026-11-22 14:30", by: "@reviewer-b", kind: "override", from: "low", to: "medium", text: "Override with rationale (see record)." }
        ] },
      { id: "EX-04", title: "Debug header inside a sealed, tamper-evident enclosure", impact: "severe",
        vector: "AP:2021/ET:1M/SE:EXP/KN:RES/WO:NEX/EQ:SPE",
        not_exploitable_basis: "Header sits inside a potted, tamper-evident housing that is inspected at every service; the path is out of reach in the intended operating environment.",
        history: [
          { at: "2026-11-20 09:00", by: "tmodel", kind: "default_method", to: "attack_potential" },
          { at: "2026-11-20 09:05", by: "AI hook", kind: "proposed", to: "AP:2021/ET:1M/SE:EXP/KN:RES/WO:MOD/EQ:SPE", ref: "proposal P-EX04" },
          { at: "2026-11-22 09:20", by: "@reviewer-b", kind: "changed", factor: "WO", from: "MOD", to: "NEX", vector_after: "AP:2021/ET:1M/SE:EXP/KN:RES/WO:NEX/EQ:SPE",
            text: "Not exploitable: sealed housing; basis recorded." }
        ] },
      { id: "EX-05", title: "Pairing window on the Bluetooth interface", impact: "moderate",
        vector: "CV:3.1/AV:A/AC:L/PR:N/UI:R",
        history: [
          { at: "2026-11-20 09:00", by: "tmodel", kind: "default_method", to: "attack_potential" },
          { at: "2026-11-21 13:00", by: "@analyst-a", kind: "method_changed", from: "attack_potential", to: "cvss", vector_after: "CV:3.1/AV:A/AC:L/PR:N/UI:R",
            text: "A published CVSS vector exists for this stack; rate with the CVSS approach." }
        ] },
      { id: "EX-06", title: "Malicious update from a USB maintenance stick", impact: "major",
        vector: "CV:3.1/AV:L/AC:L/PR:L/UI:N",
        history: [
          { at: "2026-11-20 09:00", by: "tmodel", kind: "default_method", to: "attack_potential" },
          { at: "2026-11-20 16:00", by: "@analyst-a", kind: "method_changed", from: "attack_potential", to: "cvss", vector_after: "CV:3.1/AV:L/AC:H/PR:L/UI:N" },
          { at: "2026-11-23 08:00", by: "tmodel import", kind: "changed", factor: "AC", from: "H", to: "L", text: "Re-import of the vendor advisory changed attack complexity." }
        ] },
      { id: "EX-07", title: "Concept phase: telematics modem reachable from the network", impact: "major",
        vector: "AX:2021/AV:N",
        history: [
          { at: "2026-11-20 09:00", by: "tmodel", kind: "default_method", to: "attack_potential" },
          { at: "2026-11-20 09:06", by: "AI hook", kind: "proposed", to: "AX:2021/AV:N", text: "Concept phase: no paths yet, so the attack-vector approach is proposed." }
        ] },
      { id: "EX-08", title: "Older path with a human label only", impact: "moderate", label: "medium", history: [] },
      { id: "EX-09", title: "Replay of unlock messages near the vehicle", impact: "major",
        vector: "AP:2021/ET:1M/SE:PRO/KN:RES/WO:MOD/EQ:SPE",
        history: [
          { at: "2026-11-20 09:00", by: "tmodel", kind: "default_method", to: "attack_potential" },
          { at: "2026-11-20 09:07", by: "AI hook", kind: "proposed", to: "AP:2021/ET:1M/SE:PRO/KN:RES/WO:MOD/EQ:SPE", ref: "proposal P-EX09" },
          { at: "2026-11-21 10:30", by: "@analyst-a", kind: "reviewed", vector_after: "AP:2021/ET:1M/SE:PRO/KN:RES/WO:MOD/EQ:SPE", ref: "accept A-EX09" },
          { at: "2026-11-22 08:05", by: "@reviewer-b", kind: "commented", factor: "KN", text: "Supplier sheet is under NDA; check it is not also on a forum." },
          { at: "2026-11-22 08:11", by: "@reviewer-b", kind: "disputed", factor: "WO", text: "Range is longer with an amplifier; may be easy rather than moderate. Open." }
        ] },
      { id: "EX-10", title: "Downgrade the gateway firmware", impact: "severe",
        vector: "AP:2021/ET:1M/SE:EXP/KN:CON/WO:MOD/EQ:SPE",
        override: { level: "medium", rationale: "Downgrade tooling has leaked; treat as more feasible than the factors show.",
          decided_by: "@reviewer-b", decided_at: "2026-11-21 17:00", vector_at_decision: "AP:2021/ET:1M/SE:EXP/KN:RES/WO:MOD/EQ:SPE" },
        history: [
          { at: "2026-11-20 09:00", by: "tmodel", kind: "default_method", to: "attack_potential" },
          { at: "2026-11-20 09:08", by: "AI hook", kind: "proposed", to: "AP:2021/ET:1M/SE:EXP/KN:RES/WO:MOD/EQ:SPE", ref: "proposal P-EX10" },
          { at: "2026-11-21 17:00", by: "@reviewer-b", kind: "override", from: "low", to: "medium", text: "Override with rationale (see record)." },
          { at: "2026-11-23 09:40", by: "@analyst-a", kind: "changed", factor: "KN", from: "RES", to: "CON", vector_after: "AP:2021/ET:1M/SE:EXP/KN:CON/WO:MOD/EQ:SPE",
            text: "Bootloader map is confidential, not just restricted." }
        ] }
    ]
  };
  if (typeof module === "object" && module.exports) module.exports = data;
  else root.FEASIBILITY_EXAMPLES = data;
})(typeof globalThis !== "undefined" ? globalThis : this);
