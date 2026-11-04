#!/usr/bin/env python3
"""Check requirement extraction files against the rules in README.md (#169).

    python3 research/0017-requirements-extraction/check.py research/0017-requirements-extraction/*.yaml

linkml-validate checks the shape and check-edges.py checks that references
resolve. This checks what neither can:

1. Every Requirement has source_ref, source_locator, text_origin,
   requirement_kind and normativity; its id and source_ref name this file's record.
2. A licensed source (record id starting iso- or iec-) is never `verbatim`.
3. No link slot is filled directly: addresses, satisfied_by, refines,
   derived_from, conflicts_with, maps_to and Mitigation.stated_as stay empty.
4. Every Assertion is `proposed` or `accepted`, has a description that gives its
   basis, and uses a predicate this pass allows. refines, derived_from and
   conflicts_with stay within the file's own source.
5. An `accepted` Assertion has an accepting Review, and a `proposed` one has
   none. Every Review is `accepted` or `rejected`, has a justification, and its
   reviewer is a person.

Empty `text` and `# REVIEW:` marks are reported as notes, not errors: a skeleton
from convert.py is valid until someone fills it in.
"""
import pathlib
import re
import sys

import yaml

REQUIRED = ["source_ref", "source_locator", "text_origin", "requirement_kind", "normativity"]
LINK_SLOTS = ["addresses", "satisfied_by", "refines", "derived_from", "conflicts_with", "maps_to"]
PREDICATES = {"addresses", "stated_as", "satisfied_by", "refines", "derived_from", "conflicts_with"}
WITHIN_SOURCE = {"refines", "derived_from", "conflicts_with"}
LICENSED = re.compile(r"^(iso|iec)-")


def check(path):
    path = pathlib.Path(path)
    raw = path.read_text()
    doc = yaml.safe_load(raw) or {}
    record = path.stem
    errs, notes = [], []
    reqs = doc.get("requirements") or []
    req_ids = {r.get("id") for r in reqs}
    if not reqs:
        errs.append("no requirements")

    for r in reqs:
        rid = r.get("id", "<no id>")
        for k in REQUIRED:
            if not r.get(k):
                errs.append(f"{rid}: no {k}")
        if not str(rid).startswith(f"requirement:{record}-"):
            errs.append(f"{rid}: id does not start with requirement:{record}-")
        if r.get("source_ref") and not str(r["source_ref"]).startswith(f"library:{record}#"):
            errs.append(f"{rid}: source_ref {r['source_ref']} is not library:{record}#...")
        if LICENSED.match(record) and r.get("text_origin") == "verbatim":
            errs.append(f"{rid}: licensed source, but text_origin is verbatim")
        if not str(r.get("text") or "").strip():
            notes.append(rid)
        for k in LINK_SLOTS:
            if r.get(k):
                errs.append(f"{rid}: {k} is filled; propose it as an Assertion instead")
    for m in doc.get("mitigations") or []:
        if m.get("stated_as"):
            errs.append(f"{m.get('id')}: stated_as is filled; propose it as an Assertion instead")

    persons = {p.get("id") for p in doc.get("parties") or [] if p.get("party_kind") == "person"}
    reviews = {}
    for v in doc.get("reviews") or []:
        vid = v.get("id", "<no id>")
        if v.get("review_status") not in ("accepted", "rejected"):
            errs.append(f"{vid}: review_status {v.get('review_status')!r} is not accepted or rejected")
        if not str(v.get("justification") or "").strip():
            errs.append(f"{vid}: no justification")
        if v.get("reviewer") not in persons:
            errs.append(f"{vid}: reviewer {v.get('reviewer')!r} is not a person in parties")
        reviews.setdefault(v.get("reviews"), []).append(v.get("review_status"))

    for a in doc.get("assertions") or []:
        aid = a.get("id", "<no id>")
        status, pred = a.get("assertion_status"), a.get("predicate")
        if status not in ("proposed", "accepted"):
            errs.append(f"{aid}: assertion_status {status!r} is not proposed or accepted")
        if "Basis:" not in str(a.get("description") or ""):
            errs.append(f"{aid}: description gives no 'Basis:'")
        if pred == "maps_to":
            errs.append(f"{aid}: maps_to between sources is out of scope here (MAP-0001)")
        elif pred not in PREDICATES:
            errs.append(f"{aid}: predicate {pred!r} is not one of {', '.join(sorted(PREDICATES))}")
        if pred in WITHIN_SOURCE and a.get("object") not in req_ids:
            errs.append(f"{aid}: {pred} must point at a requirement in this file")
        verdicts = reviews.get(aid, [])
        if status == "accepted" and "accepted" not in verdicts:
            errs.append(f"{aid}: accepted without an accepting Review")
        if status == "proposed" and "accepted" in verdicts:
            errs.append(f"{aid}: an accepting Review exists, so assertion_status should be accepted")

    marks = raw.count("# REVIEW:")
    return len(reqs), errs, notes, marks


def main(paths):
    ok = True
    for p in paths:
        n, errs, empty, marks = check(p)
        status = "OK" if not errs else f"{len(errs)} ERRORS"
        extra = []
        if empty:
            extra.append(f"{len(empty)} empty text")
        if marks:
            extra.append(f"{marks} # REVIEW: marks")
        print(f"{pathlib.Path(p).name}: {n} requirements -> {status}"
              + (f" (notes: {', '.join(extra)})" if extra else ""))
        for e in errs:
            ok = False
            print(f"    {e}")
    print("EXTRACTION RULES: " + ("ALL PASS" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
