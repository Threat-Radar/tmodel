"""Write a starter model from a CycloneDX SBOM and its Grype scan (#257, DL-0068).

    tmodel import-sbom SBOM.json [--scan SCAN.json] -o MODEL.yaml [--report FILE] [--force]

Input is two files radar's tools write (ADR-0001, ARCH-0001 R-002): Syft's CycloneDX
1.7 JSON SBOM of a container image, and Grype's JSON scan of that SBOM
(`grype sbom:SBOM.json -o json`). tradar runs the same two tools; its own saved scan
file drops the CWEs and match details, so read Grype's file instead. Making the SBOM
and scanning it stay radar's job; this module only reads the two files.

Output is a starter model that `linkml-validate` accepts as `ExampleModelProposed`
and the engine loads, plus an import report. The mapping is RPT-0004 Table 6
(`research/0004-product-composition/mapping.md`) and its candidate rules:

- a Product keyed by the image's versionless purl (R-ID-2), and a ProductInstance for
  the scanned build, keyed by its platform manifest digest (R-ID-1), whose
  `build_composed_of` lists the components (ADR-0011 A4). The SBOM never fills the
  design-level `composed_of` (R-EDGE-2);
- one Component per SBOM entry other than files (R-ID-4), keyed by its purl without
  qualifiers or subpath (R-ID-3), with `version`, `component_kind` from CycloneDX's
  `type` (A3), and every purl and CPE the entry carries in `identifiers`;
- `supplied_by` and `manufactured_by` only from a `supplier` or `manufacturer`
  field: a publisher or package maintainer is not a supplier (Table 6c);
- each `dependsOn` as `uses_component`, from the dependent to the dependency
  (R-EDGE-1, R-EDGE-3);
- one Vulnerability per CVE a match names (its own id, or one in
  `relatedVulnerabilities`); a match that names no CVE keeps the id Grype reports
  (GHSA, ALAS, GO and so on). A match's other id goes in `alias_ids` only when it
  names exactly one CVE; an advisory that names several is listed in the report.
  Ids that appear only inside a URL are never read;
- one proposed `propagates_to` Assertion from a Vulnerability to each Component a
  match puts it in, joined to the SBOM by purl, not by `bom-ref` (R-MATCH-1,
  R-MATCH-2), with `confidence` from Grype's match type;
- one proposed `instance_of` Assertion per (CVE, CWE, source), `asserted_by` whoever
  assigned the CWE, skipping placeholders such as `NVD-CWE-Other` (R-CWE-1).

Every Assertion is `proposed`, with no Review (R-018), and records when (the scan's
time), how (`generated_by`: the tool, its version and the database build time,
R-PROV-2) and from what (`evidence`: the input files' SHA-256, R-PROV-1). Nothing
else is written: no assets, trust boundaries, data flows, threats, attack paths or
mitigations (Table 6f).

Deterministic: the same two files give the same model and report, byte for byte.
Every input is checked before anything is written, and an existing file is never
replaced without `--force`, because people edit starter models.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

import yaml

from engine import __version__

# A Juice Shop image's SBOM and scan are a few MB each; this leaves wide room.
MAX_INPUT_BYTES = 64 * 1024 * 1024
CYCLONEDX_VERSION = "1.7"
CONTAINER_SCHEMA = "spec/vectors/example-container-proposed.linkml.yaml"
MODEL_SUFFIXES = (".yaml", ".yml")

DIGEST = re.compile(r"sha256:[0-9a-f]{64}")
CVE_ID = re.compile(r"CVE-\d{4}-\d{4,}")
CWE_ID = re.compile(r"CWE-\d+")

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


@dataclass(frozen=True)
class ScanInfo:
    tool: str
    timestamp: str
    db_schema: str | None
    db_built: str

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
) -> ImportResult:
    """Read the inputs, write the model (and the report, when asked), and return both."""
    out = Path(output)
    report_path = Path(report) if report is not None else None
    _check_outputs(Path(sbom), None if scan is None else Path(scan), out, report_path, force)
    result = build(sbom, scan=scan, output_name=_display_path(out))
    _write(out, result.model_text)
    if report_path is not None:
        _write(report_path, result.report_text)
    return result


def build(
    sbom: str | Path, *, scan: str | Path | None = None, output_name: str = "MODEL.yaml"
) -> ImportResult:
    """The model and report texts for these inputs; nothing is written."""
    sbom_file, sbom_doc = _read_json(Path(sbom), "SBOM")
    info = _check_sbom(sbom_doc, sbom_file.name)
    scan_file = scan_doc = scan_info = None
    if scan is not None:
        scan_file, scan_doc = _read_json(Path(scan), "scan")
        scan_info = _check_scan(scan_doc, scan_file.name, info)
    builder = _Builder(sbom_file, sbom_doc, info, scan_file, scan_doc, scan_info)
    doc = builder.model()
    _self_check(doc)
    model_text = _header(builder, output_name) + _dump(doc)
    report_text = builder.report(output_name)
    return ImportResult(model_text, report_text, builder.counts())


# Reading and checking the inputs -----------------------------------------------------


def _read_json(path: Path, label: str) -> tuple[InputFile, Any]:
    data = _read(path)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SbomImportError(f"{path.name}: not UTF-8 text, so not JSON") from exc
    try:
        doc = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SbomImportError(
            f"{path.name}: not valid JSON (line {exc.lineno}, column {exc.colno}: {exc.msg})"
        ) from exc
    if not isinstance(doc, dict):
        raise SbomImportError(f"{path.name}: expected a JSON object at the top level")
    sha = hashlib.sha256(data).hexdigest()
    return InputFile(label, path.name, len(data), sha), doc


def _read(path: Path) -> bytes:
    """The bytes of a regular file of at most MAX_INPUT_BYTES, checked before reading."""
    too_large = f"{path.name}: larger than {MAX_INPUT_BYTES} bytes, so it is not read"
    try:
        with open(path, "rb", opener=_open_without_waiting) as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise SbomImportError(f"{path.name}: not a regular file, so it is not read")
            if info.st_size > MAX_INPUT_BYTES:
                raise SbomImportError(too_large)
            data = handle.read(MAX_INPUT_BYTES + 1)
    except OSError as exc:
        raise SbomImportError(f"{path.name}: cannot read ({exc.strerror or exc})") from exc
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
    tool = _sbom_tool(metadata.get("tools"))
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
    image = component.get("name")
    if not isinstance(image, str) or not image.strip():
        raise SbomImportError(f"{name}: metadata.component has no name")
    digest = component.get("version")
    if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
        raise SbomImportError(
            f"{name}: metadata.component.version is {digest!r}, not the image's digest, so "
            "the scanned build has no key (R-ID-1). Name the image by digest, as in "
            "`syft IMAGE@sha256:...`"
        )
    components = doc.get("components", [])
    if not isinstance(components, list):
        raise SbomImportError(f"{name}: components is not a list")
    dependencies = doc.get("dependencies", [])
    if not isinstance(dependencies, list):
        raise SbomImportError(f"{name}: dependencies is not a list")
    return SbomInfo(
        serial=_text(doc.get("serialNumber")),
        timestamp=_utc(metadata.get("timestamp")),
        tool=tool,
        image=image.strip(),
        digest=digest,
        bom_ref=_text(component.get("bom-ref")),
    )


def _sbom_tool(tools: Any) -> str | None:
    """'syft 1.52.0' when metadata.tools names Syft (CycloneDX 1.5+ or the older list)."""
    entries = tools.get("components") if isinstance(tools, dict) else tools
    for entry in entries if isinstance(entries, list) else []:
        if isinstance(entry, dict) and str(entry.get("name", "")).lower() == "syft":
            version = _text(entry.get("version"))
            return f"syft {version}" if version else "syft"
    return None


def _check_scan(doc: Mapping[str, Any], name: str, sbom: SbomInfo) -> ScanInfo:
    descriptor = doc.get("descriptor")
    if not isinstance(descriptor, dict) or str(descriptor.get("name", "")).lower() != "grype":
        raise SbomImportError(f"{name}: not Grype's JSON output (descriptor.name is not grype)")
    if not isinstance(doc.get("matches"), list):
        raise SbomImportError(f"{name}: no matches list")
    timestamp = _utc(descriptor.get("timestamp"))
    if timestamp is None:
        raise SbomImportError(f"{name}: descriptor.timestamp is missing or not a date and time")
    db = descriptor.get("db") if isinstance(descriptor.get("db"), dict) else {}
    status = db.get("status") if isinstance(db.get("status"), dict) else db
    built = _utc(status.get("built"))
    if built is None:
        raise SbomImportError(
            f"{name}: the scan does not record its database's build time, so its answer "
            "cannot be dated (R-PROV-2)"
        )
    source = doc.get("source")
    target = source.get("target") if isinstance(source, dict) else None
    scanned = target.get("manifestDigest") if isinstance(target, dict) else None
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
    version = _text(descriptor.get("version"))
    tool = f"Grype {version}" if version else "Grype"
    return ScanInfo(tool, timestamp, _text(status.get("schemaVersion")), built)


# Building the model ---------------------------------------------------------------


@dataclass
class _Component:
    key: str
    id: str
    name: str
    version: str | None
    kind: str
    description: str | None
    identifiers: list[str]
    supplier: str | None
    manufacturer: str | None
    entries: int = 1
    uses: set[str] = field(default_factory=set)


@dataclass
class _Vulnerability:
    ref: str
    id: str
    aliases: set[str] = field(default_factory=set)
    description: str | None = None


@dataclass
class _Match:
    vulnerability: str
    component: str
    ids: set[str] = field(default_factory=set)
    types: set[str] = field(default_factory=set)
    matchers: set[str] = field(default_factory=set)
    namespaces: set[str] = field(default_factory=set)
    constraints: set[str] = field(default_factory=set)


class _Builder:
    def __init__(
        self,
        sbom_file: InputFile,
        sbom: Mapping[str, Any],
        info: SbomInfo,
        scan_file: InputFile | None,
        scan: Mapping[str, Any] | None,
        scan_info: ScanInfo | None,
    ) -> None:
        self.sbom_file = sbom_file
        self.sbom = sbom
        self.info = info
        self.scan_file = scan_file
        self.scan = scan
        self.scan_info = scan_info
        self.ids: dict[str, str] = {}  # object id -> the key it was made from
        self.notes: Counter[str] = Counter()  # what was left out, by reason
        self.listed: dict[str, list[str]] = {}  # report lists, by heading
        self.types: Counter[str] = Counter()  # SBOM component entries, by CycloneDX type
        self.components: dict[str, _Component] = {}
        self.by_ref: dict[str, str] = {}  # bom-ref -> component key
        self.parties: dict[str, dict[str, Any]] = {}
        self.vulnerabilities: dict[str, _Vulnerability] = {}
        self.weaknesses: dict[str, str] = {}  # CWE id -> object id
        self.matches: dict[tuple[str, str], _Match] = {}
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

    def _id(self, prefix: str, key: str, readable: str) -> str:
        """A stable id from `readable`; the same key always gets the same id."""
        slug = _slug(readable)
        candidate = f"{prefix}:{slug}"
        owner = self.ids.get(candidate)
        if owner is not None and owner != key:
            candidate = f"{prefix}:{_slug(slug, limit=70)}-{_short_hash(key)}"
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
        self.instance_purl = f"pkg:oci/{purl_name}@{digest}?repository_url={url}"
        short = repository.removeprefix("library/")
        self.product_id = self._id("product", self.product_purl, short)
        hex12 = self.info.digest.removeprefix("sha256:")[:12]
        self.instance_id = self._id("product-instance", self.info.digest, f"{short}-{hex12}")

    # components

    def _components(self) -> None:
        raw = list(_flatten(self.sbom.get("components") or [], self.sbom_file.name))
        seen_refs: set[str] = set()
        made: list[_Component] = []
        for entry in raw:
            kind = entry.get("type")
            self.types[str(kind)] += 1
            ref = _text(entry.get("bom-ref"))
            if ref is not None:
                if ref in seen_refs:
                    raise SbomImportError(f"{self.sbom_file.name}: bom-ref {ref!r} appears twice")
                seen_refs.add(ref)
            if kind not in COMPONENT_KINDS:
                raise SbomImportError(
                    f"{self.sbom_file.name}: a component's type is {kind!r}, not one of "
                    "CycloneDX 1.7's component types"
                )
            if kind == "file":
                self.notes["SBOM file entries (R-ID-4: content identity is post-MVP)"] += 1
                continue
            name = _text(entry.get("name"))
            if name is None:
                raise SbomImportError(f"{self.sbom_file.name}: a {kind} component has no name")
            version = _text(entry.get("version"))
            purl = _text(entry.get("purl"))
            key = _purl_key(purl) if purl else None
            if key is None:
                key = f"{kind}/{name}" + (f"@{version}" if version else "")
                if purl:
                    self.notes["SBOM purls that do not parse (kept in identifiers)"] += 1
            component = self.components.get(key)
            identifiers = _identifiers(entry)
            if component is None:
                component = _Component(
                    key=key,
                    id="",
                    name=f"{name} {version}" if version else name,
                    version=version,
                    kind=COMPONENT_KINDS[kind],
                    description=_prose(entry.get("description")),
                    identifiers=identifiers,
                    supplier=_entity_name(entry.get("supplier")),
                    manufacturer=_entity_name(entry.get("manufacturer")),
                )
                self.components[key] = component
                made.append(component)
            else:
                component.entries += 1
                for identifier in identifiers:
                    if identifier not in component.identifiers:
                        component.identifiers.append(identifier)
                self.listed.setdefault("SBOM entries recorded as one Component", []).append(
                    f"{key} ({name})"
                )
            if ref is not None:
                self.by_ref[ref] = key
        for component in sorted(made, key=lambda c: c.key):
            readable = component.key.removeprefix("pkg:")
            component.id = self._id("component", component.key, readable)
        for component in made:
            for role, party in (
                ("supplier", component.supplier),
                ("manufacturer", component.manufacturer),
            ):
                if party is not None:
                    self._party(party, role)

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

    # dependencies

    def _dependencies(self) -> None:
        for entry in self.sbom.get("dependencies") or []:
            if not isinstance(entry, dict):
                raise SbomImportError(
                    f"{self.sbom_file.name}: a dependencies entry is not an object"
                )
            ref = _text(entry.get("ref"))
            targets = entry.get("dependsOn") or []
            if ref is None or not isinstance(targets, list):
                raise SbomImportError(f"{self.sbom_file.name}: a dependencies entry is malformed")
            for target in targets:
                target = _text(target)
                if target is None:
                    raise SbomImportError(f"{self.sbom_file.name}: a dependsOn entry is not text")
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
                if dependency not in self.components[source].uses:
                    self.components[source].uses.add(dependency)
                    self.edges += 1

    # the scan

    def _matches(self) -> None:
        assert self.scan is not None and self.scan_file is not None
        matches = self.scan["matches"]
        named: list[tuple[str, list[str], list[str], Mapping[str, Any], Mapping[str, Any]]] = []
        alias_of: dict[str, set[str]] = {}
        for index, match in enumerate(matches):
            vulnerability, related, artifact = _match_parts(match, index, self.scan_file.name)
            vid = _text(vulnerability["id"]) or ""
            ids = [vid] + [_text(r["id"]) or "" for r in related]
            cves = sorted({i for i in ids if CVE_ID.fullmatch(i)})
            others = [i for i in dict.fromkeys(ids) if not CVE_ID.fullmatch(i)]
            if len(cves) == 1:
                for other in others:
                    alias_of.setdefault(other, set()).add(cves[0])
            named.append((vid, cves, others, match, artifact))
        for vid, cves, others, match, artifact in named:
            # Joined by purl, not by ref (R-MATCH-2). A match on a part that is not a
            # Component here is left out whole, so no Vulnerability is left unlinked.
            purl = _text(artifact.get("purl"))
            key = _purl_key(purl) if purl else None
            if key is None or key not in self.components:
                self.notes["matches on a part that is not a Component of this SBOM"] += 1
                self.listed.setdefault("Matches left out (no Component with that purl)", []).append(
                    f"{vid} on {artifact.get('name')} {artifact.get('version')} ({purl})"
                )
                continue
            if not cves:
                # A GHSA-only match whose id another match pairs with one CVE is that CVE.
                known = set().union(*(alias_of.get(o, set()) for o in others)) if others else set()
                if len(known) == 1:
                    cves = sorted(known)
            if cves:
                refs = cves
                for other in others:
                    if len(cves) == 1:
                        self._vulnerability(cves[0]).aliases.add(other)
                    else:
                        self.listed.setdefault(
                            "Advisories that name several CVEs (one Vulnerability per CVE; "
                            "the advisory id is not an alias)",
                            [],
                        ).append(f"{other}: {', '.join(cves)}")
            else:
                refs = [vid]
                for other in others[1:]:
                    self._vulnerability(vid).aliases.add(other)
            for ref in refs:
                self._describe(self._vulnerability(ref), match, ref)
            self.scan_parts.add(key)
            details = match.get("matchDetails") or []
            for ref in refs:
                link = self.matches.setdefault((ref, key), _Match(vulnerability=ref, component=key))
                link.ids.add(vid)
                for detail in details if isinstance(details, list) else []:
                    if not isinstance(detail, dict):
                        continue
                    if isinstance(detail.get("type"), str):
                        link.types.add(detail["type"])
                        if detail["type"] not in MATCH_CONFIDENCE:
                            self.notes[
                                f"match details of a type this import does not rank "
                                f"({detail['type']}; no confidence from it)"
                            ] += 1
                    if isinstance(detail.get("matcher"), str):
                        link.matchers.add(detail["matcher"])
                    searched = detail.get("searchedBy")
                    if isinstance(searched, dict) and isinstance(searched.get("namespace"), str):
                        link.namespaces.add(searched["namespace"])
                    found = detail.get("found")
                    if isinstance(found, dict) and isinstance(found.get("versionConstraint"), str):
                        link.constraints.add(found["versionConstraint"])
            for record in [match.get("vulnerability")] + list(
                match.get("relatedVulnerabilities") or []
            ):
                self._cwes(record)

    def _vulnerability(self, ref: str) -> _Vulnerability:
        vulnerability = self.vulnerabilities.get(ref)
        if vulnerability is None:
            vulnerability = _Vulnerability(ref=ref, id=self._id("vulnerability", ref, ref))
            self.vulnerabilities[ref] = vulnerability
        return vulnerability

    def _describe(self, vulnerability: _Vulnerability, match: Mapping[str, Any], ref: str) -> None:
        if vulnerability.description is not None:
            return
        for record in [match.get("vulnerability")] + list(
            match.get("relatedVulnerabilities") or []
        ):
            if isinstance(record, dict) and record.get("id") == ref:
                text = _prose(record.get("description"))
                if text is not None:
                    vulnerability.description = text
                    return

    def _cwes(self, record: Any) -> None:
        if not isinstance(record, dict):
            return
        for entry in record.get("cwes") or []:
            if not isinstance(entry, dict):
                continue
            cve, cwe, source = (_text(entry.get(k)) for k in ("cve", "cwe", "source"))
            if cve is None or cve not in self.vulnerabilities:
                self.notes["CWE entries for an id that is not a Vulnerability here"] += 1
                continue
            if cwe is None or not CWE_ID.fullmatch(cwe):
                self.notes[f"CWE placeholders such as {cwe} (no weakness named; Table 6d)"] += 1
                continue
            if source is None:
                source = UNNAMED_SOURCE
            elif (cve, cwe, source) not in self.cwe_links:
                self._party(source, "cwe source")
            kinds = self.cwe_links.setdefault((cve, cwe, source), set())
            if isinstance(entry.get("type"), str):
                kinds.add(entry["type"])
            if cwe not in self.weaknesses:
                self.weaknesses[cwe] = self._id("weakness", cwe, cwe)

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
        doc["product_instances"] = [
            {
                "id": self.instance_id,
                "name": f"{self.info.image} at {self.info.digest[:19]}",
                "description": (
                    "The scanned build, keyed by the platform manifest digest the SBOM "
                    f"records (R-ID-1). SBOM made by {self.info.tool}"
                    + (f" at {self.info.timestamp}" if self.info.timestamp else "")
                    + "."
                ),
                "of_product": self.product_id,
                "version": self.info.digest,
                "identifiers": [self.info.digest, self.instance_purl],
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
        assert self.scan_file is not None
        out = []
        for (ref, key), link in sorted(self.matches.items()):
            vulnerability = self.vulnerabilities[ref]
            component = self.components[key]
            confidences = [MATCH_CONFIDENCE[t] for t in link.types if t in MATCH_CONFIDENCE]
            readable = f"{ref}-in-{component.id.removeprefix('component:')}"
            obj: dict[str, Any] = {
                "id": self._id("assertion", f"match:{ref}:{key}", readable),
                "name": f"{ref} is in {component.name} (Grype match, proposed)",
                "description": _match_description(link),
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


# The report -----------------------------------------------------------------------

# Where each input field goes. Any field not listed here is reported as left out with
# "not read by this import", so a new field never disappears unnoticed.
SBOM_FIELDS = {
    "": {
        "bomFormat": "checked: CycloneDX",
        "specVersion": f"checked: {CYCLONEDX_VERSION}",
        "serialNumber": "the model's header and this report (R-PROV-1: evidence, never a key)",
        "metadata": "see metadata",
        "components": "see components",
        "dependencies": "see dependencies",
        "$schema": "left out: the JSON schema's URL",
        "version": "left out: the BOM's revision number",
    },
    "metadata": {
        "timestamp": "the ProductInstance description and the model's header",
        "tools": "checked: Syft; its version goes in the header and this report",
        "component": "see metadata.component",
    },
    "metadata.component": {
        "type": "checked: container",
        "name": "Product.name and the versionless purl in Product.identifiers (R-ID-2)",
        "version": "ProductInstance.version and identifiers: the platform manifest digest (R-ID-1)",
        "bom-ref": "matched against dependencies[].ref",
    },
    "components": {
        "type": "Component.component_kind (A3); file entries are left out (R-ID-4)",
        "name": "Component.name",
        "version": "Component.version and the name",
        "purl": "Component.identifiers, and the Component's key without qualifiers (R-ID-3)",
        "cpe": "Component.identifiers",
        "properties": "the syft:cpe23 CPEs go in Component.identifiers; the rest is left out",
        "description": "Component.description",
        "bom-ref": "joins dependencies to Components",
        "supplier": "Component.supplied_by (Table 6c)",
        "manufacturer": "Component.manufactured_by (Table 6c)",
        "publisher": "left out: a publisher or maintainer is not a supplier (Table 6c)",
        "author": "left out: an author is not a supplier (Table 6c)",
        "authors": "left out: an author is not a supplier (Table 6c)",
        "licenses": "left out: no slot",
        "hashes": "left out: content identity is post-MVP (R-ID-4)",
        "externalReferences": "left out: no slot",
        "swid": "left out: no slot in this mapping",
    },
    "dependencies": {
        "ref": "the dependent Component",
        "dependsOn": "Component.uses_component, dependent to dependency (R-EDGE-1, R-EDGE-3)",
    },
}
SCAN_FIELDS = {
    "": {
        "matches": "see matches",
        "descriptor": "see descriptor",
        "source": "see source",
        "distro": "left out: the distribution Grype detected (also in the SBOM)",
    },
    "descriptor": {
        "name": "checked: grype",
        "version": "Assertion.generated_by (R-PROV-2)",
        "timestamp": "Assertion.asserted_at, in UTC",
        "db": "its schema version and build time go in Assertion.generated_by (R-PROV-2); "
        "the providers' capture times and the local path are left out",
        "configuration": "left out: Grype's settings",
    },
    "source": {
        "type": "left out: what kind of source Grype read (target's digest is what is checked)",
        "target": "its manifestDigest is checked against the SBOM's digest; the rest is left out",
    },
    "matches": {
        "vulnerability": "see matches.vulnerability",
        "relatedVulnerabilities": "see matches.relatedVulnerabilities",
        "matchDetails": "see matches.matchDetails",
        "artifact": "see matches.artifact",
    },
    "matches.vulnerability": {
        "id": "Vulnerability.catalog_ref, or alias_ids beside the CVE it names",
        "cwes": "instance_of Assertions to Weaknesses (R-CWE-1)",
        "description": "Vulnerability.description",
        "dataSource": "left out: no slot",
        "namespace": "left out: no slot (the match's namespace is in its Assertion)",
        "severity": "left out: no slot (ADR-0006 rates risk; RPT-0004 Table 6)",
        "urls": "left out: ids inside URLs are never read",
        "cvss": "left out: no slot (Table 6)",
        "epss": "left out: no slot (Table 6)",
        "fix": "left out: no slot (Table 6)",
        "advisories": "left out: no slot",
        "risk": "left out: Grype's risk number, not a tmodel risk (ADR-0006)",
        "knownExploited": "left out: no slot",
    },
    "matches.relatedVulnerabilities": {
        "id": "Vulnerability.catalog_ref (a CVE) or alias_ids",
        "cwes": "instance_of Assertions to Weaknesses (R-CWE-1)",
        "description": "Vulnerability.description",
        "dataSource": "left out: no slot",
        "namespace": "left out: no slot",
        "severity": "left out: no slot",
        "urls": "left out: ids inside URLs are never read",
        "cvss": "left out: no slot",
        "epss": "left out: no slot",
        "knownExploited": "left out: no slot",
    },
    "matches.matchDetails": {
        "type": "Assertion.confidence (R-MATCH-1) and its description",
        "matcher": "the Assertion's description",
        "searchedBy": "its namespace goes in the Assertion's description; the rest is left out",
        "found": "its versionConstraint goes in the Assertion's description; the rest is left out",
        "fix": "left out: no slot (Table 6)",
    },
    "matches.artifact": {
        "purl": "joins the match to its Component (R-MATCH-2)",
        "id": "left out: the join is by purl, not by ref (R-MATCH-2)",
        "name": "left out: the Component has it",
        "version": "left out: the Component has it",
        "type": "left out: the Component has it",
        "cpes": "left out: the Component has the SBOM's CPEs",
        "locations": "left out: content identity is post-MVP (R-ID-4)",
        "language": "left out: no slot",
        "licenses": "left out: no slot",
        "upstreams": "left out: no slot",
        "metadataType": "left out: no slot",
        "metadata": "left out: no slot",
    },
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
        lines.append(f"- Image: {b.info.image}, platform manifest digest {b.info.digest}.")
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
        if b.notes:
            lines += ["", "## Left out, with counts", ""]
            lines += [f"- {n} {reason}" for reason, n in sorted(b.notes.items())]
        for heading, items in sorted(b.listed.items()):
            lines += ["", f"## {heading}", ""]
            lines += [f"- {item}" for item in sorted(set(items))]
        lines += ["", "## Fields, and where they went", ""]
        lines += self._fields("SBOM", SBOM_FIELDS, self._sbom_inventory())
        if b.scan is not None:
            lines += self._fields("Scan", SCAN_FIELDS, self._scan_inventory())
        lines += [
            "",
            "## Next",
            "",
            "Check the model against the schema:",
            "",
            f"    linkml-validate -s {CONTAINER_SCHEMA} -C ExampleModelProposed {self.output_name}",
            "",
        ]
        return "\n".join(lines)

    def _fields(
        self, label: str, known: Mapping[str, Mapping[str, str]], seen: Mapping[str, Counter[str]]
    ) -> list[str]:
        lines = []
        for level in sorted(seen):
            where = known.get(level, {})
            name = f"{label} {level}" if level else f"{label} top level"
            lines.append(f"- {name}:")
            for key, n in sorted(seen[level].items()):
                target = where.get(key, "left out: not read by this import")
                lines.append(f"  - `{key}` ({n}): {target}")
        return lines

    def _sbom_inventory(self) -> dict[str, Counter[str]]:
        doc = self.b.sbom
        seen: dict[str, Counter[str]] = {"": Counter(doc.keys())}
        metadata = doc.get("metadata") or {}
        seen["metadata"] = Counter(metadata.keys())
        seen["metadata.component"] = Counter((metadata.get("component") or {}).keys())
        components = Counter()
        for entry in _flatten(doc.get("components") or [], self.b.sbom_file.name):
            components.update(entry.keys())
        seen["components"] = components
        dependencies = Counter()
        for entry in doc.get("dependencies") or []:
            dependencies.update(entry.keys())
        seen["dependencies"] = dependencies
        return seen

    def _scan_inventory(self) -> dict[str, Counter[str]]:
        doc = self.b.scan or {}
        seen: dict[str, Counter[str]] = {"": Counter(doc.keys())}
        seen["descriptor"] = Counter((doc.get("descriptor") or {}).keys())
        seen["source"] = Counter((doc.get("source") or {}).keys())
        for level in (
            "matches",
            "matches.vulnerability",
            "matches.relatedVulnerabilities",
            "matches.matchDetails",
            "matches.artifact",
        ):
            seen[level] = Counter()
        for match in doc.get("matches") or []:
            seen["matches"].update(match.keys())
            seen["matches.vulnerability"].update((match.get("vulnerability") or {}).keys())
            seen["matches.artifact"].update((match.get("artifact") or {}).keys())
            for record in match.get("relatedVulnerabilities") or []:
                seen["matches.relatedVulnerabilities"].update(record.keys())
            details = match.get("matchDetails")
            for detail in details if isinstance(details, list) else []:
                if isinstance(detail, dict):  # the builder skips any other entry too
                    seen["matches.matchDetails"].update(detail.keys())
        return {level: counter for level, counter in seen.items() if counter}


# Writing ----------------------------------------------------------------------------


def _header(builder: _Builder, output_name: str) -> str:
    b = builder
    lines = [
        f"# STARTER MODEL, imported by `tmodel import-sbom` (tmodel {__version__}; #257, DL-0068)",
        "#",
        f"# Product: {b.info.image}, the image whose platform manifest digest is",
        f"# {b.info.digest}.",
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
        "",
        "",
    ]
    return "\n".join(lines)


class _Dumper(yaml.SafeDumper):
    """Block YAML as the example models write it: lists indented under their key, keys in
    the order given, and no anchors or aliases."""

    def ignore_aliases(self, data: Any) -> bool:
        return True

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        return super().increase_indent(flow, False)


def _dump(doc: Mapping[str, Any]) -> str:
    return yaml.dump(
        doc,
        Dumper=_Dumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=1_000_000,
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


def _check_outputs(
    sbom: Path, scan: Path | None, out: Path, report: Path | None, force: bool
) -> None:
    if out.suffix not in MODEL_SUFFIXES:
        raise SbomImportError(
            f"{out.name}: the model file must end in .yaml, so the engine reads it"
        )
    inputs = {_same_file_key(p) for p in (sbom, scan) if p is not None}
    for path in [out] + ([report] if report is not None else []):
        if _same_file_key(path) in inputs:
            raise SbomImportError(f"{path.name}: is an input; refusing to write over it")
        if path.exists() and not force:
            raise SbomImportError(
                f"{path.name}: already exists; people edit starter models, so it is not "
                "replaced without --force"
            )
        if not path.parent.is_dir():
            raise SbomImportError(f"{path.name}: its folder does not exist")
    if report is not None and _same_file_key(report) == _same_file_key(out):
        raise SbomImportError("the report and the model cannot be the same file")


def _same_file_key(path: Path) -> str:
    return str(path.resolve(strict=False))


def _write(path: Path, text: str) -> None:
    """Write `text` to a temporary file beside `path`, then move it into place."""
    handle = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=".import-sbom-", suffix=".tmp", delete=False
    )
    try:
        with handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(handle.name, path)
    except BaseException:
        Path(handle.name).unlink(missing_ok=True)
        raise


def _display_path(path: Path) -> str:
    """The output path as given, or only its name when it is absolute (no home folders)."""
    return path.name if path.is_absolute() else path.as_posix()


# Small helpers ---------------------------------------------------------------------


def _flatten(entries: Iterable[Any], name: str, depth: int = 0) -> Iterable[Mapping[str, Any]]:
    """Components and their nested components, depth first. Syft writes no nesting."""
    if depth > 32:
        raise SbomImportError(f"{name}: components nest more than 32 levels deep")
    for entry in entries:
        if not isinstance(entry, dict):
            raise SbomImportError(f"{name}: a component is not a JSON object")
        yield entry
        nested = entry.get("components")
        if isinstance(nested, list):
            yield from _flatten(nested, name, depth + 1)


def _match_parts(
    match: Any, index: int, name: str
) -> tuple[Mapping[str, Any], list[Mapping[str, Any]], Mapping[str, Any]]:
    if not isinstance(match, dict):
        raise SbomImportError(f"{name}: matches[{index}] is not a JSON object")
    vulnerability = match.get("vulnerability")
    if not isinstance(vulnerability, dict) or not _text(vulnerability.get("id")):
        raise SbomImportError(f"{name}: matches[{index}] has no vulnerability id")
    related = match.get("relatedVulnerabilities") or []
    if not isinstance(related, list) or not all(
        isinstance(r, dict) and _text(r.get("id")) for r in related
    ):
        raise SbomImportError(f"{name}: matches[{index}].relatedVulnerabilities is malformed")
    artifact = match.get("artifact")
    if not isinstance(artifact, dict):
        raise SbomImportError(f"{name}: matches[{index}] has no artifact")
    return vulnerability, related, artifact


def _match_description(link: _Match) -> str:
    parts = [f"Grype matched {', '.join(sorted(link.ids))}"]
    if link.types:
        parts.append(f"by {', '.join(sorted(link.types))}")
    if link.matchers:
        parts.append(f"({', '.join(sorted(link.matchers))})")
    text = " ".join(parts)
    if link.namespaces:
        text += f" in {', '.join(sorted(link.namespaces))}"
    if link.constraints:
        text += f"; affected versions {'; '.join(sorted(link.constraints))}"
    return text + ". A match is a lead, not a verdict (R-MATCH-1)."


def _identifiers(entry: Mapping[str, Any]) -> list[str]:
    """The entry's purl and CPEs, as written: purl, then `cpe`, then Syft's syft:cpe23."""
    out: list[str] = []
    for value in [entry.get("purl"), entry.get("cpe")] + [
        p.get("value")
        for p in entry.get("properties") or []
        if isinstance(p, dict) and p.get("name") == "syft:cpe23"
    ]:
        text = _text(value)
        if text is not None and text not in out:
            out.append(text)
    return out


def _purl_key(purl: str) -> str | None:
    """`pkg:type/namespace/name@version`, with the type lowercased and no qualifiers or subpath."""
    if not purl.lower().startswith("pkg:"):
        return None
    rest = purl[4:].split("#", 1)[0].split("?", 1)[0].strip("/")
    if "/" not in rest:
        return None
    kind, remainder = rest.split("/", 1)
    if not kind or not remainder:
        return None
    return f"pkg:{kind.lower()}/{remainder}"


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


def _entity_name(value: Any) -> str | None:
    if isinstance(value, dict):
        return _text(value.get("name"))
    return None


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
    """An RFC 3339 date and time in UTC, to the second, or None."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        moment = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if moment.tzinfo is None:
        return None
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug(text: str, limit: int = 80) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "x"
    if len(slug) > limit:
        slug = slug[: limit - 9].rstrip("-") + "-" + _short_hash(text)
    return slug


def _short_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
