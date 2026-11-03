"""Load an example model (a `spec/vectors/*.yaml` file) into an AttackGraph.

Stand-in for the library loader and store façade (#60, #65) until they exist:
only the attack structure is read; everything else in the file is ignored.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from engine.graph import AttackGraph, GraphError

MODEL_SUFFIXES = (".yaml", ".yml")


def load_vector(path: str | Path) -> AttackGraph:
    """Load and validate the attack-graph portion of an example model."""
    path = Path(path)
    doc = load_vector_document(path)
    try:
        return AttackGraph.from_dict(doc)
    except GraphError as exc:
        raise GraphError(f"{path}: {exc}") from exc


def load_vector_document(path: str | Path) -> Mapping[str, Any]:
    """Read an example model using the same YAML checks as ``load_vector``.

    The graph projection uses the complete mapping while attack-path enumeration
    continues to consume ``AttackGraph``. Keeping parsing here gives both API
    surfaces one loader and one set of file-format errors.
    """
    path = Path(path)
    if path.suffix not in MODEL_SUFFIXES:
        raise GraphError(f"{path}: expected a .yaml or .yml model file")
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise GraphError(f"{path}: cannot read ({exc.strerror or exc})") from exc
    except UnicodeDecodeError as exc:
        raise GraphError(f"{path}: not UTF-8 text") from exc
    except (yaml.YAMLError, ValueError) as exc:  # PyYAML raises ValueError for e.g. 2026-02-30
        raise GraphError(f"{path}: not valid YAML ({exc})") from exc
    if not isinstance(doc, dict):
        raise GraphError(f"{path}: expected a mapping at the top level")
    return doc
