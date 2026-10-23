"""Schema-driven reference check for spec/vectors/*.yaml (DL-0024).

DL-0021's check-edges.py lists its reference slots by hand, so a new slot is never
checked. This reads them from the LinkML schema instead: a slot is a reference when
its range (or any of its any_of ranges) is a class and it is not inlined. Every such
value must be the id of an object declared in the same vector file.

  python3 design-log/0024-schema-proposal-g13/check-refs.py spec/vectors/*.yaml
"""
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
schema = yaml.safe_load((ROOT / "spec/schema/tmodel-object-model.linkml.yaml").read_text())
classes = set(schema.get("classes") or {})


def ranges(defn):
    out = {defn.get("range")}
    for alt in defn.get("any_of") or []:
        out.add(alt.get("range"))
    return {r for r in out if r}


# A slot inlined as a nested object (for example RiskScore.impact) holds a value, not an id.
REF_SLOTS = {
    name for name, d in (schema.get("slots") or {}).items()
    if ranges(d or {}) & classes and not (d or {}).get("inlined")
}

total_objs = total_refs = 0
ok = True
for path in sys.argv[1:]:
    doc = yaml.safe_load(pathlib.Path(path).read_text()) or {}
    items = [it for v in doc.values() if isinstance(v, list) for it in v if isinstance(it, dict)]
    declared = {it["id"] for it in items if "id" in it}
    refs, bad = 0, []
    for it in items:
        for slot, val in it.items():
            if slot not in REF_SLOTS:
                continue
            for v in val if isinstance(val, list) else [val]:
                if v is None or isinstance(v, dict):
                    continue
                refs += 1
                if v not in declared:
                    bad.append((it.get("id", "<no id>"), slot, v))
    total_objs += len(declared)
    total_refs += refs
    print(f"{pathlib.Path(path).name}: {len(declared)} objects, {refs} references -> {'OK' if not bad else f'{len(bad)} UNRESOLVED'}")
    for oid, slot, v in bad:
        ok = False
        print(f"    UNRESOLVED  {oid}.{slot} -> {v}")
print(f"\n{len(REF_SLOTS)} reference slots read from the schema")
print(f"TOTAL: {total_objs} objects, {total_refs} references across {len(sys.argv) - 1} vectors")
print("REFERENCES: " + ("ALL RESOLVE" if ok else "FAILURES ABOVE"))
sys.exit(0 if ok else 1)
