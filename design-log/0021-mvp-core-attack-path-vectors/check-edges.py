import sys, yaml, pathlib

# Reference (id-ref, inlined:false) slots in the CORE object model. Literal/enum/
# inlined-value slots (identifiers, catalog_ref, external_refs, predicate, risk,
# focus_query, *_status, confidence, feasibility, impact, code, party_kind,
# method_facet, source_method, violates_property, kill_chain_phase, priority,
# justification, review_status, valid_from/to, projection, name, description) are
# NOT references and are intentionally excluded.
REF_SLOTS = {
    "composed_of","manufactured_by","supplied_by","owned_by","of_product",
    "current_phase","depends_on","uses_component","affects","reported_by",
    "assigned_by","realizes_damage","applies_in_phase","precedes","steps",
    "realizes_threat","pivots_to","mitigates","implementation_owner","threat",
    "attack_paths","damage_scenario","for_stakeholder","reviews","reviewer",
    "subject","object",
    # Requirement in the core (ADR-0012, DL-0025)
    "refines","derived_from","conflicts_with","maps_to","addresses","satisfied_by",
    "applies_to","stated_as",
}
# DEC-001b slots a CORE vector must not set (ADR-0012 keeps them proposal-level).
GOVERNED_SLOTS = {"conformance_status"}

def check(path):
    doc = yaml.safe_load(pathlib.Path(path).read_text())
    declared = set()
    for coll, items in (doc or {}).items():
        if isinstance(items, list):
            for it in items:
                if isinstance(it, dict) and "id" in it:
                    declared.add(it["id"])
    refs = 0
    bad = []
    for coll, items in (doc or {}).items():
        if not isinstance(items, list):
            continue
        for it in items:
            if not isinstance(it, dict):
                continue
            oid = it.get("id","<no id>")
            for slot in GOVERNED_SLOTS & set(it):
                bad.append((oid, slot, "(DEC-001b slot; not allowed in a core vector)"))
            for slot, val in it.items():
                if slot not in REF_SLOTS:
                    continue
                vals = val if isinstance(val, list) else [val]
                for v in vals:
                    if v is None:
                        continue
                    refs += 1
                    if v not in declared:
                        bad.append((oid, slot, v))
    return len(declared), refs, bad

total_objs = total_refs = 0
all_ok = True
for path in sys.argv[1:]:
    d, r, bad = check(path)
    total_objs += d; total_refs += r
    status = "OK" if not bad else f"{len(bad)} UNRESOLVED"
    print(f"{pathlib.Path(path).name}: {d} objects, {r} id-references -> {status}")
    for oid, slot, v in bad:
        all_ok = False
        print(f"    UNRESOLVED  {oid}.{slot} -> {v}")
print(f"\nTOTAL: {total_objs} objects, {total_refs} id-references across {len(sys.argv)-1} vectors")
print("EDGE INTEGRITY: " + ("ALL REFERENCES RESOLVE" if all_ok else "FAILURES ABOVE"))
sys.exit(0 if all_ok else 1)
