#!/usr/bin/env python3
"""Convert a library requirements.yaml into a skeleton tmodel requirement file (#169).

    python3 research/0017-requirements-extraction/convert.py \
        <library>/records/<body>/<record-id> --owner <github-id> \
        [--only PREFIX,...] [--skip-file skips.yaml] [--normativity VALUE=TMODEL ...] \
        [--empty-text] [--library-commit SHA] [--date YYYY-MM-DD] [-o FILE] [--force]

It reads the record's `record.yaml` and `distilled/requirements.yaml`
(`library-requirements/v2`) and writes one Requirement per provision, in the
format in README.md. It copies what the library already extracted (designator,
locator, normativity) and never adds a link: the output has no Assertions.

- `normativity`: requirement and prohibition -> mandatory, recommendation ->
  recommended, permission -> optional, informative -> informative. Any other
  value is skipped with its reason unless `--normativity VALUE=TMODEL` maps it.
- `requirement_kind` is a default from the library's `nature` and `actor`,
  marked `# REVIEW:` for a human or agent to confirm.
- A licensed source (a record under `records/iso/`, or a publisher naming ISO,
  IEC or SAE) gets an EMPTY `text` and `text_origin: paraphrase`. Its wording is
  never copied, not even the library's short title.
- A free source gets the library's verbatim text with `text_origin: verbatim`,
  marked for a one-line paraphrase. `--empty-text` leaves it empty instead.

Stdlib and PyYAML only. The output is re-parsed before it is written.
"""
import argparse
import datetime
import pathlib
import re
import subprocess
import sys
import textwrap

import yaml

NORMATIVITY = {
    "requirement": "mandatory",
    "prohibition": "mandatory",
    "recommendation": "recommended",
    "permission": "optional",
    "informative": "informative",
}
TMODEL_NORMATIVITY = {"mandatory", "recommended", "optional", "informative", "conditional"}
KIND_FROM_NATURE = {
    "process": "process",
    "deliverable": "documentation",
    "deliverable-producing": "process",  # an activity that yields a work product
    "product": "technical",
    "property": "technical",
}
ORG_ACTOR = re.compile(r"^(the )?(organi[sz]ation|top management|management)\b", re.I)
LICENSED_PUBLISHER = re.compile(r"\b(ISO|IEC|SAE)\b")
INACTIVE = {"withdrawn", "retired", "rescinded"}
WIDTH = 88


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def designator(entry, record_id):
    if entry.get("designator"):
        return str(entry["designator"])
    rid = str(entry["id"])
    prefix = record_id + "#"
    return rid[len(prefix):] if rid.startswith(prefix) else rid


def actors(entry):
    a = entry.get("actor")
    vals = a if isinstance(a, list) else ([a] if a else [])
    return [re.sub(r"\s*\(implied\)\s*$", "", str(v)).strip() for v in vals]


def default_kind(entry):
    nature = entry.get("nature")
    kind = KIND_FROM_NATURE.get(nature, "other")
    acts = actors(entry)
    if kind == "process" and acts and all(ORG_ACTOR.match(v) for v in acts):
        kind = "organizational"
        why = f"nature {nature}, actor {', '.join(acts)}"
    else:
        why = f"nature {nature}" if nature else "no nature in the record"
    return kind, why


def locator(entry, des):
    loc = str(entry.get("locator") or "").strip()
    if not loc:
        return ""
    # The designator counts as present only as a whole token: "1" is not in "§1".
    return loc if des in re.split(r"[\s,;()]+", loc) else f"{des} ({loc})"


def is_licensed(record, record_dir):
    if record.get("body") == "iso" or record_dir.parent.name == "iso":
        return True
    return bool(LICENSED_PUBLISHER.search(str(record.get("publisher") or "")))


def q(s):
    """A double-quoted YAML scalar (JSON strings are valid YAML)."""
    import json
    return json.dumps(str(s), ensure_ascii=False)


def folded(key, text, indent):
    pad = " " * indent
    text = " ".join(str(text).split())
    lines = textwrap.wrap(text, WIDTH - indent - 2, break_long_words=False, break_on_hyphens=False)
    return [f"{pad}{key}: >-"] + [f"{pad}  {ln}" for ln in lines]


def git_commit(path):
    try:
        out = subprocess.run(["git", "-C", str(path), "rev-parse", "--short=7", "HEAD"],
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except Exception:
        return ""


def parse_kv(values, what):
    out = {}
    for v in values or []:
        if "=" not in v:
            sys.exit(f"convert.py: {what} must be VALUE=TMODEL, got {v!r}")
        k, t = v.split("=", 1)
        if t not in TMODEL_NORMATIVITY:
            sys.exit(f"convert.py: {t!r} is not a tmodel Normativity ({', '.join(sorted(TMODEL_NORMATIVITY))})")
        out[k] = t
    return out


def convert(record_dir, owner, only=(), skips=None, extra_normativity=None, empty_text=False,
            library_commit="", date=None):
    record_dir = pathlib.Path(record_dir)
    record = yaml.safe_load((record_dir / "record.yaml").read_text())
    reqs_doc = yaml.safe_load((record_dir / "distilled" / "requirements.yaml").read_text())
    record_id = record["id"]
    if reqs_doc.get("record") not in (None, record_id):
        sys.exit(f"convert.py: requirements.yaml names record {reqs_doc.get('record')!r}, not {record_id!r}")
    schema = reqs_doc.get("schema")
    if schema != "library-requirements/v2":
        print(f"convert.py: warning: {record_id} is {schema!r}, not library-requirements/v2", file=sys.stderr)
    digest = (record.get("content") or {}).get("sha256") or reqs_doc.get("source_digest") or ""
    if reqs_doc.get("source_digest") and digest and reqs_doc["source_digest"] != digest:
        print(f"convert.py: warning: record.yaml sha256 and requirements.yaml source_digest differ; "
              f"using record.yaml's", file=sys.stderr)
    licensed = is_licensed(record, record_dir)
    normativity = dict(NORMATIVITY, **(extra_normativity or {}))
    skips = skips or {}
    owner = owner.lstrip("@")
    date = date or datetime.date.today().isoformat()

    entries = reqs_doc.get("requirements") or []
    converted, skipped, seen = [], [], {}
    for e in entries:
        des = designator(e, record_id)
        if only and not any(des.startswith(p) for p in only):
            skipped.append((des, "outside --only"))
            continue
        if des in skips:
            skipped.append((des, str(skips[des])))
            continue
        if str(e.get("status") or "active") in INACTIVE:
            skipped.append((des, f"status {e['status']} in the library record"))
            continue
        lib_norm = str(e.get("normativity") or "")
        if lib_norm not in normativity:
            skipped.append((des, f"normativity {lib_norm or '(none)'} has no tmodel equivalent; "
                                 f"map it with --normativity {lib_norm or 'VALUE'}=..."))
            continue
        rid = f"requirement:{record_id}-{slug(des)}"
        if rid in seen:
            sys.exit(f"convert.py: {des!r} and {seen[rid]!r} both give id {rid}")
        seen[rid] = des
        converted.append((e, des, rid, normativity[lib_norm]))

    lines = [
        f"# {record_id}: requirement extraction, AI-proposed, UNREVIEWED unless a Review below says otherwise.",
        f"# Source: library:{record_id} (digest {digest}), read {date}.",
        f"# Agent: none yet (converter skeleton). Human owner: @{owner}.",
        "#",
        f"# Converted by research/0017-requirements-extraction/convert.py from "
        f"library{'@' + library_commit if library_commit else ''} {record_dir.parent.name}/{record_id}.",
        f"# Coverage: {len(entries)} in the source, {len(converted)} converted, {len(skipped)} skipped.",
    ]
    reasons = {}
    for des, why in skipped:
        reasons.setdefault(why, []).append(des)
    for why, ds in reasons.items():
        lines.append(f"#   skipped ({why}): {', '.join(ds)}")
    if licensed:
        lines.append("# Licensed source: every `text` is empty and must be a one-sentence paraphrase. "
                     "Never copy its wording.")
    lines.append("# `# REVIEW:` marks a value the converter defaulted. Confirm or change it, then drop the mark.")
    lines += ["", "requirements:"]

    for e, des, rid, norm in converted:
        lines.append(f"  - id: {rid}")
        title = None if licensed else (e.get("short_title") or e.get("title"))
        if title:
            lines.append(f"    name: {q(des + ' — ' + ' '.join(str(title).split()))}")
        else:
            lines.append(f"    name: {q(des)}  # REVIEW: add a short title in your own words")
        if licensed or empty_text:
            note = "licensed source; write a one-sentence paraphrase" if licensed else \
                "write a one-sentence paraphrase"
            lines.append(f'    text: ""  # REVIEW: {note}')
            lines.append("    text_origin: paraphrase")
        else:
            lines += folded("text", e.get("text") or "", 4)
            lines.append("    text_origin: verbatim  # REVIEW: verbatim from the library; "
                         "a one-line paraphrase is preferred")
        kind, why = default_kind(e)
        lines.append(f"    requirement_kind: {kind}  # REVIEW: default from {why}")
        cond = e.get("condition")
        mark = f"  # REVIEW: the source states a condition ({' '.join(str(cond).split())[:60]}); " \
               f"consider conditional" if cond else ""
        lines.append(f"    normativity: {norm}{mark}")
        lines.append(f"    source_ref: {q('library:' + record_id + '#' + des)}")
        lines.append(f"    source_locator: {q(locator(e, des))}")

    lines += [
        "",
        "# The human reviewer. Add stub nodes (weaknesses, attack_patterns, threat_instances,",
        "# mitigations) only for targets a proposed Assertion points at.",
        "parties:",
        f"  - id: party:{slug(owner)}",
        f"    name: {q('@' + owner)}",
        "    description: Human owner and reviewer of this file (GitHub id).",
        "    party_kind: person",
        "",
        "# Every proposed link is an Assertion (README.md). The converter proposes none.",
        "assertions: []",
        "",
        "reviews: []",
        "",
    ]
    out = "\n".join(lines)

    doc = yaml.safe_load(out)
    assert len(doc["requirements"]) == len(converted)
    for (e, des, rid, norm), r in zip(converted, doc["requirements"]):
        assert r["id"] == rid and r["normativity"] == norm
        if not (licensed or empty_text):
            assert r["text"] == " ".join(str(e.get("text") or "").split()), rid
        else:
            assert r["text"] == "", rid
    return out, len(entries), len(converted), skipped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("record_dir", help="library records/<body>/<record-id> directory")
    ap.add_argument("--owner", required=True, help="GitHub id of the human owner (no real names)")
    ap.add_argument("--only", default="", help="comma-separated designator prefixes to convert")
    ap.add_argument("--skip-file", help="YAML map {designator: reason} of provisions to skip")
    ap.add_argument("--normativity", action="append", metavar="VALUE=TMODEL",
                    help="map another library normativity value, e.g. principle=informative")
    ap.add_argument("--empty-text", action="store_true", help="leave `text` empty for a free source too")
    ap.add_argument("--library-commit", default="", help="library commit, if record_dir is not a git checkout")
    ap.add_argument("--date", help="read date for the header (default: today)")
    ap.add_argument("-o", "--output", help="output file (default: stdout)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing output file")
    a = ap.parse_args(argv)

    skips = yaml.safe_load(pathlib.Path(a.skip_file).read_text()) if a.skip_file else {}
    only = [p for p in a.only.split(",") if p]
    commit = a.library_commit or git_commit(a.record_dir)
    out, n, m, skipped = convert(a.record_dir, a.owner, only, skips,
                                 parse_kv(a.normativity, "--normativity"), a.empty_text, commit, a.date)
    if a.output:
        p = pathlib.Path(a.output)
        if p.exists() and not a.force:
            sys.exit(f"convert.py: {p} exists; it may hold reviewed work. Use --force to overwrite.")
        p.write_text(out)
    else:
        sys.stdout.write(out)
    print(f"convert.py: {n} in the source, {m} converted, {len(skipped)} skipped", file=sys.stderr)


if __name__ == "__main__":
    main()
