"""Write a starter model from a CycloneDX SBOM and its Grype scan (#257, DL-0068).

    tmodel import-sbom SBOM.json [--scan SCAN.json] [--platform OS/ARCH[/VARIANT]]
        -o MODEL.yaml [--report FILE] [--force]

Input is two files radar's tools write (ADR-0001, ARCH-0001 R-002): Syft's CycloneDX
1.7 JSON SBOM of a container image, and Grype's JSON scan of that SBOM
(`grype sbom:SBOM.json -o json`). tradar runs the same two tools; its own saved scan
file drops the CWEs and match details, so read Grype's file instead. Making the SBOM
and scanning it stay radar's job; this module only reads the two files.

Output is a starter model that `linkml-validate` accepts as `ExampleModelProposed`
and the engine loads, plus an import report. The mapping is RPT-0004 Table 6
(`research/0004-product-composition/mapping.md`) and its candidate rules:

- a Product keyed by the image's versionless purl (R-ID-2), and a ProductInstance for
  the scanned build, keyed by the digest the SBOM records and the build's platform
  (R-ID-1), whose `build_composed_of` lists the components (ADR-0011 A4). The SBOM does
  not say whether its digest is a platform manifest's or an index's, which every
  platform of a release shares, so the platform comes from `--platform` or from a scan
  Grype made of the image itself, and is checked against the packages' `arch`
  qualifiers. The ids are made from the keys: the whole repository, and the whole
  digest with the platform. The SBOM never fills the design-level `composed_of`
  (R-EDGE-2);
- one Component per SBOM entry other than files (R-ID-4), keyed by its purl, qualifiers
  and all, normalized by the rules the purl specification gives every type (R-ID-3),
  with `version`, `component_kind` from CycloneDX's `type` (A3), and every purl and CPE
  the entry carries in `identifiers`. Entries merge only on the same normalized purl;
- `supplied_by` and `manufactured_by` only from a `supplier` or `manufacturer`
  field: a publisher or package maintainer is not a supplier (Table 6c);
- each `dependsOn` as `uses_component`, from the dependent to the dependency
  (R-EDGE-1, R-EDGE-3);
- one Vulnerability per CVE a match names (its own id, or one in
  `relatedVulnerabilities`); a match that names no CVE keeps the id Grype reports
  (GHSA, ALAS, GO and so on). Another id goes in `alias_ids` only when the whole scan
  pairs it with exactly one CVE; an advisory paired with several is listed in the
  report. Ids that appear only inside a URL are never read;
- one proposed `propagates_to` Assertion for each match and each Vulnerability it
  names, to the Component whose purl the match gives, joined to the SBOM by purl, not
  by `bom-ref` (R-MATCH-1, R-MATCH-2), with `confidence` from Grype's match type;
- one proposed `instance_of` Assertion per (CVE, CWE, source), `asserted_by` whoever
  assigned the CWE, skipping placeholders such as `NVD-CWE-Other` (R-CWE-1).

Every Assertion is `proposed`, with no Review (R-018), and records when (the scan's
time), how (`generated_by`: the tool, its version and the database build time,
R-PROV-2) and from what (`evidence`: the input files' SHA-256, R-PROV-1). Nothing
else is written: no assets, trust boundaries, data flows, threats, attack paths or
mitigations (Table 6f).

Deterministic: the same two files give the same model and report, byte for byte, and
the order of the scan's matches changes nothing but the scan's digest. Every input is
checked before anything is written: a field the import reads that has the wrong type,
or a scan of another image, is refused with a message naming it. The model and the
report are written to temporary files and put in place together, and an existing
file is never replaced without `--force`, because people edit starter models: not
even one that appears while the import runs, or one a Mac's volume reads as the same
name in another case or Unicode form.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import shutil
import stat
import tempfile
import unicodedata
from collections import Counter
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote

import yaml

from engine import __version__

# A Juice Shop image's SBOM and scan are a few MB each; this leaves wide room.
MAX_INPUT_BYTES = 64 * 1024 * 1024
# Syft's SBOM and Grype's scan nest fewer than ten levels deep; this leaves wide room,
# and keeps every walk over a file well inside Python's recursion limit.
MAX_DEPTH = 64
CYCLONEDX_VERSION = "1.7"
CONTAINER_SCHEMA = "spec/vectors/example-container-proposed.linkml.yaml"
MODEL_SUFFIXES = (".yaml", ".yml")

DIGEST = re.compile(r"sha256:[0-9a-f]{64}")
CVE_ID = re.compile(r"CVE-\d{4}-\d{4,}")
CWE_ID = re.compile(r"CWE-\d+")
# A Grype release such as 0.119.0. A build without one says "[not provided]".
GRYPE_VERSION = re.compile(r"v?\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.+-]+)?")
# What an image reference holds: a registry, a path, a tag and a digest. No spaces.
IMAGE_NAME = re.compile(r"[A-Za-z0-9._/:@-]+")
# Grype's source schemes: those of the first kind name an image, the second a file or a
# folder, which has no repository to compare.
IMAGE_SCHEME = re.compile(r"(?:docker|podman|registry|containerd):")
PATH_SCHEME = re.compile(r"(?:sbom|dir|file|docker-archive|oci-archive|oci-dir|singularity):")
# The purl specification's rules for a type and a qualifier key, the same for every type.
PURL_TYPE = re.compile(r"[a-z.+-][a-z0-9.+-]*")
QUALIFIER_KEY = re.compile(r"[a-z._-][a-z0-9._-]*")
SURROGATE = re.compile("[\ud800-\udfff]")
# One part of an OCI platform (linux/arm64/v8): an image index writes Go's GOOS and
# GOARCH names, and a variant such as v7 or v8, all in lower case.
PLATFORM_PART = re.compile(r"[a-z0-9]+(?:[._-][a-z0-9]+)*")
PLATFORM_EXAMPLE = "linux/arm64/v8"

# The names distributions write in a purl's `arch` qualifier, as the architecture an
# OCI image index names (Go's GOARCH): Alpine's (x86_64, aarch64, x86, armhf, armv7),
# Debian's (amd64, arm64, i386, armel, armhf, ppc64el) and RPM's (x86_64, aarch64,
# i686), with the OCI names themselves for an `oci` purl. A name not here is listed
# in the report as not checked; noarch, all and any (NO_ARCHITECTURE) name no CPU.
ARCHITECTURES = {
    "amd64": "amd64",
    "x86_64": "amd64",
    "arm64": "arm64",
    "aarch64": "arm64",
    "386": "386",
    "i386": "386",
    "i686": "386",
    "x86": "386",
    "arm": "arm",
    "armel": "arm",
    "armhf": "arm",
    "armv7": "arm",
    "ppc64le": "ppc64le",
    "ppc64el": "ppc64le",
    "s390x": "s390x",
    "riscv64": "riscv64",
}
NO_ARCHITECTURE = frozenset({"noarch", "all", "any"})
# A 64-bit platform runs its 32-bit sibling's packages too, which Debian's multiarch
# and RPM's multilib install beside the native ones (libc6:i386 on amd64).
ALSO_RUNS = {"amd64": "386", "arm64": "arm"}

# CycloneDX 1.7's component types, written as ComponentKind values (ADR-0011 A3).
COMPONENT_KINDS = {
    "application": "application",
    "framework": "framework",
    "library": "library",
    "container": "container",
    "platform": "platform",
    "operating-system": "operating_system",
    "device": "device",
    "device-driver": "device_driver",
    "firmware": "firmware",
    "file": "file",
    "machine-learning-model": "machine_learning_model",
    "data": "data",
    "cryptographic-asset": "cryptographic_asset",
}

# R-MATCH-1: exact direct, then exact indirect, then a CPE match, which Anchore says
# needs verification. The scale stays open (DL-0068), so the words are the ones the
# example models already use.
MATCH_CONFIDENCE = {
    "exact-direct-match": "high",
    "exact-indirect-match": "medium",
    "cpe-match": "low",
}
CONFIDENCE_RANK = {"high": 3, "medium": 2, "low": 1}

# The link from a Vulnerability to the Component a scan finds it in. The name stays
# open (R-MATCH-1); pv-03 already writes this predicate for the same kind of link,
# and the app's model report lists it under each vulnerability (DL-0068).
MATCH_PREDICATE = "propagates_to"
CWE_PREDICATE = "instance_of"

GRYPE_PARTY = "party:grype"
# A CWE entry with no source still becomes a link, with no asserted_by.
UNNAMED_SOURCE = "an unnamed source"

# Report headings for what is listed one by one.
MERGED = "SBOM entries recorded as one Component"
MERGED_APART = "SBOM entries recorded as one Component that disagree (the field is left out)"
VERSION_APART = "SBOM entries whose version differs from their purl's (the entry's is written)"
UNJOINED = "Matches left out (no Component with that purl)"
DISAGREE = "Matches left out (the scan's package and the SBOM's disagree)"
NO_ALIAS = (
    "Advisory ids written as no Vulnerability's alias (the scan pairs each with more than "
    "one CVE or Vulnerability)"
)
DESCRIBED = (
    "Vulnerabilities the scan describes in more than one way (the description written "
    "is the one from the namespace first in sorted order)"
)
ADVISORY_WORDS = (
    "Advisory descriptions left out (a description is written only on its own record's "
    "Vulnerability, and these advisories' matches are written as another id, most often "
    "a CVE)"
)
UNCHECKED_ARCH = (
    "Package architectures not checked against the platform (names this import does not know)"
)

# What became of a description that is not written, by reason, for the report's field
# inventory (`_Builder.words`).
WORDS_ADVISORY = "an advisory's, whose match is written as another id"
WORDS_OTHER = "in other words than the one written for its Vulnerability"
WORDS_MATCH = "with their match"
DESCRIPTION_PATHS = (
    "matches[].vulnerability.description",
    "matches[].relatedVulnerabilities[].description",
)


class SbomImportError(ValueError):
    """An input this import refuses, or an output it will not write."""


@dataclass(frozen=True)
class InputFile:
    """One input file as read: its name (never its full path), size and SHA-256."""

    label: str
    name: str
    size: int
    sha256: str

    @property
    def digest(self) -> str:
        return f"sha256:{self.sha256}"


@dataclass(frozen=True)
class SbomInfo:
    serial: str | None
    timestamp: str | None
    tool: str
    image: str
    digest: str
    bom_ref: str | None
    purl: str | None


@dataclass(frozen=True)
class Platform:
    """An OCI platform, as an image index names one build: os/architecture, and the
    CPU's variant when one is given (linux/arm64/v8)."""

    os: str
    architecture: str
    variant: str | None = None

    def __str__(self) -> str:
        return "/".join(p for p in (self.os, self.architecture, self.variant) if p)


# Each part of a platform, and where a scan Grype made of the image itself records it.
# Grype writes Syft's image metadata there, whose variant field is architectureVariant.
PLATFORM_FIELDS = (
    ("os", "os"),
    ("architecture", "architecture"),
    ("variant", "architectureVariant"),
)


@dataclass(frozen=True)
class ScanInfo:
    tool: str
    timestamp: str
    db_schema: str | None
    db_built: str
    image: str | None  # source.target.userInput: the image as Grype was given it
    image_id: str | None  # source.target.imageID
    also: tuple[str, ...]  # the rest of what source.target says, for the report
    distro: str | None  # the distribution Grype detected, as "name version"
    # The platform source.target records, part by part (os, architecture, variant).
    # Grype fills it when it read the image itself, and leaves it empty for an SBOM.
    platform: tuple[str | None, str | None, str | None] = (None, None, None)

    @property
    def generated_by(self) -> str:
        schema = f" {self.db_schema}" if self.db_schema else ""
        return f"{self.tool}, vulnerability database{schema} built {self.db_built}"


@dataclass
class ImportResult:
    """The model and report texts, and what was written."""

    model_text: str
    report_text: str
    counts: dict[str, int] = field(default_factory=dict)


def run(
    sbom: str | Path,
    *,
    scan: str | Path | None = None,
    output: str | Path,
    report: str | Path | None = None,
    force: bool = False,
    platform: str | None = None,
) -> ImportResult:
    """Read the inputs, write the model (and the report, when asked), and return both.
    `platform` is the build's, as `--platform` gives it (linux/arm64/v8)."""
    out = Path(output)
    report_path = Path(report) if report is not None else None
    inputs = [Path(sbom)] + ([Path(scan)] if scan is not None else [])
    outputs = [out] + ([report_path] if report_path is not None else [])
    _check_outputs(inputs, outputs, force)
    result = build(sbom, scan=scan, platform=platform, output_name=_display_path(out))
    texts = [result.model_text] + ([result.report_text] if report_path is not None else [])
    _publish(list(zip(outputs, texts, strict=True)), force)
    return result


def build(
    sbom: str | Path,
    *,
    scan: str | Path | None = None,
    platform: str | None = None,
    output_name: str = "MODEL.yaml",
) -> ImportResult:
    """The model and report texts for these inputs; nothing is written."""
    given = parse_platform(platform) if platform is not None else None
    sbom_file, sbom_doc = _read_json(Path(sbom), "SBOM")
    info = _check_sbom(sbom_doc, _one_line(sbom_file.name))
    scan_file = scan_doc = scan_info = None
    if scan is not None:
        scan_file, scan_doc = _read_json(Path(scan), "scan")
        scan_info = _check_scan(scan_doc, _one_line(scan_file.name), info)
    scan_name = _one_line(scan_file.name) if scan_file is not None else None
    build_platform = _build_platform(given, scan_info, _one_line(sbom_file.name), scan_name)
    builder = _Builder(sbom_file, sbom_doc, info, scan_file, scan_doc, scan_info, *build_platform)
    doc = builder.model()
    _self_check(doc)
    model_text = _header(builder, output_name) + _dump(doc)
    _read_back(model_text, doc)
    report_text = builder.report(output_name)
    return ImportResult(model_text, report_text, builder.counts())


# Reading and checking the inputs -----------------------------------------------------


class _RepeatedKey(ValueError):
    """A JSON object names one key twice; json would keep only the last value."""


class _NotJson(ValueError):
    """A value Python's json reads but JSON does not have, such as NaN."""


def _read_json(path: Path, label: str) -> tuple[InputFile, Any]:
    name = _one_line(path.name)
    data = _read(path)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SbomImportError(f"{name}: not UTF-8 text, so not JSON") from exc
    try:
        doc = json.loads(text, object_pairs_hook=_object, parse_constant=_not_json)
    except _RepeatedKey as exc:
        raise SbomImportError(
            f"{name}: the key {exc.args[0]!r} appears twice in one JSON object, so one of "
            "its values would be lost"
        ) from exc
    except json.JSONDecodeError as exc:
        raise SbomImportError(
            f"{name}: not valid JSON (line {exc.lineno}, column {exc.colno}: {exc.msg})"
        ) from exc
    except _NotJson as exc:
        raise SbomImportError(
            f"{name}: not valid JSON ({exc.args[0]} is not a JSON value)"
        ) from exc
    except RecursionError as exc:
        raise SbomImportError(f"{name}: nests too deeply to read") from exc
    except ValueError as exc:  # an integer with more digits than Python converts
        raise SbomImportError(
            f"{name}: not valid JSON, or holds a number too long to read"
        ) from exc
    if not isinstance(doc, dict):
        raise SbomImportError(f"{name}: expected a JSON object at the top level")
    _check_sound(doc, name)
    sha = hashlib.sha256(data).hexdigest()
    return InputFile(label, path.name, len(data), sha), doc


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    doc: dict[str, Any] = {}
    for key, value in pairs:
        if key in doc:
            raise _RepeatedKey(key)
        doc[key] = value
    return doc


def _not_json(constant: str) -> Any:
    raise _NotJson(constant)


def _check_sound(doc: Any, name: str) -> None:
    """At most MAX_DEPTH levels deep, and every key and text valid Unicode: JSON can
    spell half of a surrogate pair, which no UTF-8 file can hold."""
    pending: list[tuple[Any, int]] = [(doc, 1)]
    while pending:
        value, depth = pending.pop()
        if depth > MAX_DEPTH:
            raise SbomImportError(f"{name}: nests too deeply (more than {MAX_DEPTH} levels)")
        if isinstance(value, dict):
            for key, item in value.items():
                if SURROGATE.search(key):
                    raise SbomImportError(f"{name}: a key is not valid Unicode text")
                pending.append((item, depth + 1))
        elif isinstance(value, list):
            pending.extend((item, depth + 1) for item in value)
        elif isinstance(value, str) and SURROGATE.search(value):
            raise SbomImportError(f"{name}: a text value is not valid Unicode text")


def _read(path: Path) -> bytes:
    """The bytes of a regular file of at most MAX_INPUT_BYTES, checked before reading."""
    name = _one_line(path.name)
    too_large = f"{name}: larger than {MAX_INPUT_BYTES} bytes, so it is not read"
    try:
        with open(path, "rb", opener=_open_without_waiting) as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise SbomImportError(f"{name}: not a regular file, so it is not read")
            if info.st_size > MAX_INPUT_BYTES:
                raise SbomImportError(too_large)
            data = handle.read(MAX_INPUT_BYTES + 1)
    except OSError as exc:
        raise SbomImportError(f"{name}: cannot read ({exc.strerror or exc})") from exc
    if len(data) > MAX_INPUT_BYTES:  # it grew after the check
        raise SbomImportError(too_large)
    return data


def _open_without_waiting(path: str | Path, flags: int) -> int:
    # A FIFO with no writer would block open(); O_NONBLOCK returns at once so _read can
    # refuse it. A regular file reads the same either way.
    return os.open(path, flags | getattr(os, "O_NONBLOCK", 0))


def _check_sbom(doc: Mapping[str, Any], name: str) -> SbomInfo:
    if doc.get("bomFormat") != "CycloneDX":
        raise SbomImportError(f"{name}: not a CycloneDX SBOM (bomFormat is not CycloneDX)")
    if doc.get("specVersion") != CYCLONEDX_VERSION:
        raise SbomImportError(
            f"{name}: CycloneDX {doc.get('specVersion')!r}; this import reads CycloneDX "
            f"{CYCLONEDX_VERSION} as Syft writes it (other versions are a follow-up)"
        )
    metadata = doc.get("metadata")
    if not isinstance(metadata, dict):
        raise SbomImportError(f"{name}: no metadata, so no tool and no product")
    tool = _sbom_tool(metadata.get("tools"), name)
    if tool is None:
        raise SbomImportError(
            f"{name}: metadata.tools does not name Syft; this import reads Syft's SBOMs "
            "(the mapping was checked on Syft's output, RPT-0004 pilot.md)"
        )
    component = metadata.get("component")
    if not isinstance(component, dict):
        raise SbomImportError(f"{name}: no metadata.component, so no product")
    if component.get("type") != "container":
        raise SbomImportError(
            f"{name}: metadata.component.type is {component.get('type')!r}, not container; "
            "this import reads SBOMs of container images, whose build has a digest (R-ID-1)"
        )
    image = _text_at(component, "name", name, "metadata.component")
    if image is None:
        raise SbomImportError(f"{name}: metadata.component has no name")
    if not IMAGE_NAME.fullmatch(image):
        raise SbomImportError(f"{name}: metadata.component.name is {image!r}, not an image name")
    digest = component.get("version")
    if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
        raise SbomImportError(
            f"{name}: metadata.component.version is {digest!r}, not the image's digest, so "
            "the scanned build has no key (R-ID-1). Name the image by digest, as in "
            "`syft IMAGE@sha256:...`"
        )
    named = image.split("@", 1)[1] if "@" in image else None
    if named is not None and named != digest:
        raise SbomImportError(
            f"{name}: metadata.component.name names the digest {named}, but "
            f"metadata.component.version is {digest}; the import cannot tell which build "
            "the SBOM describes (R-ID-1)"
        )
    purl = _text_at(component, "purl", name, "metadata.component")
    if purl is not None:
        _check_image_purl(purl, image, digest, name)
    raw_time = metadata.get("timestamp")
    timestamp = _utc(raw_time)
    if raw_time is not None and timestamp is None:
        raise SbomImportError(
            f"{name}: metadata.timestamp is {raw_time!r}, not a date and time with a time zone"
        )
    _list_at(doc, "components", name, "")
    _list_at(doc, "dependencies", name, "")
    return SbomInfo(
        serial=_text_at(doc, "serialNumber", name, ""),
        timestamp=timestamp,
        tool=tool,
        image=image,
        digest=digest,
        bom_ref=_text_at(component, "bom-ref", name, "metadata.component"),
        purl=purl,
    )


def _sbom_tool(tools: Any, name: str) -> str | None:
    """'syft 1.52.0' when metadata.tools names Syft (CycloneDX 1.5+ or the older list)."""
    if isinstance(tools, dict):
        entries = _list_at(tools, "components", name, "metadata.tools")
        where = "metadata.tools.components"
    elif isinstance(tools, list) or tools is None:
        entries, where = tools or [], "metadata.tools"
    else:
        raise SbomImportError(f"{name}: metadata.tools is not an object or a list")
    for index, entry in enumerate(entries):
        at = f"{where}[{index}]"
        if not isinstance(entry, dict):
            raise SbomImportError(f"{name}: {at} is not an object")
        tool = _text_at(entry, "name", name, at)
        if tool is not None and tool.lower() == "syft":
            version = _text_at(entry, "version", name, at)
            return f"syft {version}" if version else "syft"
    return None


def _check_image_purl(purl: str, image: str, digest: str, name: str) -> None:
    """The image's own purl, when Syft writes one, must name the same image and build."""
    parsed = _parse_purl(purl)
    if parsed is None or parsed.type != "oci":
        raise SbomImportError(
            f"{name}: metadata.component.purl is {purl!r}, not an OCI package URL"
        )
    if parsed.version is not None and parsed.version != digest:
        raise SbomImportError(
            f"{name}: metadata.component.purl names the digest {parsed.version}, but "
            f"metadata.component.version is {digest} (R-ID-1)"
        )
    url = dict(parsed.qualifiers).get("repository_url")
    if url is not None and _image_repository(url.split("://", 1)[-1]) != _image_repository(image):
        raise SbomImportError(
            f"{name}: metadata.component.purl names the repository {url}, but "
            f"metadata.component.name is {image} (R-ID-2)"
        )


def _check_scan(doc: Mapping[str, Any], name: str, sbom: SbomInfo) -> ScanInfo:
    descriptor = doc.get("descriptor")
    if not isinstance(descriptor, dict) or str(descriptor.get("name", "")).lower() != "grype":
        raise SbomImportError(f"{name}: not Grype's JSON output (descriptor.name is not grype)")
    if not isinstance(doc.get("matches"), list):
        raise SbomImportError(f"{name}: no matches list")
    version = _text_at(descriptor, "version", name, "descriptor")
    if version is None:
        raise SbomImportError(
            f"{name}: descriptor.version is missing, so the Assertions could not say which "
            "Grype made them (R-PROV-2)"
        )
    if not GRYPE_VERSION.fullmatch(version):
        raise SbomImportError(
            f"{name}: descriptor.version is {version!r}, not a Grype release version, so the "
            "Assertions could not say which Grype made them (R-PROV-2)"
        )
    timestamp = _utc(descriptor.get("timestamp"))
    if timestamp is None:
        raise SbomImportError(f"{name}: descriptor.timestamp is missing or not a date and time")
    schema, built = _scan_database(descriptor, name, timestamp)
    source = doc["source"] if isinstance(doc.get("source"), dict) else {}
    target = source["target"] if isinstance(source.get("target"), dict) else {}
    scanned = target.get("manifestDigest")
    if not isinstance(scanned, str) or not DIGEST.fullmatch(scanned):
        raise SbomImportError(
            f"{name}: the scan does not name the image digest it scanned, so it cannot be "
            "matched to this SBOM"
        )
    if scanned != sbom.digest:
        raise SbomImportError(
            f"{name}: the scan is of {scanned}, but the SBOM is of {sbom.digest}; give the "
            "scan of this SBOM (grype sbom:FILE -o json)"
        )
    # The digest alone may be an index digest that every platform shares (R-ID-1), so
    # what else the scan says about its image must agree with the SBOM too.
    kind = _text_at(source, "type", name, "source")
    if kind != "image":
        raise SbomImportError(
            f"{name}: the scan's source is {kind!r}, not an image, so it is not a scan of "
            "this SBOM's image"
        )
    image = _text_at(target, "userInput", name, "source.target")
    if image is not None and _names_another_image(image, sbom.image):
        raise SbomImportError(
            f"{name}: the scan names the image {image!r}, but the SBOM is of {sbom.image}; "
            "give the scan of this SBOM (grype sbom:FILE -o json)"
        )
    image_id = _text_at(target, "imageID", name, "source.target")
    if (
        image_id is not None
        and not DIGEST.fullmatch(image_id)
        and sbom.bom_ref is not None
        and image_id != sbom.bom_ref
    ):
        # Read from an SBOM, Grype records the SBOM's root bom-ref as the image id; read
        # from the image itself, it records the configuration digest (RPT-0004 Table 6a).
        raise SbomImportError(
            f"{name}: the scan was made from another SBOM of this digest: its image id is "
            f"{image_id!r}, and this SBOM's root bom-ref is {sbom.bom_ref!r}, so the two may "
            "describe different platforms (R-ID-1)"
        )
    return ScanInfo(
        tool=f"Grype {version}",
        timestamp=timestamp,
        db_schema=schema,
        db_built=built,
        image=image,
        image_id=image_id,
        also=_scan_target_extras(target, name),
        distro=_scan_distro(doc.get("distro"), name),
        platform=_scan_platform(target, name),
    )


def parse_platform(text: str) -> Platform:
    """`--platform OS/ARCH[/VARIANT]`, as `docker --platform` takes it, in any case."""
    parts = text.strip().lower().split("/")
    if len(parts) not in (2, 3) or not all(_platform_part(part) for part in parts):
        raise SbomImportError(
            f"--platform is {text!r}, not OS/ARCH or OS/ARCH/VARIANT (for example "
            f"{PLATFORM_EXAMPLE})"
        )
    _check_architecture_name(parts[1], "--platform")
    return Platform(*parts)


def _platform_part(text: str) -> bool:
    return len(text) <= 20 and PLATFORM_PART.fullmatch(text) is not None


def _check_architecture_name(arch: str, where: str) -> None:
    """A platform names its architecture as an image index does (arm64), not as a
    distribution does (aarch64), which would give one build two keys."""
    oci = ARCHITECTURES.get(arch)
    if oci is not None and oci != arch:
        raise SbomImportError(
            f"{where} names the architecture {arch!r}, a distribution's name for {oci}; "
            f"give the name an image index uses, as in linux/{oci}"
        )


def _scan_platform(target: Mapping[str, Any], name: str) -> tuple[str | None, ...]:
    """The platform source.target records, part by part, each None where Grype left it
    empty, as it does when it read an SBOM rather than the image."""
    parts = []
    for part, key in PLATFORM_FIELDS:
        value = _text_at(target, key, name, "source.target")
        if value is not None:
            value = value.lower()
            if not _platform_part(value):
                raise SbomImportError(
                    f"{name}: source.target.{key} is {value!r}, not a platform's {part}"
                )
            if part == "architecture":
                _check_architecture_name(value, f"{name}: source.target.{key}")
        parts.append(value)
    return tuple(parts)


def _build_platform(
    given: Platform | None, scan: ScanInfo | None, sbom_name: str, scan_name: str | None
) -> tuple[Platform, str]:
    """The platform of the build the SBOM's digest names, and where it came from. The
    SBOM does not say whether its digest is a platform manifest's or an index's, which
    every platform of a release shares (R-ID-1), so the digest names one build only with
    a platform: `--platform`, or what a scan of the image itself records. A part both
    give must agree; a part only one gives (often the variant) is taken from it."""
    recorded = scan.platform if scan is not None else (None, None, None)
    wanted = (given.os, given.architecture, given.variant) if given else (None, None, None)
    for (part, key), mine, theirs in zip(PLATFORM_FIELDS, wanted, recorded, strict=True):
        if mine is not None and theirs is not None and mine != theirs:
            raise SbomImportError(
                f"{scan_name}: --platform gives the {part} {mine}, but the scan records "
                f"{theirs} (source.target.{key}), so they do not describe one build"
            )
    os_name, architecture, variant = (m or t for m, t in zip(wanted, recorded, strict=True))
    if os_name is None or architecture is None:
        if scan is None:
            scanned = ""
        elif any(recorded):
            scanned = "; the scan records only part of it (" + (
                "/".join(p or "?" for p in recorded) + ")"
            )
        else:
            scanned = "; the scan does not either (Grype leaves it empty when it read an SBOM)"
        raise SbomImportError(
            f"{sbom_name}: the SBOM does not record which platform its digest names (an "
            f"index's digest names every platform of a release){scanned}. Pass --platform "
            f"OS/ARCH[/VARIANT], for example --platform {PLATFORM_EXAMPLE}"
        )
    sources = [
        source
        for source, parts in (("--platform", wanted), ("the scan (source.target)", recorded))
        if any(parts)
    ]
    return Platform(os_name, architecture, variant), " and ".join(sources)


def _scan_database(
    descriptor: Mapping[str, Any], name: str, scanned: str
) -> tuple[str | None, str]:
    """The database's schema version and build time, refusing a database Grype marks
    invalid or one dated after the scan (R-PROV-2)."""
    no_time = (
        f"{name}: the scan does not record its database's build time, so its answer "
        "cannot be dated (R-PROV-2)"
    )
    db = descriptor.get("db")
    if not isinstance(db, dict):
        raise SbomImportError(no_time)
    # Grype writes db.status since its v6 database, and the same fields on db before it.
    status, where = db, "descriptor.db"
    if "status" in db:
        status, where = db["status"], "descriptor.db.status"
    if not isinstance(status, dict):
        raise SbomImportError(f"{name}: {where} is not an object")
    built = _utc(status.get("built"))
    if built is None:
        raise SbomImportError(no_time)
    if built > scanned:
        raise SbomImportError(
            f"{name}: the scan's database is dated after the scan (built {built}, scanned "
            f"{scanned}), so its dates do not hold together (R-PROV-2)"
        )
    schema = status.get("schemaVersion")
    if isinstance(schema, bool) or not isinstance(schema, str | int | None):
        raise SbomImportError(f"{name}: {where}.schemaVersion is {schema!r}, not a schema version")
    valid = status.get("valid")
    if valid is not None and not isinstance(valid, bool):
        raise SbomImportError(f"{name}: {where}.valid is {valid!r}, not true or false")
    if valid is False:
        raise SbomImportError(
            f"{name}: {where}.valid is false: Grype marks its vulnerability database invalid, "
            "so its matches are no evidence (R-PROV-2)"
        )
    error = _text_at(status, "error", name, where)
    if error is not None:
        raise SbomImportError(
            f"{name}: {where}.error says the vulnerability database did not load ({error!r})"
        )
    return (None if schema is None else (str(schema).strip() or None)), built


def _names_another_image(user_input: str, image: str) -> bool:
    """Whether the image Grype was given names another repository than the SBOM's. A file
    or a folder (`sbom:FILE`, `dir:PATH`) names none, so it is not compared."""
    if PATH_SCHEME.match(user_input):
        return False
    scheme = IMAGE_SCHEME.match(user_input)
    given = user_input[scheme.end() :] if scheme else user_input
    return _image_repository(given) != _image_repository(image)


def _scan_target_extras(target: Mapping[str, Any], name: str) -> tuple[str, ...]:
    """What else source.target records about the image: kept for the report."""
    where = "source.target"
    also = []
    for key, label in (("tags", "tags"), ("repoDigests", "repository digests")):
        values = []
        for index, value in enumerate(_list_at(target, key, name, where)):
            if not isinstance(value, str):
                raise SbomImportError(f"{name}: {where}.{key}[{index}] is not text")
            values.append(value)
        if values:
            also.append(f"{label} {', '.join(values)}")
    return tuple(also)  # the platform has a report line of its own (_Report.text)


def _scan_distro(distro: Any, name: str) -> str | None:
    if distro is None:
        return None
    if not isinstance(distro, dict):
        raise SbomImportError(f"{name}: distro is not an object")
    parts = [_text_at(distro, key, name, "distro") for key in ("name", "version")]
    return " ".join(p for p in parts if p) or None


def _text_at(obj: Mapping[str, Any], key: str, name: str, where: str) -> str | None:
    """obj[key] as text without surrounding space; None when absent, null or blank, and
    an error naming the field when it is there but not text."""
    value = obj.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise SbomImportError(f"{name}: {_at(where, key)} is not text")
    return value.strip() or None


def _list_at(obj: Mapping[str, Any], key: str, name: str, where: str) -> list[Any]:
    value = obj.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise SbomImportError(f"{name}: {_at(where, key)} is not a list")
    return value


def _object_at(obj: Mapping[str, Any], key: str, name: str, where: str) -> dict[str, Any] | None:
    value = obj.get(key)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise SbomImportError(f"{name}: {_at(where, key)} is not an object")
    return value


def _at(where: str, key: str) -> str:
    return f"{where}.{key}" if where else key


# Building the model ---------------------------------------------------------------


@dataclass(frozen=True)
class _Entry:
    """One SBOM entry other than a file, as read and checked."""

    where: str
    key: str
    name: str
    version: str | None
    kind: str
    readable: str
    base: str | None
    description: str | None
    identifiers: tuple[str, ...]
    supplier: str | None
    manufacturer: str | None
    arch: str | None = None  # its purl's arch qualifier, which is part of its key


@dataclass
class _Component:
    key: str
    entry_name: str
    version: str | None
    kind: str
    readable: str  # what its id is made from
    base: str | None  # its purl without qualifiers or subpath, to name near misses
    arch: str | None = None  # the CPU its purl says it is built for
    id: str = ""
    description: str | None = None
    identifiers: list[str] = field(default_factory=list)
    supplier: str | None = None
    manufacturer: str | None = None
    entries: int = 1
    uses: set[str] = field(default_factory=set)

    @property
    def name(self) -> str:
        return f"{self.entry_name} {self.version}" if self.version else self.entry_name


@dataclass
class _Vulnerability:
    ref: str
    id: str
    aliases: set[str] = field(default_factory=set)
    description: str | None = None


@dataclass(frozen=True)
class _Record:
    """A vulnerability record of a match: its own, or one in relatedVulnerabilities."""

    id: str
    namespace: str | None
    description: str | None
    cwes: tuple[tuple[str | None, str | None, str | None, str | None], ...]


@dataclass(frozen=True)
class _Detail:
    type: str | None
    matcher: str | None
    namespace: str | None
    constraint: str | None


@dataclass(frozen=True)
class _Row:
    """One of the scan's matches, as read and checked."""

    vid: str
    records: tuple[_Record, ...]
    cves: tuple[str, ...]  # the CVEs it names, sorted
    others: tuple[str, ...]  # its other ids, each once, in order
    repeated_ids: int  # ids it names more than once
    purl: str | None
    name: str | None
    version: str | None
    details: tuple[_Detail, ...]
    fingerprint: str  # the SHA-256 of the match as canonical JSON


@dataclass(frozen=True)
class _Match:
    """One proposed propagates_to Assertion: a match, and one Vulnerability it names."""

    ref: str
    component: str
    row: _Row


class _Builder:
    def __init__(
        self,
        sbom_file: InputFile,
        sbom: Mapping[str, Any],
        info: SbomInfo,
        scan_file: InputFile | None,
        scan: Mapping[str, Any] | None,
        scan_info: ScanInfo | None,
        platform: Platform,
        platform_source: str,
    ) -> None:
        self.sbom_file = sbom_file
        self.sbom = sbom
        self.info = info
        self.scan_file = scan_file
        self.scan = scan
        self.scan_info = scan_info
        self.platform = platform
        self.platform_source = platform_source  # "--platform", the scan, or both
        self.ids: dict[str, str] = {}  # object id -> the key it was made from
        self.notes: Counter[str] = Counter()  # what was left out, by reason
        self.repeats: Counter[str] = Counter()  # what the inputs repeat, written once
        self.listed: dict[str, list[str]] = {}  # report lists, by heading
        self.types: Counter[str] = Counter()  # SBOM component entries, by CycloneDX type
        # Components by the architecture their purl names: (OCI name, purl's name) -> n.
        self.architectures: Counter[tuple[str, str]] = Counter()
        # Descriptions in the scan that are not written, by field path and reason.
        self.words: dict[str, Counter[str]] = {path: Counter() for path in DESCRIPTION_PATHS}
        self.words_written: Counter[str] = Counter()  # and those that are, by path
        self.components: dict[str, _Component] = {}
        self.by_ref: dict[str, str] = {}  # bom-ref -> component key
        self.systems: list[str] = []  # the SBOM's operating systems, as "name version"
        self.parties: dict[str, dict[str, Any]] = {}
        self.vulnerabilities: dict[str, _Vulnerability] = {}
        self.weaknesses: dict[str, str] = {}  # CWE id -> object id
        self.matches: list[_Match] = []
        self.cwe_links: dict[tuple[str, str, str], set[str]] = {}
        self.edges = 0
        self.scan_parts: set[str] = set()
        if scan is not None:
            # Reserved first, so no supplier or CWE source can take the scanner's id.
            self.ids[GRYPE_PARTY] = "software_agent:grype"
            self.parties[GRYPE_PARTY] = {
                "_key": "software_agent:grype",
                "_roles": {"scanner"},
                "name": "Grype",
            }
        self._product()
        self._components()
        self._dependencies()
        if scan is not None:
            self._matches()

    # ids

    def _id(self, prefix: str, key: str, readable: str, limit: int = 80) -> str:
        """A stable id from `readable`; the same key always gets the same id."""
        slug = _slug(readable, limit=limit)
        candidate = f"{prefix}:{slug}"
        owner = self.ids.get(candidate)
        if owner is not None and owner != key:
            candidate = f"{prefix}:{_slug(slug, limit=limit - 10)}-{_short_hash(key)}"
        self.ids[candidate] = key
        return candidate

    # the product and the scanned build

    def _product(self) -> None:
        registry, repository = _image_repository(self.info.image)
        self.repository_url = f"{registry}/{repository}"
        purl_name = repository.rsplit("/", 1)[-1].lower()
        url = quote(self.repository_url, safe="/:")
        self.product_purl = f"pkg:oci/{purl_name}?repository_url={url}"
        digest = quote(self.info.digest, safe="")
        arch = quote(self.platform.architecture, safe="")
        # The oci purl type's arch qualifier, and the qualifiers sorted by key.
        self.instance_purl = f"pkg:oci/{purl_name}@{digest}?arch={arch}&repository_url={url}"
        # Each id is made from its key, whole: the repository with its registry (R-ID-2),
        # and the digest with the platform (R-ID-1), since an index digest names every
        # platform of a release and the SBOM does not say which kind it holds. So another
        # registry, path or platform gives another id. An id is a readable slug; the purl
        # in identifiers stays the key. A platform's parts are short (_platform_part), so
        # the build's id keeps the whole digest and platform.
        self.product_id = self._id("product", self.product_purl, self.repository_url)
        self.instance_key = f"{self.info.digest} {self.platform}"
        self.instance_id = self._id(
            "product-instance", self.instance_key, self.instance_key, limit=160
        )

    # components

    def _components(self) -> None:
        name = _one_line(self.sbom_file.name)
        seen_refs: set[str] = set()
        entries: dict[str, list[_Entry]] = {}
        for where, entry in _flatten(self.sbom.get("components") or [], name, "components"):
            kind = entry.get("type")
            if not isinstance(kind, str) or kind not in COMPONENT_KINDS:
                raise SbomImportError(
                    f"{name}: {where}.type is {kind!r}, not one of CycloneDX 1.7's component types"
                )
            self.types[kind] += 1
            ref = _text_at(entry, "bom-ref", name, where)
            if ref is not None:
                if ref in seen_refs:
                    raise SbomImportError(f"{name}: bom-ref {ref!r} appears twice")
                seen_refs.add(ref)
            if kind == "file":
                self.notes["SBOM file entries (R-ID-4: content identity is post-MVP)"] += 1
                continue
            read = self._entry(entry, kind, name, where)
            entries.setdefault(read.key, []).append(read)
            if ref is not None:
                self.by_ref[ref] = read.key
            if kind == "operating-system":
                self.systems.append(" ".join(p for p in (read.name, read.version) if p))
        for key in sorted(entries):
            self.components[key] = self._component(entries[key], name)
        self._check_architectures(name)
        for component in self.components.values():  # in key order
            component.id = self._id("component", component.key, component.readable)
        named = {(c.supplier, "supplier") for c in self.components.values() if c.supplier}
        named |= {
            (c.manufacturer, "manufacturer") for c in self.components.values() if c.manufacturer
        }
        for party, role in sorted(named):
            self._party(party, role)

    def _entry(self, entry: Mapping[str, Any], kind: str, name: str, where: str) -> _Entry:
        label = _text_at(entry, "name", name, where)
        if label is None:
            raise SbomImportError(f"{name}: {where} (a {kind} component) has no name")
        version = _text_at(entry, "version", name, where)
        purl = _text_at(entry, "purl", name, where)
        identifiers = self._identifiers(entry, name, where)
        parsed = _parse_purl(purl) if purl is not None else None
        if parsed is not None:
            key, readable, base = parsed.key, parsed.readable, parsed.base
            if version and parsed.version and not _same_version(version, parsed):
                self.listed.setdefault(VERSION_APART, []).append(
                    f"{label}: version {version}, but its purl says {parsed.version}"
                )
        else:
            key = f"{kind}/{label}" + (f"@{version}" if version else "")
            readable, base = key, None
            if purl is not None:
                self.notes["SBOM purls that do not parse (kept in identifiers)"] += 1
        return _Entry(
            where=where,
            key=key,
            name=label,
            version=version,
            kind=kind,
            readable=readable,
            base=base,
            description=_prose(_text_at(entry, "description", name, where)),
            identifiers=tuple(identifiers),
            supplier=self._organization(entry, "supplier", name, where),
            manufacturer=self._organization(entry, "manufacturer", name, where),
            arch=dict(parsed.qualifiers).get("arch") if parsed is not None else None,
        )

    def _component(self, entries: list[_Entry], name: str) -> _Component:
        """One Component from the entries that share a key. They must agree on what the
        Component is: every name, type and version any of them gives, all against all,
        so an entry that gives none cannot hide two that differ. The Component takes the
        one value they give. Where they disagree on a description or a party, it is left
        out and listed, so no value is picked silently."""
        first = entries[0]
        for label, slot in (("names", "name"), ("types", "kind"), ("versions", "version")):
            given: dict[str, _Entry] = {}  # each value given, and the first entry to give it
            for entry in entries:
                value = getattr(entry, slot)
                if value is not None:
                    given.setdefault(value, entry)
            if len(given) > 1:
                (mine, one), (theirs, other) = list(given.items())[:2]
                raise SbomImportError(
                    f"{name}: {one.where} and {other.where} have the same purl, "
                    f"{first.key}, but give different {label} ({mine!r} and {theirs!r}); "
                    "the import cannot tell which package is meant (R-ID-3)"
                )
        component = _Component(
            key=first.key,
            entry_name=first.name,
            version=next((e.version for e in entries if e.version is not None), None),
            kind=COMPONENT_KINDS[first.kind],
            readable=first.readable,
            base=first.base,
            arch=first.arch,
            entries=len(entries),
        )
        for slot, label in (
            ("description", "descriptions"),
            ("supplier", "suppliers"),
            ("manufacturer", "manufacturers"),
        ):
            values = sorted({getattr(e, slot) for e in entries if getattr(e, slot)})
            if len(values) == 1:
                setattr(component, slot, values[0])
            elif values:
                self.listed.setdefault(MERGED_APART, []).append(
                    f"{first.key}: {len(values)} different {label}"
                )
        for entry in entries:
            for identifier in entry.identifiers:
                if identifier not in component.identifiers:
                    component.identifiers.append(identifier)
                else:
                    self.repeats["identifiers that entries recorded as one Component share"] += 1
        if len(entries) > 1:
            self.listed.setdefault(MERGED, []).append(
                f"{first.key} ({first.name}): {len(entries)} entries"
            )
        return component

    def _identifiers(self, entry: Mapping[str, Any], name: str, where: str) -> list[str]:
        """The entry's purl and CPEs, as written: purl, then `cpe`, then Syft's syft:cpe23."""
        values = [_text_at(entry, "purl", name, where), _text_at(entry, "cpe", name, where)]
        for index, prop in enumerate(_list_at(entry, "properties", name, where)):
            at = f"{where}.properties[{index}]"
            if not isinstance(prop, dict):
                raise SbomImportError(f"{name}: {at} is not an object")
            if _text_at(prop, "name", name, at) == "syft:cpe23":
                values.append(_text_at(prop, "value", name, at))
            else:
                self.notes["SBOM component properties other than syft:cpe23 (no slot)"] += 1
        out: list[str] = []
        for value in values:
            if value is None:
                continue
            if value in out:
                self.repeats["identifiers an SBOM entry repeats (written once)"] += 1
            else:
                out.append(value)
        return out

    def _organization(
        self, entry: Mapping[str, Any], key: str, name: str, where: str
    ) -> str | None:
        value = _object_at(entry, key, name, where)
        if value is None:
            return None
        party = _text_at(value, "name", name, f"{where}.{key}")
        if party is None:
            self.notes[f"SBOM {key}s with no name (no Party can be made)"] += 1
        return party

    def _party(self, name: str, role: str) -> str:
        key = f"organization:{name}"
        for party_id, party in self.parties.items():
            if party["_key"] == key:
                party["_roles"].add(role)
                return party_id
        party_id = self._id("party", key, name)
        self.parties[party_id] = {"_key": key, "_roles": {role}, "name": name}
        return party_id

    def _party_id(self, name: str) -> str:
        key = f"organization:{name}"
        return next(pid for pid, party in self.parties.items() if party["_key"] == key)

    # the platform, checked against the SBOM

    def _check_architectures(self, name: str) -> None:
        """The SBOM's own record of its CPU must fit the platform (R-ID-1): the image's
        purl, when it has an arch, names the platform's architecture, and each package's
        arch qualifier, read through ARCHITECTURES, names it too, or the 32-bit sibling a
        64-bit platform also runs, with some package built for the platform's own. A name
        not in the table is listed, not checked; noarch, all and any are skipped."""
        platform = self.platform.architecture
        given = f"the platform is {self.platform} (from {self.platform_source})"
        image = _parse_purl(self.info.purl) if self.info.purl is not None else None
        image_arch = dict(image.qualifiers).get("arch") if image is not None else None
        # An oci purl names its arch as an image index does, so a name not in the table
        # is compared as it is.
        if image_arch is not None and ARCHITECTURES.get(image_arch.lower(), image_arch) != platform:
            raise SbomImportError(
                f"{name}: metadata.component.purl says arch={image_arch}, but {given}"
            )
        names: dict[str, set[str]] = {}  # OCI architecture -> the names packages give it
        unknown: Counter[str] = Counter()
        for component in self.components.values():
            arch = component.arch
            if arch is None or arch.lower() in NO_ARCHITECTURE:
                continue
            oci = ARCHITECTURES.get(arch.lower())
            if oci is None:
                unknown[arch] += 1
                continue
            names.setdefault(oci, set()).add(arch)
            self.architectures[oci, arch] += 1
        foreign = sorted(set(names) - {platform, ALSO_RUNS.get(platform)})
        if foreign:
            oci = foreign[0]
            raise SbomImportError(
                f"{name}: the SBOM's packages are built for {oci} "
                f"(arch={', '.join(sorted(names[oci]))}), but {given}; the SBOM is not of "
                "that build"
            )
        if names and platform not in names:
            said = ", ".join(sorted(arch for found in names.values() for arch in found))
            raise SbomImportError(
                f"{name}: none of the SBOM's packages is built for {platform}, though {given}; "
                f"they say arch={said}"
            )
        for arch, n in sorted(unknown.items()):
            self.listed.setdefault(UNCHECKED_ARCH, []).append(
                f"{_one_line(arch)}: {n} Component{'' if n == 1 else 's'}"
            )

    # dependencies

    def _dependencies(self) -> None:
        name = _one_line(self.sbom_file.name)
        seen: set[str] = set()
        for index, entry in enumerate(self.sbom.get("dependencies") or []):
            where = f"dependencies[{index}]"
            if not isinstance(entry, dict):
                raise SbomImportError(f"{name}: {where} is not an object")
            ref = _text_at(entry, "ref", name, where)
            if ref is None:
                raise SbomImportError(f"{name}: {where} has no ref")
            if ref in seen:
                self.repeats["dependencies entries for a ref listed before (read too)"] += 1
            seen.add(ref)
            for number, target in enumerate(_list_at(entry, "dependsOn", name, where)):
                if not isinstance(target, str) or not target.strip():
                    raise SbomImportError(f"{name}: {where}.dependsOn[{number}] is not text")
                target = target.strip()
                if ref == self.info.bom_ref:
                    self.notes[
                        "dependency edges from the image itself (its parts are build_composed_of)"
                    ] += 1
                    continue
                source, dependency = self.by_ref.get(ref), self.by_ref.get(target)
                if source is None or dependency is None:
                    self.notes["dependency edges to or from an entry that is not a Component"] += 1
                    continue
                if source == dependency:
                    self.notes["dependency edges from a Component to itself"] += 1
                    continue
                if dependency in self.components[source].uses:
                    self.repeats["dependency edges that repeat one already written"] += 1
                    continue
                self.components[source].uses.add(dependency)
                self.edges += 1

    # the scan

    def _matches(self) -> None:
        assert self.scan is not None and self.scan_file is not None
        name = _one_line(self.scan_file.name)
        parsed: list[_Row] = []  # every match, repeats too, to account for each description
        rows: list[_Row] = []
        fingerprints: set[str] = set()
        for index, raw in enumerate(self.scan["matches"]):
            row = _row(raw, index, name)
            parsed.append(row)
            if row.fingerprint in fingerprints:
                self.repeats["matches that repeat an earlier match exactly"] += 1
                continue
            fingerprints.add(row.fingerprint)
            if row.repeated_ids:
                reason = "ids a match names more than once (one Vulnerability each)"
                self.repeats[reason] += row.repeated_ids
            rows.append(row)
        # The CVEs each other id is paired with across the whole scan, so an advisory
        # paired with two CVEs in two matches is no one's alias (#257).
        cves_of: dict[str, set[str]] = {}
        for row in rows:
            for other in row.others:
                cves_of.setdefault(other, set()).update(row.cves)
        kept: list[tuple[_Row, str, tuple[str, ...]]] = []
        for row in rows:
            key = self._join(row)
            if key is not None:
                kept.append((row, key, row.cves or _refs(row, cves_of)))
        for ref in sorted({ref for _, _, refs in kept for ref in refs}):
            self.vulnerabilities[ref] = _Vulnerability(ref, self._id("vulnerability", ref, ref))
        self._aliases(kept, cves_of)
        self._descriptions(kept)
        self._account_for_descriptions(parsed, {row.fingerprint: refs for row, _, refs in kept})
        for row, key, refs in kept:
            self.scan_parts.add(key)
            self.matches.extend(_Match(ref, key, row) for ref in refs)
            for detail in row.details:
                if detail.type is not None and detail.type not in MATCH_CONFIDENCE:
                    self.notes[
                        f"match details of a type this import does not rank "
                        f"({_one_line(detail.type)}; no confidence from it)"
                    ] += 1
        # Only now, with every Vulnerability known, the CWE entries: so none is left out
        # because the match that makes its CVE a Vulnerability comes later (R-CWE-1).
        for row, _, _ in kept:
            for record in row.records:
                for cve, cwe, source, kind in record.cwes:
                    self._cwe(cve, cwe, source, kind)
        for source in sorted({source for _, _, source in self.cwe_links} - {UNNAMED_SOURCE}):
            self._party(source, "cwe source")
        for cwe in sorted({cwe for _, cwe, _ in self.cwe_links}):
            self.weaknesses[cwe] = self._id("weakness", cwe, cwe)

    def _join(self, row: _Row) -> str | None:
        """The Component the match is on: the one with the same normalized purl (R-MATCH-2)
        and the same name and version. Any other match is left out whole and listed, so
        no Vulnerability is left unlinked and none lands on another build."""
        parsed = _parse_purl(row.purl) if row.purl is not None else None
        component = self.components.get(parsed.key) if parsed is not None else None
        if component is None:
            package = " ".join(p for p in (row.name, row.version) if p) or "an unnamed package"
            item = f"{row.vid} on {package} ({row.purl or 'no purl'})"
            near = sorted(
                c.key for c in self.components.values() if parsed and c.base == parsed.base
            )
            if near:
                item += f"; the SBOM has it only as {', '.join(near)}"
            self.notes["matches on a part that is not a Component of this SBOM"] += 1
            self.listed.setdefault(UNJOINED, []).append(item)
            return None
        if (row.name is not None and row.name != component.entry_name) or (
            row.version is not None and row.version != component.version
        ):
            self.notes["matches whose package the SBOM names differently"] += 1
            self.listed.setdefault(DISAGREE, []).append(
                f"{row.vid} on {row.purl}: the scan says {row.name} {row.version}, the SBOM "
                f"says {component.entry_name} {component.version}"
            )
            return None
        return component.key

    def _aliases(
        self, kept: list[tuple[_Row, str, tuple[str, ...]]], cves_of: Mapping[str, set[str]]
    ) -> None:
        """An id is an alias only of the one Vulnerability the whole scan pairs it with,
        and only when it is not a Vulnerability itself (#257, A6)."""
        named: dict[str, set[str]] = {}
        for row, _, refs in kept:
            for other in row.others:
                if other not in refs:
                    named.setdefault(other, set()).update(cves_of.get(other) or refs)
        for other, targets in sorted(named.items()):
            target = next(iter(targets)) if len(targets) == 1 else None
            if target in self.vulnerabilities and other not in self.vulnerabilities:
                self.vulnerabilities[target].aliases.add(other)
            else:
                self.listed.setdefault(NO_ALIAS, []).append(
                    f"{other}: {', '.join(sorted(targets))}"
                )

    def _descriptions(self, kept: list[tuple[_Row, str, tuple[str, ...]]]) -> None:
        """Each Vulnerability's description, from a record with its own id. When records
        differ, the one whose namespace sorts first is written, whatever the match order."""
        found: dict[str, set[tuple[str, str]]] = {}
        for row, _, refs in kept:
            for record in row.records:
                if record.id in refs and record.description is not None:
                    found.setdefault(record.id, set()).add(
                        (record.namespace or "", record.description)
                    )
        for ref, options in found.items():
            namespace, text = min(options)
            self.vulnerabilities[ref].description = text
            texts = {t for _, t in options}
            if len(texts) > 1:
                others = sorted({ns or "no namespace" for ns, t in options if t != text})
                left = ", ".join(f"{other}'s" for other in others)
                self.listed.setdefault(DESCRIBED, []).append(
                    f"{ref}: {len(texts)} descriptions; written: "
                    f"{namespace or 'no namespace'}'s; left out: {left}"
                )

    def _account_for_descriptions(
        self, rows: list[_Row], refs_of: Mapping[str, tuple[str, ...]]
    ) -> None:
        """What became of each description in the scan, by its field, so the report never
        says one was written that was not. A description is written only on its own
        record's Vulnerability, and only the one picked for it (`_descriptions`); the rest
        are left out, each listed: an advisory's whose match is written as another id
        (most often a CVE), one in other words than the one written, or one whose match
        is left out whole."""
        for row in rows:
            refs = refs_of.get(row.fingerprint)  # None when the match is left out
            for number, record in enumerate(row.records):
                if record.description is None:
                    continue
                path = DESCRIPTION_PATHS[min(number, 1)]  # its own record, or a related one
                if refs is None:
                    self.words[path][WORDS_MATCH] += 1
                elif record.id not in refs:
                    self.words[path][WORDS_ADVISORY] += 1
                    item = f"{record.id}: its match is written as {', '.join(refs)}"
                    aliased = [r for r in refs if record.id in self.vulnerabilities[r].aliases]
                    if aliased:
                        item += f", and {record.id} as an alias of {aliased[0]}"
                    self.listed.setdefault(ADVISORY_WORDS, []).append(item)
                elif record.description != self.vulnerabilities[record.id].description:
                    self.words[path][WORDS_OTHER] += 1
                else:
                    self.words_written[path] += 1

    def _cwe(self, cve: str | None, cwe: str | None, source: str | None, kind: str | None) -> None:
        if cve is None or cve not in self.vulnerabilities:
            self.notes["CWE entries for an id that is not a Vulnerability here"] += 1
            return
        if cwe is None:
            self.notes["CWE entries that name no CWE"] += 1
            return
        if not CWE_ID.fullmatch(cwe):
            shown = _one_line(cwe)
            self.notes[f"CWE placeholders such as {shown} (no weakness named; Table 6d)"] += 1
            return
        link = (cve, cwe, source or UNNAMED_SOURCE)
        if link in self.cwe_links:
            self.repeats["CWE entries that repeat a link already written"] += 1
        kinds = self.cwe_links.setdefault(link, set())
        if kind is not None:
            kinds.add(kind)

    # the model

    def model(self) -> dict[str, Any]:
        doc: dict[str, Any] = {}
        parties = self._party_objects()
        if parties:
            doc["parties"] = parties
        doc["products"] = [
            {
                "id": self.product_id,
                "name": self.info.image,
                "description": (
                    "The container image the SBOM describes, keyed by its versionless "
                    "package URL (R-ID-2)."
                ),
                "identifiers": [self.product_purl],
            }
        ]
        identifiers = [self.info.digest, self.instance_purl]
        if self.info.purl is not None and self.info.purl not in identifiers:
            identifiers.append(self.info.purl)
        doc["product_instances"] = [
            {
                "id": self.instance_id,
                "name": f"{self.info.image} at {self.info.digest[:19]} for {self.platform}",
                "description": (
                    "The scanned build, keyed by the digest the SBOM records and the "
                    f"platform, {self.platform} (from {self.platform_source}): the SBOM "
                    "does not say whether its digest is a platform manifest's or an "
                    "index's, which every platform of a release shares (R-ID-1). SBOM "
                    f"made by {self.info.tool}"
                    + (f" at {self.info.timestamp}" if self.info.timestamp else "")
                    + "."
                ),
                "of_product": self.product_id,
                "version": self.info.digest,
                "identifiers": identifiers,
                "build_composed_of": sorted(c.id for c in self.components.values()),
            }
        ]
        doc["components"] = [self._component_object(c) for c in self._sorted_components()]
        if self.scan is not None:
            if self.weaknesses:
                doc["weaknesses"] = [
                    {"id": wid, "name": cwe, "catalog_ref": cwe}
                    for cwe, wid in sorted(self.weaknesses.items(), key=lambda kv: kv[1])
                ]
            if self.vulnerabilities:
                doc["vulnerabilities"] = [
                    self._vulnerability_object(v)
                    for v in sorted(self.vulnerabilities.values(), key=lambda v: v.id)
                ]
            assertions = self._match_assertions() + self._cwe_assertions()
            if assertions:
                doc["assertions"] = sorted(assertions, key=lambda a: a["id"])
        return doc

    def _sorted_components(self) -> list[_Component]:
        return sorted(self.components.values(), key=lambda c: c.id)

    def _party_objects(self) -> list[dict[str, Any]]:
        objects = []
        for party_id, party in sorted(self.parties.items()):
            roles = party["_roles"]
            obj: dict[str, Any] = {"id": party_id, "name": party["name"]}
            if party_id == GRYPE_PARTY:
                obj["description"] = (
                    "Anchore's vulnerability scanner. It matched the SBOM's packages to "
                    f"known vulnerabilities ({self.scan_info.tool if self.scan_info else 'Grype'})."
                )
                obj["party_kind"] = "software_agent"
            else:
                said = []
                if roles & {"supplier", "manufacturer"}:
                    said.append(
                        "named as "
                        + " and ".join(
                            sorted(r for r in roles if r in {"supplier", "manufacturer"})
                        )
                        + " in the SBOM"
                    )
                if "cwe source" in roles:
                    said.append("assigned CWEs to CVEs, as the scan's database records")
                text = ", and ".join(said) or "named in the inputs"
                obj["description"] = text[:1].upper() + text[1:] + "."
                obj["party_kind"] = "organization"
            objects.append(obj)
        return objects

    def _component_object(self, component: _Component) -> dict[str, Any]:
        obj: dict[str, Any] = {"id": component.id, "name": component.name}
        if component.description:
            obj["description"] = component.description
        obj["component_kind"] = component.kind
        if component.version is not None:
            obj["version"] = component.version
        if component.identifiers:
            obj["identifiers"] = list(component.identifiers)
        if component.supplier is not None:
            obj["supplied_by"] = self._party_id(component.supplier)
        if component.manufacturer is not None:
            obj["manufactured_by"] = self._party_id(component.manufacturer)
        if component.uses:
            obj["uses_component"] = sorted(self.components[k].id for k in component.uses)
        return obj

    def _vulnerability_object(self, vulnerability: _Vulnerability) -> dict[str, Any]:
        obj: dict[str, Any] = {"id": vulnerability.id, "name": vulnerability.ref}
        if vulnerability.description:
            obj["description"] = vulnerability.description
        obj["catalog_ref"] = vulnerability.ref
        aliases = sorted(vulnerability.aliases - {vulnerability.ref})
        if aliases:
            obj["alias_ids"] = aliases
        return obj

    def _provenance(self, evidence: list[str]) -> dict[str, Any]:
        assert self.scan_info is not None
        return {
            "assertion_status": "proposed",
            "asserted_at": self.scan_info.timestamp,
            "generated_by": self.scan_info.generated_by,
            "evidence": evidence,
        }

    def _match_assertions(self) -> list[dict[str, Any]]:
        """One Assertion for each match and each Vulnerability it names (R-MATCH-1), so two
        findings on one Component keep their own match type, confidence and evidence."""
        assert self.scan_file is not None
        out = []
        ordered = sorted(
            self.matches,
            key=lambda m: (m.ref, self.components[m.component].id, m.row.vid, m.row.fingerprint),
        )
        for link in ordered:
            vulnerability = self.vulnerabilities[link.ref]
            component = self.components[link.component]
            row = link.row
            confidences = [
                MATCH_CONFIDENCE[d.type] for d in row.details if d.type in MATCH_CONFIDENCE
            ]
            readable = f"{link.ref}-in-{component.id.removeprefix('component:')}"
            via = ""
            if row.vid != link.ref:
                readable += f"-from-{row.vid}"
                via = f" on {row.vid}"
            obj: dict[str, Any] = {
                "id": self._id(
                    "assertion", f"match:{link.ref}:{link.component}:{row.fingerprint}", readable
                ),
                "name": f"{link.ref} is in {component.name} (Grype match{via}, proposed)",
                "description": _match_description(row),
                "subject": vulnerability.id,
                "predicate": MATCH_PREDICATE,
                "object": component.id,
            }
            if confidences:
                obj["confidence"] = max(confidences, key=CONFIDENCE_RANK.__getitem__)
            obj["asserted_by"] = GRYPE_PARTY
            obj.update(self._provenance([self.scan_file.digest, self.sbom_file.digest]))
            out.append(obj)
        return out

    def _cwe_assertions(self) -> list[dict[str, Any]]:
        assert self.scan_file is not None
        out = []
        for (cve, cwe, source), kinds in sorted(self.cwe_links.items()):
            party = None if source == UNNAMED_SOURCE else self._party_id(source)
            readable = f"{cve}-{cwe}-from-{source}"
            obj: dict[str, Any] = {
                "id": self._id("assertion", f"cwe:{cve}:{cwe}:{source}", readable),
                "name": f"{cve} is an instance of {cwe} (assigned by {source}, proposed)",
                "description": (
                    f"The scan's database records {source} assigning {cwe} to {cve}"
                    + (f" as {' and '.join(sorted(kinds))}" if kinds else "")
                    + " (R-CWE-1)."
                ),
                "subject": self.vulnerabilities[cve].id,
                "predicate": CWE_PREDICATE,
                "object": self.weaknesses[cwe],
            }
            if party is not None:
                obj["asserted_by"] = party
            obj.update(self._provenance([self.scan_file.digest]))
            out.append(obj)
        return out

    # counts and the report

    def counts(self) -> dict[str, int]:
        return {
            "components": len(self.components),
            "dependency_edges": self.edges,
            "vulnerabilities": len(self.vulnerabilities),
            "weaknesses": len(self.weaknesses),
            "match_assertions": len(self.matches),
            "cwe_assertions": len(self.cwe_links),
            "parties": len(self.parties),
        }

    def report(self, output_name: str) -> str:
        return _Report(self, output_name).text()


def _refs(row: _Row, cves_of: Mapping[str, set[str]]) -> tuple[str, ...]:
    """The Vulnerability a match naming no CVE is: the one CVE the rest of the scan pairs
    its ids with, or else the id Grype reports (#257)."""
    paired = set().union(*(cves_of.get(other, set()) for other in row.others))
    return tuple(paired) if len(paired) == 1 else (row.vid,)


# The report -----------------------------------------------------------------------

# Where each input field goes, by its path in the file: `a.b` is field b of object a, and
# `a[]` each item of list a. A field marked INSIDE is broken into the fields inside it;
# any other text is the answer for the field's whole value. A field not listed is
# reported as "left out: not read by this import", with the values it holds, so a field
# a newer Syft or Grype adds, at any depth, never disappears unnoticed.
INSIDE = "see the fields inside it"
UNREAD = "left out: not read by this import"
NO_SLOT = "left out: no slot"
PLATFORM_RULE = (
    "the platform, when not empty (Grype leaves it empty when it read an SBOM): checked "
    "against --platform; the ProductInstance's key, id, name and purl (R-ID-1)"
)

SBOM_FIELDS = {
    "$schema": "left out: the JSON schema's URL",
    "bomFormat": "checked: CycloneDX",
    "specVersion": f"checked: {CYCLONEDX_VERSION}",
    "serialNumber": "the model's header and this report (R-PROV-1: evidence, never a key)",
    "version": "left out: the BOM's revision number",
    "metadata": INSIDE,
    "metadata.timestamp": "the ProductInstance description and the model's header",
    "metadata.tools": INSIDE,
    "metadata.tools.components": INSIDE,
    "metadata.tools.components[].name": "checked: Syft",
    "metadata.tools.components[].version": (
        "Syft's: the model's header and this report (R-PROV-1); another tool's is left out"
    ),
    "metadata.tools.components[].type": "left out: the tool's kind of component",
    "metadata.tools.components[].author": "left out: the tool's maker (no slot)",
    "metadata.tools[].name": "checked: Syft (the list form before CycloneDX 1.5)",
    "metadata.tools[].version": (
        "Syft's: the model's header and this report (R-PROV-1); another tool's is left out"
    ),
    "metadata.tools[].vendor": "left out: the tool's maker (no slot)",
    "metadata.component": INSIDE,
    "metadata.component.type": "checked: container",
    "metadata.component.name": (
        "Product.name and the versionless purl in Product.identifiers (R-ID-2); a digest in "
        "it is checked against the version"
    ),
    "metadata.component.version": (
        "ProductInstance.version and identifiers; with the platform, the ProductInstance's "
        "key and id (R-ID-1)"
    ),
    "metadata.component.bom-ref": "matched against dependencies[].ref and the scan's image id",
    "metadata.component.purl": (
        "checked against the name and the digest; ProductInstance.identifiers"
    ),
    "components": INSIDE,
    "components[].type": "Component.component_kind (A3); file entries are left out (R-ID-4)",
    "components[].name": "Component.name",
    "components[].version": "Component.version and the name, checked against the purl's version",
    "components[].purl": (
        "Component.identifiers, and the Component's key: the purl, normalized, with its "
        "qualifiers (R-ID-3); its arch qualifier is checked against the platform"
    ),
    "components[].cpe": "Component.identifiers",
    "components[].properties": INSIDE,
    "components[].properties[].name": "read, to find Syft's syft:cpe23 CPEs",
    "components[].properties[].value": (
        "a syft:cpe23 value goes in Component.identifiers; the other properties are left "
        "out, counted above"
    ),
    "components[].description": (
        "Component.description; left out where entries recorded as one Component disagree "
        "(listed above)"
    ),
    "components[].bom-ref": "joins dependencies to Components",
    "components[].supplier": INSIDE,
    "components[].supplier.name": (
        "Component.supplied_by, a Party (Table 6c); left out where entries recorded as one "
        "Component disagree (listed above)"
    ),
    "components[].supplier.url": NO_SLOT,
    "components[].supplier.contact": NO_SLOT,
    "components[].supplier.address": NO_SLOT,
    "components[].supplier.bom-ref": NO_SLOT,
    "components[].manufacturer": INSIDE,
    "components[].manufacturer.name": (
        "Component.manufactured_by, a Party (Table 6c); left out where entries recorded as "
        "one Component disagree (listed above)"
    ),
    "components[].manufacturer.url": NO_SLOT,
    "components[].manufacturer.contact": NO_SLOT,
    "components[].manufacturer.address": NO_SLOT,
    "components[].manufacturer.bom-ref": NO_SLOT,
    "components[].publisher": "left out: a publisher or maintainer is not a supplier (Table 6c)",
    "components[].author": "left out: an author is not a supplier (Table 6c)",
    "components[].authors": "left out: an author is not a supplier (Table 6c)",
    "components[].licenses": NO_SLOT,
    "components[].hashes": "left out: content identity is post-MVP (R-ID-4)",
    "components[].externalReferences": NO_SLOT,
    "components[].swid": "left out: no slot in this mapping",
    "components[].components": (
        "read as components; their fields are counted with the components above (Syft "
        "writes no nesting)"
    ),
    "dependencies": INSIDE,
    "dependencies[].ref": "the dependent Component",
    "dependencies[].dependsOn": (
        "Component.uses_component, dependent to dependency (R-EDGE-1, R-EDGE-3); an edge "
        "from the image, to or from an entry that is not a Component, or from a Component "
        "to itself is left out, counted above"
    ),
}
# A nested component is read as a component, so its fields count under components[].
SBOM_NESTED = {"components[].components": "components"}

_CWE_FIELDS = {
    "cwes": INSIDE,
    "cwes[].cve": (
        "the Vulnerability of an instance_of Assertion (R-CWE-1); an entry for an id that is "
        "not a Vulnerability here is left out, counted above"
    ),
    "cwes[].cwe": (
        "the Weakness of an instance_of Assertion; placeholders, and entries that name no "
        "CWE, are left out, counted above"
    ),
    "cwes[].source": "the instance_of Assertion's asserted_by, a Party (R-CWE-1)",
    "cwes[].type": "the instance_of Assertion's description (NVD's Primary or Secondary)",
}
_RECORD_FIELDS = {
    "id": (
        "Vulnerability.catalog_ref (a CVE), or alias_ids beside the CVE it names; an id the "
        "scan pairs with more than one Vulnerability is listed above, not written"
    ),
    "description": "Vulnerability.description",
    "namespace": (
        "picks a description when records differ; otherwise left out (the match's "
        "namespace is in its Assertion)"
    ),
    "dataSource": NO_SLOT,
    "severity": "left out: no slot (ADR-0006 rates risk; RPT-0004 Table 6)",
    "urls": "left out: ids inside URLs are never read",
    "cvss": "left out: no slot (Table 6)",
    "epss": "left out: no slot (Table 6)",
    "fix": "left out: no slot (Table 6)",
    "advisories": NO_SLOT,
    "risk": "left out: Grype's risk number, not a tmodel risk (ADR-0006)",
    "knownExploited": NO_SLOT,
    **_CWE_FIELDS,
}
SCAN_FIELDS = {
    "matches": INSIDE,
    "matches[].vulnerability": INSIDE,
    **{f"matches[].vulnerability.{k}": v for k, v in _RECORD_FIELDS.items()},
    "matches[].relatedVulnerabilities": INSIDE,
    **{f"matches[].relatedVulnerabilities[].{k}": v for k, v in _RECORD_FIELDS.items()},
    "matches[].matchDetails": INSIDE,
    "matches[].matchDetails[].type": "Assertion.confidence (R-MATCH-1) and its description",
    "matches[].matchDetails[].matcher": "the Assertion's description",
    "matches[].matchDetails[].searchedBy": INSIDE,
    "matches[].matchDetails[].searchedBy.namespace": "the Assertion's description",
    "matches[].matchDetails[].searchedBy.package": "left out: the Component has the package",
    "matches[].matchDetails[].searchedBy.distro": "left out: the search key (no slot, R-MATCH-1)",
    "matches[].matchDetails[].searchedBy.cpes": "left out: the search key (no slot, R-MATCH-1)",
    "matches[].matchDetails[].found": INSIDE,
    "matches[].matchDetails[].found.versionConstraint": (
        "the Assertion's description, as written (R-RANGE-1)"
    ),
    "matches[].matchDetails[].found.vulnerabilityID": "left out: the match's own id says it",
    "matches[].matchDetails[].found.cpes": "left out: no slot (R-MATCH-1)",
    "matches[].matchDetails[].fix": "left out: no slot (Table 6)",
    "matches[].artifact": INSIDE,
    "matches[].artifact.purl": "joins the match to its Component (R-MATCH-2)",
    "matches[].artifact.name": "checked against the Component's name",
    "matches[].artifact.version": "checked against the Component's version",
    "matches[].artifact.id": "left out: the join is by purl, not by ref (R-MATCH-2)",
    "matches[].artifact.type": "left out: the Component has it",
    "matches[].artifact.cpes": "left out: the Component has the SBOM's CPEs",
    "matches[].artifact.locations": "left out: content identity is post-MVP (R-ID-4)",
    "matches[].artifact.language": NO_SLOT,
    "matches[].artifact.licenses": NO_SLOT,
    "matches[].artifact.upstreams": NO_SLOT,
    "matches[].artifact.metadataType": NO_SLOT,
    "matches[].artifact.metadata": NO_SLOT,
    "descriptor": INSIDE,
    "descriptor.name": "checked: grype",
    "descriptor.version": "checked: a release version; Assertion.generated_by (R-PROV-2)",
    "descriptor.timestamp": "Assertion.asserted_at, in UTC",
    "descriptor.configuration": "left out: Grype's settings",
    "descriptor.db": INSIDE,
    "descriptor.db.status": INSIDE,
    "descriptor.db.status.built": "Assertion.generated_by (R-PROV-2); checked: not after the scan",
    "descriptor.db.status.schemaVersion": "Assertion.generated_by (R-PROV-2)",
    "descriptor.db.status.valid": "checked: not false",
    "descriptor.db.status.error": "checked: empty",
    "descriptor.db.status.from": "left out: where the database was downloaded from",
    "descriptor.db.status.path": "left out: a local path",
    "descriptor.db.providers": (
        "left out: each provider's capture time (R-PROV-2 asks for them; no slot yet)"
    ),
    "descriptor.db.built": "Assertion.generated_by (R-PROV-2); checked: not after the scan",
    "descriptor.db.schemaVersion": "Assertion.generated_by (R-PROV-2)",
    "descriptor.db.valid": "checked: not false",
    "descriptor.db.error": "checked: empty",
    "source": INSIDE,
    "source.type": "checked: image",
    "source.target": INSIDE,
    "source.target.manifestDigest": "checked: the SBOM's digest (R-ID-1)",
    "source.target.userInput": "checked: the SBOM's repository (R-ID-2); this report",
    "source.target.imageID": (
        "checked: the SBOM's root bom-ref, when Grype read an SBOM; this report"
    ),
    "source.target.tags": "this report (R-ID-1 keeps tags beside the digest; no slot yet)",
    "source.target.repoDigests": "this report (the index digest, when Grype read it; no slot yet)",
    "source.target.architecture": PLATFORM_RULE,
    "source.target.architectureVariant": PLATFORM_RULE,
    "source.target.os": PLATFORM_RULE,
    "source.target.mediaType": NO_SLOT,
    "source.target.imageSize": NO_SLOT,
    "source.target.layers": "left out: content identity is post-MVP (R-ID-4)",
    "source.target.manifest": NO_SLOT,
    "source.target.config": NO_SLOT,
    "distro": INSIDE,
    "distro.name": "this report, beside the SBOM's operating system",
    "distro.version": "this report, beside the SBOM's operating system",
    "distro.idLike": NO_SLOT,
}


class _Report:
    def __init__(self, builder: _Builder, output_name: str) -> None:
        self.b = builder
        self.output_name = output_name

    def text(self) -> str:
        b = self.b
        lines = ["# tmodel import-sbom report", ""]
        lines += ["## Inputs", ""]
        lines.append(
            f"- SBOM `{b.sbom_file.name}`: {b.sbom_file.digest}, {b.sbom_file.size} bytes. "
            f"CycloneDX {CYCLONEDX_VERSION} from {b.info.tool}"
            + (f", serial {b.info.serial}" if b.info.serial else "")
            + (f", made {b.info.timestamp}" if b.info.timestamp else "")
            + "."
        )
        if b.scan_file is not None and b.scan_info is not None:
            lines.append(
                f"- Scan `{b.scan_file.name}`: {b.scan_file.digest}, {b.scan_file.size} bytes. "
                f"{b.scan_info.generated_by}; scanned {b.scan_info.timestamp}."
            )
        else:
            lines.append(
                "- No scan was given, so no vulnerabilities were imported. A model without a "
                "scan says nothing about known vulnerabilities."
            )
        lines.append(
            f"- Image: {b.info.image}, digest {b.info.digest}. Platform: {b.platform}, from "
            f"{b.platform_source}. The SBOM does not say whether the digest is a platform "
            "manifest's or an index's, which every platform of a release shares, so the "
            "build is keyed by the two (R-ID-1)."
        )
        lines.append(self._architectures())
        if b.scan_info is not None:
            lines += self._scan_identity(b.scan_info)
        counts = b.counts()
        lines += ["", f"## Written to `{self.output_name}`", ""]
        lines.append(
            f"1 Product, 1 ProductInstance, {counts['components']} Components, "
            f"{counts['vulnerabilities']} Vulnerabilities, {counts['weaknesses']} Weaknesses, "
            f"{counts['parties']} Parties and "
            f"{counts['match_assertions'] + counts['cwe_assertions']} Assertions "
            f"({counts['match_assertions']} package matches, {counts['cwe_assertions']} CWE "
            "links). Every Assertion is proposed, and no Review is recorded (R-018). No "
            "assets, trust boundaries, data flows, threats, attack paths or mitigations: "
            "add them by hand or with `tmodel propose` (Table 6f)."
        )
        lines += ["", "## What the SBOM held", ""]
        kinds = ", ".join(f"{n} {t}" for t, n in sorted(b.types.items()))
        lines.append(f"- {sum(b.types.values())} component entries: {kinds or 'none'}.")
        lines.append(f"- {counts['components']} Components written.")
        lines.append(f"- {b.edges} dependency edges written as `uses_component`.")
        if b.scan is not None:
            lines += ["", "## What the scan held", ""]
            matches = len(b.scan["matches"])
            lines.append(
                f"- {matches} matches on {len(b.scan_parts)} of the {counts['components']} "
                "Components."
            )
            cves = sum(1 for ref in b.vulnerabilities if CVE_ID.fullmatch(ref))
            lines.append(
                f"- {counts['vulnerabilities']} Vulnerabilities: {cves} CVEs and "
                f"{counts['vulnerabilities'] - cves} without a CVE."
            )
            lines.append(
                "- A part with no match is not proven safe: a scan finds only known "
                "vulnerabilities in the parts it can name, and an SBOM can miss parts."
            )
        for heading, counter in (
            ("Left out, with counts", b.notes),
            ("Repeated in the inputs, written once", b.repeats),
        ):
            counted = [(reason, n) for reason, n in sorted(counter.items()) if n]
            if counted:
                lines += ["", f"## {heading}", ""]
                lines += [f"- {n} {reason}" for reason, n in counted]
        for heading, items in sorted(b.listed.items()):
            lines += ["", f"## {heading}", ""]
            lines += [f"- {item}" for item in sorted(set(items))]
        lines += ["", "## Fields, and where they went", ""]
        lines.append(
            "Every field of each file by its path (`a.b` is field b of a, and `a[]` each item "
            "of list a), how often it occurs, and where it went. A field whose whole value is "
            "left out is counted with the values it holds. Where it went is for the entries "
            "and matches the import keeps: file entries, and the matches listed above as left "
            "out, are left out whole."
        )
        lines += ["", "- SBOM:"]
        lines += _inventory(b.sbom, SBOM_FIELDS, SBOM_NESTED)
        if b.scan is not None:
            lines.append("- Scan:")
            lines += _inventory(b.scan, {**SCAN_FIELDS, **self._descriptions()}, {})
        lines += [
            "",
            "## Next",
            "",
            "Check the model against the schema:",
            "",
            f"    linkml-validate -s {CONTAINER_SCHEMA} -C ExampleModelProposed {self.output_name}",
            "",
        ]
        # Every line holds input text; none may break, so each prints on one line.
        return "\n".join(_one_line(line) for line in lines)

    def _architectures(self) -> str:
        """What the packages' arch qualifiers say, checked against the platform."""
        b = self.b
        platform = b.platform.architecture
        if not b.architectures:
            return (
                "- No package's purl names an architecture this import knows, so the platform "
                "is not checked against the packages."
            )
        said = []
        native_first = sorted(b.architectures.items(), key=lambda kv: (kv[0][0] != platform, kv))
        for (oci, arch), n in native_first:
            text = f"{n} Component{'' if n == 1 else 's'} built for {oci} (arch={arch})"
            if oci != platform:
                text += f", which {platform} also runs (multiarch and multilib)"
            said.append(text)
        return f"- The packages fit the platform: {'; '.join(said)}."

    def _descriptions(self) -> dict[str, str]:
        """Where the scan's descriptions went, for each description field that has some
        left out, so its line never says they were all written (`_Builder.words`)."""
        b = self.b
        rules = {}
        for path, left in b.words.items():
            if not left:
                continue  # each one was written, as the field table says
            reasons = ", ".join(f"{n} {why}" for why, n in sorted(left.items()))
            text = f"left out: {reasons} (each listed above)"
            written = b.words_written[path]
            rules[path] = f"Vulnerability.description, for {written}; {text}" if written else text
        return rules

    def _scan_identity(self, scan: ScanInfo) -> list[str]:
        b = self.b
        lines = []
        said = f"- The scan names the image {scan.image or '(none)'}"
        if scan.image_id is None:
            lines.append(said + " and records no image id.")
        elif scan.image_id == b.info.bom_ref:
            lines.append(
                said + f" and image id {scan.image_id}, this SBOM's root bom-ref: Grype read "
                "this SBOM."
            )
        elif DIGEST.fullmatch(scan.image_id):
            lines.append(
                said + f" and image id {scan.image_id}, a configuration digest: Grype read "
                "the image itself, with this SBOM's digest."
            )
        else:  # the SBOM has no root bom-ref to compare with
            lines.append(said + f" and image id {scan.image_id}.")
        if scan.also:
            lines.append(f"- The scan also records {'; '.join(scan.also)}.")
        if scan.distro is not None:
            if not b.systems:
                lines.append(
                    f"- Grype's distro is {scan.distro}; the SBOM names no operating system."
                )
            elif scan.distro in b.systems:
                lines.append(
                    f"- Grype's distro is {scan.distro}, as the SBOM's operating system says."
                )
            else:
                lines.append(
                    f"- Grype's distro is {scan.distro}, but the SBOM's operating system is "
                    f"{', '.join(b.systems)}: check that the scan is of this SBOM."
                )
        return lines


def _inventory(
    doc: Mapping[str, Any], rules: Mapping[str, str], nested: Mapping[str, str]
) -> list[str]:
    """One report line per field path in `doc`: how often it occurs and where it went."""
    seen: Counter[str] = Counter()
    holding: Counter[str] = Counter()
    pending: list[tuple[Any, str]] = [(doc, "")]
    while pending:
        value, path = pending.pop()
        if isinstance(value, dict):
            for key, item in value.items():
                name = f"{path}.{key}" if path else key
                seen[name] += 1
                if name in nested:
                    pending.append((item, nested[name]))
                elif rules.get(name) == INSIDE:
                    pending.append((item, name))
                elif isinstance(item, dict | list):
                    holding[name] += _values(item)
        elif isinstance(value, list):
            pending.extend((item, f"{path}[]") for item in value)
        else:  # a value where an object was expected: an item of a list of values
            seen[path] += 1
    lines = []
    for name in sorted(seen):
        n = holding[name]
        inside = f", holding {n} value{'' if n == 1 else 's'}" if n else ""
        lines.append(f"  - `{name}` ({seen[name]}{inside}): {rules.get(name, UNREAD)}")
    return lines


def _values(value: Any) -> int:
    """How many values (text, numbers, true, false and null) `value` holds."""
    if isinstance(value, dict):
        return sum(_values(item) for item in value.values())
    if isinstance(value, list):
        return sum(_values(item) for item in value)
    return 1


# Writing ----------------------------------------------------------------------------


def _header(builder: _Builder, output_name: str) -> str:
    b = builder
    lines = [
        f"# STARTER MODEL, imported by `tmodel import-sbom` (tmodel {__version__}; #257, DL-0068)",
        "#",
        f"# Product: {b.info.image}. The build: digest",
        f"# {b.info.digest}",
        f"# for {b.platform} (from {b.platform_source}).",
        "#",
        f"# SBOM: {b.sbom_file.name}, {b.sbom_file.digest}",
        f"#   CycloneDX {CYCLONEDX_VERSION} from {b.info.tool}"
        + (f", serial {b.info.serial}" if b.info.serial else ""),
    ]
    if b.info.timestamp:
        lines.append(f"#   made {b.info.timestamp}")
    if b.scan_file is not None and b.scan_info is not None:
        lines += [
            f"# Scan: {b.scan_file.name}, {b.scan_file.digest}",
            f"#   {b.scan_info.generated_by}",
            f"#   scanned {b.scan_info.timestamp}",
        ]
    else:
        lines.append("# Scan: none given, so no vulnerabilities are listed.")
    lines += [
        "#",
        "# It holds only what the two files say: the product, the scanned build, its parts",
        "# and their dependencies, and the known vulnerabilities and CWEs the scan found. No",
        "# assets, trust boundaries, data flows, threats, attack paths or mitigations: add",
        "# them by hand or with `tmodel propose` (RPT-0004 Table 6f).",
        "#",
        "# IMPORTED, NOT REVIEWED. Every Assertion is `proposed` and no Review is recorded",
        "# (R-018). A package match is a lead, not a verdict.",
        "#",
        "# Validate:",
        f"#   linkml-validate -s {CONTAINER_SCHEMA} \\",
        f"#     -C ExampleModelProposed {output_name}",
    ]
    # Input text (a serial, a tool's version, a file name) may hold a line break or a
    # control character; escaped, it cannot end a comment and spill into the model.
    return "\n".join(_one_line(line) for line in lines) + "\n\n"


class _Dumper(yaml.SafeDumper):
    """Block YAML as the example models write it: lists indented under their key, keys in
    the order given, and no anchors or aliases."""

    def ignore_aliases(self, data: Any) -> bool:
        return True

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        return super().increase_indent(flow, False)


def _represent_text(dumper: yaml.SafeDumper, text: str) -> yaml.ScalarNode:
    # Text with a character that does not print (a line break, a tab, NEL) is written
    # double-quoted, where YAML escapes it; another style can fold it into a space.
    style = None if text.isprintable() else '"'
    return dumper.represent_scalar("tag:yaml.org,2002:str", text, style=style)


_Dumper.add_representer(str, _represent_text)


def _dump(doc: Mapping[str, Any]) -> str:
    return yaml.dump(
        doc,
        Dumper=_Dumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=1_000_000,
    )


def _read_back(text: str, doc: Mapping[str, Any]) -> None:
    """The model's text must read back as the model it was made from, header and all (a
    bug here, never bad input, since input text is escaped), or nothing is written."""
    try:
        loaded = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise SbomImportError(
            f"internal error: the model does not read back as YAML ({type(exc).__name__}); "
            "nothing was written"
        ) from exc
    if loaded != doc:
        raise SbomImportError(
            "internal error: the model does not read back as the data it was made from; "
            "nothing was written"
        )


def _self_check(doc: Mapping[str, Any]) -> None:
    """Every id the model references is an object in it (a bug here, never bad input)."""
    from engine.graph import GraphError
    from engine.model_graph import project_model_graph

    try:
        project_model_graph(doc)
    except GraphError as exc:  # pragma: no cover - only a bug in this module reaches here
        raise SbomImportError(f"internal error: the model does not hold together ({exc})") from exc
    ids = {obj["id"] for items in doc.values() for obj in items}
    for assertion in doc.get("assertions", []):
        for end in ("subject", "object"):
            if assertion[end] not in ids:  # pragma: no cover - a bug, not bad input
                raise SbomImportError(f"internal error: {assertion['id']} names {assertion[end]}")


def _check_outputs(inputs: list[Path], outputs: list[Path], force: bool) -> None:
    """The model (first) and the report may not be an input or each other, by any name a
    link or a case- or normalization-insensitive volume gives them, and are never
    replaced unforced."""
    model = outputs[0]
    if model.suffix not in MODEL_SUFFIXES:
        raise SbomImportError(
            f"{_one_line(model.name)}: the model file must end in .yaml, so the engine reads it"
        )
    for path in outputs:
        name = _one_line(path.name)
        if any(_same_place(path, source) for source in inputs):
            raise SbomImportError(
                f"{name}: is an input (by its own name, a link, a second name for the file, or "
                "the same name in another case or Unicode form); refusing to write over it"
            )
        if os.path.isdir(path):
            raise SbomImportError(f"{name}: is a folder")
        if os.path.lexists(path) and not force:  # a dangling link exists too
            raise _taken(path)
        if not path.parent.is_dir():
            raise SbomImportError(f"{name}: its folder does not exist")
    if len(outputs) == 2 and _same_place(outputs[0], outputs[1]):
        raise SbomImportError("the report and the model cannot be the same file")


def _same_place(first: Path, second: Path) -> bool:
    """Whether two paths name one file: the same file when both exist (through a link or
    a second name), or else the same real path as a Mac's volume compares names, which
    ignores case and Unicode normalization (é as one character, or as e and an accent).
    On a volume that tells such names apart, they are refused too, which costs nothing."""
    try:
        if os.path.exists(first) and os.path.exists(second) and os.path.samefile(first, second):
            return True
    except OSError:
        pass
    return _place(first) == _place(second)


def _place(path: Path) -> str:
    """The real path in Unicode's canonical caseless form, NFD(casefold(NFD(text))), so
    two paths a case- and normalization-insensitive volume (APFS, HFS+) reads as one
    name give one text. Where a volume folds names some other way, `_publish` still
    never writes over a file that is there."""
    real = os.path.normcase(os.path.realpath(path))
    return unicodedata.normalize("NFD", unicodedata.normalize("NFD", real).casefold())


def _taken(path: Path) -> SbomImportError:
    return SbomImportError(
        f"{_one_line(path.name)}: already exists; people edit starter models, so it is not "
        "replaced without --force"
    )


# Where this import put a file: the path, which file it put there (device and inode),
# and the second name keeping the file --force replaced, if any.
_Placed = tuple[Path, tuple[int, int], Path | None]


def _publish(files: list[tuple[Path, str]], force: bool) -> None:
    """Write each text to a temporary file beside its path, then put them all in place.
    Unforced, each is put where nothing is, by an operation that fails if anything is
    there by then (`_place_new`), so a file that appeared after `_check_outputs`, or
    one the volume reads as the same name as the other output, is never written over.
    With --force, each is moved over its path, and a second name keeps the file it
    replaces (`_keep`). A failure on the way takes back what this import put in place
    and puts back what --force replaced, so a failed import never leaves half of its
    output; and it never removes or replaces a file this import did not put there."""
    temporaries: list[Path] = []
    backups: list[Path | None] = []
    kept: list[Path] = []  # second names whose file could not be put back
    try:
        for path, text in files:
            temporaries.append(_temporary(path, text))
        if force:
            backups = [_keep(path) if os.path.lexists(path) else None for path, _ in files]
        placed: list[_Placed] = []
        try:
            for index, ((path, text), temporary) in enumerate(zip(files, temporaries, strict=True)):
                if not force:
                    _place_new(temporary, path, text, placed)
                    continue
                stamp = _stamp(temporary)
                os.replace(temporary, path)  # atomic: a failed move leaves the old file
                placed.append((path, stamp, backups[index]))
        except BaseException as exc:
            keep, notes = _take_back(placed)
            kept += keep
            for note in notes:
                exc.add_note(note)
            raise
    finally:
        for leftover in [*temporaries, *(b for b in backups if b is not None and b not in kept)]:
            leftover.unlink(missing_ok=True)  # in place already, unless something failed


def _place_new(temporary: Path, path: Path, text: str, placed: list[_Placed]) -> None:
    """Put the text at `path` only if nothing is there: the temporary file under a second
    name, by a hard link, which fails if anything is at `path`, even a dangling link or a
    name the volume reads as the same; or, on a volume without hard links, a file
    created exclusively. Each is recorded in `placed` once it exists, so a failure can
    take it back."""
    stamp = _stamp(temporary)  # the file the link gives a second name
    try:
        os.link(temporary, path)
    except FileExistsError:
        raise _taken(path) from None
    except OSError:  # a volume without hard links, such as FAT or exFAT
        _create_new(path, text, placed)
    else:
        placed.append((path, stamp, None))
    temporary.unlink()


def _create_new(path: Path, text: str, placed: list[_Placed]) -> None:
    """Create `path` exclusively (it must not exist, even as a link) and write the text."""
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
    except FileExistsError:
        raise _taken(path) from None
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        info = os.fstat(handle.fileno())
        placed.append((path, (info.st_dev, info.st_ino), None))
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())


def _take_back(placed: list[_Placed]) -> tuple[list[Path], list[str]]:
    """Undo the placements, last first: put back the file --force replaced, or remove
    the new one, but only where the path still holds the file this import put there;
    another program's file is left be. Returns the second names to keep, because the
    file in them could not be put back, and a note for each path not taken back. (The
    check and the removal are two steps: POSIX has no removal by file identity.)"""
    keep: list[Path] = []
    notes: list[str] = []
    for path, stamp, backup in reversed(placed):
        name = _one_line(path.name)
        if not _holds(path, stamp):
            why = "was replaced by another program while the import ran, and is left as it is"
        else:
            try:
                if backup is not None:
                    os.replace(backup, path)
                else:
                    os.unlink(path)
                continue
            except OSError as exc:
                why = f"could not be taken back ({exc.strerror or exc})"
        notes.append(f"{name}: the file this import put there {why}")
        if backup is not None:
            keep.append(backup)
            notes.append(f"{name}: the file --force was replacing is kept as {backup.name}")
    return keep, [_one_line(note) for note in notes]


def _stamp(path: Path) -> tuple[int, int]:
    """Which file is at `path`, by its device and inode, not following a link."""
    info = os.lstat(path)
    return info.st_dev, info.st_ino


def _holds(path: Path, stamp: tuple[int, int]) -> bool:
    try:
        return _stamp(path) == stamp
    except OSError:  # gone, or not to be read: either way, not one to remove
        return False


def _temporary(path: Path, text: str) -> Path:
    handle = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=".import-sbom-", suffix=".tmp", delete=False
    )
    try:
        with handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        Path(handle.name).unlink(missing_ok=True)
        raise
    return Path(handle.name)


def _keep(path: Path) -> Path:
    """A second name beside `path` for what is there now (a file or a link), so a failed
    import can put it back. The file itself stays where it is until it is replaced."""
    backup = path.parent / f".import-sbom-{secrets.token_hex(8)}.old"
    if os.path.islink(path):
        os.symlink(os.readlink(path), backup)
        return backup
    try:
        os.link(path, backup)
    except OSError:  # a volume without hard links: a copy keeps the same bytes
        shutil.copy2(path, backup)
    return backup


def _display_path(path: Path) -> str:
    """The output path as given, or only its name when it is absolute (no home folders)."""
    return path.name if path.is_absolute() else path.as_posix()


# Small helpers ---------------------------------------------------------------------


def _flatten(
    entries: list[Any], name: str, where: str, depth: int = 0
) -> Iterator[tuple[str, Mapping[str, Any]]]:
    """Components and their nested components, depth first, each with where it is in the
    file (`components[3]`, `components[3].components[0]`). Syft writes no nesting."""
    if depth > 32:
        raise SbomImportError(f"{name}: components nest more than 32 levels deep")
    for index, entry in enumerate(entries):
        at = f"{where}[{index}]"
        if not isinstance(entry, dict):
            raise SbomImportError(f"{name}: {at} is not a JSON object")
        yield at, entry
        yield from _flatten(
            _list_at(entry, "components", name, at), name, f"{at}.components", depth + 1
        )


def _row(match: Any, index: int, name: str) -> _Row:
    """One match, with every field the import reads checked."""
    at = f"matches[{index}]"
    if not isinstance(match, dict):
        raise SbomImportError(f"{name}: {at} is not a JSON object")
    vulnerability = _object_at(match, "vulnerability", name, at)
    if vulnerability is None or _text_at(vulnerability, "id", name, f"{at}.vulnerability") is None:
        raise SbomImportError(f"{name}: {at} has no vulnerability id")
    records = [_record(vulnerability, name, f"{at}.vulnerability")]
    for number, related in enumerate(_list_at(match, "relatedVulnerabilities", name, at)):
        where = f"{at}.relatedVulnerabilities[{number}]"
        if not isinstance(related, dict):
            raise SbomImportError(f"{name}: {where} is not an object")
        records.append(_record(related, name, where))
    ids = [record.id for record in records]
    unique = list(dict.fromkeys(ids))
    details = tuple(
        _detail(detail, name, f"{at}.matchDetails[{number}]")
        for number, detail in enumerate(_list_at(match, "matchDetails", name, at))
    )
    artifact = _object_at(match, "artifact", name, at)
    if artifact is None:
        raise SbomImportError(f"{name}: {at} has no artifact")
    where = f"{at}.artifact"
    canonical = json.dumps(match, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return _Row(
        vid=ids[0],
        records=tuple(records),
        cves=tuple(sorted(i for i in unique if CVE_ID.fullmatch(i))),
        others=tuple(i for i in unique if not CVE_ID.fullmatch(i)),
        repeated_ids=len(ids) - len(unique),
        purl=_text_at(artifact, "purl", name, where),
        name=_text_at(artifact, "name", name, where),
        version=_text_at(artifact, "version", name, where),
        details=details,
        fingerprint=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    )


def _record(record: Mapping[str, Any], name: str, where: str) -> _Record:
    cwes = []
    for number, entry in enumerate(_list_at(record, "cwes", name, where)):
        at = f"{where}.cwes[{number}]"
        if not isinstance(entry, dict):
            raise SbomImportError(f"{name}: {at} is not an object")
        cwes.append(
            tuple(_text_at(entry, key, name, at) for key in ("cve", "cwe", "source", "type"))
        )
    vid = _text_at(record, "id", name, where)
    if vid is None:
        raise SbomImportError(f"{name}: {where} has no id")
    return _Record(
        id=vid,
        namespace=_text_at(record, "namespace", name, where),
        description=_prose(_text_at(record, "description", name, where)),
        cwes=tuple(cwes),
    )


def _detail(detail: Any, name: str, where: str) -> _Detail:
    if not isinstance(detail, dict):
        raise SbomImportError(f"{name}: {where} is not an object")
    searched = _object_at(detail, "searchedBy", name, where) or {}
    found = _object_at(detail, "found", name, where) or {}
    return _Detail(
        type=_text_at(detail, "type", name, where),
        matcher=_text_at(detail, "matcher", name, where),
        namespace=_text_at(searched, "namespace", name, f"{where}.searchedBy"),
        constraint=_text_at(found, "versionConstraint", name, f"{where}.found"),
    )


def _match_description(row: _Row) -> str:
    def joined(values: set[str | None], glue: str = ", ") -> str:
        return glue.join(sorted(v for v in values if v))

    types = joined({d.type for d in row.details})
    matchers = joined({d.matcher for d in row.details})
    namespaces = joined({d.namespace for d in row.details})
    constraints = joined({d.constraint for d in row.details}, "; ")
    parts = [f"Grype matched {row.vid}"]
    if types:
        parts.append(f"by {types}")
    if matchers:
        parts.append(f"({matchers})")
    text = " ".join(parts)
    if namespaces:
        text += f" in {namespaces}"
    if constraints:
        text += f"; affected versions {constraints}"
    return text + ". A match is a lead, not a verdict (R-MATCH-1)."


@dataclass(frozen=True)
class _Purl:
    """A package URL split by the purl specification's parsing steps, each part decoded."""

    type: str
    namespace: tuple[str, ...]
    name: str
    version: str | None
    qualifiers: tuple[tuple[str, str], ...]  # sorted by key
    subpath: tuple[str, ...]

    @property
    def base(self) -> str:
        """The purl up to its qualifiers: type, namespace, name and version."""
        path = "/".join(_encode(part) for part in (*self.namespace, self.name))
        return f"pkg:{self.type}/{path}" + (f"@{_encode(self.version)}" if self.version else "")

    @property
    def key(self) -> str:
        """The purl in one spelling: each part encoded one way and the qualifiers sorted,
        so two spellings of one purl are one key and two purls are two."""
        text = self.base
        if self.qualifiers:
            text += "?" + "&".join(f"{k}={_encode(v, safe='/:')}" for k, v in self.qualifiers)
        if self.subpath:
            text += "#" + "/".join(_encode(part) for part in self.subpath)
        return text

    @property
    def readable(self) -> str:
        return "/".join((self.type, *self.namespace, self.name)) + (
            f"@{self.version}" if self.version else ""
        )


def _purl_key(purl: str) -> str | None:
    """A Component's key: its purl, qualifiers and all, in one spelling (R-ID-3)."""
    parsed = _parse_purl(purl)
    return parsed.key if parsed is not None else None


def _parse_purl(text: str) -> _Purl | None:
    """`text` split as the purl specification's "how to parse" steps say, or None when it
    is not a purl. Only the rules every type shares are applied: which names ignore case
    differs by type, and changed between purl-spec versions (DL-0015), so two purls that
    differ only in such a case stay two, and a match on one never joins the other."""
    try:
        return _split_purl(text)
    except UnicodeDecodeError:  # a percent-encoded byte that is not UTF-8
        return None


def _split_purl(text: str) -> _Purl | None:
    rest, subpath = _cut(text, "#")
    rest, query = _cut(rest, "?")
    scheme, colon, rest = rest.partition(":")
    if not colon or scheme.lower() != "pkg":
        return None
    kind, slash, rest = rest.strip("/").partition("/")
    kind = kind.lower()
    if not slash or not PURL_TYPE.fullmatch(kind):
        return None
    rest, version = _cut(rest, "@")
    namespace, _, name = rest.rpartition("/")
    name = _decode(name)
    spaces = tuple(_decode(part) for part in namespace.split("/") if part)
    if not name or any("/" in part for part in spaces):
        return None
    qualifiers: dict[str, str] = {}
    for pair in query.split("&") if query else []:
        key, _, value = pair.partition("=")
        key = key.lower()
        if not QUALIFIER_KEY.fullmatch(key) or key in qualifiers:
            return None
        if _decode(value):  # an empty value is no qualifier at all
            qualifiers[key] = _decode(value)
    path = tuple(
        _decode(part) for part in subpath.strip("/").split("/") if part not in ("", ".", "..")
    )
    if any(part in ("", ".", "..") or "/" in part for part in path):
        return None
    return _Purl(
        kind, spaces, name, _decode(version) or None, tuple(sorted(qualifiers.items())), path
    )


def _cut(text: str, mark: str) -> tuple[str, str]:
    """(before, after) the last `mark` in `text`, or (text, "") when it has none."""
    before, found, after = text.rpartition(mark)
    return (before, after) if found else (text, "")


def _decode(text: str) -> str:
    return unquote(text, encoding="utf-8", errors="strict")


def _encode(text: str, safe: str = ":") -> str:
    return quote(text, safe=safe)


def _same_version(version: str, purl: _Purl) -> bool:
    """Whether an entry's version is its purl's: an RPM's purl keeps its epoch apart."""
    epoch = dict(purl.qualifiers).get("epoch")
    return version in (purl.version, f"{epoch}:{purl.version}" if epoch else None)


def _image_repository(image: str) -> tuple[str, str]:
    """(registry, repository) for an image name, as Docker resolves a short name."""
    name = image.split("@", 1)[0]
    head, _, tail = name.rpartition("/")
    if ":" in tail:  # a tag after the last slash
        name = f"{head}/{tail.split(':', 1)[0]}" if head else tail.split(":", 1)[0]
    parts = name.split("/")
    if len(parts) > 1 and ("." in parts[0] or ":" in parts[0] or parts[0] == "localhost"):
        registry, path = parts[0], "/".join(parts[1:])
    else:
        registry, path = "index.docker.io", name
    if registry == "docker.io":
        registry = "index.docker.io"
    if registry == "index.docker.io" and "/" not in path:
        path = f"library/{path}"
    return registry.lower(), path.lower()


def _text(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _prose(value: Any) -> str | None:
    """A description on one line: the source's line breaks and runs of spaces become one
    space, so the model reads as the hand-written ones do. The words are unchanged."""
    text = _text(value)
    return " ".join(text.split()) if text is not None else None


def _utc(value: Any) -> str | None:
    """An RFC 3339 date and time in UTC, to the second, or None: also for a time that,
    moved to UTC, falls outside the years 1 to 9999 Python's datetime holds, such as
    0001-01-01T00:00:00+14:00, so the caller's message names it as for any other."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        moment = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if moment.tzinfo is None:
        return None
    try:
        moment = moment.astimezone(UTC)
    except OverflowError:
        return None
    # isoformat writes the year with four digits everywhere; strftime's %Y does not on
    # every platform, and these times are compared as text (_scan_database).
    return moment.replace(microsecond=0, tzinfo=None).isoformat() + "Z"


def _one_line(text: str) -> str:
    """`text` with each character that does not print (a line break, a tab, a control or
    format character) written as its escape, such as \\n or \\u2028, so input text can
    never end a comment or a report line."""
    if text.isprintable():
        return text
    return "".join(
        ch if ch.isprintable() else ch.encode("unicode_escape").decode("ascii") for ch in text
    )


def _slug(text: str, limit: int = 80) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "x"
    if len(slug) > limit:
        slug = slug[: limit - 9].rstrip("-") + "-" + _short_hash(text)
    return slug


def _short_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
