"""`tmodel import-sbom`: a starter model from Syft's SBOM and Grype's scan (#257, DL-0068).

The fixture is the image RPT-0004's pilot scanned: alpine 3.24.2 for linux/arm64,
platform manifest digest sha256:260479a1cfaf..., SBOM by Syft 1.52.0 and scan by
Grype 0.119.0 with the database built 2026-10-08T06:33:47Z. Its numbers are the
pilot's (pilot.md): 95 SBOM entries (16 library, 1 operating-system, 78 file), 12
dependency entries with 24 edges, and 30 matches for 15 CVEs. The scan file is Grype's
output with only its local paths shortened (DL-0068).

The sections headed "Review of c39f2a4" hold the regression tests for the eight findings
of @kriishnaa-18's review; each failed on c39f2a4 before its fix (DL-0068, "Review
changes").
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
from collections import Counter
from pathlib import Path

import pytest
import yaml

from engine import cli, core, import_sbom
from engine.import_sbom import SbomImportError
from engine.load.vector import load_vector

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures" / "sbom-import"
SBOM = FIXTURES / "alpine-3.24.2.cdx.json"
SCAN = FIXTURES / "alpine-3.24.2.grype.json"
DIGEST = "sha256:260479a1cfaf304c4c20da7f8405d3ce313513dcd534bb743257bdd2fe0f3e2d"
ZLIB = "pkg:apk/alpine/zlib@1.3.2-r0?arch=aarch64&distro=alpine-3.24.2"
X86_ZLIB = ZLIB.replace("arch=aarch64", "arch=x86_64")  # the same package for another CPU
BUSYBOX = "pkg:apk/alpine/busybox@1.37.0-r31?arch=aarch64&distro=alpine-3.24.2"


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def dump(tmp_path: Path, name: str, doc: object) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def sbom_doc() -> dict:
    return json.loads(SBOM.read_text(encoding="utf-8"))


def scan_doc() -> dict:
    return json.loads(SCAN.read_text(encoding="utf-8"))


def by_id(doc: dict, collection: str) -> dict[str, dict]:
    return {obj["id"]: obj for obj in doc.get(collection, [])}


def folder(tmp_path: Path, name: str) -> Path:
    path = tmp_path / name
    path.mkdir()
    return path


@pytest.fixture
def imported(tmp_path: Path) -> tuple[Path, dict, str]:
    out = tmp_path / "pv-05-alpine.yaml"
    result = import_sbom.run(SBOM, scan=SCAN, output=out)
    return out, load(out), result.report_text


# The fixture: what the pilot found ---------------------------------------------------


def test_the_alpine_fixture_gives_the_pilots_numbers(imported) -> None:
    _, doc, _ = imported
    kinds = Counter(c["component_kind"] for c in doc["components"])
    assert kinds == {"library": 16, "operating_system": 1}  # the 78 files are left out
    edges = sum(len(c.get("uses_component", [])) for c in doc["components"])
    assert edges == 24
    assert len(doc["vulnerabilities"]) == 15
    assert all(v["catalog_ref"].startswith("CVE-") for v in doc["vulnerabilities"])
    predicates = Counter(a["predicate"] for a in doc["assertions"])
    assert predicates == {"propagates_to": 30, "instance_of": 15}
    assert len(doc["weaknesses"]) == 9


def test_the_product_and_the_scanned_build_have_their_keys(imported) -> None:
    _, doc, _ = imported
    (product,) = doc["products"]
    assert product["identifiers"] == [
        "pkg:oci/alpine?repository_url=index.docker.io/library/alpine"
    ]
    (instance,) = doc["product_instances"]
    assert instance["of_product"] == product["id"]
    assert instance["version"] == DIGEST
    assert instance["identifiers"][0] == DIGEST  # R-ID-1
    assert sorted(instance["build_composed_of"]) == sorted(c["id"] for c in doc["components"])
    assert "composed_of" not in product  # the SBOM never fills the design level (R-EDGE-2)


def test_components_keep_every_purl_and_cpe(imported) -> None:
    _, doc, _ = imported
    zlib = next(c for c in doc["components"] if c["name"] == "zlib 1.3.2-r0")
    assert zlib["version"] == "1.3.2-r0"
    assert zlib["identifiers"][0] == ZLIB
    assert all(i.startswith(("pkg:", "cpe:2.3:")) for i in zlib["identifiers"])
    assert "cpe:2.3:a:zlib:zlib:1.3.2-r0:*:*:*:*:*:*:*" in zlib["identifiers"]


def test_every_claim_is_proposed_with_its_provenance(imported) -> None:
    _, doc, _ = imported
    for assertion in doc["assertions"]:
        assert assertion["assertion_status"] == "proposed"
        assert assertion["asserted_at"] == "2026-11-25T09:54:07Z"  # the scan's time, in UTC
        assert assertion["generated_by"] == (
            "Grype 0.119.0, vulnerability database v6.1.10 built 2026-10-08T06:33:47Z"
        )
        assert sha256(SCAN) in assertion["evidence"]
    for match in (a for a in doc["assertions"] if a["predicate"] == "propagates_to"):
        assert match["asserted_by"] == "party:grype"
        assert match["evidence"] == [sha256(SCAN), sha256(SBOM)]
    assert by_id(doc, "parties")["party:grype"]["party_kind"] == "software_agent"
    for absent in ("reviews", "threat_instances", "attack_steps", "attack_paths", "mitigations"):
        assert absent not in doc  # an SBOM and a scan say nothing about these (Table 6f)


def test_confidence_follows_grypes_match_type(imported) -> None:
    _, doc, _ = imported
    matches = [a for a in doc["assertions"] if a["predicate"] == "propagates_to"]
    exact = [a for a in matches if a["confidence"] == "high"]
    assert [a["subject"] for a in exact] == ["vulnerability:cve-2026-85091"]  # Alpine's feed
    assert "exact-direct-match" in exact[0]["description"]
    assert Counter(a["confidence"] for a in matches) == {"high": 1, "low": 29}  # NVD CPE data


def test_each_cwe_link_names_who_assigned_it(imported) -> None:
    _, doc, _ = imported
    parties = by_id(doc, "parties")
    link = next(
        a
        for a in doc["assertions"]
        if a["predicate"] == "instance_of" and a["subject"] == "vulnerability:cve-2026-85091"
    )
    assert link["object"] == "weakness:cwe-787"
    assert parties[link["asserted_by"]]["name"] == "disclosure@vulncheck.com"
    assert by_id(doc, "weaknesses")["weakness:cwe-787"]["catalog_ref"] == "CWE-787"


def test_the_same_files_give_the_same_bytes(tmp_path: Path) -> None:
    (tmp_path / "one").mkdir()
    (tmp_path / "two").mkdir()
    first = import_sbom.run(SBOM, scan=SCAN, output=tmp_path / "one" / "model.yaml")
    second = import_sbom.run(SBOM, scan=SCAN, output=tmp_path / "two" / "model.yaml")
    model = (tmp_path / "one" / "model.yaml").read_bytes()
    assert model == (tmp_path / "two" / "model.yaml").read_bytes()
    assert model == first.model_text.encode("utf-8")
    assert first.report_text == second.report_text


def test_the_report_accounts_for_every_field(imported) -> None:
    _, _, report = imported
    assert sha256(SBOM) in report and sha256(SCAN) in report
    assert "78 SBOM file entries (R-ID-4" in report
    assert (
        "`components[].publisher` (16): left out: a publisher or maintainer is not a supplier"
        in report
    )
    assert "`matches[].vulnerability.cvss` (30, holding " in report
    assert "30 matches on 6 of the 17 Components" in report
    assert "not read by this import" not in report  # the fixture holds no unknown field
    assert "A part with no match is not proven safe" in report


# The engine and the schema accept it -------------------------------------------------


def test_the_engine_lists_and_opens_the_model(imported, tmp_path: Path, monkeypatch) -> None:
    out, _, _ = imported
    vectors = tmp_path / "spec" / "vectors"
    vectors.mkdir(parents=True)
    shutil.copy(out, vectors / out.name)
    monkeypatch.setattr(core, "APPROVED_VECTOR_DIRECTORY", vectors)
    listed = core.list_models()
    assert listed["problems"] == []
    assert [m["file"] for m in listed["models"]] == [out.name]
    graph = core.model_graph(out.name)
    edges = Counter(e["relationship_type"] for e in graph["edges"])
    assert edges["propagates_to"] == 30 and edges["instance_of"] == 15
    assert edges["uses_component"] == 24 and edges["build_composed_of"] == 17
    load_vector(out)  # the attack-graph checks pass too: the model has no paths yet


def test_the_model_is_a_valid_proposed_example(imported) -> None:
    validator = pytest.importorskip("linkml.validator", reason="linkml is the schema job's tool")
    out, _, _ = imported
    report = validator.validate_file(
        out,
        str(ROOT / "spec" / "vectors" / "example-container-proposed.linkml.yaml"),
        "ExampleModelProposed",
    )
    assert [r.message for r in report.results] == []


# Vulnerability ids (#257: one Vulnerability per CVE) ---------------------------------


def match(vid: str, related: tuple[str, ...] = (), *, purl: str = ZLIB, cwes=(), urls=()):
    """A Grype match shaped like the fixture's, on zlib unless `purl` names another of the
    SBOM's packages, whose name and version it then carries, as Grype's artifact does."""
    template = copy.deepcopy(scan_doc()["matches"][0])
    vulnerability = template["vulnerability"]
    vulnerability.update(id=vid, urls=list(urls), cwes=[])
    vulnerability.pop("description", None)
    vulnerability["cwes"] = [
        {"cve": cve, "cwe": cwe, "source": source, "type": "Primary"} for cve, cwe, source in cwes
    ]
    template["relatedVulnerabilities"] = [
        {"id": r, "namespace": "nvd:cpe", "urls": [], "cwes": []} for r in related
    ]
    template["matchDetails"] = [{"type": "exact-direct-match", "matcher": "apk-matcher"}]
    template["artifact"]["purl"] = purl
    entry = next((c for c in sbom_doc()["components"] if c.get("purl") == purl), None)
    if entry is not None:
        template["artifact"].update(name=entry["name"], version=entry["version"])
    return template


def import_matches(tmp_path: Path, matches: list[dict], sbom: dict | None = None):
    """Import the fixture's SBOM (or `sbom`) with a scan holding only `matches`."""
    scan = scan_doc()
    scan["matches"] = matches
    sbom_path = SBOM if sbom is None else dump(tmp_path, "sbom.json", sbom)
    path = dump(tmp_path, "scan.json", scan)
    result = import_sbom.run(sbom_path, scan=path, output=tmp_path / "model.yaml")
    return load(tmp_path / "model.yaml"), result.report_text


def vulnerabilities(doc: dict) -> dict[str, list[str]]:
    return {v["catalog_ref"]: v.get("alias_ids", []) for v in doc.get("vulnerabilities", [])}


def test_an_advisory_naming_one_cve_is_that_cves_alias(tmp_path: Path) -> None:
    doc, _ = import_matches(tmp_path, [match("GHSA-aaaa-bbbb-cccc", ("CVE-2026-0001",))])
    assert vulnerabilities(doc) == {"CVE-2026-0001": ["GHSA-aaaa-bbbb-cccc"]}


def test_a_match_with_no_cve_keeps_grypes_id(tmp_path: Path) -> None:
    doc, _ = import_matches(tmp_path, [match("GHSA-aaaa-bbbb-cccc")])
    assert vulnerabilities(doc) == {"GHSA-aaaa-bbbb-cccc": []}


def test_an_advisory_naming_several_cves_is_listed_not_aliased(tmp_path: Path) -> None:
    doc, report = import_matches(
        tmp_path, [match("ALAS-2026-1001", ("CVE-2026-0001", "CVE-2026-0002"))]
    )
    assert vulnerabilities(doc) == {"CVE-2026-0001": [], "CVE-2026-0002": []}
    assert "- ALAS-2026-1001: CVE-2026-0001, CVE-2026-0002" in report
    assert sum(a["predicate"] == "propagates_to" for a in doc["assertions"]) == 2


def test_an_advisory_id_another_match_pairs_with_a_cve_is_that_cve(tmp_path: Path) -> None:
    doc, _ = import_matches(
        tmp_path,
        [match("GHSA-aaaa-bbbb-cccc"), match("GHSA-aaaa-bbbb-cccc", ("CVE-2026-0001",))],
    )
    assert vulnerabilities(doc) == {"CVE-2026-0001": ["GHSA-aaaa-bbbb-cccc"]}


def test_an_id_only_inside_a_url_is_not_read(tmp_path: Path) -> None:
    url = "https://rustsec.org/advisories/RUSTSEC-2024-0429.html"
    doc, _ = import_matches(tmp_path, [match("CVE-2026-0001", urls=(url,))])
    assert vulnerabilities(doc) == {"CVE-2026-0001": []}


def test_placeholder_cwes_are_left_out_and_counted(tmp_path: Path) -> None:
    cwes = (
        ("CVE-2026-0001", "NVD-CWE-Other", "nvd@nist.gov"),
        ("CVE-2026-0001", "CWE-79", "nvd@nist.gov"),
    )
    doc, report = import_matches(tmp_path, [match("CVE-2026-0001", cwes=cwes)])
    links = [a for a in doc["assertions"] if a["predicate"] == "instance_of"]
    assert [a["object"] for a in links] == ["weakness:cwe-79"]
    assert "1 CWE placeholders such as NVD-CWE-Other" in report


def test_a_match_on_a_part_the_sbom_lacks_is_reported(tmp_path: Path) -> None:
    doc, report = import_matches(tmp_path, [match("CVE-2026-0001", purl="pkg:npm/left-pad@1.0.0")])
    for left_out in ("vulnerabilities", "assertions", "weaknesses"):
        assert left_out not in doc  # the whole match is left out, not half of it
    assert "CVE-2026-0001 on zlib 1.3.2-r0 (pkg:npm/left-pad@1.0.0)" in report


# The SBOM side -------------------------------------------------------------------


def import_sbom_doc(tmp_path: Path, sbom: dict, **kwargs) -> tuple[dict, str]:
    path = dump(tmp_path, "sbom.json", sbom)
    result = import_sbom.run(path, output=tmp_path / "model.yaml", **kwargs)
    return load(tmp_path / "model.yaml"), result.report_text


def test_supplier_and_manufacturer_come_only_from_those_fields(tmp_path: Path) -> None:
    sbom = sbom_doc()
    zlib = next(c for c in sbom["components"] if c.get("name") == "zlib")
    zlib["supplier"] = {"name": "Example Supplier Inc."}
    zlib["manufacturer"] = {"name": "Example Maker Ltd."}
    doc, _ = import_sbom_doc(tmp_path, sbom)
    parties = {p["id"]: p["name"] for p in doc["parties"]}
    component = next(c for c in doc["components"] if c["name"] == "zlib 1.3.2-r0")
    assert parties[component["supplied_by"]] == "Example Supplier Inc."
    assert parties[component["manufactured_by"]] == "Example Maker Ltd."
    # The 16 publishers (package maintainers) are not suppliers (Table 6c).
    assert sorted(parties.values()) == ["Example Maker Ltd.", "Example Supplier Inc."]
    assert sum("supplied_by" in c for c in doc["components"]) == 1


def test_without_a_scan_there_are_no_vulnerabilities(tmp_path: Path) -> None:
    doc, report = import_sbom_doc(tmp_path, sbom_doc())
    assert len(doc["components"]) == 17
    for absent in ("vulnerabilities", "weaknesses", "assertions", "parties"):
        assert absent not in doc
    assert "No scan was given" in report


def test_dependency_edges_that_are_not_between_components_are_counted(tmp_path: Path) -> None:
    sbom = sbom_doc()
    zlib = next(c for c in sbom["components"] if c.get("name") == "zlib")
    a_file = next(c for c in sbom["components"] if c["type"] == "file")
    image = sbom["metadata"]["component"]["bom-ref"]
    sbom["dependencies"] += [
        {"ref": zlib["bom-ref"], "dependsOn": [a_file["bom-ref"], zlib["bom-ref"]]},
        {"ref": image, "dependsOn": [zlib["bom-ref"]]},
    ]
    doc, report = import_sbom_doc(tmp_path, sbom)
    assert sum(len(c.get("uses_component", [])) for c in doc["components"]) == 24
    assert "1 dependency edges to or from an entry that is not a Component" in report
    assert "1 dependency edges from a Component to itself" in report
    assert "1 dependency edges from the image itself" in report


def zlib_copy(sbom: dict, purl: str = ZLIB) -> dict:
    """A second zlib entry in `sbom`, with its own bom-ref and the given purl."""
    zlib = copy.deepcopy(next(c for c in sbom["components"] if c.get("name") == "zlib"))
    zlib["bom-ref"] += "-copy"
    zlib["purl"] = purl
    sbom["components"].append(zlib)
    return zlib


def test_entries_with_the_same_purl_are_one_component(tmp_path: Path) -> None:
    sbom = sbom_doc()
    zlib_copy(sbom)  # the same package found twice, as in an image with two copies
    doc, report = import_sbom_doc(tmp_path, sbom)
    assert len(doc["components"]) == 17
    merged = next(c for c in doc["components"] if c["name"] == "zlib 1.3.2-r0")
    assert [i for i in merged["identifiers"] if i.startswith("pkg:")] == [ZLIB]
    assert "SBOM entries recorded as one Component" in report


# Refusals: nothing is written --------------------------------------------------------


def mutate(doc: dict, path: str, value: object) -> dict:
    node = doc
    *parents, last = path.split(".")
    for key in parents:
        node = node[int(key)] if key.isdigit() else node[key]
    node[int(last) if last.isdigit() else last] = value
    return doc


@pytest.mark.parametrize(
    ("which", "path", "value", "message"),
    [
        ("sbom", "bomFormat", "SPDX", "not a CycloneDX SBOM"),
        ("sbom", "specVersion", "1.6", "CycloneDX '1.6'"),
        ("sbom", "metadata.tools.components.0.name", "trivy", "does not name Syft"),
        ("sbom", "metadata.component.type", "application", "is 'application', not container"),
        ("sbom", "metadata.component.version", "3.24.2", "not the image's digest"),
        ("sbom", "components.0.type", "widget", "not one of CycloneDX 1.7's component types"),
        ("scan", "descriptor.name", "trivy", "not Grype's JSON output"),
        ("scan", "matches", {}, "no matches list"),
        ("scan", "descriptor.timestamp", "yesterday", "descriptor.timestamp"),
        ("scan", "descriptor.db.status.built", None, "build time"),
        ("scan", "source.target.manifestDigest", "sha256:" + "0" * 64, "the scan is of"),
    ],
)
def test_bad_inputs_are_refused_before_anything_is_written(
    tmp_path: Path, which: str, path: str, value: object, message: str
) -> None:
    sbom, scan = sbom_doc(), scan_doc()
    mutate(sbom if which == "sbom" else scan, path, value)
    out = tmp_path / "model.yaml"
    with pytest.raises(SbomImportError, match=message):
        import_sbom.run(
            dump(tmp_path, "s.json", sbom), scan=dump(tmp_path, "g.json", scan), output=out
        )
    assert not out.exists()


def test_a_repeated_bom_ref_is_refused(tmp_path: Path) -> None:
    sbom = sbom_doc()
    sbom["components"][1]["bom-ref"] = sbom["components"][0]["bom-ref"]
    with pytest.raises(SbomImportError, match="appears twice"):
        import_sbom.run(dump(tmp_path, "s.json", sbom), output=tmp_path / "model.yaml")


def test_text_that_is_not_json_is_refused(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{ not json", encoding="utf-8")
    with pytest.raises(SbomImportError, match="not valid JSON"):
        import_sbom.run(bad, output=tmp_path / "model.yaml")
    with pytest.raises(SbomImportError, match="a JSON object at the top level"):
        import_sbom.run(dump(tmp_path, "list.json", []), output=tmp_path / "model.yaml")


def test_an_oversized_file_is_refused(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(import_sbom, "MAX_INPUT_BYTES", 100)
    with pytest.raises(SbomImportError, match="larger than 100 bytes"):
        import_sbom.run(SBOM, output=tmp_path / "model.yaml")


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="needs a FIFO")
def test_a_fifo_is_refused_without_waiting(tmp_path: Path) -> None:
    fifo = tmp_path / "sbom.json"
    os.mkfifo(fifo)
    with pytest.raises(SbomImportError, match="not a regular file"):
        import_sbom.run(fifo, output=tmp_path / "model.yaml")


def test_an_existing_model_is_kept_unless_forced(tmp_path: Path) -> None:
    out = tmp_path / "model.yaml"
    out.write_text("edited by a person\n", encoding="utf-8")
    with pytest.raises(SbomImportError, match="already exists"):
        import_sbom.run(SBOM, scan=SCAN, output=out)
    assert out.read_text(encoding="utf-8") == "edited by a person\n"
    import_sbom.run(SBOM, scan=SCAN, output=out, force=True)
    assert load(out)["products"]


@pytest.mark.parametrize(
    ("output", "report", "message"),
    [
        ("model.json", None, "must end in .yaml"),
        ("missing/model.yaml", None, "its folder does not exist"),
        ("model.yaml", "model.yaml", "cannot be the same file"),
    ],
)
def test_bad_outputs_are_refused(tmp_path: Path, output: str, report, message: str) -> None:
    with pytest.raises(SbomImportError, match=message):
        import_sbom.run(
            SBOM, output=tmp_path / output, report=None if report is None else tmp_path / report
        )


def test_an_input_is_never_written_over(tmp_path: Path) -> None:
    sbom = tmp_path / "sbom.yaml"  # an SBOM saved under a .yaml name
    shutil.copy(SBOM, sbom)
    with pytest.raises(SbomImportError, match="is an input"):
        import_sbom.run(sbom, output=sbom, force=True)
    assert sbom.read_bytes() == SBOM.read_bytes()


def test_the_header_never_names_a_home_folder(tmp_path: Path) -> None:
    out = tmp_path / "pv-05-alpine.yaml"
    import_sbom.run(SBOM, scan=SCAN, output=out)  # an absolute path
    text = out.read_text(encoding="utf-8")
    assert f"-C ExampleModelProposed {out.name}\n" in text
    assert str(tmp_path) not in text


# The command line ----------------------------------------------------------------


def test_the_command_prints_the_report(tmp_path: Path, capsys) -> None:
    out = tmp_path / "model.yaml"
    assert cli.main(["import-sbom", str(SBOM), "--scan", str(SCAN), "-o", str(out)]) == 0
    assert capsys.readouterr().out.startswith("# tmodel import-sbom report")
    assert load(out)["product_instances"][0]["version"] == DIGEST


def test_the_command_can_write_the_report(tmp_path: Path, capsys) -> None:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    argv = ["import-sbom", str(SBOM), "-o", str(out), "--report", str(report)]
    assert cli.main(argv) == 0
    assert capsys.readouterr().out.startswith("wrote ")
    assert report.read_text(encoding="utf-8").startswith("# tmodel import-sbom report")


def test_the_command_exits_2_on_a_refused_input(tmp_path: Path, capsys) -> None:
    bad = dump(tmp_path, "bad.json", {"bomFormat": "SPDX"})
    assert cli.main(["import-sbom", str(bad), "-o", str(tmp_path / "model.yaml")]) == 2
    assert "error: bad.json: not a CycloneDX SBOM" in capsys.readouterr().err
    assert not (tmp_path / "model.yaml").exists()


# Helpers -------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("image", "expected"),
    [
        ("alpine", ("index.docker.io", "library/alpine")),
        ("index.docker.io/library/alpine", ("index.docker.io", "library/alpine")),
        ("docker.io/library/alpine:3.24.2", ("index.docker.io", "library/alpine")),
        ("bkimminich/juice-shop", ("index.docker.io", "bkimminich/juice-shop")),
        ("ghcr.io/Org/App@sha256:" + "a" * 64, ("ghcr.io", "org/app")),
        ("localhost:5000/team/app:dev", ("localhost:5000", "team/app")),
    ],
)
def test_image_names_resolve_as_docker_resolves_them(image: str, expected) -> None:
    assert import_sbom._image_repository(image) == expected


@pytest.mark.parametrize(
    ("purl", "key"),
    [
        (ZLIB, ZLIB),  # Syft's purls are already in this form
        (X86_ZLIB, X86_ZLIB),  # a qualifier is part of the key (R-ID-3)
        ("pkg:apk/alpine/zlib@1.3.2-r0?distro=alpine-3.24.2&arch=aarch64", ZLIB),
        ("pkg:APK/alpine/zlib@1.3.2%2Dr0?ARCH=aarch64&distro=alpine-3.24.2&empty=", ZLIB),
        ("pkg:npm/@angular/core@17.0.0", "pkg:npm/%40angular/core@17.0.0"),
        (
            "pkg:NPM/%40angular/core@17.0.0?x=y#sub/./path/",
            "pkg:npm/%40angular/core@17.0.0?x=y#sub/path",
        ),
        ("pkg://golang/github.com/a/b@v1.2.3", "pkg:golang/github.com/a/b@v1.2.3"),
        ("pkg:deb/debian/curl@7.88.1-10%2Bdeb12u5", "pkg:deb/debian/curl@7.88.1-10%2Bdeb12u5"),
        ("pkg:deb/debian/curl@7.88.1-10+deb12u5", "pkg:deb/debian/curl@7.88.1-10%2Bdeb12u5"),
        ("not-a-purl", None),
        ("pkg:npm", None),
        ("pkg:npm/a@1?x=1&X=2", None),  # a qualifier key may appear once
        ("pkg:1npm/a@1", None),  # a type cannot start with a digit
    ],
)
def test_a_components_key_is_its_normalized_purl(purl: str, key) -> None:
    assert import_sbom._purl_key(purl) == key


@pytest.mark.parametrize(
    ("value", "utc"),
    [
        ("2026-11-25T01:54:07.434011-08:00", "2026-11-25T09:54:07Z"),
        ("2026-10-08T06:33:47Z", "2026-10-08T06:33:47Z"),
        ("2026-11-25T01:54:07", None),  # no time zone: not a moment
        ("yesterday", None),
        (None, None),
    ],
)
def test_times_are_read_as_utc(value, utc) -> None:
    assert import_sbom._utc(value) == utc


# Review of c39f2a4, finding 1: a Component's purl keeps its qualifiers ----------------


def test_entries_whose_purls_differ_in_a_qualifier_are_two_components(tmp_path: Path) -> None:
    sbom = sbom_doc()
    zlib_copy(sbom, X86_ZLIB)  # the same name and version, built for another CPU
    doc, report = import_sbom_doc(tmp_path, sbom)
    assert len(doc["components"]) == 18
    zlibs = [c for c in doc["components"] if c["name"] == "zlib 1.3.2-r0"]
    assert sorted(c["identifiers"][0] for c in zlibs) == sorted([ZLIB, X86_ZLIB])
    assert "SBOM entries recorded as one Component" not in report


def test_a_match_joins_only_the_component_with_its_purl(tmp_path: Path) -> None:
    sbom = sbom_doc()
    zlib_copy(sbom, X86_ZLIB)
    doc, _ = import_matches(tmp_path, [match("CVE-2026-0001", purl=X86_ZLIB)], sbom)
    (link,) = [a for a in doc["assertions"] if a["predicate"] == "propagates_to"]
    assert by_id(doc, "components")[link["object"]]["identifiers"][0] == X86_ZLIB


def test_a_match_on_a_build_the_sbom_lacks_is_left_out(tmp_path: Path) -> None:
    # The SBOM's zlib is the aarch64 build; a match on the x86_64 one is not about it.
    doc, report = import_matches(tmp_path, [match("CVE-2026-0001", purl=X86_ZLIB)])
    for left_out in ("vulnerabilities", "assertions"):
        assert left_out not in doc
    assert f"CVE-2026-0001 on zlib 1.3.2-r0 ({X86_ZLIB}); the SBOM has it only as {ZLIB}" in report


def test_equivalent_spellings_of_a_purl_join(tmp_path: Path) -> None:
    # Qualifiers in another order, an upper-case type and key, and a percent-encoded
    # version spell the same purl (the purl specification's rules for every type).
    spelled = "pkg:APK/alpine/zlib@1.3.2%2Dr0?distro=alpine-3.24.2&ARCH=aarch64"
    doc, _ = import_matches(tmp_path, [match("CVE-2026-0001", purl=spelled)])
    (link,) = [a for a in doc["assertions"] if a["predicate"] == "propagates_to"]
    assert by_id(doc, "components")[link["object"]]["identifiers"][0] == ZLIB


def test_entries_sharing_a_purl_but_not_a_version_are_refused(tmp_path: Path) -> None:
    sbom = sbom_doc()
    zlib_copy(sbom)["version"] = "1.3.2-r1"
    out = tmp_path / "model.yaml"
    with pytest.raises(SbomImportError, match="give different versions"):
        import_sbom.run(dump(tmp_path, "s.json", sbom), output=out)
    assert not out.exists()


def test_a_version_that_differs_from_its_purls_is_reported(tmp_path: Path) -> None:
    sbom = sbom_doc()
    zlib = next(c for c in sbom["components"] if c.get("name") == "zlib")
    zlib["version"] = "1.3.2-r9"  # its purl says 1.3.2-r0
    _, report = import_sbom_doc(tmp_path, sbom)
    assert "zlib: version 1.3.2-r9, but its purl says 1.3.2-r0" in report


def test_a_match_whose_package_disagrees_with_the_sbom_is_left_out(tmp_path: Path) -> None:
    row = match("CVE-2026-0001")
    row["artifact"]["version"] = "1.3.2-r1"  # the SBOM's zlib with this purl is 1.3.2-r0
    doc, report = import_matches(tmp_path, [row])
    assert "assertions" not in doc
    expected = f"CVE-2026-0001 on {ZLIB}: the scan says zlib 1.3.2-r1, the SBOM says zlib 1.3.2-r0"
    assert expected in report


# Review of c39f2a4, finding 2: what the import writes over ---------------------------


def test_a_report_named_like_the_model_in_another_case_is_refused(tmp_path: Path) -> None:
    with pytest.raises(SbomImportError, match="cannot be the same file"):
        import_sbom.run(SBOM, output=tmp_path / "model.yaml", report=tmp_path / "MODEL.yaml")
    assert list(tmp_path.iterdir()) == []


def test_an_input_named_in_another_case_is_never_written_over(tmp_path: Path) -> None:
    sbom = tmp_path / "sbom.yaml"
    shutil.copy(SBOM, sbom)
    with pytest.raises(SbomImportError, match="is an input"):
        import_sbom.run(sbom, output=tmp_path / "SBOM.yaml", force=True)
    assert sbom.read_bytes() == SBOM.read_bytes()


def test_a_second_name_for_an_input_is_never_written_over(tmp_path: Path) -> None:
    sbom = tmp_path / "sbom.json"
    shutil.copy(SBOM, sbom)
    os.link(sbom, tmp_path / "model.yaml")  # a hard link: one file with two names
    with pytest.raises(SbomImportError, match="is an input"):
        import_sbom.run(sbom, output=tmp_path / "model.yaml", force=True)
    assert sbom.read_bytes() == SBOM.read_bytes()


@pytest.mark.parametrize("which", ["model", "report"])
def test_a_dangling_link_is_an_existing_output(tmp_path: Path, which: str) -> None:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    link = out if which == "model" else report
    link.symlink_to(tmp_path / "missing")
    with pytest.raises(SbomImportError, match="already exists"):
        import_sbom.run(SBOM, output=out, report=report)
    assert link.is_symlink() and [p.name for p in tmp_path.iterdir()] == [link.name]


@pytest.mark.skipif(
    os.name != "posix" or os.geteuid() == 0, reason="needs a folder this user cannot write"
)
def test_a_report_that_cannot_be_written_leaves_no_model(tmp_path: Path) -> None:
    locked = folder(tmp_path, "locked")
    locked.chmod(0o500)
    try:
        with pytest.raises(OSError):
            import_sbom.run(
                SBOM, scan=SCAN, output=tmp_path / "model.yaml", report=locked / "report.md"
            )
    finally:
        locked.chmod(0o700)
    assert [p.name for p in tmp_path.iterdir()] == ["locked"]
    assert list(locked.iterdir()) == []


def failing_move(monkeypatch, target: Path) -> None:
    """Make moving a file onto `target` fail, as a full disk would."""
    real = os.replace

    def replace(src, dst, *args, **kwargs):
        if Path(dst) == target:
            raise OSError(28, "No space left on device")
        return real(src, dst, *args, **kwargs)

    monkeypatch.setattr(import_sbom.os, "replace", replace)


def test_a_failed_move_leaves_neither_file(tmp_path: Path, monkeypatch) -> None:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    failing_move(monkeypatch, report)
    with pytest.raises(OSError, match="No space left"):
        import_sbom.run(SBOM, scan=SCAN, output=out, report=report)
    assert list(tmp_path.iterdir()) == []


def test_a_failed_forced_import_keeps_what_it_would_replace(tmp_path: Path, monkeypatch) -> None:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    out.write_text("edited by a person\n", encoding="utf-8")
    report.write_text("an older report\n", encoding="utf-8")
    failing_move(monkeypatch, report)
    with pytest.raises(OSError, match="No space left"):
        import_sbom.run(SBOM, scan=SCAN, output=out, report=report, force=True)
    assert out.read_text(encoding="utf-8") == "edited by a person\n"
    assert report.read_text(encoding="utf-8") == "an older report\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["model.yaml", "report.md"]


# Review of c39f2a4, finding 3: the model reads back as written -----------------------


@pytest.mark.parametrize("char", ["\n", "\r", "\x85", " ", "\x1b", "\x00"])
def test_input_text_cannot_escape_the_models_header(tmp_path: Path, char: str) -> None:
    sbom = sbom_doc()
    sbom["serialNumber"] = f"urn:uuid:7efb25f4{char}injected: true"
    sbom["metadata"]["tools"]["components"][0]["version"] = f"1.52.0{char}also: true"
    out = tmp_path / "model.yaml"
    import_sbom.run(dump(tmp_path, "s.json", sbom), output=out)
    text = out.read_text(encoding="utf-8")
    header = text[: text.index("\nproducts:")]
    assert all(line.startswith("#") for line in header.splitlines())
    assert set(load(out)) == {"products", "product_instances", "components"}


def test_a_name_with_a_next_line_character_reads_back_exactly(tmp_path: Path) -> None:
    sbom = sbom_doc()
    zlib = next(c for c in sbom["components"] if c.get("name") == "zlib")
    zlib["name"] = "zlib\x85next"  # NEL, which YAML reads as a line break
    doc, _ = import_sbom_doc(tmp_path, sbom)
    assert "zlib\x85next 1.3.2-r0" in [c["name"] for c in doc["components"]]


def test_a_model_that_does_not_read_back_is_not_written(tmp_path: Path, monkeypatch) -> None:
    out = tmp_path / "model.yaml"
    for broken in ("products: [\n", "products: []\n"):  # not YAML, then the wrong data
        monkeypatch.setattr(import_sbom, "_dump", lambda doc, text=broken: text)
        with pytest.raises(SbomImportError, match="does not read back"):
            import_sbom.run(SBOM, output=out)
        assert not out.exists()


# Review of c39f2a4, finding 4: advisories across the scan, and one Assertion a match --


@pytest.mark.parametrize(
    ("rows", "expected"),
    [
        # One GHSA paired with a different CVE in each of two matches.
        (
            [
                ("GHSA-aaaa-bbbb-cccc", ("CVE-2026-0001",)),
                ("GHSA-aaaa-bbbb-cccc", ("CVE-2026-0002",)),
            ],
            {"CVE-2026-0001": [], "CVE-2026-0002": []},
        ),
        # The same, and a match naming only the GHSA: it keeps the GHSA's own id.
        (
            [
                ("GHSA-aaaa-bbbb-cccc", ("CVE-2026-0001",)),
                ("GHSA-aaaa-bbbb-cccc", ("CVE-2026-0002",)),
                ("GHSA-aaaa-bbbb-cccc", ()),
            ],
            {"CVE-2026-0001": [], "CVE-2026-0002": [], "GHSA-aaaa-bbbb-cccc": []},
        ),
        # An advisory naming two CVEs in one match, and only one of them in another.
        (
            [
                ("ALAS-2026-1001", ("CVE-2026-0001", "CVE-2026-0002")),
                ("CVE-2026-0001", ("ALAS-2026-1001",)),
            ],
            {"CVE-2026-0001": [], "CVE-2026-0002": []},
        ),
    ],
)
def test_an_advisory_paired_with_several_cves_anywhere_is_no_alias(
    tmp_path: Path, rows, expected
) -> None:
    doc, report = import_matches(tmp_path, [match(vid, related) for vid, related in rows])
    assert vulnerabilities(doc) == expected
    assert f"- {rows[0][0]}: CVE-2026-0001, CVE-2026-0002" in report


def test_distinct_matches_on_one_component_are_distinct_assertions(tmp_path: Path) -> None:
    direct = match("CVE-2026-0001")  # an exact direct match, as from Alpine's feed
    advisory = match("GHSA-aaaa-bbbb-cccc", ("CVE-2026-0001",))
    advisory["matchDetails"] = [{"type": "cpe-match", "matcher": "apk-matcher"}]
    doc, _ = import_matches(tmp_path, [direct, advisory])
    assert vulnerabilities(doc) == {"CVE-2026-0001": ["GHSA-aaaa-bbbb-cccc"]}
    links = [a for a in doc["assertions"] if a["predicate"] == "propagates_to"]
    assert sorted((a["description"].split(" by ")[0], a["confidence"]) for a in links) == [
        ("Grype matched CVE-2026-0001", "high"),
        ("Grype matched GHSA-aaaa-bbbb-cccc", "low"),
    ]
    assert len({a["id"] for a in links}) == 2


def test_a_match_repeated_exactly_is_one_assertion_and_counted(tmp_path: Path) -> None:
    doc, report = import_matches(tmp_path, [match("CVE-2026-0001"), match("CVE-2026-0001")])
    assert sum(a["predicate"] == "propagates_to" for a in doc["assertions"]) == 1
    assert "1 matches that repeat an earlier match exactly" in report


# Review of c39f2a4, finding 5: the order of the matches changes nothing --------------


def test_the_order_of_the_matches_changes_nothing(tmp_path: Path) -> None:
    # A CWE entry can name a CVE that only another match makes a Vulnerability, and two
    # matches can describe one CVE in different words.
    advisory = match("GHSA-aaaa-bbbb-cccc", cwes=[("CVE-2026-0001", "CWE-79", "nvd@nist.gov")])
    advisory["vulnerability"]["description"] = "The advisory's words."
    nvd = match("CVE-2026-0001", purl=BUSYBOX)
    nvd["vulnerability"].update(namespace="nvd:cpe", description="NVD's words.")
    alpine = match("CVE-2026-0001")
    alpine["vulnerability"]["description"] = "Alpine's words."
    models = []
    for name, rows in (("forward", [advisory, nvd, alpine]), ("backward", [alpine, nvd, advisory])):
        doc, _ = import_matches(folder(tmp_path, name), rows)
        for assertion in doc["assertions"]:
            assertion.pop("evidence")  # the two scan files differ, so their digests do too
        models.append(doc)
    assert models[0] == models[1]
    cwe_links = {
        (a["subject"], a["object"])
        for a in models[0]["assertions"]
        if a["predicate"] == "instance_of"
    }
    assert cwe_links == {("vulnerability:cve-2026-0001", "weakness:cwe-79")}


# Review of c39f2a4, finding 6: the product and the scanned build ---------------------


def test_ids_follow_the_identity_keys(imported, tmp_path: Path) -> None:
    _, doc, _ = imported
    assert doc["products"][0]["id"] == "product:index-docker-io-library-alpine"  # R-ID-2
    assert doc["product_instances"][0]["id"] == "product-instance:" + DIGEST.replace(":", "-")
    products = set()
    for n, image in enumerate(("ghcr.io/org/app", "index.docker.io/org/app", "quay.io/org/app")):
        sbom = sbom_doc()
        sbom["metadata"]["component"]["name"] = image
        model, _ = import_sbom_doc(folder(tmp_path, str(n)), sbom)
        products.add(model["products"][0]["id"])
    assert len(products) == 3  # three repositories, three Products


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        ("source.type", "directory", "not an image"),
        ("source.target.userInput", "index.docker.io/library/busybox", "but the SBOM is of"),
        ("source.target.imageID", "0123456789abcdef", "made from another SBOM"),
    ],
)
def test_a_scan_of_another_image_is_refused(tmp_path: Path, path: str, value, message) -> None:
    scan = mutate(scan_doc(), path, value)
    out = tmp_path / "model.yaml"
    with pytest.raises(SbomImportError, match=message):
        import_sbom.run(SBOM, scan=dump(tmp_path, "g.json", scan), output=out)
    assert not out.exists()


def test_a_scan_grype_made_from_the_image_itself_is_read(tmp_path: Path) -> None:
    # Run on the image, not the SBOM, Grype names it by tag and its configuration digest.
    scan = scan_doc()
    scan["source"]["target"].update(userInput="alpine:3.24.2", imageID="sha256:" + "c" * 64)
    out = tmp_path / "model.yaml"
    import_sbom.run(SBOM, scan=dump(tmp_path, "g.json", scan), output=out)
    assert len(load(out)["vulnerabilities"]) == 15


def test_an_sbom_naming_two_digests_is_refused(tmp_path: Path) -> None:
    sbom = sbom_doc()
    sbom["metadata"]["component"]["name"] += "@sha256:" + "0" * 64
    with pytest.raises(SbomImportError, match="names the digest"):
        import_sbom.run(dump(tmp_path, "s.json", sbom), output=tmp_path / "model.yaml")


def test_the_scans_identity_is_reported(imported, tmp_path: Path) -> None:
    _, _, report = imported
    assert "image id caf3142caa4aa41f, this SBOM's root bom-ref" in report
    assert "Grype's distro is alpine 3.24.2, as the SBOM's operating system says" in report
    scan = scan_doc()
    scan["distro"]["version"] = "3.23.0"
    other = folder(tmp_path, "other")
    result = import_sbom.run(SBOM, scan=dump(other, "g.json", scan), output=other / "model.yaml")
    assert (
        "Grype's distro is alpine 3.23.0, but the SBOM's operating system is alpine 3.24.2"
        in result.report_text
    )


# Review of c39f2a4, finding 7: the report accounts for every field and repeat --------


@pytest.mark.parametrize(
    ("path", "old", "new"),
    [
        (SBOM, '"specVersion":"1.7"', '"specVersion":"1.6","specVersion":"1.7"'),
        (SCAN, '"version":"0.119.0"', '"version":"0.1.0","version":"0.119.0"'),
    ],
)
def test_a_key_repeated_in_one_object_is_refused(tmp_path: Path, path: Path, old, new) -> None:
    text = path.read_text(encoding="utf-8")
    assert text.count(old) == 1
    changed = tmp_path / path.name
    changed.write_text(text.replace(old, new), encoding="utf-8")
    sbom, scan = (changed, None) if path == SBOM else (SBOM, changed)
    with pytest.raises(SbomImportError, match="appears twice in one JSON object"):
        import_sbom.run(sbom, scan=scan, output=tmp_path / "model.yaml")


def test_the_report_lists_nested_fields_by_path(imported) -> None:
    _, _, report = imported
    # The fields inside what the import reads are listed one by one...
    assert "`metadata.tools.components[].author` (1): left out" in report
    assert "`matches[].matchDetails[].searchedBy.namespace` (31): " in report
    assert "`matches[].vulnerability.cwes[].source` (30): " in report
    assert "`source.target.imageID` (1): " in report
    # ...and a field left out whole is counted with the values it holds.
    assert "`components[].licenses` (16, holding 16 values): left out: no slot" in report
    assert "`descriptor.configuration` (1, holding " in report


def test_a_nested_field_the_import_does_not_know_is_reported(tmp_path: Path) -> None:
    sbom = sbom_doc()
    sbom["metadata"]["tools"]["components"][0]["hashes"] = [{"alg": "SHA-256", "content": "ab"}]
    zlib = next(c for c in sbom["components"] if c.get("name") == "zlib")
    zlib["supplier"] = {"name": "Example Supplier Inc.", "url": ["https://example.com"]}
    _, report = import_sbom_doc(tmp_path, sbom)
    unread = "left out: not read by this import"
    assert f"`metadata.tools.components[].hashes` (1, holding 2 values): {unread}" in report
    assert "`components[].supplier.name` (1): Component.supplied_by" in report
    assert "`components[].supplier.url` (1, holding 1 value): left out: no slot" in report


def test_repeated_values_are_counted_in_the_report(tmp_path: Path) -> None:
    sbom = sbom_doc()
    zlib = next(c for c in sbom["components"] if c.get("name") == "zlib")
    zlib["properties"].append({"name": "syft:cpe23", "value": zlib["cpe"]})  # a CPE twice
    edges = sbom["dependencies"][0]
    edges["dependsOn"].append(edges["dependsOn"][0])  # an edge twice
    sbom["dependencies"].append(copy.deepcopy(edges))  # the whole entry twice
    _, report = import_sbom_doc(tmp_path, sbom)
    assert "1 identifiers an SBOM entry repeats" in report
    assert "4 dependency edges that repeat one already written" in report
    assert "1 dependencies entries for a ref listed before" in report


def test_the_fixtures_repeated_values_are_counted(imported) -> None:
    _, _, report = imported
    # 31 CWE entries give 15 links, and zlib's match names its CVE twice (Alpine, NVD).
    assert "16 CWE entries that repeat a link already written" in report
    assert "1 ids a match names more than once" in report


# Review of c39f2a4, finding 8: malformed input and provenance ------------------------


@pytest.mark.parametrize(
    ("which", "path", "value", "message"),
    [
        ("sbom", "components.0.properties", 5, r"components\[0\]\.properties is not a list"),
        ("sbom", "components.0.version", 5, r"components\[0\]\.version is not text"),
        ("sbom", "components.0.purl", 5, r"components\[0\]\.purl is not text"),
        ("sbom", "components.0.supplier", "Example Inc.", r"\[0\]\.supplier is not an object"),
        ("sbom", "components.0.components", {}, r"components\[0\]\.components is not a list"),
        ("sbom", "metadata.tools.components.0.version", 1.52, r"\[0\]\.version is not text"),
        ("sbom", "metadata.timestamp", "yesterday", "metadata.timestamp is 'yesterday'"),
        ("scan", "matches.0.vulnerability.cwes", 5, r"\[0\]\.vulnerability\.cwes is not a list"),
        ("scan", "matches.0.vulnerability.cwes.0.cwe", 787, r"cwes\[0\]\.cwe is not text"),
        ("scan", "matches.1.vulnerability.description", 5, r"\.description is not text"),
        ("scan", "matches.0.matchDetails", {}, r"matches\[0\]\.matchDetails is not a list"),
        ("scan", "matches.0.matchDetails.0.searchedBy", 5, r"\.searchedBy is not an object"),
        ("scan", "matches.0.artifact.purl", 5, r"matches\[0\]\.artifact\.purl is not text"),
        ("scan", "descriptor.version", None, "descriptor.version is missing"),
        ("scan", "descriptor.version", "[not provided]", "not a Grype release version"),
        ("scan", "descriptor.db.status.valid", False, "marks its vulnerability database invalid"),
        ("scan", "descriptor.db.status.schemaVersion", 6.1, "6.1, not a schema version"),
        ("scan", "descriptor.db.status.built", "2026-11-26T00:00:00Z", "dated after the scan"),
    ],
)
def test_a_malformed_field_is_refused_with_its_path(
    tmp_path: Path, which: str, path: str, value: object, message: str
) -> None:
    sbom, scan = sbom_doc(), scan_doc()
    mutate(sbom if which == "sbom" else scan, path, value)
    out = tmp_path / "model.yaml"
    with pytest.raises(SbomImportError, match=message):
        import_sbom.run(
            dump(tmp_path, "s.json", sbom), scan=dump(tmp_path, "g.json", scan), output=out
        )
    assert not out.exists()


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ('{"bomFormat": NaN}', "not valid JSON"),
        ('{"version": ' + "1" * 5000 + "}", "not valid JSON"),
        ("[" * 100_000 + "]" * 100_000, "nests too deeply"),
        ('{"a": ' * 100 + "1" + "}" * 100, "nests too deeply"),
        ('{"name": "\\ud800"}', "not valid Unicode"),
    ],
)
def test_json_that_python_reads_but_is_not_sound_is_refused(tmp_path: Path, text, message) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(text, encoding="utf-8")
    with pytest.raises(SbomImportError, match=message):
        import_sbom.run(bad, output=tmp_path / "model.yaml")


def test_the_command_exits_2_on_a_malformed_field(tmp_path: Path, capsys) -> None:
    sbom = dump(tmp_path, "s.json", mutate(sbom_doc(), "components.0.properties", 5))
    assert cli.main(["import-sbom", str(sbom), "-o", str(tmp_path / "model.yaml")]) == 2
    assert "components[0].properties is not a list" in capsys.readouterr().err
    assert not (tmp_path / "model.yaml").exists()
