"""Load an example model (a `spec/vectors/*.yaml` file) into an AttackGraph.

Stand-in for the library loader and store façade (#60, #65) until they exist:
only the attack structure is read; everything else in the file is ignored.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from engine.graph import AttackGraph, GraphError

MODEL_SUFFIXES = (".yaml", ".yml")


def load_vector(path: str | Path) -> AttackGraph:
    path = Path(path)
    if path.suffix not in MODEL_SUFFIXES:
        raise GraphError(f"{path}: expected a .yaml or .yml model file")
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise GraphError(f"{path}: cannot read ({exc.strerror or exc})") from exc
    except yaml.YAMLError as exc:
        raise GraphError(f"{path}: not valid YAML ({exc})") from exc
    if not isinstance(doc, dict):
        raise GraphError(f"{path}: expected a mapping at the top level")
    return AttackGraph.from_dict(doc)
