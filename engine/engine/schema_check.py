"""Check a model document against an example container's LinkML schema (#288).

CI validates the example models with `linkml-validate` (spec/vectors/README.md), but
LinkML is too large to bundle into the app (engine/pyproject.toml). The workspace
still has to check every saved version against the schema, so this reads the same
container and object-model YAML and applies the part of LinkML they use: classes
with `is_a`, `slots`, `attributes` and `slot_usage`; slots with `range`, `any_of`,
`multivalued`, `inlined`, `required` and `identifier`; enums; and the `string`,
`integer`, `boolean`, `date`, `datetime` and `uriorcurie` types. Like
`linkml-validate`, every class is closed (an unknown key is an error) and an id
reference is only checked to be a string. Whether it resolves is the model graph's
check (`engine.model_graph.project_model_graph`).

A schema feature outside that set raises SchemaError when the container is loaded,
so a schema change cannot silently weaken the check.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import yaml

# The example containers the workspace can store, by tree-root class (spec/vectors/README.md).
CONTAINER_FILES = {
    "ExampleModelCore": "example-container-core.linkml.yaml",
    "ExampleModelProposed": "example-container-proposed.linkml.yaml",
    "ExampleModel": "example-container.linkml.yaml",
    "ExampleModelSdl": "example-container-sdl.linkml.yaml",
}
BUILTIN_IMPORTS = frozenset({"linkml:types"})
TYPES = frozenset({"string", "integer", "boolean", "date", "datetime", "uriorcurie"})
CLASS_KEYS = frozenset(
    {"description", "slots", "is_a", "slot_usage", "abstract", "attributes", "tree_root"}
)
SLOT_KEYS = frozenset(
    {
        "description",
        "range",
        "multivalued",
        "inlined",
        "inlined_as_list",
        "required",
        "any_of",
        "identifier",
        "examples",
    }
)
ENUM_KEYS = frozenset({"description", "permissible_values"})
# Schema-level keys that do not change what a document may contain.
SCHEMA_KEYS = frozenset(
    {
        "id",
        "name",
        "title",
        "description",
        "version",
        "status",
        "annotations",
        "prefixes",
        "default_prefix",
        "default_range",
        "imports",
        "classes",
        "slots",
        "enums",
    }
)


class SchemaError(RuntimeError):
    """The schema uses a LinkML feature this checker does not implement."""


@dataclass(frozen=True)
class Problem:
    field: str
    message: str


@dataclass(frozen=True)
class Slot:
    name: str
    ranges: tuple[str, ...]
    multivalued: bool
    inlined: bool | None
    required: bool


class Container:
    """One container's classes, slots and enums, merged across its imports."""

    def __init__(self, root: str, classes: dict, slots: dict, enums: dict) -> None:
        self.root = root
        self._classes = classes
        self._slots = slots
        self._enums = enums
        self._induced: dict[str, dict[str, Slot]] = {}
        for name in classes:
            self.slots_of(name)  # resolve every class now, so a bad schema fails at load

    def slots_of(self, class_name: str) -> dict[str, Slot]:
        if class_name not in self._induced:
            self._induced[class_name] = {
                name: self._slot(class_name, name, raw)
                for name, raw in self._raw_slots(class_name, ()).items()
            }
        return self._induced[class_name]

    def _raw_slots(self, class_name: str, seen: tuple[str, ...]) -> dict[str, dict]:
        """A class's slot definitions: its parent's, then its own slots, attributes and usage."""
        if class_name in seen:
            raise SchemaError(f"{class_name}: is_a cycle")
        defn = self._classes.get(class_name)
        if defn is None:
            raise SchemaError(f"unknown class {class_name}")
        _known_keys(defn, CLASS_KEYS, f"class {class_name}")
        parent = defn.get("is_a")
        merged = self._raw_slots(parent, (*seen, class_name)) if parent else {}
        for name in defn.get("slots") or []:
            if name not in self._slots:
                raise SchemaError(f"class {class_name}: unknown slot {name}")
            merged[name] = dict(self._slots[name] or {})
        for name, local in (defn.get("attributes") or {}).items():
            merged[name] = dict(local or {})
        for name, usage in (defn.get("slot_usage") or {}).items():
            if name not in merged:
                raise SchemaError(f"class {class_name}: slot_usage for unknown slot {name}")
            merged[name] = {**merged[name], **(usage or {})}
        return merged

    def _slot(self, class_name: str, name: str, raw: Mapping[str, Any]) -> Slot:
        _known_keys(raw, SLOT_KEYS, f"slot {class_name}.{name}")
        ranges = [alt.get("range") for alt in raw.get("any_of") or []]
        if not ranges:
            ranges = [raw.get("range") or "string"]
        for kind in ranges:
            if kind not in TYPES and kind not in self._classes and kind not in self._enums:
                raise SchemaError(f"slot {class_name}.{name}: unknown range {kind}")
        return Slot(
            name=name,
            ranges=tuple(ranges),
            multivalued=bool(raw.get("multivalued")),
            inlined=raw.get("inlined"),
            required=bool(raw.get("required") or raw.get("identifier")),
        )

    def is_class(self, name: str) -> bool:
        return name in self._classes

    def is_inlined(self, slot: Slot, class_name: str) -> bool:
        """LinkML's default: a class with an identifier is referenced by id, else inlined."""
        if slot.inlined is not None:
            return bool(slot.inlined)
        return not any(s.required and s.name == "id" for s in self.slots_of(class_name).values())

    def enum_values(self, name: str) -> frozenset[str] | None:
        if name not in self._enums:
            return None
        return frozenset(str(v) for v in (self._enums[name].get("permissible_values") or {}))


def check(document: Any, container: Container, limit: int = 20) -> list[Problem]:
    """Every way `document` breaks the container's schema, up to `limit`, in document order."""
    problems: list[Problem] = []
    _check_object(document, container.root, "", container, problems, limit)
    return problems[:limit]


def _check_object(
    value: Any, class_name: str, where: str, c: Container, out: list[Problem], limit: int
) -> None:
    if not isinstance(value, Mapping):
        out.append(Problem(where or "model", f"expected an object ({class_name})"))
        return
    slots = c.slots_of(class_name)
    for key in value:
        if len(out) >= limit:
            return
        if not isinstance(key, str) or key not in slots:
            out.append(Problem(_join(where, str(key)), f"{class_name} has no field {key!r}"))
    for name, slot in slots.items():
        if len(out) >= limit:
            return
        field = _join(where, name)
        if name not in value or value[name] is None:
            if slot.required:
                out.append(Problem(field, f"{class_name} requires {name}"))
            continue
        item = value[name]
        if slot.multivalued:
            if not isinstance(item, list):
                out.append(Problem(field, "expected a list"))
                continue
            for index, element in enumerate(item):
                _check_value(element, slot, class_name, f"{field}[{index}]", c, out, limit)
        else:
            _check_value(item, slot, class_name, field, c, out, limit)


def _check_value(
    value: Any,
    slot: Slot,
    owner: str,
    where: str,
    c: Container,
    out: list[Problem],
    limit: int,
) -> None:
    if len(out) >= limit:
        return
    if value is None:
        out.append(Problem(where, "expected a value, not null"))
        return
    failures: list[list[Problem]] = []
    for kind in slot.ranges:
        attempt: list[Problem] = []
        if c.is_class(kind) and c.is_inlined(slot, kind):
            _check_object(value, kind, where, c, attempt, limit)
        elif c.is_class(kind):
            if not isinstance(value, str):
                attempt.append(Problem(where, f"expected the id of a {kind}"))
        elif (values := c.enum_values(kind)) is not None:
            if not isinstance(value, str) or value not in values:
                allowed = ", ".join(sorted(values))
                attempt.append(Problem(where, f"{value!r} is not a {kind} value ({allowed})"))
        elif not _is_type(value, kind):
            attempt.append(Problem(where, f"expected {_TYPE_NAMES[kind]}"))
        if not attempt:
            return
        failures.append(attempt)
    if len(failures) == 1:
        out.extend(failures[0])
    else:
        names = " or ".join(slot.ranges)
        out.append(Problem(where, f"expected the id of a {names}"))


_TYPE_NAMES = {
    "string": "text",
    "uriorcurie": "a URI or CURIE",
    "integer": "a whole number",
    "boolean": "true or false",
    "date": "a date (YYYY-MM-DD)",
    "datetime": "a date and time (ISO 8601)",
}


def _is_type(value: Any, kind: str) -> bool:
    if kind in ("string", "uriorcurie"):
        return isinstance(value, str)
    if kind == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == "boolean":
        return isinstance(value, bool)
    if kind == "date":
        if isinstance(value, dt.date) and not isinstance(value, dt.datetime):
            return True
        return isinstance(value, str) and _parses(dt.date.fromisoformat, value)
    if kind == "datetime":
        if isinstance(value, dt.datetime):
            return True
        return isinstance(value, str) and _parses(dt.datetime.fromisoformat, value)
    raise SchemaError(f"unknown type {kind}")


def _parses(parse: Any, text: str) -> bool:
    try:
        parse(text)
    except ValueError:
        return False
    return True


def _join(where: str, name: str) -> str:
    return f"{where}.{name}" if where else name


def _known_keys(defn: Mapping[str, Any], allowed: frozenset[str], what: str) -> None:
    unknown = set(defn) - allowed
    if unknown:
        raise SchemaError(f"{what}: unsupported LinkML keys {sorted(unknown)}")


@cache
def load_container(vector_directory: Path, root: str) -> Container:
    """The container whose tree root is `root`, read from `vector_directory`."""
    if root not in CONTAINER_FILES:
        raise SchemaError(f"unknown container {root}")
    classes: dict = {}
    slots: dict = {}
    enums: dict = {}
    for schema in _schemas(vector_directory / CONTAINER_FILES[root], ()):
        _known_keys(schema, SCHEMA_KEYS, "schema")
        if (schema.get("default_range") or "string") != "string":
            raise SchemaError("only default_range: string is supported")
        for name, defn in (schema.get("enums") or {}).items():
            _known_keys(defn or {}, ENUM_KEYS, f"enum {name}")
        classes.update(schema.get("classes") or {})
        slots.update(schema.get("slots") or {})
        enums.update(schema.get("enums") or {})
    if not (classes.get(root) or {}).get("tree_root"):
        raise SchemaError(f"{root}: not a tree root")
    return Container(root, classes, slots, enums)


def _schemas(path: Path, seen: tuple[Path, ...]) -> list[dict]:
    """The schema at `path` after everything it imports, imports first."""
    path = path.resolve()
    if path in seen:
        return []
    try:
        schema = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SchemaError(f"cannot read schema {path.name}") from exc
    found: list[dict] = []
    for name in schema.get("imports") or []:
        if name in BUILTIN_IMPORTS:
            continue
        found += _schemas(path.parent / f"{name}.yaml", (*seen, path))
    return [*found, schema]
