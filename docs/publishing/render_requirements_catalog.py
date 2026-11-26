"""Generate the public extracted-standards Requirement catalog.

The three research YAML fragments remain authoritative.  This renderer validates
their extraction rules, projects them through the engine's storage-neutral graph
adapter, and writes the deterministic asset bundled by Vite in both desktop and
GitHub Pages builds.

    engine/.venv/bin/python docs/publishing/render_requirements_catalog.py
    engine/.venv/bin/python docs/publishing/render_requirements_catalog.py --check
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research" / "0017-requirements-extraction"
OUT = ROOT / "apps" / "desktop" / "public" / "data" / "requirements" / "catalog.json"
sys.path.insert(0, str(ROOT / "engine"))

try:
    from engine.load.vector import load_vector_document
    from engine.model_graph import project_model_graph
except ImportError as exc:
    raise SystemExit(
        f"render_requirements_catalog: cannot import the engine ({exc}); "
        "run with engine/.venv/bin/python"
    ) from exc

from public_data_guard import render_public_json

SOURCES = (
    {
        "id": "owasp-asvs-5",
        "name": "OWASP ASVS",
        "version": "5.0.0",
        "file": "owasp-asvs-5.yaml",
        "count": 34,
    },
    {
        "id": "eu-cra-2024-2847",
        "name": "EU Cyber Resilience Act",
        "version": "Regulation (EU) 2024/2847",
        "file": "eu-cra-2024-2847.yaml",
        "count": 23,
    },
    {
        "id": "iec-62443-4-1-2018",
        "name": "IEC 62443-4-1",
        "version": "2018",
        "file": "iec-62443-4-1-2018.yaml",
        "count": 52,
    },
)
EXPECTED_TOTAL = 109
PUBLIC_REVIEWER_PREFIX = "party:catalog-human-reviewer"


def _load_extraction_check() -> Any:
    path = RESEARCH / "check.py"
    spec = importlib.util.spec_from_file_location("requirements_extraction_check", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load extraction validator at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _replace_identity(text: str, identities: set[str]) -> str:
    result = text
    for identity in sorted(identities, key=len, reverse=True):
        if identity:
            result = re.sub(
                re.escape(identity), "the human reviewer", result, flags=re.IGNORECASE
            )
    return result


def _public_document(document: dict[str, Any]) -> dict[str, Any]:
    """Preserve evidence while replacing unpublished project identities by role."""
    result = copy.deepcopy(document)
    people = [
        party
        for party in result.get("parties") or []
        if party.get("party_kind") == "person" and isinstance(party.get("id"), str)
    ]
    replacements: dict[str, str] = {}
    identities: set[str] = set()
    for index, party in enumerate(people, start=1):
        old_id = party["id"]
        public_id = f"{PUBLIC_REVIEWER_PREFIX}-{index}"
        replacements[old_id] = public_id
        identities.update(
            {old_id, old_id.removeprefix("party:"), str(party.get("name") or "")}
        )
        party["id"] = public_id
        party["name"] = "Human reviewer"

    for review in result.get("reviews") or []:
        reviewer = review.get("reviewer")
        if reviewer in replacements:
            review["reviewer"] = replacements[reviewer]
        justification = review.get("justification")
        if isinstance(justification, str):
            review["justification"] = _replace_identity(justification, identities)
    return result


def build_catalog() -> dict[str, Any]:
    extraction_check = _load_extraction_check()
    sources: list[dict[str, Any]] = []
    requirement_ids: set[str] = set()
    total = 0

    for metadata in SOURCES:
        path = RESEARCH / metadata["file"]
        count, errors, _notes, _marks = extraction_check.check(path)
        if errors:
            raise RuntimeError(
                f"{path.name}: extraction validation failed: {'; '.join(errors)}"
            )
        if count != metadata["count"]:
            raise RuntimeError(
                f"{path.name}: expected {metadata['count']} Requirements, found {count}"
            )

        loaded = load_vector_document(path)
        public = _public_document(dict(loaded))
        graph = project_model_graph(public).to_dict()
        graph_requirements = [
            node for node in graph["nodes"] if node["domain_type"] == "Requirement"
        ]
        if len(graph_requirements) != count:
            raise RuntimeError(
                f"{path.name}: graph contains {len(graph_requirements)} Requirements, expected {count}"
            )
        duplicates = requirement_ids.intersection(
            node["id"] for node in graph_requirements
        )
        if duplicates:
            raise RuntimeError(
                f"duplicate Requirement ids across sources: {', '.join(sorted(duplicates))}"
            )
        requirement_ids.update(node["id"] for node in graph_requirements)
        total += count
        sources.append(
            {
                "id": metadata["id"],
                "name": metadata["name"],
                "version": metadata["version"],
                "count": count,
                "graph": {"file": path.name, **graph},
            }
        )

    if total != EXPECTED_TOTAL or len(requirement_ids) != EXPECTED_TOTAL:
        raise RuntimeError(
            f"catalog must contain {EXPECTED_TOTAL} unique Requirements, "
            f"found {total} rows and {len(requirement_ids)} unique ids"
        )
    return {
        "schema_version": 1,
        "name": "Extracted Standards Catalog",
        "count": total,
        "sources": sources,
    }


def render() -> str:
    return render_public_json(
        build_catalog(), root=ROOT, context="requirements catalog"
    )


def write() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")


def check() -> int:
    expected = render().encode()
    current = OUT.read_bytes() if OUT.is_file() else b""
    if current != expected:
        print(
            f"render_requirements_catalog: {OUT.relative_to(ROOT)} is out of date",
            file=sys.stderr,
        )
        return 1
    print(
        "render_requirements_catalog: catalog is up to date "
        "(34 ASVS, 23 CRA, 52 IEC; 109 total)"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--check", action="store_true", help="fail if the catalog is stale"
    )
    args = parser.parse_args()
    if args.check:
        return check()
    write()
    print(
        f"render_requirements_catalog: wrote {OUT.relative_to(ROOT)} "
        "(34 ASVS, 23 CRA, 52 IEC; 109 total)"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError) as exc:
        print(f"render_requirements_catalog: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
