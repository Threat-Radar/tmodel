"""`tmodel` command line — the agentic surface over the same engine the GUI uses.

  tmodel serve [--projects]    start the local engine (loopback only); --projects also
                               serves the project folders the host opens (#288)
  tmodel health [--json]       ask the running engine whether it is healthy
  tmodel version [--json]      ask the running engine for its version
  tmodel risk FILE --matrix annex-h-table-h8 [--goal G] [--json]
                               derive risk from recorded path ratings (#63)
  tmodel models [--json]       the example models the app can open
  tmodel tara FILE --matrix annex-h-table-h8 [--output FILE]
                               collect a repeatable JSON TARA intermediate (#181)
  tmodel paths FILE [--goal G] [--json]
                               attack paths to a step or threat in a model file;
                               without --goal, list the file's threats
  tmodel coverage FILE --product ID [--json]  recorded requirement coverage (#170)
  tmodel library [--id I] [--type T] [--topic T] [--status S] [--json]
                               the library's records, optionally filtered; the
                               library is $TMODEL_LIBRARY or the pinned submodule
  tmodel weaknesses [--search S] [--abstraction A] [--structure S] [--status S]
                [--usage U] [--sort F] [--order asc|desc] [--limit N] [--offset N] [--json]
  tmodel weaknesses --id CWE-79 [--json]
                               CWE weaknesses from the release the library pins,
                               read from $TMODEL_CWE_CATALOG (#144), and the local
                               tr-weak ones in $TMODEL_LOCAL_WEAKNESSES (#145); with
                               --id, one entry in full (CWE-79 or tr-weak-0001)
  tmodel weaknesses --relationships [--id CWE-79] [--view CWE-1000,699] [--stated-only]
                [--limit N] [--offset N] [--json]
                               their relationships, each in its CWE view, with the
                               inverses the schema declares unless --stated-only (#145)
  tmodel attack-patterns [--search S] [--abstraction A] [--status S]
                [--likelihood L] [--severity S] [--sort F] [--order asc|desc]
                [--limit N] [--offset N] [--json]
  tmodel attack-patterns --id CAPEC-66 [--json]
                               CAPEC attack patterns from the release the library
                               pins, read from $TMODEL_CAPEC_CATALOG (#244); with
                               --id, one entry in full
  tmodel sdl [FILE] [--program P] [--json]
                               the SDL program view of an SDL model (DL-0043);
                               without FILE, list the SDL models
  tmodel propose PATCH [--dry-run] [--json]
                               check an agent's patch to a threat model, SDL model
                               or saved KG views and append it to the model's
                               proposals file; never accepts (DL-0044, DL-0046)
  tmodel proposals [FILE] [--json]
                               pending proposals and saved KG views of a model;
                               without FILE, pending counts per model (DL-0046)
  tmodel accept PROPOSAL --model FILE --reviewer PARTY --justification TEXT
                [--verdict accepted|rejected|changes_requested] [--declare-sponsor GH]
                               the sponsor decides one proposal, in a branch; always
                               in-process, never through the API (DL-0046)
  tmodel import-sbom SBOM [--scan SCAN] [--platform OS/ARCH[/VARIANT]] -o MODEL
                [--report FILE] [--force]
                               write a starter model from Syft's CycloneDX SBOM of a
                               container image and Grype's JSON scan of it; every
                               claim proposed (#257, DL-0068); always in-process.
                               --platform names the build (linux/arm64/v8) unless
                               the scan records it

By default these go through the local API, exactly like the desktop app
(APP-0001 A-030, A-060). `--in-process` calls the engine code directly
instead, for scripts that do not want a server.

Exit codes: 0 ok · 1 engine unreachable, unhealthy, an engine error, or incomplete
risk inputs; for `import-sbom`, a file it could not write (the error and what it left
are printed) · 2 usage error, or an input `import-sbom` refuses. `import-sbom` exits 0
with its warnings printed, such as an SBOM most of whose packages are another
platform's, or a backup it could not remove once both outputs were written.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from engine import core
from engine.api import server
from engine.client import EngineError, EngineTimeout, EngineUnreachable, get
from engine.load import local_weaknesses
from engine.tara import serialize as serialize_tara

LOCAL: dict[str, Callable[[], dict[str, Any]]] = {"health": core.health, "version": core.version}


def _print(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload))
        return
    if "status" in payload:
        print(f"{payload['status']} · {payload['engine']} v{payload['version']}")
    else:
        print(f"{payload['engine']} v{payload['version']} (python {payload['python']})")


PATHS_TIMEOUT_S = 60.0  # enumeration can take longer than /health


def _call(fetch: Callable[[], dict[str, Any]]) -> dict[str, Any] | None:
    """Run a request; on failure print one error line (no traceback) and return None."""
    try:
        return fetch()
    except EngineTimeout as exc:
        print(f"error: {exc}; it may still be working (try --in-process)", file=sys.stderr)
    except EngineUnreachable as exc:
        print(f"error: {exc}\nstart it with: tmodel serve", file=sys.stderr)
    except (EngineError, ValueError, core.Unavailable) as exc:  # ValueError covers GraphError
        print(f"error: {exc}", file=sys.stderr)
    return None


def _query(args: argparse.Namespace) -> int:
    payload = _call(
        lambda: LOCAL[args.command]() if args.in_process else get(f"/{args.command}", args.url)
    )
    if payload is None:
        return 1
    _print(payload, args.json)
    return 0 if payload.get("status", "ok") == "ok" else 1


def _short(step_id: str) -> str:
    return step_id.split(":", 1)[-1]


def _review_note(review: dict[str, Any]) -> str:
    """Empty for a reviewed path; otherwise says why it is not (R-018)."""
    if review.get("reviewed"):
        return ""
    recorded = review.get("review_status") or review.get("assertion_status")
    return f"  [not reviewed: {recorded}]" if recorded else "  [not reviewed]"


def _print_paths(payload: dict[str, Any]) -> None:
    if "goal" not in payload:
        reviewed = set(payload.get("reviewed_threats", []))
        print(f"{payload['file']}: {payload['steps']} steps; threats:")
        for threat in payload["threats"]:
            print(f"  {threat}" + ("" if threat in reviewed else "  [not reviewed]"))
        if payload.get("assets"):
            print("assets:")
            for asset in payload["assets"]:
                print(f"  {asset}")
        return
    paths = payload["paths"]
    print(f"{payload['goal']}: {len(paths)} path{'s' if len(paths) != 1 else ''}")
    for i, path in enumerate(paths, 1):
        steps = " -> ".join(_short(s) for s in path["steps"])
        threat = f" [{path['threat']}]" if path.get("threat") else ""
        print(f"  {i}.{threat} {steps}{_review_note(path.get('review', {}))}")


def _paths(args: argparse.Namespace) -> int:
    # absolute, without following symlinks: the server may run from another directory
    file = os.path.abspath(args.file)
    params = {"file": file, **({"goal": args.goal} if args.goal is not None else {})}
    payload = _call(
        lambda: (
            core.attack_paths(file, args.goal)
            if args.in_process
            else get("/attack-paths", args.url, timeout=PATHS_TIMEOUT_S, params=params)
        )
    )
    if payload is None:
        return 1
    if args.json:
        print(json.dumps(payload))
    else:
        _print_paths(payload)
    return 0


def _print_models(payload: dict[str, Any]) -> None:
    models = payload["models"]
    print(f"{payload['count']} example model{'s' if payload['count'] != 1 else ''}")
    width = max((len(m["file"]) for m in models), default=0)
    for m in models:
        threats = m["counts"]["threats"]
        noun = "threat" if threats == 1 else "threats"
        print(
            f"  {m['file']:<{width}}  {m['title']}"
            f"  ({m['kind_label']}; {threats} {noun}, {m['reviewed_threats']} reviewed)"
        )
    for problem in payload["problems"]:
        print(f"  {problem['file']}: not loaded ({problem['error']})")


def _models(args: argparse.Namespace) -> int:
    payload = _call(lambda: core.list_models() if args.in_process else get("/models", args.url))
    if payload is None:
        return 1
    if args.json:
        print(json.dumps(payload))
    else:
        _print_models(payload)
    return 0


LIBRARY_TIMEOUT_S = 60.0  # the engine's first request loads every record


def _tara(args: argparse.Namespace) -> int:
    file = os.path.abspath(args.file) if os.path.dirname(args.file) else args.file
    payload = _call(
        lambda: (
            core.collect_tara(file, args.matrix)
            if args.in_process
            else get(
                "/tara",
                args.url,
                timeout=PATHS_TIMEOUT_S,
                params={"file": file, "matrix": args.matrix},
            )
        )
    )
    if payload is None:
        return 1
    try:
        text = serialize_tara(payload)
        if args.output is None:
            print(text, end="")
        else:
            output = Path(args.output)
            # Prevent overwriting an input model, including an alias/symlink.
            if output.suffix.lower() != ".json":
                raise ValueError("tara: --output must name a .json file")
            if output.resolve() == Path(file).resolve():
                raise ValueError("tara: output must not replace the input model")
            # Keep staging private while creating the file with normal umask
            # permissions for a subsequent renderer. The rename stays atomic.
            with tempfile.TemporaryDirectory(prefix=".tmodel-tara-", dir=output.parent) as staging:
                temporary = Path(staging) / output.name
                with temporary.open("x", encoding="utf-8", newline="\n") as stream:
                    stream.write(text)
                os.replace(temporary, output)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    # Incomplete/unreviewed assessment inputs belong in a successful draft export.
    return 0


def _risk(args: argparse.Namespace) -> int:
    # Basenames are convenient for bundled examples; paths are relative to the caller.
    file = os.path.abspath(args.file) if os.path.dirname(args.file) else args.file
    params = {"file": file, "matrix": args.matrix}
    if args.goal is not None:
        params["goal"] = args.goal
    payload = _call(
        lambda: (
            core.risk_assessments(file, args.matrix, args.goal)
            if args.in_process
            else get("/risk", args.url, timeout=PATHS_TIMEOUT_S, params=params)
        )
    )
    if payload is None:
        return 1
    if args.json:
        print(json.dumps(payload))
    else:
        print(f"{payload['file']} · matrix {payload['matrix']}")
        for assessment in payload["assessments"]:
            state = "complete" if assessment["complete"] else "incomplete"
            print(f"  {assessment['threat']} [{state}]")
            print(f"    feasibility: {assessment['feasibility'] or 'not assessed'}")
            for category, value in assessment["derived_risk"].items():
                impact = assessment["impact"][category] or "not rated"
                print(f"    {category}: impact {impact}; risk {value if value else 'not assessed'}")
            print(f"    mitigation status: {assessment['mitigation_status'] or 'not recorded'}")
            for index, route in enumerate(assessment["routes"], 1):
                sources = ", ".join(route["rating_paths"]) or "no matching rating"
                rating = route["feasibility"] or "not assessed"
                vector = ", ".join(
                    f"{category}={value if value is not None else 'not assessed'}"
                    for category, value in route["derived_risk"].items()
                )
                print(f"    route {index} ({sources}): feasibility {rating}; {vector}")
            for problem in assessment["problems"]:
                print(f"    needs input: {problem}")
    # JSON is still emitted for incomplete data, while scripts can detect it.
    return 0 if all(item["complete"] for item in payload["assessments"]) else 1


def _print_library(payload: dict[str, Any]) -> None:
    records, library = payload["records"], payload["library"]
    print(f"{payload['count']} of {library['count']} records in {library['root']}")
    columns = ("id", "type", "status")
    width = {c: max((len(r[c]) for r in records), default=0) for c in columns}
    for r in records:
        cells = "  ".join(f"{r[c]:<{width[c]}}" for c in columns)
        print(f"  {cells}  {r['title']}")


def _library(args: argparse.Namespace) -> int:
    filters = {name: getattr(args, name) for name in core.LIBRARY_FILTERS}
    filters = {name: value for name, value in filters.items() if value is not None}
    payload = _call(
        lambda: (
            core.library_records(filters)
            if args.in_process
            else get("/library", args.url, timeout=LIBRARY_TIMEOUT_S, params=filters)
        )
    )
    if payload is None:
        return 1
    if args.json:
        print(json.dumps(payload))
    else:
        _print_library(payload)
    problems = payload["library"]["problems"]
    if problems:  # the records that loaded are printed; say what is missing
        noun = "record" if len(problems) == 1 else "records"
        print(
            f"warning: {len(problems)} library {noun} failed to load; --json lists them",
            file=sys.stderr,
        )
        return 1
    return 0


def _print_weakness_table(payload: dict[str, Any]) -> None:
    catalog = payload["catalog"]
    print(
        f"{payload['count']} of {payload['total']} matching weaknesses "
        f"({catalog['name']} {catalog['version']}, {catalog['date']}: "
        f"{catalog['weaknesses']} weaknesses)"
    )
    columns = ("id", "abstraction", "status", "usage")
    rows = payload["rows"]
    width = {c: max((len(r[c] or "") for r in rows), default=0) for c in columns}
    for r in rows:
        cells = "  ".join(f"{r[c] or '':<{width[c]}}" for c in columns)
        print(f"  {cells}  {r['name']}")


def _relationship_line(r: dict[str, Any]) -> str:
    """One relationship: CWE-79 ChildOf CWE-74 (CWE-1000, Primary)."""
    notes = [r["view"], *(n for n in (r["ordinal"], r["chain"] and f"chain {r['chain']}") if n)]
    if r["derived"]:
        notes.append("derived")
    return f"{r['source']} {r['nature']} {r['target']} ({', '.join(notes)})"


def _print_relationships(payload: dict[str, Any]) -> None:
    catalog, local, query = payload["catalog"], payload["local"], payload["query"]
    views = ", ".join(query["views"]) if query["views"] else "every view"
    sources = f"{catalog['name']} {catalog['version']}"
    if local is not None:
        sources += f" and {local['name']} {local['version']}"
    print(f"{payload['count']} of {payload['total']} relationships in {views} ({sources})")
    for r in payload["relationships"]:
        print(f"  {_relationship_line(r)}")


def _print_weakness(payload: dict[str, Any]) -> None:
    catalog, entry = payload["catalog"], payload["entry"]
    if entry is None:
        where = f"{catalog['name']} {catalog['version']}"
        if local_weaknesses.local_number(payload["id"]) is not None:
            local = payload["local"]
            where = (
                f"{local['name']} {local['version']}"
                if local is not None
                else f"any local file ({local_weaknesses.LOCAL_ENV} is not set)"
            )
        print(f"{payload['id']}: not in {where}")
        return
    print(f"{entry['id']}  {entry['name']}")
    shape = "/".join(v for v in (entry["abstraction"], entry["structure"]) if v)
    print(
        f"  {entry['kind']}{f' ({shape})' if shape else ''}; status {entry['status']}; "
        f"usage {entry['usage'] or 'none'}"
    )
    if entry["kind"] == "Weakness":
        print(
            f"  {len(entry['attack_patterns'])} CAPEC links, "
            f"{len(entry['observed_examples'])} observed examples, "
            f"{entry['mitigations']} mitigations"
        )
    if entry["url"]:
        print(f"  {entry['url']}")
    for r in (*entry["relationships"], *payload["derived_relationships"]):
        print(f"  {_relationship_line(r)}")


def _weaknesses(args: argparse.Namespace) -> int:
    names = core.WEAKNESS_FILTERS + core.TABLE_OPTIONS
    table = {n: getattr(args, n) for n in names if getattr(args, n) is not None}
    if args.relationships:
        refused = [n for n in table if n not in ("limit", "offset")]
        if refused:  # they would be ignored, so refuse them, as the API does
            given = ", ".join(f"--{n}" for n in refused)
            print(
                f"error: --relationships takes --id, --view, --stated-only, --limit and "
                f"--offset, not the table's options ({given})",
                file=sys.stderr,
            )
            return 2
        params = dict(table)
        if args.id is not None:
            params["id"] = args.id
        if args.view is not None:
            params["view"] = args.view
        if args.stated_only:
            params["derived"] = "false"
        return _show_weaknesses(
            args,
            "/weaknesses/relationships",
            params,
            core.weakness_relationships,
            _print_relationships,
        )
    if args.view is not None or args.stated_only:
        print("error: --view and --stated-only go with --relationships", file=sys.stderr)
        return 2
    if args.id is not None:
        if table:  # they would be ignored, so refuse them, as GET /weaknesses does
            given = ", ".join(f"--{n}" for n in table)
            print(
                f"error: --id shows one entry and takes no table options ({given})",
                file=sys.stderr,
            )
            return 2
        return _show_weaknesses(
            args, "/weaknesses", {"id": args.id}, core.weaknesses, _print_weakness
        )
    return _show_weaknesses(
        args, "/weaknesses/table", table, core.weakness_table, _print_weakness_table
    )


def _show_weaknesses(
    args: argparse.Namespace,
    path: str,
    params: dict[str, str],
    local: Callable[[dict[str, str]], dict[str, Any]],
    show: Callable[[dict[str, Any]], None],
) -> int:
    """Ask the engine (or, with --in-process, its code) and print its answer."""
    payload = _call(
        lambda: (
            local(params)
            if args.in_process
            else get(path, args.url, timeout=LIBRARY_TIMEOUT_S, params=params)
        )
    )
    if payload is None:
        return 1
    if args.json:
        print(json.dumps(payload))
    else:
        show(payload)
    unknown = payload["catalog"]["unknown_fields"]
    if unknown:  # kept, not dropped; say so, since the import does not map them yet
        noun = "field" if unknown == 1 else "fields"
        print(
            f"warning: the catalog has {unknown} entry {noun} this reader does not know; "
            "they are kept, and GET /weaknesses lists them",
            file=sys.stderr,
        )
    return 0


def _print_attack_pattern_table(payload: dict[str, Any]) -> None:
    catalog = payload["catalog"]
    print(
        f"{payload['count']} of {payload['total']} matching attack patterns "
        f"({catalog['name']} {catalog['version']}, {catalog['date']}: "
        f"{catalog['attack_patterns']} attack patterns)"
    )
    columns = ("id", "abstraction", "status", "severity")
    rows = payload["rows"]
    width = {c: max((len(r[c] or "") for r in rows), default=0) for c in columns}
    for r in rows:
        cells = "  ".join(f"{r[c] or '':<{width[c]}}" for c in columns)
        print(f"  {cells}  {r['name']}")


def _print_attack_pattern(payload: dict[str, Any]) -> None:
    catalog, entry = payload["catalog"], payload["entry"]
    if entry is None:
        print(f"{payload['id']}: not in {catalog['name']} {catalog['version']}")
        return
    print(f"{entry['id']}  {entry['name']}")
    shape = entry["abstraction"] or entry["view_type"]
    rated = "; ".join(
        f"{label} {entry[key]}"
        for label, key in (("likelihood", "likelihood"), ("severity", "severity"))
        if entry[key]
    )
    print(
        f"  {entry['kind'].replace('_', ' ')}{f' ({shape})' if shape else ''}; "
        f"status {entry['status']}{f'; {rated}' if rated else ''}"
    )
    if entry["kind"] == "Attack_Pattern":
        counts = (
            (len(entry["weaknesses"]), "CWE link"),
            (len(entry["attack_techniques"]), "ATT&CK technique"),
            (entry["steps"], "attack step"),
            (entry["mitigations"], "mitigation"),
        )
        print("  " + ", ".join(f"{n} {noun}{'' if n == 1 else 's'}" for n, noun in counts))
    print(f"  {entry['url']}")


def _attack_patterns(args: argparse.Namespace) -> int:
    names = core.ATTACK_PATTERN_FILTERS + core.TABLE_OPTIONS
    table = {n: getattr(args, n) for n in names if getattr(args, n) is not None}
    if args.id is not None:
        if table:  # they would be ignored, so refuse them, as GET /attack-patterns does
            given = ", ".join(f"--{n}" for n in table)
            print(
                f"error: --id shows one entry and takes no table options ({given})",
                file=sys.stderr,
            )
            return 2
        path, params, local = "/attack-patterns", {"id": args.id}, core.attack_patterns
    else:
        path, params, local = "/attack-patterns/table", table, core.attack_pattern_table
    payload = _call(
        lambda: (
            local(params)
            if args.in_process
            else get(path, args.url, timeout=LIBRARY_TIMEOUT_S, params=params)
        )
    )
    if payload is None:
        return 1
    if args.json:
        print(json.dumps(payload))
    elif args.id is not None:
        _print_attack_pattern(payload)
    else:
        _print_attack_pattern_table(payload)
    unknown = payload["catalog"]["unknown_fields"]
    if unknown:  # kept, not dropped; say so, since the import does not map them yet
        noun = "field" if unknown == 1 else "fields"
        print(
            f"warning: the catalog has {unknown} entry {noun} this reader does not know; "
            "they are kept, and GET /attack-patterns lists them",
            file=sys.stderr,
        )
    return 0


def _print_sdl(payload: dict[str, Any]) -> None:
    if "models" in payload:
        for m in payload["models"]:
            progs = ", ".join(p["id"] for p in m.get("programs", [])) or m.get("error", "")
            print(f"  {m['file']}  {progs}")
        return
    print(f"{payload['file']}: {payload['program']['name']} ({payload['proposal']})")
    for phase in payload["phases"]:
        print(f"  {phase['name']}")
        for it in phase["items"]:
            print(f"    [{it['status']}] {it['name']}  ({it['decision']['state']})")
    print(f"  {len(payload['awaiting_review'])} selections awaiting human review (PROC-0002)")


def _sdl(args: argparse.Namespace) -> int:
    params = {k: v for k, v in (("file", args.file), ("program", args.program)) if v}
    payload = _call(
        lambda: core.sdl(params) if args.in_process else get("/sdl", args.url, params=params)
    )
    if payload is None:
        return 1
    if args.json:
        print(json.dumps(payload))
    else:
        _print_sdl(payload)
    return 0


def _propose(args: argparse.Namespace) -> int:
    import yaml  # the engine's one dependency

    try:
        text = sys.stdin.read() if args.patch == "-" else open(args.patch, encoding="utf-8").read()
        patch = yaml.safe_load(text)
    except (OSError, yaml.YAMLError) as exc:
        print(f"error: cannot read the patch: {exc}", file=sys.stderr)
        return 2
    payload = _call(lambda: core.propose(patch, write=not args.dry_run))
    if payload is None:
        return 1
    if args.json:
        print(json.dumps(payload))
        return 0
    rec = payload["proposal"]
    where = payload["file"] or "(dry run, nothing written)"
    print(f"{rec['id']}: proposed by {rec['proposed_by']} -> {where}")
    print("  status: proposed. A human decides it in a PR (PROC-0002).")
    return 0


def _add_transport(cmd: argparse.ArgumentParser) -> None:
    cmd.add_argument("--json", action="store_true", help="print JSON")
    cmd.add_argument("--url", default=None, help="engine URL (default http://127.0.0.1:47811)")
    cmd.add_argument(
        "--in-process", action="store_true", help="call the engine directly, no server"
    )


def _proposals(args: argparse.Namespace) -> int:
    params = {"file": args.file} if args.file else {}
    payload = _call(
        lambda: (
            core.pending_proposals(params)
            if args.in_process
            else get("/proposals", args.url, params=params)
        )
    )
    if payload is None:
        return 1
    if args.json:
        print(json.dumps(payload))
        return 0
    if "models" in payload:
        for m in payload["models"]:
            print(f"  {m['file']}  {m.get('pending', m.get('error'))} pending")
        return 0
    for p in payload["proposals"]:
        n = len(p["objects"]) + len(p["changes"]) + len(p["assertions"])
        print(f"  {p['id']}  by {p['by']}  {n} changes  ({p['state']})")
    for v in payload["views"]:
        print(f"  view {v['id']}  [{v['state']}]  {len(v['node_ids'])} objects")
    return 0


def _accept(args: argparse.Namespace) -> int:
    from engine import accept  # a human's command: never reachable from the API

    try:
        model = core._model_path(args.model)
        xwalk = core.load_vector_document(core.CROSSWALK_FILE)
        out = accept.decide(
            model,
            args.proposal,
            verdict=args.verdict,
            reviewer=args.reviewer,
            justification=args.justification,
            xwalk=xwalk,
            declare_sponsor=args.declare_sponsor,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(out))
        return 0
    changed = "model updated" if out["model_changed"] else "model unchanged"
    print(f"{out['proposal']}: {out['verdict']} by {out['decided_by']} ({changed})")
    print("  Commit the model, proposals and decision log, and open a pull request.")
    return 0


def _import_sbom(args: argparse.Namespace) -> int:
    from engine import import_sbom  # a file-to-file step: never reachable from the API

    try:
        result = import_sbom.run(
            args.sbom,
            scan=args.scan,
            output=args.output,
            report=args.report,
            force=args.force,
            platform=args.platform,
        )
    except import_sbom.SbomImportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        _print_notes(exc)
        return 2
    except OSError as exc:
        print(f"error: cannot write ({exc.strerror or exc})", file=sys.stderr)
        _print_notes(exc)
        return 1
    if args.report is None:
        print(result.report_text, end="")
    else:
        print(f"wrote {args.output} and the import report {args.report}")
    # What the import wrote but the user should know (import_sbom.ImportResult.warnings),
    # such as an SBOM most of whose packages are another platform's: the import stands.
    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return 0


def _print_notes(exc: BaseException) -> None:
    # What a failed import kept, such as the file --force was replacing (import_sbom).
    for note in getattr(exc, "__notes__", ()):
        print(f"  {note}", file=sys.stderr)


def _coverage(args: argparse.Namespace) -> int:
    file = os.path.abspath(args.file) if os.path.dirname(args.file) else args.file
    params = {"file": file, "product": args.product}
    payload = _call(
        lambda: (
            core.requirement_coverage(params)
            if args.in_process
            else get("/coverage", args.url, params=params)
        )
    )
    if payload is None:
        return 1
    if args.json:
        print(json.dumps(payload))
    else:
        print(f"{payload['product']}: {payload['count']} requirements")
        for row in payload["requirements"]:
            print(f"  [{row['status']}] {row['id']}")
        print(f"  {len(payload['unaddressed_threats'])} unaddressed threats")
        print(f"  {len(payload['proposed_assertions'])} proposed links (not counted)")
        print(payload["interpretation"])
    return 0


def _serve(args: argparse.Namespace) -> int:
    host_token = None
    if args.projects:  # the host's secret comes from the environment, never argv (#288)
        host_token = os.environ.get("TMODEL_HOST_TOKEN")
        if not host_token:
            print(
                "error: --projects needs TMODEL_HOST_TOKEN, a secret of at least 32 "
                "characters, such as one from secrets.token_urlsafe(32)",
                file=sys.stderr,
            )
            return 1
    try:
        server.serve(port=args.port, exit_with_parent=args.exit_with_parent, host_token=host_token)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tmodel", description="tmodel engine command line")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="start the local engine (127.0.0.1 only)")
    serve.add_argument("--port", type=int, default=None, help="port (default 47811; 0 = any)")
    serve.add_argument(
        "--exit-with-parent",
        action="store_true",
        help="stop when stdin closes (the desktop app starts the engine this way)",
    )
    serve.add_argument(
        "--projects",
        action="store_true",
        help="let the host open and create threat model project folders (#288); the "
        "host's secret is read from TMODEL_HOST_TOKEN; off by default",
    )
    serve.set_defaults(func=_serve)

    for name, text in (("health", "engine health"), ("version", "engine version")):
        cmd = sub.add_parser(name, help=text)
        _add_transport(cmd)
        cmd.set_defaults(func=_query)

    models = sub.add_parser("models", help="the example models the app can open (#208)")
    _add_transport(models)
    models.set_defaults(func=_models)

    paths = sub.add_parser("paths", help="attack paths in a model file (#63)")
    paths.add_argument(
        "file", help="model file, e.g. spec/vectors/mvp-01-software-doc-service.yaml"
    )
    paths.add_argument("--goal", default=None, help="asset, step or threat id; omit to list goals")
    _add_transport(paths)
    paths.set_defaults(func=_paths)

    coverage = sub.add_parser("coverage", help="recorded product requirement coverage (#170)")
    coverage.add_argument("file", help="approved example filename or path")
    coverage.add_argument("--product", required=True, help="Product id")
    _add_transport(coverage)
    coverage.set_defaults(func=_coverage)

    risk = sub.add_parser("risk", help="derive a risk vector from recorded path ratings (#63)")
    risk.add_argument("file", help="approved model filename or path below spec/vectors")
    risk.add_argument("--matrix", required=True, help="explicit profile: annex-h-table-h8")
    risk.add_argument("--goal", default=None, help="only this threat-instance id")
    _add_transport(risk)
    risk.set_defaults(func=_risk)

    tara = sub.add_parser("tara", help="collect a draft TARA intermediate as JSON (#181)")
    tara.add_argument("file", help="approved model filename or path below spec/vectors")
    tara.add_argument("--matrix", required=True, help="explicit profile: annex-h-table-h8")
    tara.add_argument("--output", default=None, help="write a .json file instead of stdout")
    _add_transport(tara)
    tara.set_defaults(func=_tara)

    library = sub.add_parser("library", help="the library's records (#140)")
    for name in core.LIBRARY_FILTERS:
        library.add_argument(f"--{name}", default=None, help=f"only records with this {name}")
    _add_transport(library)
    library.set_defaults(func=_library)

    weak = sub.add_parser("weaknesses", help="CWE weaknesses from the pinned release (#144)")
    weak.add_argument("--id", default=None, help="one entry in full, e.g. CWE-79 or tr-weak-0001")
    weak.add_argument(
        "--relationships",
        action="store_true",
        help="relationships, each in its CWE view (#145); with --id, that entry's",
    )
    weak.add_argument(
        "--view", default=None, help="with --relationships: only these views, e.g. CWE-1000,699"
    )
    weak.add_argument(
        "--stated-only",
        action="store_true",
        help="with --relationships: only the written ones, no derived inverses",
    )
    for name in core.WEAKNESS_FILTERS:
        weak.add_argument(f"--{name}", default=None, help=f"only weaknesses with this {name}")
    weak.add_argument(
        "--search", default=None, help="text in the id, name, description or alternate terms"
    )
    weak.add_argument("--sort", default=None, choices=core.WEAKNESS_SORTS, help="default id")
    weak.add_argument("--order", default=None, choices=("asc", "desc"), help="default asc")
    weak.add_argument("--limit", default=None, help="at most this many rows")
    weak.add_argument("--offset", default=None, help="skip this many rows first")
    _add_transport(weak)
    weak.set_defaults(func=_weaknesses)

    patterns = sub.add_parser(
        "attack-patterns", help="CAPEC attack patterns from the pinned release (#244)"
    )
    patterns.add_argument("--id", default=None, help="one entry in full, e.g. CAPEC-66")
    for name in core.ATTACK_PATTERN_FILTERS:
        patterns.add_argument(
            f"--{name}", default=None, help=f"only attack patterns with this {name}"
        )
    patterns.add_argument(
        "--search",
        default=None,
        help="text in the id, name, description, alternate terms, CWE or ATT&CK ids",
    )
    patterns.add_argument(
        "--sort", default=None, choices=core.ATTACK_PATTERN_SORTS, help="default id"
    )
    patterns.add_argument("--order", default=None, choices=("asc", "desc"), help="default asc")
    patterns.add_argument("--limit", default=None, help="at most this many rows")
    patterns.add_argument("--offset", default=None, help="skip this many rows first")
    _add_transport(patterns)
    patterns.set_defaults(func=_attack_patterns)

    sdl = sub.add_parser("sdl", help="SDL program view of an SDL model (DL-0043)")
    sdl.add_argument("file", nargs="?", default=None, help="e.g. sdl-01-tmodel-desktop.yaml")
    sdl.add_argument("--program", default=None, help="SecurityProgram id, if the file has several")
    _add_transport(sdl)
    sdl.set_defaults(func=_sdl)

    propose = sub.add_parser(
        "propose", help="write an agent's patch as proposals only (DL-0044, DL-0046)"
    )
    propose.add_argument("patch", help="patch file (YAML or JSON), or - for stdin")
    propose.add_argument("--dry-run", action="store_true", help="check only, write nothing")
    propose.add_argument("--json", action="store_true", help="print JSON")
    propose.set_defaults(func=_propose)

    pending = sub.add_parser("proposals", help="pending proposals and saved KG views (DL-0046)")
    pending.add_argument(
        "file", nargs="?", default=None, help="e.g. mvp-01-software-doc-service.yaml"
    )
    _add_transport(pending)
    pending.set_defaults(func=_proposals)

    decide = sub.add_parser("accept", help="the sponsor decides one proposal (DL-0046)")
    decide.add_argument("proposal", help="proposal id, e.g. proposal:20261107T200000Z-abc123")
    decide.add_argument("--model", required=True, help="the model file the proposal targets")
    decide.add_argument("--reviewer", required=True, help="the sponsor's Party id")
    decide.add_argument("--justification", required=True, help="why; goes on the Review")
    decide.add_argument(
        "--verdict", choices=("accepted", "rejected", "changes_requested"), default="accepted"
    )
    decide.add_argument(
        "--declare-sponsor",
        default=None,
        metavar="GITHUB",
        help="add the reviewer as a sponsor Party if the model has none",
    )
    decide.add_argument("--json", action="store_true", help="print JSON")
    decide.set_defaults(func=_accept)

    imported = sub.add_parser(
        "import-sbom",
        help="write a starter model from an image's SBOM and its Grype scan (#257)",
    )
    imported.add_argument(
        "sbom", help="Syft's CycloneDX 1.7 JSON SBOM of a container image named by digest"
    )
    imported.add_argument("--scan", help="Grype's JSON scan of that SBOM: grype sbom:FILE -o json")
    imported.add_argument(
        "--platform",
        metavar="OS/ARCH[/VARIANT]",
        help=(
            "the platform of the build the SBOM's digest names, e.g. linux/arm64/v8: the "
            "SBOM does not say whether its digest is a platform's or an index's, which "
            "every platform shares. Needed unless the scan records it, as Grype does when "
            "it read the image itself (not the SBOM)"
        ),
    )
    imported.add_argument(
        "-o",
        "--output",
        required=True,
        help="the model file to write, e.g. spec/vectors/pv-05-NAME.yaml",
    )
    imported.add_argument("--report", help="write the import report here instead of printing it")
    imported.add_argument(
        "--force", action="store_true", help="replace the model or report if it exists"
    )
    imported.set_defaults(func=_import_sbom)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
