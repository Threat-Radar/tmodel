"""`tmodel import-sbom`: a starter model from Syft's SBOM and Grype's scan (#257, DL-0068).

The fixture is the image RPT-0004's pilot scanned: alpine 3.24.2 for linux/arm64/v8,
platform manifest digest sha256:260479a1cfaf..., SBOM by Syft 1.52.0 and scan by
Grype 0.119.0 with the database built 2026-10-08T06:33:47Z. Its numbers are the
pilot's (pilot.md): 95 SBOM entries (16 library, 1 operating-system, 78 file), 12
dependency entries with 24 edges, and 30 matches for 15 CVEs. The scan file is Grype's
output with only its local paths shortened (DL-0068). Neither file says which platform
the digest names, so each import here gives it, as `--platform linux/arm64/v8` does.

The sections headed "Review of c39f2a4" hold the regression tests for the eight findings
of @kriishnaa-18's review, those headed "Review of 9207ad9" the tests for the five of the
re-review, those headed "Review of e12ab07" the tests for the four of the third round
(@kriishnaa-18's three and @Maimcghee's one), those headed "Review of f21f4a5" the tests
for the two of the fourth, and those headed "Review of 4be86c1" the tests for the
fifth's seventeen items: the review's three findings, and fourteen defects an
independent review found while those fixes were checked. Each failed before its fix,
unless its item says it guards one (DL-0068, "Review changes", and its second to fifth
rounds). The fifth round turned the tests that expected a refusal from the packages'
architectures into tests of the warning that replaces it, where they stand.
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
PLATFORM = "linux/arm64/v8"  # the fixture's build, as the image index lists it
INSTANCE = f"product-instance:{DIGEST.replace(':', '-')}-linux-arm64-v8"
ZLIB = "pkg:apk/alpine/zlib@1.3.2-r0?arch=aarch64&distro=alpine-3.24.2"
X86_ZLIB = ZLIB.replace("arch=aarch64", "arch=x86_64")  # the same package for another CPU
# The same package for the 32-bit CPU an arm64 build also runs, which one image can hold
# beside the arm64 one (multiarch), where it cannot hold an x86_64 one (finding 2 of the
# review of 9207ad9).
ARM32_ZLIB = ZLIB.replace("arch=aarch64", "arch=armv7")
BUSYBOX = "pkg:apk/alpine/busybox@1.37.0-r31?arch=aarch64&distro=alpine-3.24.2"
MUSL = "pkg:apk/alpine/musl@1.2.6-r2?arch=aarch64&distro=alpine-3.24.2"
X86_MUSL = MUSL.replace("arch=aarch64", "arch=x86_64")


def run(sbom: Path, **kwargs) -> import_sbom.ImportResult:
    """`import_sbom.run` for the fixture's platform, unless the test gives another one
    (`platform=None` for none): the SBOM does not record it (DL-0068, decision 2)."""
    return import_sbom.run(sbom, **{"platform": PLATFORM, **kwargs})


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
    result = run(SBOM, scan=SCAN, output=out)
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
    assert instance["identifiers"] == [  # R-ID-1: the digest, and the purl with its platform
        DIGEST,
        "pkg:oci/alpine@sha256%3A260479a1cfaf304c4c20da7f8405d3ce313513dcd534bb743257bdd2fe0f3e2d"
        "?arch=arm64&repository_url=index.docker.io/library/alpine",
    ]
    assert instance["name"].endswith(f" for {PLATFORM}")
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
    first = run(SBOM, scan=SCAN, output=tmp_path / "one" / "model.yaml")
    second = run(SBOM, scan=SCAN, output=tmp_path / "two" / "model.yaml")
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


def import_matches(tmp_path: Path, matches: list[dict], sbom: dict | None = None, **kwargs):
    """Import the fixture's SBOM (or `sbom`) with a scan holding only `matches`."""
    scan = scan_doc()
    scan["matches"] = matches
    sbom_path = SBOM if sbom is None else dump(tmp_path, "sbom.json", sbom)
    path = dump(tmp_path, "scan.json", scan)
    result = run(sbom_path, scan=path, output=tmp_path / "model.yaml", **kwargs)
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
    result = run(path, output=tmp_path / "model.yaml", **kwargs)
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
        run(dump(tmp_path, "s.json", sbom), scan=dump(tmp_path, "g.json", scan), output=out)
    assert not out.exists()


def test_a_repeated_bom_ref_is_refused(tmp_path: Path) -> None:
    sbom = sbom_doc()
    sbom["components"][1]["bom-ref"] = sbom["components"][0]["bom-ref"]
    with pytest.raises(SbomImportError, match="appears twice"):
        run(dump(tmp_path, "s.json", sbom), output=tmp_path / "model.yaml")


def test_text_that_is_not_json_is_refused(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{ not json", encoding="utf-8")
    with pytest.raises(SbomImportError, match="not valid JSON"):
        run(bad, output=tmp_path / "model.yaml")
    with pytest.raises(SbomImportError, match="a JSON object at the top level"):
        run(dump(tmp_path, "list.json", []), output=tmp_path / "model.yaml")


def test_an_oversized_file_is_refused(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(import_sbom, "MAX_INPUT_BYTES", 100)
    with pytest.raises(SbomImportError, match="larger than 100 bytes"):
        run(SBOM, output=tmp_path / "model.yaml")


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="needs a FIFO")
def test_a_fifo_is_refused_without_waiting(tmp_path: Path) -> None:
    fifo = tmp_path / "sbom.json"
    os.mkfifo(fifo)
    with pytest.raises(SbomImportError, match="not a regular file"):
        run(fifo, output=tmp_path / "model.yaml")


def test_an_existing_model_is_kept_unless_forced(tmp_path: Path) -> None:
    out = tmp_path / "model.yaml"
    out.write_text("edited by a person\n", encoding="utf-8")
    with pytest.raises(SbomImportError, match="already exists"):
        run(SBOM, scan=SCAN, output=out)
    assert out.read_text(encoding="utf-8") == "edited by a person\n"
    run(SBOM, scan=SCAN, output=out, force=True)
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
        run(SBOM, output=tmp_path / output, report=None if report is None else tmp_path / report)


def test_an_input_is_never_written_over(tmp_path: Path) -> None:
    sbom = tmp_path / "sbom.yaml"  # an SBOM saved under a .yaml name
    shutil.copy(SBOM, sbom)
    with pytest.raises(SbomImportError, match="is an input"):
        run(sbom, output=sbom, force=True)
    assert sbom.read_bytes() == SBOM.read_bytes()


def test_the_header_never_names_a_home_folder(tmp_path: Path) -> None:
    out = tmp_path / "pv-05-alpine.yaml"
    run(SBOM, scan=SCAN, output=out)  # an absolute path
    text = out.read_text(encoding="utf-8")
    assert f"-C ExampleModelProposed {out.name}\n" in text
    assert str(tmp_path) not in text


# The command line ----------------------------------------------------------------


def test_the_command_prints_the_report(tmp_path: Path, capsys) -> None:
    out = tmp_path / "model.yaml"
    argv = ["import-sbom", str(SBOM), "--scan", str(SCAN), "--platform", PLATFORM, "-o", str(out)]
    assert cli.main(argv) == 0
    assert capsys.readouterr().out.startswith("# tmodel import-sbom report")
    assert load(out)["product_instances"][0]["version"] == DIGEST


def test_the_command_can_write_the_report(tmp_path: Path, capsys) -> None:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    argv = [
        "import-sbom",
        str(SBOM),
        "--platform",
        PLATFORM,
        "-o",
        str(out),
        "--report",
        str(report),
    ]
    assert cli.main(argv) == 0
    assert capsys.readouterr().out.startswith("wrote ")
    assert report.read_text(encoding="utf-8").startswith("# tmodel import-sbom report")


def test_the_command_exits_2_on_a_refused_input(tmp_path: Path, capsys) -> None:
    bad = dump(tmp_path, "bad.json", {"bomFormat": "SPDX"})
    argv = ["import-sbom", str(bad), "--platform", PLATFORM, "-o", str(tmp_path / "model.yaml")]
    assert cli.main(argv) == 2
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
        ("0001-01-01T00:00:00+14:00", None),  # in UTC, before the year 1 (review of 9207ad9)
        ("9999-12-31T23:59:59-14:00", None),  # in UTC, after the year 9999
        ("0001-01-02T00:00:00Z", "0001-01-02T00:00:00Z"),  # four digits on every platform
    ],
)
def test_times_are_read_as_utc(value, utc) -> None:
    assert import_sbom._utc(value) == utc


# Review of c39f2a4, finding 1: a Component's purl keeps its qualifiers ----------------


def test_entries_whose_purls_differ_in_a_qualifier_are_two_components(tmp_path: Path) -> None:
    sbom = sbom_doc()
    zlib_copy(sbom, ARM32_ZLIB)  # the same name and version, built for another CPU
    doc, report = import_sbom_doc(tmp_path, sbom)
    assert len(doc["components"]) == 18
    zlibs = [c for c in doc["components"] if c["name"] == "zlib 1.3.2-r0"]
    assert sorted(c["identifiers"][0] for c in zlibs) == sorted([ZLIB, ARM32_ZLIB])
    assert "SBOM entries recorded as one Component" not in report


def test_a_match_joins_only_the_component_with_its_purl(tmp_path: Path) -> None:
    sbom = sbom_doc()
    zlib_copy(sbom, ARM32_ZLIB)
    doc, _ = import_matches(tmp_path, [match("CVE-2026-0001", purl=ARM32_ZLIB)], sbom)
    (link,) = [a for a in doc["assertions"] if a["predicate"] == "propagates_to"]
    assert by_id(doc, "components")[link["object"]]["identifiers"][0] == ARM32_ZLIB


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
        run(dump(tmp_path, "s.json", sbom), output=out)
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
        run(SBOM, output=tmp_path / "model.yaml", report=tmp_path / "MODEL.yaml")
    assert list(tmp_path.iterdir()) == []


def test_an_input_named_in_another_case_is_never_written_over(tmp_path: Path) -> None:
    sbom = tmp_path / "sbom.yaml"
    shutil.copy(SBOM, sbom)
    with pytest.raises(SbomImportError, match="is an input"):
        run(sbom, output=tmp_path / "SBOM.yaml", force=True)
    assert sbom.read_bytes() == SBOM.read_bytes()


def test_a_second_name_for_an_input_is_never_written_over(tmp_path: Path) -> None:
    sbom = tmp_path / "sbom.json"
    shutil.copy(SBOM, sbom)
    os.link(sbom, tmp_path / "model.yaml")  # a hard link: one file with two names
    with pytest.raises(SbomImportError, match="is an input"):
        run(sbom, output=tmp_path / "model.yaml", force=True)
    assert sbom.read_bytes() == SBOM.read_bytes()


@pytest.mark.parametrize("which", ["model", "report"])
def test_a_dangling_link_is_an_existing_output(tmp_path: Path, which: str) -> None:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    link = out if which == "model" else report
    link.symlink_to(tmp_path / "missing")
    with pytest.raises(SbomImportError, match="already exists"):
        run(SBOM, output=out, report=report)
    assert link.is_symlink() and [p.name for p in tmp_path.iterdir()] == [link.name]


@pytest.mark.skipif(
    os.name != "posix" or os.geteuid() == 0, reason="needs a folder this user cannot write"
)
def test_a_report_that_cannot_be_written_leaves_no_model(tmp_path: Path) -> None:
    locked = folder(tmp_path, "locked")
    locked.chmod(0o500)
    try:
        with pytest.raises(OSError):
            run(SBOM, scan=SCAN, output=tmp_path / "model.yaml", report=locked / "report.md")
    finally:
        locked.chmod(0o700)
    assert [p.name for p in tmp_path.iterdir()] == ["locked"]
    assert list(locked.iterdir()) == []


def failing_move(monkeypatch, target: Path) -> None:
    """Make putting a file at `target` fail, as a full disk would: by a hard link or an
    exclusive create (unforced) or by a move (with --force)."""
    for name, at in (("link", 1), ("open", 0), ("replace", 1)):
        real = getattr(os, name)

        def fail(*args, real=real, at=at, **kwargs):
            if os.fspath(args[at]) == os.fspath(target):
                raise OSError(28, "No space left on device")
            return real(*args, **kwargs)

        monkeypatch.setattr(import_sbom.os, name, fail)


def test_a_failed_move_leaves_neither_file(tmp_path: Path, monkeypatch) -> None:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    failing_move(monkeypatch, report)
    with pytest.raises(OSError, match="No space left"):
        run(SBOM, scan=SCAN, output=out, report=report)
    assert list(tmp_path.iterdir()) == []


def test_a_failed_forced_import_keeps_what_it_would_replace(tmp_path: Path, monkeypatch) -> None:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    out.write_text("edited by a person\n", encoding="utf-8")
    report.write_text("an older report\n", encoding="utf-8")
    failing_move(monkeypatch, report)
    with pytest.raises(OSError, match="No space left"):
        run(SBOM, scan=SCAN, output=out, report=report, force=True)
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
    run(dump(tmp_path, "s.json", sbom), output=out)
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
            run(SBOM, output=out)
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
    # R-ID-2: the repository's slug, and a short hash of the Product's key, its purl
    # (review of 4be86c1, finding 2 and item 7)
    assert doc["products"][0]["id"] == "product:index-docker-io-library-alpine-d27fdaeb"
    assert doc["product_instances"][0]["id"] == INSTANCE  # R-ID-1: the digest and the platform
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
        run(SBOM, scan=dump(tmp_path, "g.json", scan), output=out)
    assert not out.exists()


def test_a_scan_grype_made_from_the_image_itself_is_read(tmp_path: Path) -> None:
    # Run on the image, not the SBOM, Grype names it by tag and its configuration digest.
    scan = scan_doc()
    scan["source"]["target"].update(userInput="alpine:3.24.2", imageID="sha256:" + "c" * 64)
    out = tmp_path / "model.yaml"
    run(SBOM, scan=dump(tmp_path, "g.json", scan), output=out)
    assert len(load(out)["vulnerabilities"]) == 15


def test_an_sbom_naming_two_digests_is_refused(tmp_path: Path) -> None:
    sbom = sbom_doc()
    sbom["metadata"]["component"]["name"] += "@sha256:" + "0" * 64
    with pytest.raises(SbomImportError, match="names the digest"):
        run(dump(tmp_path, "s.json", sbom), output=tmp_path / "model.yaml")


def test_the_scans_identity_is_reported(imported, tmp_path: Path) -> None:
    _, _, report = imported
    assert "image id caf3142caa4aa41f, this SBOM's root bom-ref" in report
    assert "Grype's distro is alpine 3.24.2, as the SBOM's operating system says" in report
    scan = scan_doc()
    scan["distro"]["version"] = "3.23.0"
    other = folder(tmp_path, "other")
    result = run(SBOM, scan=dump(other, "g.json", scan), output=other / "model.yaml")
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
        run(sbom, scan=scan, output=tmp_path / "model.yaml")


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
        run(dump(tmp_path, "s.json", sbom), scan=dump(tmp_path, "g.json", scan), output=out)
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
        run(bad, output=tmp_path / "model.yaml")


def test_the_command_exits_2_on_a_malformed_field(tmp_path: Path, capsys) -> None:
    sbom = dump(tmp_path, "s.json", mutate(sbom_doc(), "components.0.properties", 5))
    argv = ["import-sbom", str(sbom), "--platform", PLATFORM, "-o", str(tmp_path / "model.yaml")]
    assert cli.main(argv) == 2
    assert "components[0].properties is not a list" in capsys.readouterr().err
    assert not (tmp_path / "model.yaml").exists()


# Review of 9207ad9, finding 1: names a Mac reads as one, and files that appear later --

NFC, NFD = "café", "café"  # one name: é as one character, or as e and an accent


@pytest.mark.parametrize("report", [f"{NFD}.yaml", "CAFÉ.YAML"])
def test_names_a_mac_reads_as_one_are_one_place(tmp_path: Path, report: str) -> None:
    # APFS and HFS+ ignore both the Unicode form and the case of a name, so on a Mac the
    # report would land on the model; Linux tells them apart, and the refusal costs nothing.
    with pytest.raises(SbomImportError, match="cannot be the same file"):
        run(SBOM, scan=SCAN, output=tmp_path / f"{NFC}.yaml", report=tmp_path / report)
    assert list(tmp_path.iterdir()) == []


def test_an_input_named_in_another_unicode_form_is_never_written_over(tmp_path: Path) -> None:
    sbom = tmp_path / f"{NFC}.yaml"
    shutil.copy(SBOM, sbom)
    with pytest.raises(SbomImportError, match="is an input"):
        run(sbom, output=tmp_path / f"{NFD}.yaml", force=True)
    assert sbom.read_bytes() == SBOM.read_bytes()
    assert len(list(tmp_path.iterdir())) == 1


def when_placed(monkeypatch, path: Path, action, *, before: bool = False) -> None:
    """Run `action` once, just after (or just before) the import puts its file at `path`,
    as another program writing to the same folder would."""
    done: list[bool] = []
    for name in ("link", "replace"):  # how a file is put in place, unforced or forced
        real = getattr(os, name)

        def place(src, dst, *args, real=real, **kwargs):
            mine = Path(dst) == path and Path(src).name.startswith(".import-sbom-") and not done
            if mine and before:
                done.append(True)
                action()
            result = real(src, dst, *args, **kwargs)
            if mine and not before:
                done.append(True)
                action()
            return result

        monkeypatch.setattr(import_sbom.os, name, place)


def test_a_file_that_appears_after_the_check_is_never_written_over(
    tmp_path: Path, monkeypatch
) -> None:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    when_placed(monkeypatch, out, lambda: report.write_text("theirs\n", encoding="utf-8"))
    with pytest.raises(SbomImportError, match="report.md: already exists"):
        run(SBOM, scan=SCAN, output=out, report=report)
    assert report.read_text(encoding="utf-8") == "theirs\n"
    assert [p.name for p in tmp_path.iterdir()] == ["report.md"]  # nothing of this import's


def test_the_outputs_get_the_usual_file_permissions(tmp_path: Path) -> None:
    """The model and the report are saved like any file the user writes: the umask
    decides their mode, not the owner-only mode of a temporary file (0600)."""
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    old = os.umask(0o022)
    try:
        run(SBOM, scan=SCAN, output=out, report=report)
        assert [oct(p.stat().st_mode & 0o777) for p in (out, report)] == ["0o644", "0o644"]
        run(SBOM, scan=SCAN, output=out, report=report, force=True)
        assert [oct(p.stat().st_mode & 0o777) for p in (out, report)] == ["0o644", "0o644"]
    finally:
        os.umask(old)


def test_the_undo_never_removes_a_file_this_import_did_not_place(
    tmp_path: Path, monkeypatch
) -> None:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"

    def another_program() -> None:  # replaces the model just written, and takes the report
        (tmp_path / "theirs").write_text("their model\n", encoding="utf-8")
        os.replace(tmp_path / "theirs", out)
        report.write_text("their report\n", encoding="utf-8")

    when_placed(monkeypatch, report, another_program, before=True)
    with pytest.raises(SbomImportError, match="already exists"):
        run(SBOM, scan=SCAN, output=out, report=report)
    assert out.read_text(encoding="utf-8") == "their model\n"
    assert report.read_text(encoding="utf-8") == "their report\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["model.yaml", "report.md"]


def test_a_forced_undo_keeps_what_it_cannot_put_back(tmp_path: Path, monkeypatch) -> None:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    out.write_text("edited by a person\n", encoding="utf-8")

    def another_program() -> None:  # replaces the model this import just put in place
        (tmp_path / "theirs").write_text("their model\n", encoding="utf-8")
        os.replace(tmp_path / "theirs", out)

    failing_move(monkeypatch, report)  # first, so the other program acts before it fails
    when_placed(monkeypatch, report, another_program, before=True)
    with pytest.raises(OSError, match="No space left") as raised:
        run(SBOM, scan=SCAN, output=out, report=report, force=True)
    assert out.read_text(encoding="utf-8") == "their model\n"  # not replaced by the undo
    (kept,) = [p for p in tmp_path.iterdir() if p.name.endswith(".old")]
    assert kept.read_text(encoding="utf-8") == "edited by a person\n"
    assert any(kept.name in note for note in raised.value.__notes__)


def test_a_forced_undo_that_cannot_put_a_file_back_keeps_it(tmp_path: Path, monkeypatch) -> None:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    out.write_text("edited by a person\n", encoding="utf-8")
    failing_move(monkeypatch, report)
    real = os.replace

    def replace(src, dst, *args, **kwargs):  # putting the person's file back fails too
        if Path(src).name.endswith(".old"):
            raise OSError(5, "Input/output error")
        return real(src, dst, *args, **kwargs)

    monkeypatch.setattr(import_sbom.os, "replace", replace)
    with pytest.raises(OSError, match="No space left") as raised:
        run(SBOM, scan=SCAN, output=out, report=report, force=True)
    (kept,) = [p for p in tmp_path.iterdir() if p.name.endswith(".old")]
    assert kept.read_text(encoding="utf-8") == "edited by a person\n"
    assert any(kept.name in note for note in raised.value.__notes__)


def test_a_volume_without_hard_links_is_written_by_exclusive_create(
    tmp_path: Path, monkeypatch
) -> None:
    def no_links(src, dst, *args, **kwargs):  # as on FAT and exFAT
        raise PermissionError(1, "Operation not permitted")

    monkeypatch.setattr(import_sbom.os, "link", no_links)
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    result = run(SBOM, scan=SCAN, output=out, report=report)
    assert out.read_text(encoding="utf-8") == result.model_text
    assert report.read_text(encoding="utf-8") == result.report_text
    assert sorted(p.name for p in tmp_path.iterdir()) == ["model.yaml", "report.md"]


def unicode_forms_are_one_name(folder: Path) -> bool:
    probe = folder / f"probe-{NFC}"
    probe.write_text("", encoding="utf-8")
    try:
        return (folder / f"probe-{NFD}").exists()
    finally:
        probe.unlink()


def test_a_volume_that_reads_two_forms_as_one_name_is_not_written_over(
    tmp_path: Path, monkeypatch
) -> None:
    if not unicode_forms_are_one_name(tmp_path):
        pytest.skip("this volume tells the two forms apart (Linux's ext4 does; APFS does not)")
    # Past the check that refuses such names, the volume itself must refuse the report.
    monkeypatch.setattr(import_sbom, "_same_place", lambda first, second: False)
    with pytest.raises(SbomImportError, match="already exists"):
        run(SBOM, scan=SCAN, output=tmp_path / f"{NFC}.yaml", report=tmp_path / f"{NFD}.yaml")
    assert list(tmp_path.iterdir()) == []


# Review of 9207ad9, finding 2: the build is the digest and the platform ----------------


def built_for(sbom: dict, arch: str, distribution: str | None = None) -> dict:
    """`sbom` with each package's arch qualifier `arch`: another platform's build; and,
    given a purl type and namespace such as `deb/debian`, as another distribution's."""
    for component in sbom["components"]:
        if "purl" in component:
            purl = component["purl"].replace("arch=aarch64", f"arch={arch}")
            if distribution is not None:
                purl = purl.replace("pkg:apk/alpine/", f"pkg:{distribution}/")
            component["purl"] = purl
    return sbom


def direct_scan(**target: str) -> dict:
    """The fixture's scan as Grype writes it when it read the image itself: named by tag,
    with its configuration digest and the platform it pulled (source.target)."""
    scan = scan_doc()
    scan["source"]["target"].update(
        userInput="alpine:3.24.2",
        imageID="sha256:" + "c" * 64,
        os="linux",
        architecture="arm64",
        architectureVariant="v8",
    )
    scan["source"]["target"].update(target)
    return scan


def test_one_digest_on_two_platforms_is_two_builds(tmp_path: Path) -> None:
    # An index digest names every platform of a release, and the CycloneDX file does
    # not say which kind of digest it holds (DL-0068, decision 2).
    arm, _ = import_sbom_doc(folder(tmp_path, "arm"), sbom_doc())
    amd, _ = import_sbom_doc(
        folder(tmp_path, "amd"), built_for(sbom_doc(), "x86_64"), platform="linux/amd64"
    )
    (arm_build,), (amd_build,) = arm["product_instances"], amd["product_instances"]
    assert arm_build["version"] == amd_build["version"] == DIGEST
    assert arm_build["id"] == INSTANCE
    assert amd_build["id"] == f"product-instance:{DIGEST.replace(':', '-')}-linux-amd64"
    assert "?arch=arm64&repository_url=" in arm_build["identifiers"][1]
    assert "?arch=amd64&repository_url=" in amd_build["identifiers"][1]


@pytest.mark.parametrize("scan", [None, SCAN])
def test_without_a_platform_the_import_is_refused(tmp_path: Path, scan) -> None:
    with pytest.raises(SbomImportError, match="does not record which platform its digest names"):
        run(SBOM, scan=scan, platform=None, output=tmp_path / "model.yaml")
    assert list(tmp_path.iterdir()) == []


def test_a_direct_scans_platform_is_the_builds(tmp_path: Path) -> None:
    out = tmp_path / "model.yaml"
    result = run(SBOM, scan=dump(tmp_path, "g.json", direct_scan()), platform=None, output=out)
    assert load(out)["product_instances"][0]["id"] == INSTANCE
    assert "Platform: linux/arm64/v8, from the scan (source.target)" in result.report_text


def test_a_variant_only_one_side_gives_is_no_disagreement(tmp_path: Path) -> None:
    scan = direct_scan()
    del scan["source"]["target"]["architectureVariant"]  # as Syft 1.52.0 leaves it out
    result = run(SBOM, scan=dump(tmp_path, "g.json", scan), output=tmp_path / "model.yaml")
    assert load(tmp_path / "model.yaml")["product_instances"][0]["id"] == INSTANCE
    assert "Platform: linux/arm64/v8, from --platform and the scan" in result.report_text


@pytest.mark.parametrize(
    ("target", "message"),
    [
        ({"architecture": "amd64"}, "gives the architecture arm64, but the scan records amd64"),
        ({"os": "windows"}, "gives the os linux, but the scan records windows"),
        ({"architectureVariant": "v7"}, "gives the variant v8, but the scan records v7"),
    ],
)
def test_a_platform_the_scan_contradicts_is_refused(tmp_path: Path, target, message) -> None:
    out = tmp_path / "model.yaml"
    with pytest.raises(SbomImportError, match=message):
        run(SBOM, scan=dump(tmp_path, "g.json", direct_scan(**target)), output=out)
    assert not out.exists()


@pytest.mark.parametrize(
    ("arch", "platform", "found", "other"),
    [
        (
            "aarch64",
            "linux/amd64",
            "16 of the SBOM's packages are built for arm64 (arch=aarch64) and none for amd64 or "
            "the 386 it also runs, though the platform is linux/amd64 (from --platform)",
            "linux/arm64/v8",
        ),
        (
            "x86",
            "linux/amd64",
            "none of the SBOM's packages is built for amd64, though the platform is linux/amd64 "
            "(from --platform); they say arch=x86 (16 Components)",
            "linux/386",
        ),
        (
            "armv7",
            "linux/arm64/v8",
            "none of the SBOM's packages is built for arm64, though the platform is "
            "linux/arm64/v8 (from --platform); they say arch=armv7 (16 Components)",
            "linux/arm/v7",
        ),
        (
            "ppc64le",
            "linux/arm64/v8",
            "16 of the SBOM's packages are built for ppc64le (arch=ppc64le) and none for arm64 "
            "or the arm it also runs, though the platform is linux/arm64/v8 (from --platform)",
            "linux/ppc64le",
        ),
    ],
)
def test_packages_that_contradict_the_platform_are_kept_with_a_warning(
    tmp_path: Path, arch: str, platform: str, found: str, other: str
) -> None:
    # These were refused until the review of 4be86c1 (finding 1): the platform comes from
    # its metadata, and the packages' architectures only warn.
    sbom = dump(tmp_path, "s.json", built_for(sbom_doc(), arch))
    result = run(sbom, platform=platform, output=tmp_path / "model.yaml")
    doc = load(tmp_path / "model.yaml")
    assert len(doc["components"]) == 17
    assert instance(doc)["name"].endswith(f" for {platform}")
    note = (
        f"{found}. Every package is kept as a Component; if the SBOM is of another build, pass "
        f"its platform, for example --platform {other}"
    )
    assert result.warnings == [f"s.json: {note}"]
    assert f"- {note}.\n" in result.report_text
    assert followed(tmp_path, result.warnings[0], sbom=built_for(sbom_doc(), arch)) == []


def test_an_image_purl_for_another_architecture_is_refused(tmp_path: Path) -> None:
    sbom = sbom_doc()
    sbom["metadata"]["component"]["purl"] = (
        "pkg:oci/alpine@" + DIGEST.replace(":", "%3A") + "?arch=amd64"
    )
    with pytest.raises(SbomImportError, match="metadata.component.purl says arch=amd64"):
        run(dump(tmp_path, "s.json", sbom), output=tmp_path / "model.yaml")


@pytest.mark.parametrize(
    ("arch", "listed"),
    [
        # Alpine's armhf is ARMv6 (review of e12ab07, finding 1: the line names the variant).
        ("armhf", "1 Component built for arm/v6 (arch=armhf), which arm64 also runs"),
        ("loongarch64", "- loongarch64: 1 Component"),
        ("noarch", None),  # names no CPU, so there is nothing to check
    ],
)
def test_package_architectures_that_are_not_the_platforms_are_reported(
    tmp_path: Path, arch: str, listed: str | None
) -> None:
    sbom = sbom_doc()
    zlib = next(c for c in sbom["components"] if c.get("name") == "zlib")
    zlib["purl"] = zlib["purl"].replace("arch=aarch64", f"arch={arch}")
    doc, report = import_sbom_doc(tmp_path, sbom)
    assert doc["product_instances"][0]["id"] == INSTANCE
    assert "15 Components built for arm64 (arch=aarch64)" in report
    if listed is not None:
        assert listed in report


@pytest.mark.parametrize(
    ("platform", "message"),
    [
        ("linux", "not OS/ARCH or OS/ARCH/VARIANT"),
        ("linux/", "not OS/ARCH or OS/ARCH/VARIANT"),
        ("linux/arm64/v8/x", "not OS/ARCH or OS/ARCH/VARIANT"),
        ("linux/arm 64", "not OS/ARCH or OS/ARCH/VARIANT"),
        ("linux/aarch64", "a distribution's name for arm64"),
    ],
)
def test_the_platform_option_is_checked(tmp_path: Path, platform: str, message: str) -> None:
    with pytest.raises(SbomImportError, match=message):
        run(SBOM, platform=platform, output=tmp_path / "model.yaml")
    assert list(tmp_path.iterdir()) == []


def test_the_platform_option_is_read_in_any_case(tmp_path: Path) -> None:
    doc, _ = import_sbom_doc(tmp_path, sbom_doc(), platform="Linux/ARM64/V8")
    assert doc["product_instances"][0]["id"] == INSTANCE


def test_the_command_refuses_an_unnamed_platform(tmp_path: Path, capsys) -> None:
    argv = ["import-sbom", str(SBOM), "--scan", str(SCAN), "-o", str(tmp_path / "model.yaml")]
    assert cli.main(argv) == 2
    err = capsys.readouterr().err
    assert "does not record which platform" in err and "--platform linux/arm64/v8" in err
    assert list(tmp_path.iterdir()) == []


# Review of 9207ad9, finding 3: every version an entry gives is compared ---------------


def test_versions_after_an_entry_with_none_must_agree(tmp_path: Path) -> None:
    sbom = sbom_doc()
    del next(c for c in sbom["components"] if c.get("name") == "zlib")["version"]
    zlib_copy(sbom)["version"] = "1.0"
    second = zlib_copy(sbom)
    second.update({"bom-ref": second["bom-ref"] + "-2", "version": "2.0"})
    out = tmp_path / "model.yaml"
    with pytest.raises(SbomImportError, match=r"give different versions \('1.0' and '2.0'\)"):
        run(dump(tmp_path, "s.json", sbom), output=out)
    assert not out.exists()


def test_an_entry_with_no_version_merges_with_one_that_gives_it(tmp_path: Path) -> None:
    sbom = sbom_doc()
    del next(c for c in sbom["components"] if c.get("name") == "zlib")["version"]
    zlib_copy(sbom)["version"] = "1.0"
    doc, _ = import_sbom_doc(tmp_path, sbom)
    (merged,) = [c for c in doc["components"] if ZLIB in c.get("identifiers", [])]
    assert (merged["name"], merged["version"]) == ("zlib 1.0", "1.0")
    assert len(doc["components"]) == 17


# Review of 9207ad9, finding 4: the report says which descriptions were written ---------


def field_lines(report: str) -> dict[str, str]:
    """The report's field inventory: each path, and where the report says it went."""
    lines = (line.split("`", 2) for line in report.splitlines() if line.startswith("  - `"))
    return {path: rest.split("): ", 1)[1] for _, path, rest in lines}


def test_an_advisorys_description_that_is_not_written_is_listed(tmp_path: Path) -> None:
    advisory = match("GHSA-aaaa-bbbb-cccc", ("CVE-2026-0001",))
    advisory["vulnerability"]["description"] = "The advisory's words."
    advisory["relatedVulnerabilities"][0]["description"] = "NVD's words."
    doc, report = import_matches(tmp_path, [advisory])
    assert vulnerabilities(doc) == {"CVE-2026-0001": ["GHSA-aaaa-bbbb-cccc"]}
    assert doc["vulnerabilities"][0]["description"] == "NVD's words."
    fields = field_lines(report)
    assert fields["matches[].vulnerability.description"] == (
        "left out: 1 an advisory's, whose match is written as another id (each listed above)"
    )
    assert fields["matches[].relatedVulnerabilities[].description"] == "Vulnerability.description"
    assert (
        "- GHSA-aaaa-bbbb-cccc: its match is written as CVE-2026-0001, and "
        "GHSA-aaaa-bbbb-cccc as an alias of CVE-2026-0001" in report
    )


def test_a_description_in_other_words_than_the_one_written_is_listed(tmp_path: Path) -> None:
    alpine = match("CVE-2026-0001")  # in the namespace alpine:distro:alpine:3.24
    alpine["vulnerability"]["description"] = "Alpine's words."
    nvd = match("CVE-2026-0001", purl=BUSYBOX)
    nvd["vulnerability"].update(namespace="nvd:cpe", description="NVD's words.")
    doc, report = import_matches(tmp_path, [alpine, nvd])
    assert doc["vulnerabilities"][0]["description"] == "Alpine's words."
    assert field_lines(report)["matches[].vulnerability.description"] == (
        "Vulnerability.description, for 1; left out: 1 in other words than the one "
        "written for its Vulnerability (each listed above)"
    )
    assert (
        "- CVE-2026-0001: 2 descriptions; written: alpine:distro:alpine:3.24's; "
        "left out: nvd:cpe's" in report
    )


def test_fields_some_of_whose_values_are_left_out_say_so(imported) -> None:
    _, _, report = imported
    fields = field_lines(report)
    assert "the import keeps: file entries, and the matches listed above" in report
    assert fields["metadata.tools.components[].version"].startswith("Syft's: ")
    assert "disagree" in fields["components[].description"]
    for party in ("supplier", "manufacturer"):  # fields the fixture does not hold
        assert "disagree" in import_sbom.SBOM_FIELDS[f"components[].{party}.name"]
    assert "an entry that is not a Component" in fields["dependencies[].dependsOn"]
    assert "more than one Vulnerability" in fields["matches[].vulnerability.id"]
    assert "not a Vulnerability here" in fields["matches[].vulnerability.cwes[].cve"]
    assert "no CWE" in fields["matches[].vulnerability.cwes[].cwe"]


# Review of 9207ad9, non-blocking: a time outside UTC's range --------------------------


@pytest.mark.parametrize(
    "value", ["0001-01-01T00:00:00+14:00", "9999-12-31T23:59:59-14:00", "yesterday"]
)
@pytest.mark.parametrize(
    ("which", "path", "message"),
    [
        ("sbom", "metadata.timestamp", "not a date and time with a time zone"),
        ("scan", "descriptor.timestamp", "descriptor.timestamp is missing or not a date and time"),
        ("scan", "descriptor.db.status.built", "does not record its database's build time"),
    ],
)
def test_a_time_outside_utcs_range_is_refused_as_an_unreadable_one(
    tmp_path: Path, which: str, path: str, message: str, value: str
) -> None:
    sbom, scan = sbom_doc(), scan_doc()
    mutate(sbom if which == "sbom" else scan, path, value)
    out = tmp_path / "model.yaml"
    with pytest.raises(SbomImportError, match=message):
        run(dump(tmp_path, "s.json", sbom), scan=dump(tmp_path, "g.json", scan), output=out)
    assert not out.exists()


def test_the_command_exits_2_on_a_time_outside_utcs_range(tmp_path: Path, capsys) -> None:
    early = "0001-01-01T00:00:00+14:00"
    sbom = dump(tmp_path, "s.json", mutate(sbom_doc(), "metadata.timestamp", early))
    argv = ["import-sbom", str(sbom), "--platform", PLATFORM, "-o", str(tmp_path / "model.yaml")]
    assert cli.main(argv) == 2
    assert "metadata.timestamp is '0001-01-01T00:00:00+14:00'" in capsys.readouterr().err
    assert not (tmp_path / "model.yaml").exists()


# Review of e12ab07, finding 1: a variant the packages pin is the build's -----------------

INSTANCE_OF = f"product-instance:{DIGEST.replace(':', '-')}-"  # and the platform's parts


def instance(doc: dict) -> dict:
    (build,) = doc["product_instances"]
    return build


def without_arch(sbom: dict) -> dict:
    """`sbom` with no arch qualifier on any package: nothing names its CPU."""
    for component in sbom["components"]:
        if "purl" in component:
            component["purl"] = component["purl"].replace("arch=aarch64&", "")
    return sbom


@pytest.mark.parametrize(
    ("arch", "distribution", "platform", "built"),
    [
        ("armv7", None, "linux/arm/v6", "arm/v7"),  # the review's example: Alpine's ARMv7
        ("armhf", None, "linux/arm/v7", "arm/v6"),  # Alpine's armhf is ARMv6
        ("armhf", "deb/debian", "linux/arm/v6", "arm/v7"),  # and Debian's ARMv7
        ("armhf", "deb/ubuntu", "linux/arm/v6", "arm/v7"),
        ("armel", "deb/debian", "linux/arm/v7", "arm/v5"),
        ("armv7hl", "rpm/fedora", "linux/arm/v6", "arm/v7"),
        ("armv6hl", "rpm/fedora", "linux/arm/v7", "arm/v6"),
    ],
)
def test_a_variant_the_packages_contradict_is_kept_with_a_warning(
    tmp_path: Path, arch: str, distribution, platform: str, built: str
) -> None:
    # Refused until the review of 4be86c1 (finding 1): the platform names the variant, and
    # the packages only warn.
    sbom = dump(tmp_path, "s.json", built_for(sbom_doc(), arch, distribution))
    result = run(sbom, platform=platform, output=tmp_path / "model.yaml")
    doc = load(tmp_path / "model.yaml")
    assert len(doc["components"]) == 17
    assert instance(doc)["id"] == f"{INSTANCE_OF}{platform.replace('/', '-')}"
    found = (
        f"16 of the SBOM's packages are built for {built} (arch={arch}) and none for "
        f"{platform.removeprefix('linux/')}, though the platform is {platform} (from --platform)"
    )
    (warning,) = result.warnings
    assert warning.startswith(f"s.json: {found}. Every package is kept as a Component; ")
    assert warning.endswith(f", for example --platform linux/{built}")
    assert f"- {found}. " in result.report_text
    assert (
        f"16 Components built for {built} (arch={arch}), not the platform's " in result.report_text
    )
    assert followed(tmp_path, warning, sbom=built_for(sbom_doc(), arch, distribution)) == []


def test_a_variant_the_scan_records_is_kept_with_a_warning(tmp_path: Path) -> None:
    sbom = dump(tmp_path, "s.json", built_for(sbom_doc(), "armv7"))
    scan = dump(tmp_path, "g.json", direct_scan(architecture="arm", architectureVariant="v6"))
    result = run(sbom, scan=scan, platform=None, output=tmp_path / "model.yaml")
    assert instance(load(tmp_path / "model.yaml"))["id"] == f"{INSTANCE_OF}linux-arm-v6"
    # The scan records v6, so the advice names a scan that records no platform.
    assert result.warnings == [
        "s.json: 16 of the SBOM's packages are built for arm/v7 (arch=armv7) and none for "
        "arm/v6, though the platform is linux/arm/v6 (from the scan (source.target)). Every "
        "package is kept as a Component; if the SBOM is of another build, pass its platform, "
        "for example --platform linux/arm/v7, with a scan Grype made of the SBOM (grype "
        "sbom:FILE -o json), not of the image"
    ]
    assert followed(tmp_path, result.warnings[0], sbom=built_for(sbom_doc(), "armv7")) == []


@pytest.mark.parametrize(
    ("arch", "distribution", "variant"),
    [
        ("armv7", None, "v7"),
        ("armhf", None, "v6"),
        ("armhf", "deb/debian", "v7"),
        ("armel", "deb/debian", "v5"),
        ("armv7hl", "rpm/fedora", "v7"),
    ],
)
def test_a_platform_with_no_variant_takes_the_one_its_packages_pin(
    tmp_path: Path, arch: str, distribution, variant: str
) -> None:
    sbom = built_for(sbom_doc(), arch, distribution)
    doc, report = import_sbom_doc(tmp_path, sbom, platform="linux/arm")
    assert instance(doc)["id"] == f"{INSTANCE_OF}linux-arm-{variant}"
    assert instance(doc)["name"].endswith(f" for linux/arm/{variant}")
    assert (
        f"Platform: linux/arm/{variant}, from --platform, and its variant {variant} from the "
        f"packages' arch={arch}." in report
    )


def test_the_arm_v6_and_v7_builds_of_one_index_are_two_builds(tmp_path: Path) -> None:
    # One index digest, and --platform linux/arm for both: the packages tell them apart.
    v6, _ = import_sbom_doc(
        folder(tmp_path, "v6"), built_for(sbom_doc(), "armhf"), platform="linux/arm"
    )
    v7, _ = import_sbom_doc(
        folder(tmp_path, "v7"), built_for(sbom_doc(), "armv7"), platform="linux/arm"
    )
    assert instance(v6)["version"] == instance(v7)["version"] == DIGEST
    assert instance(v6)["id"] != instance(v7)["id"]


def test_packages_that_pin_two_variants_are_refused(tmp_path: Path) -> None:
    sbom = built_for(sbom_doc(), "armv7")
    zlib = next(c for c in sbom["components"] if c.get("name") == "zlib")
    zlib["purl"] = zlib["purl"].replace("arch=armv7", "arch=armhf")  # Alpine's ARMv6
    message = r"more than one variant of arm: arm/v6 \(arch=armhf\) and arm/v7 \(arch=armv7\)"
    with pytest.raises(SbomImportError, match=message):
        run(dump(tmp_path, "s.json", sbom), platform="linux/arm", output=tmp_path / "model.yaml")
    assert not (tmp_path / "model.yaml").exists()


@pytest.mark.parametrize(
    "sbom",
    [
        # Raspbian writes Debian's armhf for ARMv6, so its armhf pins no variant.
        lambda: built_for(sbom_doc(), "armhf", "deb/raspbian"),
        lambda: without_arch(sbom_doc()),  # no package names a CPU at all
    ],
)
def test_32_bit_arm_with_no_variant_anywhere_is_refused(tmp_path: Path, sbom) -> None:
    path = dump(tmp_path, "s.json", sbom())
    with pytest.raises(SbomImportError, match="names no variant, and no package's arch"):
        run(path, platform="linux/arm", output=tmp_path / "model.yaml")
    assert not (tmp_path / "model.yaml").exists()
    doc, _ = import_sbom_doc(tmp_path, sbom(), platform="linux/arm/v6")  # named, it is read
    assert instance(doc)["id"] == f"{INSTANCE_OF}linux-arm-v6"


def test_arm64_with_no_variant_is_v8(tmp_path: Path) -> None:
    models, reports = [], []
    for platform in ("linux/arm64", "linux/arm64/v8"):
        out = folder(tmp_path, platform.replace("/", "-")) / "model.yaml"
        reports.append(run(SBOM, scan=SCAN, platform=platform, output=out).report_text)
        models.append(out.read_bytes())
    assert models[0] == models[1]  # one platform, so one build, one id and one model
    assert instance(yaml.safe_load(models[0]))["id"] == INSTANCE
    assert (
        "linux/arm64 names no variant; for arm64 that is v8, the only arm64 variant the OCI "
        "image index specification lists" in reports[0]
    )


def test_a_32_bit_siblings_variant_is_not_the_builds(tmp_path: Path) -> None:
    sbom = sbom_doc()
    zlib_copy(sbom, ARM32_ZLIB)  # Alpine's ARMv7 zlib beside the arm64 one (multiarch)
    armhf = zlib_copy(sbom, ZLIB.replace("arch=aarch64", "arch=armhf"))  # and its ARMv6 one
    armhf["bom-ref"] += "-armhf"
    doc, report = import_sbom_doc(tmp_path, sbom, platform="linux/arm64")
    assert instance(doc)["id"] == INSTANCE  # arm64's own variant, v8, not a sibling's
    assert "16 Components built for arm64 (arch=aarch64)" in report
    assert "1 Component built for arm/v6 (arch=armhf), which arm64 also runs" in report
    assert "1 Component built for arm/v7 (arch=armv7), which arm64 also runs" in report


@pytest.mark.parametrize(
    ("platform", "message"),
    [
        ("linux/armhf", "a distribution's name for arm/v6 or arm/v7"),
        ("linux/armv7hl", "a distribution's name for arm/v7"),
    ],
)
def test_a_distributions_name_that_pins_a_variant_is_refused_as_a_platform(
    tmp_path: Path, platform: str, message: str
) -> None:
    with pytest.raises(SbomImportError, match=message):
        run(SBOM, platform=platform, output=tmp_path / "model.yaml")
    assert list(tmp_path.iterdir()) == []


# Review of e12ab07, finding 2: no two platforms give one id ------------------------------


@pytest.mark.parametrize(
    "platform",
    [
        "linux/arm64/v8-1",  # the review's example, whose id was v8.1's
        "linux/arm64/v8_1",
        "linux/arm64/v8.",
        "linux/arm64/.v8",
        "linux/arm64/v8..1",
        "linux/arm-64/v8",
        "lin_ux/arm64",
        "linux/arm64.1",
    ],
)
def test_a_platform_part_outside_its_form_is_refused(tmp_path: Path, platform: str) -> None:
    with pytest.raises(SbomImportError, match="not OS/ARCH or OS/ARCH/VARIANT: the os and"):
        run(SBOM, platform=platform, output=tmp_path / "model.yaml")
    assert list(tmp_path.iterdir()) == []


def test_a_scans_platform_part_outside_its_form_is_refused(tmp_path: Path) -> None:
    scan = dump(tmp_path, "g.json", direct_scan(architectureVariant="v8-1"))
    with pytest.raises(SbomImportError, match="architectureVariant is 'v8-1', not a platform's"):
        run(SBOM, scan=scan, platform=None, output=tmp_path / "model.yaml")


def test_v8_1_and_v8_dash_1_are_never_one_build(tmp_path: Path) -> None:
    # On e12ab07 both gave product-instance:sha256-...-linux-arm64-v8-1.
    with pytest.raises(SbomImportError, match="not OS/ARCH or OS/ARCH/VARIANT"):
        run(SBOM, platform="linux/arm64/v8-1", output=tmp_path / "model.yaml")
    doc, _ = import_sbom_doc(tmp_path, sbom_doc(), platform="linux/arm64/v8.1")
    assert instance(doc)["id"] == f"{INSTANCE_OF}linux-arm64-v8-1"  # a variant's dot, as -
    assert instance(doc)["name"].endswith(" for linux/arm64/v8.1")


def test_distinct_platforms_never_share_an_id(tmp_path: Path) -> None:
    # Every valid platform, with and without a variant, dotted variants too: the id is
    # the same exactly when the platform is (arm64 with no variant is arm64/v8).
    sbom = dump(tmp_path, "s.json", without_arch(sbom_doc()))
    variants = (None, "v1", "v7", "v8", "v8.0", "v8.1", "v81", "v8.1.1", "v8.11", "v81.1", "8.1")
    ids: dict[str, set[str]] = {}  # the platform the model names -> its ids
    for os_name in ("linux", "windows"):
        for arch in ("amd64", "arm64", "arm", "386"):
            for variant in variants:
                platform = "/".join(p for p in (os_name, arch, variant) if p)
                if arch == "arm" and variant is None:
                    continue  # refused: 32-bit ARM needs its variant (finding 1)
                result = import_sbom.build(sbom, platform=platform)
                build = instance(yaml.safe_load(result.model_text))
                named = build["name"].rsplit(" for ", 1)[1]
                assert named == (
                    f"{platform}/v8" if (arch, variant) == ("arm64", None) else platform
                )
                ids.setdefault(named, set()).add(build["id"])
    assert all(len(found) == 1 for found in ids.values())  # one platform, one id
    assert len(set().union(*ids.values())) == len(ids)  # and no id for two platforms


# Review of e12ab07, not blocking: a blank description is counted as left out -------------

BLANKS = ["", "   ", "\n\t ", "　", "​", None]  # 　 an ideographic space


@pytest.mark.parametrize("blank", BLANKS)
def test_a_blank_advisory_description_is_counted_as_left_out(tmp_path: Path, blank) -> None:
    advisory = match("GHSA-aaaa-bbbb-cccc", ("CVE-2026-0001",))
    advisory["vulnerability"]["description"] = blank  # the advisory's own record
    advisory["relatedVulnerabilities"][0]["description"] = "NVD's words."
    doc, report = import_matches(tmp_path, [advisory])
    assert doc["vulnerabilities"][0]["description"] == "NVD's words."
    fields = field_lines(report)
    assert fields["matches[].vulnerability.description"] == "left out: 1 blank (counted above)"
    assert fields["matches[].relatedVulnerabilities[].description"] == "Vulnerability.description"
    assert "- 1 scan descriptions that are blank (null, or nothing but white space" in report
    assert "Advisory descriptions left out" not in report  # nothing to list


@pytest.mark.parametrize("blank", BLANKS)
def test_a_blank_vulnerability_description_is_not_written(tmp_path: Path, blank) -> None:
    row = match("CVE-2026-0001")
    row["vulnerability"]["description"] = blank
    doc, report = import_matches(tmp_path, [row])
    assert "description" not in doc["vulnerabilities"][0]
    assert field_lines(report)["matches[].vulnerability.description"] == (
        "left out: 1 blank (counted above)"
    )


@pytest.mark.parametrize("blank", BLANKS)
def test_a_blank_component_description_is_counted_as_left_out(tmp_path: Path, blank) -> None:
    sbom = sbom_doc()
    next(c for c in sbom["components"] if c.get("name") == "zlib")["description"] = blank
    doc, report = import_sbom_doc(tmp_path, sbom)
    zlib = next(c for c in doc["components"] if c["name"] == "zlib 1.3.2-r0")
    assert "description" not in zlib
    assert "- 1 SBOM component descriptions that are blank (null, or nothing but" in report
    assert (
        "left out where it is blank (counted above)"
        in field_lines(report)["components[].description"]
    )


# Review of e12ab07 (@Maimcghee), finding 1: the depth is checked first, on every Python ---


def test_the_depth_is_checked_before_the_top_level(tmp_path: Path, monkeypatch) -> None:
    # Python 3.14's json reads a 100,000-deep array, where 3.11 to 3.13 raise
    # RecursionError; read as 3.14 reads it, the file must still nest too deeply.
    text = "[" * 100_000 + "]" * 100_000
    deep: list = []
    for _ in range(100_000 - 1):
        deep = [deep]
    real = json.loads

    def loads_as_314(given: str, *args, **kwargs):
        return deep if given == text else real(given, *args, **kwargs)

    bad = tmp_path / "deep.json"
    bad.write_text(text, encoding="utf-8")
    monkeypatch.setattr(import_sbom.json, "loads", loads_as_314)
    with pytest.raises(SbomImportError, match="nests too deeply"):
        run(bad, output=tmp_path / "model.yaml")
    assert not (tmp_path / "model.yaml").exists()


# Review of f21f4a5, finding 1: packages built for another platform are kept -------------


def package(sbom: dict, name: str) -> dict:
    return next(c for c in sbom["components"] if c.get("name") == name)


def foreign_copy(sbom: dict, name: str, arch: str) -> dict:
    """A copy of the package `name` built for another CPU, with its own bom-ref, as
    Debian's multiarch installs one beside the native build for cross-compiling."""
    copied = copy.deepcopy(package(sbom, name))
    copied["bom-ref"] += f"-{arch}"
    copied["purl"] = copied["purl"].replace("arch=aarch64", f"arch={arch}")
    sbom["components"].append(copied)
    return copied


def depends(sbom: dict, dependent: dict, dependency: dict) -> None:
    """Add the edge `dependent` dependsOn `dependency` to the SBOM's dependencies."""
    for entry in sbom["dependencies"]:
        if entry["ref"] == dependent["bom-ref"]:
            entry["dependsOn"].append(dependency["bom-ref"])
            return
    sbom["dependencies"].append({"ref": dependent["bom-ref"], "dependsOn": [dependency["bom-ref"]]})


def rebuilt(sbom: dict, arch: str, count: int) -> dict:
    """`sbom` with the first `count` of its aarch64 packages, by name, built for `arch`."""
    native = [c for c in sbom["components"] if "arch=aarch64" in c.get("purl", "")]
    for component in sorted(native, key=lambda c: c["name"])[:count]:
        component["purl"] = component["purl"].replace("arch=aarch64", f"arch={arch}")
    return sbom


def edges(doc: dict) -> set[tuple[str, str]]:
    return {(c["id"], used) for c in doc["components"] for used in c.get("uses_component", [])}


@pytest.mark.parametrize("direct", [False, True], ids=["--platform", "a scan of the image"])
def test_packages_built_for_another_platform_are_kept(imported, tmp_path: Path, direct) -> None:
    # The review's case: the native packages and the platform agree, and two packages are
    # built for x86_64, with a dependency from a native one and a match of their own.
    _, fixture, _ = imported
    sbom = sbom_doc()
    zlib, musl = (foreign_copy(sbom, name, "x86_64") for name in ("zlib", "musl"))
    depends(sbom, zlib, musl)
    depends(sbom, package(sbom, "scanelf"), zlib)  # from a native package to a foreign one
    scan = direct_scan() if direct else scan_doc()
    scan["matches"].append(match("CVE-2026-0001", purl=X86_ZLIB))
    out = tmp_path / "model.yaml"
    result = run(
        dump(tmp_path, "s.json", sbom),
        scan=dump(tmp_path, "g.json", scan),
        platform=None if direct else PLATFORM,
        output=out,
    )
    doc = load(out)
    components, theirs = by_id(doc, "components"), by_id(fixture, "components")
    assert set(theirs) < set(components)  # every Component of the fixture's model, and
    added = {components[i]["identifiers"][0]: i for i in set(components) - set(theirs)}
    assert sorted(added) == [X86_MUSL, X86_ZLIB]  # and the two foreign ones
    assert edges(doc) == edges(fixture) | {
        (added[X86_ZLIB], added[X86_MUSL]),
        ("component:apk-alpine-scanelf-1-3-9-r1-d3af478a", added[X86_ZLIB]),
    }
    assertions = by_id(doc, "assertions")
    assert set(by_id(fixture, "assertions")) < set(assertions)
    (new,) = [a for i, a in assertions.items() if i not in by_id(fixture, "assertions")]
    assert (new["predicate"], new["object"]) == ("propagates_to", added[X86_ZLIB])
    assert instance(doc)["id"] == INSTANCE
    assert set(added.values()) < set(instance(doc)["build_composed_of"])
    assert result.counts["components"] == 19 and result.counts["match_assertions"] == 31
    report = result.report_text
    assert (
        "- The packages fit the platform: 16 Components built for arm64 (arch=aarch64)." in report
    )
    assert "2 Components built for amd64 (arch=x86_64), not the platform's arm64: kept." in report
    assert (
        "# 2 Components built for another platform (amd64) are kept; the report lists them.\n"
        in result.model_text
    )


def test_arm64_packages_are_foreign_to_a_32_bit_arm_platform(tmp_path: Path) -> None:
    # A 32-bit CPU does not run 64-bit code, so arm64 packages are foreign to arm/v7, and
    # counted apart from the platform's own: 15 for arm/v7 against 1 for arm64.
    sbom = rebuilt(sbom_doc(), "armv7", 15)
    doc, report = import_sbom_doc(tmp_path, sbom, platform="linux/arm/v7")
    assert instance(doc)["id"] == f"{INSTANCE_OF}linux-arm-v7"
    assert len(doc["components"]) == 17
    assert "15 Components built for arm/v7 (arch=armv7)" in report
    assert "1 Component built for arm64 (arch=aarch64), not the platform's arm: kept." in report


@pytest.mark.parametrize(
    ("rebuild", "found", "other"),
    [
        (  # the fixture itself
            {},
            "16 of the SBOM's packages are built for arm64 (arch=aarch64) and none for amd64 or "
            "the 386 it also runs, though the platform is linux/amd64 (from --platform)",
            "linux/arm64/v8",
        ),
        (  # the fourth round's: 1 for the platform beside 15 for another
            {"x86_64": 1},
            "15 of the SBOM's packages are built for arm64 (arch=aarch64) and 1 for amd64 or the "
            "386 it also runs, though the platform is linux/amd64 (from --platform)",
            "linux/arm64/v8",
        ),
        (  # another platform's packages count with its sibling's, as the platform's do
            {"x86_64": 6, "armv7": 5},
            "10 of the SBOM's packages are built for arm64 and arm (arch=aarch64, armv7) and 6 "
            "for amd64 or the 386 it also runs, though the platform is linux/amd64 (from "
            "--platform)",
            "linux/arm64/v8",  # 10 native there: its 5 and the 5 for arm
        ),
        (  # all for the sibling, which amd64 runs, and none for amd64 itself
            {"x86": 16},
            "none of the SBOM's packages is built for amd64, though the platform is linux/amd64 "
            "(from --platform); they say arch=x86 (16 Components)",
            "linux/386",
        ),
    ],
)
def test_most_packages_built_for_another_platform_give_a_warning(
    tmp_path: Path, rebuild: dict, found: str, other: str
) -> None:
    # Refused until the review of 4be86c1 (finding 1), which keeps the counts as a warning.
    sbom = sbom_doc()
    for arch, count in rebuild.items():
        rebuilt(sbom, arch, count)
    path = dump(tmp_path, "s.json", sbom)
    result = run(path, platform="linux/amd64", output=tmp_path / "model.yaml")
    doc = load(tmp_path / "model.yaml")
    assert len(doc["components"]) == 17
    assert instance(doc)["id"] == f"{INSTANCE_OF}linux-amd64"
    note = (
        f"{found}. Every package is kept as a Component; if the SBOM is of another build, pass "
        f"its platform, for example --platform {other}"
    )
    assert result.warnings == [f"s.json: {note}"]
    assert f"- {note}.\n" in result.report_text
    assert followed(tmp_path, result.warnings[0], sbom=sbom) == []


@pytest.mark.parametrize(
    ("half", "rest", "platform", "kept"),
    [
        ("x86_64", "aarch64", "linux/arm64/v8", "amd64 (arch=x86_64), not the platform's arm64"),
        ("x86_64", "aarch64", "linux/amd64", "arm64 (arch=aarch64), not the platform's amd64"),
        # Alpine's armhf is ARMv6 and its armv7 ARMv7 (ARCH_VARIANTS): a tie of variants
        ("armhf", "armv7", "linux/arm/v6", "arm/v7 (arch=armv7), not the platform's arm/v6"),
        ("armhf", "armv7", "linux/arm/v7", "arm/v6 (arch=armhf), not the platform's arm/v7"),
    ],
)
def test_a_tie_with_another_platform_gives_no_warning(
    tmp_path: Path, half: str, rest: str, platform: str, kept: str
) -> None:
    # A tie with another build gives no warning of its own, and since the review of
    # 4be86c1 (finding 1) no note of a tie. Each case has packages for the platform's own
    # architecture; one with none still warns, for that (item 13 of the fifth round).
    sbom = built_for(rebuilt(sbom_doc(), half, 8), rest)  # 8 packages for each of two builds
    result = run(dump(tmp_path, "s.json", sbom), platform=platform, output=tmp_path / "model.yaml")
    doc = load(tmp_path / "model.yaml")
    assert instance(doc)["name"].endswith(f" for {platform}")
    assert len(doc["components"]) == 17
    assert result.warnings == []
    assert "a tie" not in result.report_text
    assert f"8 Components built for {kept}: kept." in result.report_text


def test_packages_pinning_another_variant_beside_the_platforms_are_kept(tmp_path: Path) -> None:
    sbom = built_for(rebuilt(sbom_doc(), "armhf", 1), "armv7")  # 1 for arm/v6, 15 for v7
    doc, report = import_sbom_doc(tmp_path, sbom, platform="linux/arm/v7")
    assert instance(doc)["id"] == f"{INSTANCE_OF}linux-arm-v7"
    assert len(doc["components"]) == 17
    assert "- The packages fit the platform: 15 Components built for arm/v7 (arch=armv7)." in report
    assert "1 Component built for arm/v6 (arch=armhf), not the platform's arm/v7: kept." in report


@pytest.mark.parametrize(
    ("armhf", "found"),
    [
        (  # the third round's contradicting selection
            0,
            "16 of the SBOM's packages are built for arm/v7 (arch=armv7) and none for arm/v6, "
            "though the platform is linux/arm/v6 (from --platform)",
        ),
        (  # most of them contradict it, as for an architecture
            1,
            "15 of the SBOM's packages are built for arm/v7 (arch=armv7) and 1 for arm/v6, "
            "though the platform is linux/arm/v6 (from --platform)",
        ),
    ],
)
def test_most_packages_pinning_another_variant_give_a_warning(
    tmp_path: Path, armhf: int, found: str
) -> None:
    # Refused until the review of 4be86c1 (finding 1): the platform keeps its variant.
    sbom = dump(tmp_path, "s.json", built_for(rebuilt(sbom_doc(), "armhf", armhf), "armv7"))
    result = run(sbom, platform="linux/arm/v6", output=tmp_path / "model.yaml")
    doc = load(tmp_path / "model.yaml")
    assert len(doc["components"]) == 17
    assert instance(doc)["id"] == f"{INSTANCE_OF}linux-arm-v6"
    note = (
        f"{found}. Every package is kept as a Component; if the SBOM is of another build, pass "
        "its platform, for example --platform linux/arm/v7"
    )
    assert result.warnings == [f"s.json: {note}"]
    assert f"- {note}.\n" in result.report_text
    kept = f"{16 - armhf} Components built for arm/v7 (arch=armv7), not the platform's arm/v6: kept"
    assert kept in result.report_text
    again = built_for(rebuilt(sbom_doc(), "armhf", armhf), "armv7")
    assert followed(tmp_path, result.warnings[0], sbom=again) == []


def test_two_variants_and_a_platform_that_names_none_asks_for_it(tmp_path: Path) -> None:
    sbom = dump(tmp_path, "s.json", built_for(rebuilt(sbom_doc(), "armhf", 1), "armv7"))
    message = (
        r"more than one variant of arm: arm/v6 \(arch=armhf\) and arm/v7 \(arch=armv7\), for 1 "
        r"and 15 Components, but the platform is linux/arm \(from --platform\), which names no "
        r"variant, .* Pass --platform linux/arm/VARIANT as the image index lists it, for example "
        "--platform linux/arm/v7"
    )
    with pytest.raises(SbomImportError, match=message):
        run(sbom, platform="linux/arm", output=tmp_path / "model.yaml")
    assert not (tmp_path / "model.yaml").exists()


# Review of f21f4a5, not blocking: each backup --force makes is tracked once made ----------


def failing_second_backup(monkeypatch) -> list[Path]:
    """Make the second backup --force makes fail, as a full disk would. Returns the
    backups made before it."""
    real, made = import_sbom._keep, []

    def keep(path: Path) -> Path:
        if made:
            raise OSError(28, "No space left on device")
        made.append(real(path))
        return made[-1]

    monkeypatch.setattr(import_sbom, "_keep", keep)
    return made


def forced_outputs(tmp_path: Path) -> tuple[Path, Path]:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    out.write_text("edited by a person\n", encoding="utf-8")
    report.write_text("an older report\n", encoding="utf-8")
    return out, report


def test_a_failed_second_backup_leaves_no_first_one(tmp_path: Path, monkeypatch) -> None:
    out, report = forced_outputs(tmp_path)
    made = failing_second_backup(monkeypatch)
    with pytest.raises(OSError, match="No space left"):
        run(SBOM, scan=SCAN, output=out, report=report, force=True)
    assert len(made) == 1  # the first backup was made, and is removed
    assert out.read_text(encoding="utf-8") == "edited by a person\n"
    assert report.read_text(encoding="utf-8") == "an older report\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["model.yaml", "report.md"]


def test_a_backup_that_cannot_be_removed_is_named(tmp_path: Path, monkeypatch) -> None:
    out, report = forced_outputs(tmp_path)
    made = failing_second_backup(monkeypatch)
    real = os.unlink

    def unlink(path, *args, **kwargs):  # and removing the first one fails too
        if Path(path).name.endswith(".old"):
            raise PermissionError(13, "Permission denied")
        return real(path, *args, **kwargs)

    monkeypatch.setattr(import_sbom.os, "unlink", unlink)
    with pytest.raises(OSError, match="No space left") as raised:
        run(SBOM, scan=SCAN, output=out, report=report, force=True)
    (left,) = made
    notes = getattr(raised.value, "__notes__", [])
    assert any(left.name in note and "could not be removed" in note for note in notes)
    assert out.read_text(encoding="utf-8") == "edited by a person\n"
    assert report.read_text(encoding="utf-8") == "an older report\n"


# Review of 4be86c1, finding 1: the packages' architectures warn, where they refused ------


def mostly_another_platforms(sbom: dict) -> dict:
    """`sbom` with two packages built for x86_64 beside its 16 for arm64, one depending on
    the other and an arm64 one depending on one of them: under linux/amd64, an SBOM most
    of whose packages are another platform's."""
    zlib, musl = (foreign_copy(sbom, name, "x86_64") for name in ("zlib", "musl"))
    depends(sbom, zlib, musl)
    depends(sbom, package(sbom, "scanelf"), zlib)
    return sbom


@pytest.mark.parametrize(
    ("direct", "source"),
    [(True, "--platform and the scan (source.target)"), (False, "--platform")],
    ids=["--platform and a scan of the image", "--platform alone"],
)
def test_an_sbom_mostly_for_another_platform_imports_with_a_warning(
    imported, tmp_path: Path, direct: bool, source: str
) -> None:
    # The review's case: 16 packages for arm64 and 2 for amd64, and the platform is
    # linux/amd64, as --platform and a scan Grype made of the image itself both say.
    _, fixture, _ = imported
    sbom = mostly_another_platforms(sbom_doc())
    if direct:
        scan = direct_scan(architecture="amd64")
        del scan["source"]["target"]["architectureVariant"]
    else:
        scan = scan_doc()  # made of the SBOM, so it records no platform
    scan["matches"].append(match("CVE-2026-0001", purl=X86_ZLIB))
    out = tmp_path / "model.yaml"
    result = run(
        dump(tmp_path, "s.json", sbom),
        scan=dump(tmp_path, "g.json", scan),
        platform="linux/amd64",
        output=out,
    )
    doc = load(out)
    assert instance(doc)["id"] == f"{INSTANCE_OF}linux-amd64"
    components, theirs = by_id(doc, "components"), by_id(fixture, "components")
    assert set(theirs) < set(components)  # every package of the fixture's model, and
    added = {components[i]["identifiers"][0]: i for i in set(components) - set(theirs)}
    assert sorted(added) == [X86_MUSL, X86_ZLIB]  # the two for amd64
    assert sorted(instance(doc)["build_composed_of"]) == sorted(components)
    assert edges(doc) == edges(fixture) | {
        (added[X86_ZLIB], added[X86_MUSL]),
        ("component:apk-alpine-scanelf-1-3-9-r1-d3af478a", added[X86_ZLIB]),
    }
    assertions = by_id(doc, "assertions")
    assert set(by_id(fixture, "assertions")) < set(assertions)  # the 45, and one more
    (new,) = [a for i, a in assertions.items() if i not in by_id(fixture, "assertions")]
    assert (new["predicate"], new["object"]) == ("propagates_to", added[X86_ZLIB])
    assert result.counts["components"] == 19 and result.counts["match_assertions"] == 31
    found = (
        "16 of the SBOM's packages are built for arm64 (arch=aarch64) and 2 for amd64 or the "
        f"386 it also runs, though the platform is linux/amd64 (from {source})"
    )
    advice = (
        "if the SBOM is of another build, pass its platform, for example --platform linux/arm64/v8"
    )
    if direct:  # this scan records linux/amd64, so another build needs a scan of the SBOM
        advice += ", with a scan Grype made of the SBOM (grype sbom:FILE -o json), not of the image"
    note = f"{found}. Every package is kept as a Component; {advice}"
    assert result.warnings == [f"s.json: {note}"]
    report = result.report_text
    assert f"- {note}.\n" in report
    assert (
        "- The packages fit the platform: 2 Components built for amd64 (arch=x86_64).\n" in report
    )
    assert "16 Components built for arm64 (arch=aarch64), not the platform's amd64: kept." in report
    assert (
        "# 16 Components built for another platform (arm64) are kept; the report lists them.\n"
        in result.model_text
    )
    assert followed(tmp_path, result.warnings[0], sbom=sbom) == []


def test_an_sbom_with_no_package_for_the_platforms_architecture_imports_with_a_warning(
    imported, tmp_path: Path
) -> None:
    # Every package built for 386, which amd64 also runs, and none for amd64 itself: each
    # is kept, with its edges and its matches.
    _, fixture, _ = imported
    scan = scan_doc()
    for row in scan["matches"]:
        row["artifact"]["purl"] = row["artifact"]["purl"].replace("arch=aarch64", "arch=x86")
    result = run(
        dump(tmp_path, "s.json", built_for(sbom_doc(), "x86")),
        scan=dump(tmp_path, "g.json", scan),
        platform="linux/amd64",
        output=tmp_path / "model.yaml",
    )
    doc = load(tmp_path / "model.yaml")
    # By name: each build's packages have ids of their own (item 7 of this round).
    assert by_name(doc) == by_name(fixture)
    assert result.counts == {
        "components": 17,
        "dependency_edges": 24,
        "vulnerabilities": 15,
        "weaknesses": 9,
        "match_assertions": 30,
        "cwe_assertions": 15,
        "parties": 4,
    }
    note = (
        "none of the SBOM's packages is built for amd64, though the platform is linux/amd64 "
        "(from --platform); they say arch=x86 (16 Components). Every package is kept as a "
        "Component; if the SBOM is of another build, pass its platform, for example "
        "--platform linux/386"
    )
    assert result.warnings == [f"s.json: {note}"]
    assert f"- {note}.\n" in result.report_text
    assert (
        "- The packages fit the platform: 16 Components built for 386 (arch=x86), which amd64 "
        "also runs (multiarch and multilib).\n" in result.report_text
    )
    assert followed(tmp_path, result.warnings[0], sbom=built_for(sbom_doc(), "x86")) == []


def by_name(doc: dict) -> tuple[list, list, list]:
    """A model's Components, dependency edges and Assertions by the Components' names,
    for two builds whose Components have ids of their own."""
    names = {c["id"]: c["name"] for c in doc["components"]}
    return (
        sorted(names.values()),
        sorted((names[dependent], names[used]) for dependent, used in edges(doc)),
        sorted(
            (a["subject"], a["predicate"], names.get(a["object"], a["object"]))
            for a in doc["assertions"]
        ),
    )


def advised(warning: str) -> str:
    """The platform a warning's advice names."""
    return warning.split("for example --platform ", 1)[1].split(",", 1)[0]


def followed(tmp_path: Path, warning: str, *, sbom: dict, **kwargs) -> list[str]:
    """The warnings of the same SBOM imported again, with no scan unless one is given,
    under the platform the warning advises. Each test that calls it expects none: the
    advice leads to a model with no warning (items 6 and 14 of the fifth round)."""
    name = f"followed-{len(list(tmp_path.glob('followed-*')))}"
    path = dump(folder(tmp_path, name), "s.json", sbom)
    platform = advised(warning)
    return run(path, platform=platform, output=path.with_name("model.yaml"), **kwargs).warnings


def test_metadata_that_contradicts_the_platform_is_still_refused(tmp_path: Path) -> None:
    # The packages' architectures only warn, but what gives the platform must agree: the
    # same SBOM imports under --platform, and is refused with a scan of the image pulled
    # for another platform, or with an image purl for another architecture.
    sbom = mostly_another_platforms(sbom_doc())
    out = tmp_path / "model.yaml"
    result = run(dump(tmp_path, "s.json", sbom), platform="linux/amd64", output=out)
    assert len(load(out)["components"]) == 19 and len(result.warnings) == 1
    assert followed(tmp_path, result.warnings[0], sbom=sbom) == []
    out.unlink()
    arm64 = dump(tmp_path, "g.json", direct_scan())  # pulled for linux/arm64/v8
    with pytest.raises(SbomImportError, match="gives the architecture amd64, but the scan records"):
        run(dump(tmp_path, "s.json", sbom), scan=arm64, platform="linux/amd64", output=out)
    sbom["metadata"]["component"]["purl"] = (
        "pkg:oci/alpine@" + DIGEST.replace(":", "%3A") + "?arch=arm64"
    )
    message = r"metadata.component.purl says arch=arm64, but the platform is linux/amd64 \(from"
    with pytest.raises(SbomImportError, match=message):
        run(dump(tmp_path, "s.json", sbom), platform="linux/amd64", output=out)
    assert not out.exists()


def test_the_command_prints_the_platform_warning_and_exits_0(tmp_path: Path, capsys) -> None:
    # The fixture under linux/amd64, which the fourth round refused (exit code 2).
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    argv = [
        "import-sbom",
        str(SBOM),
        "--scan",
        str(SCAN),
        "--platform",
        "linux/amd64",
        "-o",
        str(out),
        "--report",
        str(report),
    ]
    assert cli.main(argv) == 0
    captured = capsys.readouterr()
    assert captured.out.startswith("wrote ")
    assert captured.err == (
        "warning: alpine-3.24.2.cdx.json: 16 of the SBOM's packages are built for arm64 "
        "(arch=aarch64) and none for amd64 or the 386 it also runs, though the platform is "
        "linux/amd64 (from --platform). Every package is kept as a Component; if the SBOM is "
        "of another build, pass its platform, for example --platform linux/arm64/v8\n"
    )
    assert len(load(out)["components"]) == 17
    assert followed(tmp_path, captured.err.removeprefix("warning: "), sbom=sbom_doc()) == []


# Review of 4be86c1, finding 2: one repository, one Product id, in every import ------------


def product_id(tmp_path: Path, name: str, image: str, digest: str = DIGEST) -> str:
    """The Product id an import gives the fixture's SBOM of `image` at `digest`."""
    sbom = sbom_doc()
    sbom["metadata"]["component"].update(name=image, version=digest)
    model, _ = import_sbom_doc(folder(tmp_path, name), sbom)
    return model["products"][0]["id"]


def test_repositories_whose_slugs_are_one_get_distinct_product_ids(tmp_path: Path) -> None:
    # On 4be86c1 all four were product:ghcr-io-team-alpha-beta-app: the slug writes each
    # run of characters other than letters and digits as one dash.
    paths = ("alpha-beta", "alpha/beta", "alpha.beta", "alpha_beta")
    ids = [product_id(tmp_path, str(n), f"ghcr.io/team/{p}/app") for n, p in enumerate(paths)]
    assert ids == [  # the slug, and a short hash of each repository's purl (item 7)
        "product:ghcr-io-team-alpha-beta-app-e56b5526",
        "product:ghcr-io-team-alpha-beta-app-b1dbb4b7",
        "product:ghcr-io-team-alpha-beta-app-f8eb62b0",
        "product:ghcr-io-team-alpha-beta-app-84cc3bb4",
    ]


def test_one_repository_has_one_product_id_in_every_import(tmp_path: Path) -> None:
    other = "sha256:" + "a" * 64
    ids = {
        product_id(tmp_path, "tag", "ghcr.io/team/app:1.0"),
        product_id(tmp_path, "another-tag", "ghcr.io/team/app:2.0", other),
        product_id(tmp_path, "by-digest", f"ghcr.io/team/app@{other}", other),
    }
    # A short hash of the Product's key, pkg:oci/app?repository_url=ghcr.io/team/app
    assert ids == {"product:ghcr-io-team-app-5869f5a1"}


# Review of 4be86c1, finding 3: what is left once the outputs are written ------------------


def undeletable(monkeypatch, suffix: str) -> None:
    """Make removing each file whose name ends in `suffix` fail, as in a folder where this
    user can make files but not delete them."""
    real = os.unlink

    def unlink(path, *args, **kwargs):
        if Path(path).name.endswith(suffix):
            raise PermissionError(13, "Permission denied")
        return real(path, *args, **kwargs)

    monkeypatch.setattr(import_sbom.os, "unlink", unlink)


def test_a_backup_left_after_a_forced_import_is_a_warning(tmp_path: Path, monkeypatch) -> None:
    out, report = forced_outputs(tmp_path)
    undeletable(monkeypatch, ".old")  # both files are replaced; removing their backups fails
    result = run(SBOM, scan=SCAN, output=out, report=report, force=True)  # and it returns
    assert out.read_text(encoding="utf-8") == result.model_text
    assert report.read_text(encoding="utf-8") == result.report_text
    kept = {p.read_text(encoding="utf-8"): p.name for p in tmp_path.iterdir() if p.suffix == ".old"}
    assert sorted(kept) == ["an older report\n", "edited by a person\n"]
    assert len(list(tmp_path.iterdir())) == 4  # the two outputs and the two backups
    assert result.warnings == [
        f"{output}: the outputs were written, but {kept[old]}, a backup of the file --force "
        "replaced, could not be removed (Permission denied) and is left beside it; it can be "
        "deleted"
        for output, old in (
            ("model.yaml", "edited by a person\n"),
            ("report.md", "an older report\n"),
        )
    ]


def test_the_command_prints_a_kept_backup_as_a_warning_and_exits_0(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    out, report = forced_outputs(tmp_path)
    undeletable(monkeypatch, ".old")
    argv = [
        "import-sbom",
        str(SBOM),
        "--scan",
        str(SCAN),
        "--platform",
        PLATFORM,
        "-o",
        str(out),
        "--report",
        str(report),
        "--force",
    ]
    assert cli.main(argv) == 0  # on 4be86c1: 1, and "error: cannot write (Permission denied)"
    captured = capsys.readouterr()
    assert captured.out.startswith("wrote ")
    kept = sorted(p.name for p in tmp_path.iterdir() if p.suffix == ".old")
    lines = captured.err.splitlines()
    assert len(kept) == len(lines) == 2
    for name in kept:
        (line,) = [line for line in lines if name in line]
        assert line.startswith("warning: ") and "the outputs were written, but " in line
    assert load(out)["products"]
    assert report.read_text(encoding="utf-8").startswith("# tmodel import-sbom report")


def test_a_temporary_file_left_after_an_import_is_a_warning(tmp_path: Path, monkeypatch) -> None:
    # Unforced, each output is a hard link to its temporary file, which is removed once
    # both are in place; on 4be86c1, failing to remove the first took both outputs back.
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    undeletable(monkeypatch, ".tmp")
    result = run(SBOM, scan=SCAN, output=out, report=report)
    assert out.read_text(encoding="utf-8") == result.model_text
    assert report.read_text(encoding="utf-8") == result.report_text
    left = {p.read_text(encoding="utf-8"): p.name for p in tmp_path.iterdir() if p.suffix == ".tmp"}
    assert set(left) == {result.model_text, result.report_text}
    assert result.warnings == [
        f"{output}: the outputs were written, but {left[text]}, the temporary file this import "
        "wrote for it, could not be removed (Permission denied) and is left beside it; it can be "
        "deleted"
        for output, text in (("model.yaml", result.model_text), ("report.md", result.report_text))
    ]


def copies_that_fail_part_way(monkeypatch, failing: int) -> list[Path]:
    """Make --force back up each file by copying it, as on a volume without hard links,
    and make copy number `failing` (1, the model's; 2, the report's) stop half way with an
    error, as a full disk would. Returns the copies begun."""
    begun: list[Path] = []
    real = shutil.copy2

    def no_links(src, dst, *args, **kwargs):  # as on FAT and exFAT
        raise PermissionError(1, "Operation not permitted")

    def copy2(src, dst, *args, **kwargs):
        begun.append(Path(dst))
        if len(begun) < failing:
            return real(src, dst, *args, **kwargs)
        data = Path(src).read_bytes()
        Path(dst).write_bytes(data[: len(data) // 2])
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(import_sbom.os, "link", no_links)
    monkeypatch.setattr(import_sbom.shutil, "copy2", copy2)
    return begun


@pytest.mark.parametrize("failing", [1, 2], ids=["the model's backup", "the report's backup"])
def test_a_backup_copy_that_fails_part_way_leaves_nothing(
    tmp_path: Path, monkeypatch, failing: int
) -> None:
    out, report = forced_outputs(tmp_path)
    begun = copies_that_fail_part_way(monkeypatch, failing)
    with pytest.raises(OSError, match="No space left"):
        run(SBOM, scan=SCAN, output=out, report=report, force=True)
    assert len(begun) == failing  # the copies made, and the one cut short, are all removed
    assert out.read_text(encoding="utf-8") == "edited by a person\n"
    assert report.read_text(encoding="utf-8") == "an older report\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["model.yaml", "report.md"]


def test_a_partial_backup_that_cannot_be_removed_is_named(tmp_path: Path, monkeypatch) -> None:
    out, report = forced_outputs(tmp_path)
    begun = copies_that_fail_part_way(monkeypatch, 1)
    undeletable(monkeypatch, ".old")
    with pytest.raises(OSError, match="No space left") as raised:
        run(SBOM, scan=SCAN, output=out, report=report, force=True)
    (partial,) = begun
    assert partial.read_text(encoding="utf-8") == "edited by"  # half of the old model
    assert getattr(raised.value, "__notes__", []) == [
        f"model.yaml: {partial.name}, a partial copy this import made of it (the file is "
        "unchanged), could not be removed (Permission denied) and is left beside it; it can be "
        "deleted"
    ]
    assert out.read_text(encoding="utf-8") == "edited by a person\n"
    assert report.read_text(encoding="utf-8") == "an older report\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(
        ["model.yaml", "report.md", partial.name]
    )


# Review of 4be86c1, item 4: a FAT or exFAT volume's placeholder inodes -------------------

# The inode macOS's msdos driver gave one empty file in the review's probe (2**64 - 25).
PLACEHOLDER = 18446744073709551591


class Placeholder:
    """A file's status, as an empty file's reads on a FAT or exFAT volume: its inode is a
    placeholder, which changes once data is written to the file."""

    st_ino = PLACEHOLDER

    def __init__(self, info: os.stat_result) -> None:
        self._info = info

    def __getattr__(self, name: str):
        return getattr(self._info, name)


def placeholder_inodes(monkeypatch) -> None:
    """Make the volume read as FAT and exFAT do on macOS: every empty file shows one fixed
    placeholder inode, and no hard link can be made, so each output is created
    exclusively and written (_create_new)."""
    for name in ("fstat", "lstat"):
        real = getattr(os, name)

        def status(*args, real=real, **kwargs):
            info = real(*args, **kwargs)
            return Placeholder(info) if info.st_size == 0 else info

        monkeypatch.setattr(import_sbom.os, name, status)

    def no_links(src, dst, *args, **kwargs):
        raise OSError(45, "Operation not supported")

    monkeypatch.setattr(import_sbom.os, "link", no_links)


def test_a_failed_import_on_a_volume_with_placeholder_inodes_leaves_nothing(
    tmp_path: Path, monkeypatch
) -> None:
    # On 4be86c1 the model was stamped while still empty, so the undo found another inode
    # there, left the model, and said another program had replaced it.
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    placeholder_inodes(monkeypatch)
    failing_move(monkeypatch, report)  # the report cannot be created, as on a full disk
    with pytest.raises(OSError, match="No space left") as raised:
        run(SBOM, scan=SCAN, output=out, report=report)
    assert list(tmp_path.iterdir()) == []
    assert getattr(raised.value, "__notes__", []) == []  # nothing left, so nothing to say


def test_an_import_on_a_volume_with_placeholder_inodes_is_written(
    tmp_path: Path, monkeypatch
) -> None:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    placeholder_inodes(monkeypatch)
    result = run(SBOM, scan=SCAN, output=out, report=report)
    assert out.read_text(encoding="utf-8") == result.model_text
    assert report.read_text(encoding="utf-8") == result.report_text
    assert sorted(p.name for p in tmp_path.iterdir()) == ["model.yaml", "report.md"]
    assert result.warnings == []


@pytest.mark.parametrize("then", ["removed", "not removable", "replaced"])
def test_a_write_that_fails_on_a_volume_with_placeholder_inodes_is_taken_back(
    tmp_path: Path, monkeypatch, then: str
) -> None:
    # The model's own write fails (its fsync, the third after the two temporary files'),
    # and _create_new takes its file back while the path still names it.
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    placeholder_inodes(monkeypatch)
    real, calls = os.fsync, []

    def fsync(fd):
        calls.append(fd)
        if len(calls) == 3:
            if then == "replaced":  # another program puts its own file at the model's name
                (tmp_path / "theirs").write_text("their model\n", encoding="utf-8")
                os.replace(tmp_path / "theirs", out)
            raise OSError(28, "No space left on device")
        return real(fd)

    monkeypatch.setattr(import_sbom.os, "fsync", fsync)
    if then == "not removable":
        undeletable(monkeypatch, "model.yaml")
    with pytest.raises(OSError, match="No space left") as raised:
        run(SBOM, scan=SCAN, output=out, report=report)
    notes = getattr(raised.value, "__notes__", [])
    if then == "removed":
        assert list(tmp_path.iterdir()) == [] and notes == []
    elif then == "not removable":
        assert [p.name for p in tmp_path.iterdir()] == ["model.yaml"]
        assert notes == [
            "model.yaml: the file this import created there, which its failed write left "
            "unfinished, could not be removed (Permission denied) and is left there; it can "
            "be deleted"
        ]
    else:  # never removed: the path names another program's file now
        assert out.read_text(encoding="utf-8") == "their model\n"
        assert notes == [
            "model.yaml: the file this import put there was replaced by another program while "
            "the import ran, and is left as it is"
        ]


# Review of 4be86c1, item 5: a temporary file that cannot be written or removed -----------


def test_a_temporary_file_that_cannot_be_written_or_removed_is_named(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    out, report = tmp_path / "model.yaml", tmp_path / "report.md"
    real, calls = os.fsync, []

    def fsync(fd):  # the second: the report's temporary file, on a full disk
        calls.append(fd)
        if len(calls) == 2:
            raise OSError(28, "No space left on device")
        return real(fd)

    monkeypatch.setattr(import_sbom.os, "fsync", fsync)
    undeletable(monkeypatch, ".tmp")
    argv = [
        "import-sbom",
        str(SBOM),
        "--scan",
        str(SCAN),
        "--platform",
        PLATFORM,
        "-o",
        str(out),
        "--report",
        str(report),
    ]
    assert cli.main(argv) == 1
    err = capsys.readouterr().err
    left = sorted(p.name for p in tmp_path.iterdir())
    assert len(left) == 2 and all(name.endswith(".tmp") for name in left)
    # On 4be86c1 the unlink's error replaced the full disk's, and the report's temporary
    # file went unnamed.
    assert err.startswith("error: cannot write (No space left on device)\n")
    assert all(name in err for name in left)


# Review of 4be86c1, item 6: the advice never names a platform the import refuses ---------


def image_purl(sbom: dict, arch: str) -> dict:
    """`sbom` with an image purl naming the architecture `arch`, as Syft can write one."""
    sbom["metadata"]["component"]["purl"] = (
        "pkg:oci/alpine@" + DIGEST.replace(":", "%3A") + f"?arch={arch}"
    )
    return sbom


def test_an_image_purl_for_the_platform_is_named_in_place_of_another_architecture(
    tmp_path: Path,
) -> None:
    # In the round's first fixes the advice named --platform linux/arm64, which the image
    # purl then refused.
    path = dump(tmp_path, "s.json", image_purl(sbom_doc(), "amd64"))
    result = run(path, platform="linux/amd64", output=tmp_path / "model.yaml")
    assert result.warnings == [
        "s.json: 16 of the SBOM's packages are built for arm64 (arch=aarch64) and none for "
        "amd64 or the 386 it also runs, though the platform is linux/amd64 (from --platform). "
        "Every package is kept as a Component; the SBOM's own image purl also names the "
        "platform's architecture (metadata.component.purl, arch=amd64)"
    ]


def test_an_image_purl_leaves_the_advice_for_another_variant(tmp_path: Path) -> None:
    # The oci purl names no variant, so another variant of its architecture is accepted.
    sbom = image_purl(built_for(sbom_doc(), "armv7"), "arm")
    result = run(
        dump(tmp_path, "s.json", sbom), platform="linux/arm/v6", output=tmp_path / "m.yaml"
    )
    (warning,) = result.warnings
    assert advised(warning) == "linux/arm/v7"
    assert followed(tmp_path, warning, sbom=sbom) == []


@pytest.mark.parametrize("platform", ["linux/arm/v6", "linux/arm/v7"])
def test_another_architecture_outnumbering_the_platforms_gives_one_warning(
    tmp_path: Path, platform: str
) -> None:
    # The review's case, 6 Alpine armv7 packages and 10 aarch64 ones: under linux/arm/v6
    # a second warning named linux/arm/v7, under which the first came back.
    sbom = rebuilt(sbom_doc(), "armv7", 6)
    result = run(dump(tmp_path, "s.json", sbom), platform=platform, output=tmp_path / "m.yaml")
    (warning,) = result.warnings
    assert warning.startswith(
        "s.json: 10 of the SBOM's packages are built for arm64 (arch=aarch64) and 6 for arm, "
        f"though the platform is {platform} (from --platform). Every package is kept"
    )
    assert advised(warning) == "linux/arm64/v8"
    assert followed(tmp_path, warning, sbom=sbom) == []


# Review of 4be86c1, item 7: every id made from a free-form key ends in a hash of the key --


def ids_by_purl(doc: dict) -> dict[str, str]:
    return {c["identifiers"][0]: c["id"] for c in doc["components"] if c.get("identifiers")}


def test_a_components_id_is_the_same_beside_another_build_of_it(tmp_path: Path) -> None:
    # On 4be86c1 the armv7 zlib was ...-r0 alone, and ...-r0-a7ac6a88 beside the aarch64 one.
    beside = sbom_doc()
    zlib_copy(beside, ARM32_ZLIB)
    one, _ = import_sbom_doc(folder(tmp_path, "beside"), beside)
    two, _ = import_sbom_doc(
        folder(tmp_path, "alone"), built_for(sbom_doc(), "armv7"), platform="linux/arm/v7"
    )
    assert ids_by_purl(one)[ARM32_ZLIB] == ids_by_purl(two)[ARM32_ZLIB]


def test_two_builds_of_one_package_never_share_an_id(tmp_path: Path) -> None:
    # On 4be86c1 the aarch64 and the x86_64 zlib were both ...-zlib-1-3-2-r0, in their
    # separate imports, as was every other package of the two builds.
    arm, _ = import_sbom_doc(folder(tmp_path, "arm"), sbom_doc())
    amd, _ = import_sbom_doc(
        folder(tmp_path, "amd"), built_for(sbom_doc(), "x86_64"), platform="linux/amd64"
    )
    assert ids_by_purl(arm)[ZLIB] != ids_by_purl(amd)[X86_ZLIB]
    assert not set(ids_by_purl(arm).values()) & set(ids_by_purl(amd).values())


def test_parties_whose_names_slug_alike_keep_their_own_ids(tmp_path: Path) -> None:
    def parties(name: str, suppliers: dict[str, str]) -> dict[str, str]:
        sbom = sbom_doc()
        for supplied, supplier in suppliers.items():
            package(sbom, supplied)["supplier"] = {"name": supplier}
        doc, _ = import_sbom_doc(folder(tmp_path, name), sbom)
        return {p["name"]: p["id"] for p in doc["parties"]}

    both = parties("both", {"zlib": "Alpine Linux", "musl": "alpine.linux"})
    one = parties("one", {"musl": "alpine.linux"})
    assert both["Alpine Linux"] != both["alpine.linux"]
    assert one["alpine.linux"] == both["alpine.linux"]  # on 4be86c1, ...-alpine-linux here


def test_assertion_ids_hold_when_another_package_is_added(imported, tmp_path: Path) -> None:
    # A zlib whose purl has no qualifiers, and no match of its own: on 4be86c1 it took the
    # matched zlib's id, so the ids of that zlib's Assertions changed too.
    _, fixture, _ = imported
    sbom = sbom_doc()
    zlib_copy(sbom, "pkg:apk/alpine/zlib@1.3.2-r0")
    out = tmp_path / "model.yaml"
    run(dump(tmp_path, "s.json", sbom), scan=SCAN, output=out)
    assert set(by_id(load(out), "assertions")) == set(by_id(fixture, "assertions"))


# Review of 4be86c1, item 8: an id another key has taken is never given twice ------------


def test_a_purl_that_spells_another_components_id_gives_a_model(tmp_path: Path) -> None:
    # The review's crafted entry: its plain id was the armv7 zlib's fallback, which
    # 4be86c1 gave out unchecked ("internal error ... duplicate model object id").
    sbom = sbom_doc()
    zlib_copy(sbom, ARM32_ZLIB)
    crafted = "1.3.2-r0-a7ac6a88"
    sbom["components"].append(
        {
            "bom-ref": "crafted",
            "type": "library",
            "name": "zlib",
            "version": crafted,
            "purl": f"pkg:apk/alpine/zlib@{crafted}",
        }
    )
    doc, _ = import_sbom_doc(tmp_path, sbom)
    ids = [c["id"] for c in doc["components"]]
    assert len(ids) == len(set(ids)) == 19


def test_vulnerability_ids_that_spell_one_another_give_a_model(tmp_path: Path) -> None:
    # A Vulnerability's id is its slug alone, so the second of two that slug alike takes
    # its key's hash, which a third can spell: the same collision under the new rule.
    second = "ghsa-aaaa-bbbb-cccc"
    crafted = "GHSA-aaaa-bbbb-cccc-" + hashlib.sha256(second.encode()).hexdigest()[:8]
    rows = [match("GHSA-AAAA-BBBB-CCCC"), match(second), match(crafted)]
    doc, _ = import_matches(tmp_path, rows)
    ids = [v["id"] for v in doc["vulnerabilities"]]
    assert len(ids) == len(set(ids)) == 3


# Review of 4be86c1, item 9: an image purl's architecture in any case --------------------


def test_an_image_purl_names_its_architecture_in_any_case(tmp_path: Path) -> None:
    # On 4be86c1 a name the table does not know was compared as written.
    sbom = image_purl(without_arch(sbom_doc()), "MIPS64LE")
    doc, _ = import_sbom_doc(tmp_path, sbom, platform="linux/mips64le")
    assert instance(doc)["id"] == f"{INSTANCE_OF}linux-mips64le"


# Review of 4be86c1, item 10: --force keeps the mode of the file it replaces --------------


def test_a_forced_import_keeps_the_mode_of_the_file_it_replaces(tmp_path: Path) -> None:
    out, report = forced_outputs(tmp_path)
    out.chmod(0o600)  # a private model
    linked = tmp_path / "linked.md"
    linked.write_text("theirs\n", encoding="utf-8")
    linked.chmod(0o600)
    report.unlink()
    report.symlink_to(linked.name)  # and a link at the report's name
    old = os.umask(0o022)
    try:
        result = run(SBOM, scan=SCAN, output=out, report=report, force=True)
    finally:
        os.umask(old)
    assert out.read_text(encoding="utf-8") == result.model_text
    assert oct(out.stat().st_mode & 0o777) == "0o600"  # on 4be86c1, 0o644
    assert not report.is_symlink()  # the link is replaced, by a new file that follows the umask
    assert oct(report.stat().st_mode & 0o777) == "0o644"
    assert linked.read_text(encoding="utf-8") == "theirs\n"
    assert oct(linked.stat().st_mode & 0o777) == "0o600"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["linked.md", "model.yaml", "report.md"]


# Review of 4be86c1, item 11: Linux packages under another os ----------------------------


def test_linux_packages_under_another_os_give_a_warning(tmp_path: Path, capsys) -> None:
    out = tmp_path / "model.yaml"
    argv = [
        "import-sbom",
        str(SBOM),
        "--scan",
        str(SCAN),
        "--platform",
        "windows/arm64/v8",
        "-o",
        str(out),
        "--report",
        str(tmp_path / "report.md"),
    ]
    assert cli.main(argv) == 0
    warning = (
        "alpine-3.24.2.cdx.json: 16 of the SBOM's packages are apk packages, which Linux "
        "distributions install, though the platform's os is windows (the platform is "
        "windows/arm64/v8, from --platform). Every package is kept as a Component; if the "
        "SBOM is of another build, pass its platform, for example --platform linux/arm64/v8"
    )
    assert capsys.readouterr().err == f"warning: {warning}\n"
    assert instance(load(out))["id"] == f"{INSTANCE_OF}windows-arm64-v8"
    assert (
        run(SBOM, scan=SCAN, platform=advised(warning), output=tmp_path / "linux.yaml").warnings
        == []
    )


def test_two_warnings_name_one_platform_to_pass(tmp_path: Path) -> None:
    # Another os and another architecture: both warnings name linux/arm64/v8, which clears
    # them.
    result = run(SBOM, platform="windows/amd64", output=tmp_path / "model.yaml")
    assert [advised(warning) for warning in result.warnings] == ["linux/arm64/v8", "linux/arm64/v8"]
    assert followed(tmp_path, result.warnings[0], sbom=sbom_doc()) == []


# Review of 4be86c1, item 12: the report's line and the advice's placeholder ---------------


def test_the_report_says_when_no_package_fits_the_platform(tmp_path: Path) -> None:
    result = run(SBOM, platform="linux/amd64", output=tmp_path / "model.yaml")
    assert "\n- No package fits the platform.\n" in result.report_text
    assert "The packages fit the platform:" not in result.report_text


def test_the_advice_asks_for_the_variant_32_bit_arm_needs(tmp_path: Path) -> None:
    # Raspbian's armhf names 32-bit arm and pins no variant, which the platform then needs.
    sbom = built_for(sbom_doc(), "armhf", "deb/raspbian")
    result = run(dump(tmp_path, "s.json", sbom), platform="linux/amd64", output=tmp_path / "m.yaml")
    (warning,) = result.warnings
    assert warning.endswith(", for example --platform linux/arm/VARIANT")
    sbom_path = dump(folder(tmp_path, "v6"), "s.json", sbom)
    assert (
        run(sbom_path, platform="linux/arm/v6", output=sbom_path.with_name("m.yaml")).warnings == []
    )


# Review of 4be86c1, item 13: what the design log and the code said ------------------------


def test_a_tie_where_none_is_built_for_the_platforms_architecture_still_warns(
    tmp_path: Path,
) -> None:
    # 8 packages for 386 and 8 for arm64: a tie, which warns not as one, but because none
    # is built for amd64 itself.
    sbom = built_for(rebuilt(sbom_doc(), "x86", 8), "aarch64")
    result = run(dump(tmp_path, "s.json", sbom), platform="linux/amd64", output=tmp_path / "m.yaml")
    (warning,) = result.warnings
    assert warning.startswith("s.json: none of the SBOM's packages is built for amd64, though")
    assert advised(warning) == "linux/386"
    assert followed(tmp_path, warning, sbom=sbom) == []


# Review of 4be86c1, item 14: the advice leads to a model with no warning ----------------


def three_builds(sbom: dict) -> dict:
    """The review's case: 7 packages built for x86_64, 5 for Alpine's armhf (arm/v6), and
    4 left for aarch64. Under arm64, the 4 and the 5 for the arm it also runs are native."""
    rebuilt(sbom, "x86_64", 7)
    return rebuilt(sbom, "armhf", 5)


@pytest.mark.parametrize("platform", ["linux/amd64", "linux/arm/v6", "linux/386"])
def test_the_advice_names_the_platform_most_packages_are_native_to(
    tmp_path: Path, platform: str
) -> None:
    # In the round's first fixes linux/amd64 advised linux/arm/v6 and linux/arm/v6 advised
    # linux/amd64: the largest single build, which holds together only under arm64.
    sbom = three_builds(sbom_doc())
    result = run(dump(tmp_path, "s.json", sbom), platform=platform, output=tmp_path / "m.yaml")
    (warning,) = result.warnings
    assert advised(warning) == "linux/arm64/v8"  # arm64's own variant, as linux/arm64 is
    assert followed(tmp_path, warning, sbom=sbom) == []
    arm64 = dump(folder(tmp_path, "arm64"), "s.json", sbom)
    assert run(arm64, platform="linux/arm64", output=arm64.with_name("m.yaml")).warnings == []


@pytest.mark.parametrize("platform", ["linux/amd64", "linux/arm64"])
def test_packages_for_386_alone_advise_386_not_the_amd64_that_runs_them(
    tmp_path: Path, platform: str
) -> None:
    sbom = built_for(sbom_doc(), "x86")
    result = run(dump(tmp_path, "s.json", sbom), platform=platform, output=tmp_path / "m.yaml")
    (warning,) = result.warnings
    assert advised(warning) == "linux/386"
    assert followed(tmp_path, warning, sbom=sbom) == []


def test_a_tie_goes_to_the_architecture_more_packages_are_built_for(tmp_path: Path) -> None:
    # 8 packages for ppc64le, 6 for arm64 and 2 for the arm it also runs: 8 are native under
    # either, and more are built for ppc64le itself.
    sbom = rebuilt(rebuilt(sbom_doc(), "ppc64le", 8), "armv7", 2)
    result = run(dump(tmp_path, "s.json", sbom), platform="linux/amd64", output=tmp_path / "m.yaml")
    (warning,) = result.warnings
    assert advised(warning) == "linux/ppc64le"
    assert followed(tmp_path, warning, sbom=sbom) == []


# Mixes of builds, each imported under each platform: every warning's advice leads to a
# model with no warning, from wherever it is followed.
MIXES = {
    "the review's three builds": lambda sbom: three_builds(sbom),
    "amd64, arm64 and arm": lambda sbom: rebuilt(rebuilt(sbom, "x86_64", 6), "armv7", 5),
    "386 alone": lambda sbom: built_for(sbom, "x86"),
    "386 and arm64 even": lambda sbom: rebuilt(sbom, "x86", 8),
    "two variants of arm": lambda sbom: built_for(rebuilt(sbom, "armhf", 6), "armv7"),
    "ppc64le and arm64": lambda sbom: rebuilt(sbom, "ppc64le", 12),
}
STARTS = [
    "linux/amd64",
    "linux/arm64",
    "linux/arm/v6",
    "linux/arm/v7",
    "linux/386",
    "linux/ppc64le",
]


@pytest.mark.parametrize("mix", list(MIXES))
def test_the_advice_leads_to_no_warning_from_any_platform(tmp_path: Path, mix: str) -> None:
    sbom = MIXES[mix](sbom_doc())
    warned = 0
    for n, platform in enumerate(STARTS):
        path = dump(folder(tmp_path, f"start-{n}"), "s.json", sbom)
        for warning in run(path, platform=platform, output=path.with_name("m.yaml")).warnings:
            warned += 1
            assert followed(tmp_path, warning, sbom=sbom) == [], (platform, warning)
    assert warned  # each mix warns under some platform


# Review of 4be86c1, item 15: a rescan keeps every Assertion's id ------------------------


def rescanned(field: str, record: dict) -> None:
    """Change one field of a vulnerability record as a newer database would."""
    if field == "epss":
        record["epss"] = [dict(item, epss=0.5, percentile=0.9) for item in record.get("epss", [])]
    elif field == "risk":
        record["risk"] = 0.99
    elif field == "cvss":
        record["cvss"] = [dict(item, version="3.1") for item in record.get("cvss", [])]
    elif field == "description":
        record["description"] = "The words of a newer database."
    elif field == "fix state":
        record["fix"] = {"versions": [], "state": "not-fixed", "available": []}
    elif field == "urls":
        record["urls"] = ["https://example.org/a-newer-advisory"]


@pytest.mark.parametrize("field", ["epss", "risk", "cvss", "description", "fix state", "urls"])
def test_a_rescan_that_changes_only_scores_or_words_keeps_every_assertion_id(
    imported, tmp_path: Path, field: str
) -> None:
    # In the round's first fixes a match's id held a hash of the whole match, so a newer
    # database's EPSS gave the same finding a new id.
    _, fixture, _ = imported
    scan = scan_doc()
    for row in scan["matches"]:
        for record in [row["vulnerability"], *row.get("relatedVulnerabilities", [])]:
            rescanned(field, record)
        if field == "fix state":
            for detail in row["matchDetails"]:
                detail["fix"] = {"suggestedVersion": "9.9.9-r0"}
    out = tmp_path / "model.yaml"
    run(SBOM, scan=dump(tmp_path, "g.json", scan), output=out)
    assert set(by_id(load(out), "assertions")) == set(by_id(fixture, "assertions"))


@pytest.mark.parametrize("differ", ["type", "matcher"])
def test_matches_that_differ_in_type_or_matcher_keep_ids_of_their_own(
    tmp_path: Path, differ: str
) -> None:
    one = match("CVE-2026-0001")
    two = match("CVE-2026-0001")
    two["matchDetails"][0][differ] = "cpe-match" if differ == "type" else "stock-matcher"

    def ids(name: str, rows: list[dict]) -> dict[str, str]:
        doc, _ = import_matches(folder(tmp_path, name), rows)
        links = [a for a in doc["assertions"] if a["predicate"] == "propagates_to"]
        return {a["description"]: a["id"] for a in links}

    both = ids("both", [one, two])
    assert len(set(both.values())) == 2
    # Each has its own id, whatever the other: neither is told apart by order.
    assert ids("one", [one]).items() <= both.items()
    assert ids("two", [two]).items() <= both.items()


def test_matches_that_say_one_finding_get_two_ids_in_a_fixed_order(tmp_path: Path) -> None:
    # Twins: the same CVE, vulnerability, Component, type and matcher, and other scores.
    one = match("CVE-2026-0001")
    two = copy.deepcopy(one)
    two["vulnerability"]["risk"] = 0.99
    models = []
    for name, rows in (("forward", [one, two]), ("backward", [two, one])):
        doc, _ = import_matches(folder(tmp_path, name), rows)
        models.append(
            sorted(a["id"] for a in doc["assertions"] if a["predicate"] == "propagates_to")
        )
    assert len(set(models[0])) == 2  # one Assertion per match
    assert models[0] == models[1]  # told apart by an order of their own, not the scan's


def test_cwe_link_ids_are_the_round_s_own(imported) -> None:
    # A CWE link's id is its (CVE, CWE, source)'s, as since item 7 of this round.
    _, doc, _ = imported
    links = {a["id"] for a in doc["assertions"] if a["predicate"] == "instance_of"}
    assert "assertion:cve-2026-85091-cwe-787-from-disclosure-vulncheck-com-f142048c" in links


# Review of 4be86c1, item 16: what the variants say when the image purl has spoken -------


def test_an_image_purl_and_another_architecture_leave_the_variants_to_the_report(
    tmp_path: Path,
) -> None:
    # 6 Alpine armv7 packages and 10 aarch64 ones under linux/arm/v6, with an image purl for
    # arm: one warning, with no advice, and the report lists the packages for arm/v7.
    sbom = image_purl(rebuilt(sbom_doc(), "armv7", 6), "arm")
    result = run(
        dump(tmp_path, "s.json", sbom), platform="linux/arm/v6", output=tmp_path / "m.yaml"
    )
    (warning,) = result.warnings
    assert "--platform " not in warning.split(". Every package is kept", 1)[1]
    assert "6 Components built for arm/v7 (arch=armv7), not the platform's arm/v6: kept" in (
        result.report_text
    )


# Review of 4be86c1, item 18: twins keep their ids in a rescan ------------------------------


def twin_match(artifact_id: str, constraint: str, risk: float) -> dict:
    """One of two twins as Grype gives them for a package the SBOM records twice: one
    finding on two SBOM entries (`artifact.id`), here with other affected versions, so each
    Assertion's description says which match it is, and with a score of its own."""
    row = match("CVE-2026-0001")
    row["artifact"]["id"] = artifact_id
    row["matchDetails"][0]["found"] = {
        "versionConstraint": constraint,
        "vulnerabilityID": "CVE-2026-0001",
    }
    row["vulnerability"]["risk"] = risk
    return row


@pytest.mark.parametrize(
    ("first", "again"),
    [
        ((0.1, 0.2), (0.9, 0.05)),
        ((0.5, 0.6), (0.7, 0.8)),
        ((0.25, 0.75), (0.75, 0.25)),
        ((0.01, 0.02), (0.03, 0.04)),
    ],
)
def test_twins_keep_their_ids_when_their_scores_change(
    tmp_path: Path, first: tuple[float, float], again: tuple[float, float]
) -> None:
    # Ordered by the SBOM entry each is on, then by fingerprint, each twin keeps its own id
    # in a rescan whose scores differ, whatever order the scan lists them in.
    def ids(name: str, rows: list[dict]) -> dict[str, str]:
        doc, _ = import_matches(folder(tmp_path, name), rows)
        return {
            a["description"]: a["id"]
            for a in doc["assertions"]
            if a["predicate"] == "propagates_to"
        }

    scan = [
        twin_match("entry-b", "< 1.3.3", first[0]),
        twin_match("entry-a", "< 1.3.2-r1", first[1]),
    ]
    rescan = [
        twin_match("entry-a", "< 1.3.2-r1", again[1]),
        twin_match("entry-b", "< 1.3.3", again[0]),
    ]
    before, after = ids("scan", scan), ids("rescan", rescan)
    assert len(before) == 2 and len(set(before.values())) == 2  # one Assertion per match
    assert after == before
