"""The Import New Product route (#287): `tmodel import-sbom` on files the app sends.

The app's Import New Product screen, one of the three entry points of the team's
design for saving and reopening threat models, sends the bytes of an SBOM and, if the
user has one, of a Grype scan of the same image, each in base64 with its file name.
The engine runs the same import as the command line on those bytes, in memory, and
returns the model and the import report as text, with the counts and warnings.
Nothing is written to disk. The app then starts a project from the model through the
host (#288), and the model becomes the project's `original.yaml`, so the header's
validation line names that file.

The route is opt-in (`make_server(import_enabled=True)`, or `tmodel serve
--enable-import`), so the normal desktop launch stays read-only. Its errors use the
envelope of the review operations of #289 (`engine/HUMAN_REVIEW.md` on that branch):
`{"error": {"code", "message", ...}}`, with `validation_error` (422) for a malformed
request. A file name is reduced to a plain base name, and no local path is read from
a request or sent back.
"""

from __future__ import annotations

import base64
import json
import re
import threading
from typing import Any

from engine import import_sbom

PATH = "/import/sbom"
MAX_FILE_BYTES = import_sbom.MAX_INPUT_BYTES  # each file, as the command line allows
MAX_MIB = MAX_FILE_BYTES // (1024 * 1024)
_MAX_ENCODED = 4 * -(-MAX_FILE_BYTES // 3)  # a file of that size in base64
MAX_BODY_BYTES = 2 * _MAX_ENCODED + 64 * 1024  # two such files, their names, the platform
# A request is three small objects whose bulk is base64, which has no brackets or commas.
# Counting brackets and commas before parsing bounds how many values parsing can make: a
# body of nested or long lists would otherwise take many times its size. Only those
# outside strings count, so a file name or platform may hold any number of them.
MAX_STRUCTURE = 64
# A real request has about two dozen quotes, and any its two file names hold (a Mac's
# names have at most 255 characters). Each string the count finds costs a little memory,
# so a body of nothing but quotes is refused before the strings are looked for.
MAX_QUOTES = 1024
# A JSON string, from its opening quote to its closing one, or to the end of the body
# when it has none (parsing stops there). Nothing after the quote can fail to match, so
# the search never backtracks and stays linear, even on a body of escaped quotes. The
# quantifiers are possessive (Python 3.11): without that, the search keeps a step to go
# back to for every escape, about 90 bytes of memory for each byte of escapes.
_STRING = re.compile(r'"[^"\\]*+(?:\\[\s\S]?[^"\\]*+)*+"?')
READ_SECONDS = 30  # for the whole body, not for each read
WAIT_SECONDS = 60  # for an import that is already running
MODEL_FILE = "original.yaml"  # the file the model becomes in a project (#288)
FIELDS = ("sbom", "scan", "platform")
_SLOT = threading.Lock()  # one import at a time: each can hold hundreds of MB
_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


class ImportRouteError(Exception):
    """A refusal the route answers with: its HTTP status, a stable code and a message."""

    def __init__(
        self,
        status: int,
        code: str,
        message: str,
        *,
        notes: list[str] | None = None,
        field: str | None = None,
    ):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.notes = list(notes or ())
        self.field = field

    def to_dict(self) -> dict[str, Any]:
        error: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.notes:
            error["notes"] = self.notes
        if self.field:
            error["fields"] = [{"field": self.field, "message": self.message}]
        return {"error": error}


def invalid(message: str, field: str | None = None) -> ImportRouteError:
    """A malformed request, as #289's operations answer one."""
    return ImportRouteError(422, "validation_error", message, field=field)


def acquire_slot() -> bool:
    """Take the one import slot, waiting up to WAIT_SECONDS for a running import."""
    return _SLOT.acquire(timeout=WAIT_SECONDS)


def release_slot() -> None:
    _SLOT.release()


def busy() -> ImportRouteError:
    return ImportRouteError(503, "busy", "Another import is running; try again when it finishes.")


class _Repeated(ValueError):
    """A JSON object names one key twice; json would keep only the last value."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    doc: dict[str, Any] = {}
    for key, value in pairs:
        if key in doc:
            raise _Repeated(key)
        doc[key] = value
    return doc


def _constant(value: str) -> Any:
    raise ValueError(f"{value} is not a JSON value")


def _base_name(name: str, default: str) -> str:
    """A file name as a plain base name: no folders, only letters, digits, dots, dashes
    and underscores, at most 100 characters, else `default`."""
    base = name.replace("\\", "/").rsplit("/", 1)[-1]
    base = _UNSAFE.sub("-", base).strip(".-")[:100].strip(".-")
    return base or default


def _upload(value: Any, field: str, label: str) -> import_sbom.Upload | None:
    if value is None:
        return None
    if (
        not isinstance(value, dict)
        or not set(value) <= {"name", "base64"}
        or not isinstance(value.get("base64"), str)
        or not isinstance(value.get("name", ""), str)
    ):
        raise invalid(
            f"The {label} must be an object with its name and its bytes in base64.", field
        )
    encoded = value["base64"]
    if len(encoded) > _MAX_ENCODED:
        raise invalid(f"The {label} file is larger than {MAX_MIB} MiB.", field)
    try:
        data = base64.b64decode(encoded, validate=True)
    except ValueError:  # binascii.Error, or a character outside ASCII
        raise invalid(f"The {label} file's base64 is not valid.", field) from None
    if len(data) > MAX_FILE_BYTES:  # base64 rounds up, so check the bytes as well
        raise invalid(f"The {label} file is larger than {MAX_MIB} MiB.", field)
    if not data:
        raise invalid(f"The {label} file is empty.", field)
    return import_sbom.Upload(_base_name(value.get("name", ""), f"{field}.json"), data)


def structure(text: str) -> int:
    """The brackets and commas of a JSON text outside its strings: what can make the
    values parsing builds. Parsing reads strings as this does, so none is hidden."""
    bare = _STRING.sub('""', text)
    return bare.count("{") + bare.count("[") + bare.count(",")


def parse_request(
    body: bytes,
) -> tuple[import_sbom.Upload, import_sbom.Upload | None, str | None]:
    """The SBOM, the scan (or None) and the platform (or None) a request body names,
    or ImportRouteError for anything but exactly that."""
    try:
        # UTF-8 only (RFC 8259 §8.1), as the app sends, with or without a byte order mark,
        # as json reads it: json would also read UTF-16 and UTF-32, whose bytes the
        # structure count could not read as parsing does.
        text = body.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise invalid("The request body must be JSON in UTF-8.") from None
    if text.count('"') > MAX_QUOTES or structure(text) > MAX_STRUCTURE:
        raise invalid("Send only the SBOM, the scan and the platform.")
    try:
        payload = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
    except _Repeated as exc:
        raise invalid(f"The key {exc.args[0][:40]!r} appears twice in one object.") from None
    except (ValueError, RecursionError):  # not JSON, or NaN
        raise invalid("The request body is not JSON.") from None
    if not isinstance(payload, dict):
        raise invalid("The request body must be a JSON object.")
    for key in payload:
        if key not in FIELDS:
            raise invalid(f"Unknown field {key[:40]!r}: send only sbom, scan and platform.")
    sbom = _upload(payload.get("sbom"), "sbom", "SBOM")
    if sbom is None:
        raise invalid("Provide the SBOM file.", "sbom")
    scan = _upload(payload.get("scan"), "scan", "scan")
    platform = payload.get("platform")
    if platform is not None and not isinstance(platform, str):
        raise invalid("The platform must be text, such as linux/arm64/v8.", "platform")
    return sbom, scan, platform or None


def _suggested_name(product: str) -> str:
    """The repository's last path part, as a file-name slug (`alpine`)."""
    last = product.rsplit("/", 1)[-1].lower()
    return re.sub(r"[^a-z0-9]+", "-", last).strip("-") or "model"


def run_import(body: bytes) -> dict[str, Any]:
    """The route's answer to a request body, or ImportRouteError. The caller holds the
    import slot."""
    sbom, scan, platform = parse_request(body)
    try:
        result = import_sbom.build(sbom, scan=scan, platform=platform, output_name=MODEL_FILE)
    except import_sbom.SbomImportError as exc:
        notes = [str(note) for note in getattr(exc, "__notes__", ())]
        raise ImportRouteError(422, "import_refused", str(exc), notes=notes) from None
    return {
        "model_text": result.model_text,
        "report_text": result.report_text,
        "warnings": list(result.warnings),
        "counts": dict(result.counts),
        "platform": result.platform,
        "product": result.product,
        "suggested_name": _suggested_name(result.product),
    }
