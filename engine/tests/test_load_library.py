"""Library loader (#139): real records of several types, the whole pinned library,
and the error a broken record gives.

`fixtures/library/` holds byte-for-byte copies of real records (see its README).
The whole-library test needs the `library` submodule checked out. CI checks out
without submodules, so that test skips there and runs on a full local checkout.
"""

from __future__ import annotations

import dataclasses
import json
import os
import shutil
from pathlib import Path

import pytest

from engine.load.library import Library, LibraryError, load_library

TESTS = Path(__file__).resolve().parent
FIXTURES = TESTS / "fixtures" / "library"
PINNED = TESTS.parents[1] / "library"  # the submodule at the repo root


@pytest.fixture(scope="module")
def fixtures() -> Library:
    return load_library(FIXTURES)


def write(root: Path, rel: str, text: str | bytes) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_text(text, encoding="utf-8")


def record_text(record_id: str, body: str = "ietf", extra: str = "", drop: str = "") -> str:
    """A minimal valid record. `extra` adds lines; `drop` removes the line for one key."""
    lines = [
        'schema: "library-record/v1"',
        f"id: {record_id}",
        f"body: {body}",
        "type: rfc",
        f'title: "Title of {record_id}"',
        "content:",
        "  url: https://example.org/doc",
        '  retrieved: ""',
        "  local: false",
        "tags: []",
        "status: stub",
    ]
    lines = [line for line in lines if not (drop and line.startswith(f"{drop}:"))]
    return "\n".join(lines) + "\n" + extra


# --- real records of several types ----------------------------------------------


def test_every_fixture_loads_in_id_order(fixtures):
    ids = [r.id for r in fixtures]
    assert ids == sorted(ids)
    assert len(fixtures) == 12  # 13 files: the versions/ copy is not a record of its own
    assert fixtures.problems == ()
    assert {r.type for r in fixtures} == {"rfc", "draft", "paper", "web", "repo", "dataset", "spec"}
    assert {r.status for r in fixtures} == {"stub", "fetched", "summarized", "distilled"}


def test_distilled_rfc(fixtures):
    r = fixtures.get("rfc-8785")
    assert (r.type, r.status, r.profile) == ("rfc", "distilled", "full")
    assert r.maturity == "informational"
    assert r.path == "records/ietf/rfc-8785/record.yaml"
    assert r.identifier("rfc") == "8785"  # text, as written
    assert r.identifier("doi") == "10.17487/RFC8785"
    assert r.identifier("isbn") is None
    assert r.related("see_also") == ("rfc-8259", "rfc-8949", "rfc-9804")
    assert r.related("supersedes") == ()  # empty relation lists are left out
    kinds = [a.kind for a in r.artifacts]
    assert kinds == [
        "normative",
        "requirements",
        "schema",
        "messages",
        "protocol",
        "examples",
        "design-notes",
    ]
    assert not any(a.reviewed for a in r.artifacts)  # no person has checked them yet
    protocol = r.artifacts[kinds.index("protocol")]
    assert protocol.generated_from == "distilled/normative.md"
    assert len(r.raw["distillation"]["passes"]) == 3  # unmodelled fields stay in raw


def test_paper_stub_with_pages_and_extra_keys(fixtures):
    r = fixtures.get("benedetti-2024-sbom-python")
    assert (r.type, r.status, r.owner) == ("paper", "stub", "Clovier")
    assert r.authors[0] == "Giacomo Benedetti" and len(r.authors) == 4
    assert r.identifier("arxiv") == "2409.06390v1"
    c = r.content
    assert (c.pages, c.local, c.media_type) == (23, False, "application/pdf")
    assert c.retrieved == "2026-10-18"
    assert r.raw["license"] == "CC-BY-SA-4.0"
    assert r.raw["venue"].startswith("Applied Cryptography and Network Security")


def test_unquoted_arxiv_id_stays_text(fixtures):
    r = fixtures.get("sbomproof-2025")
    assert r.identifier("arxiv") == "2510.05798"
    assert r.version == "v1"


def test_spec_with_citations_and_relations(fixtures):
    r = fixtures.get("eo-14306")
    assert [c.record for c in r.cites[:2]] == ["eo-14144", "sp-800-218"]
    labelled = r.cites[2:]
    assert [c.ref for c in labelled] == ["§3", "§2(b)", "§2(d)"]
    assert all(c.record is None and c.title for c in labelled)
    assert r.relations == (
        ("updates", ("eo-14144",)),
        ("see_also", ("eo-14028", "omb-m-26-05", "sp-800-218")),
    )
    assert r.identifier("eo") == "14306"
    assert r.usefulness.verdict == "useful" and r.usefulness.assessed == "2026-10-02"
    assert dict(r.applicability) == {
        "security": "core",
        "cryptography": "adjacent",
        "this_project": "adjacent",
    }


def test_implementations_both_forms(fixtures):
    named = fixtures.get("threattree-help").implementations
    assert len(named) == 1
    assert (named[0].name, named[0].commercial, named[0].url) == (
        "ThreatTree",
        True,
        "https://threattree.com/",
    )
    assert named[0].note.startswith("Product homepage checked")
    one_line = fixtures.get("rfc-9393").implementations
    assert len(one_line) == 2
    assert all(not i.commercial and i.url is None for i in one_line)
    assert one_line[0].name.startswith("python-uswid 0.6.0")  # kept whole


def test_repo_with_blank_fields(fixtures):
    r = fixtures.get("gram")
    assert r.type == "repo"
    assert r.date is None  # blank in the file
    assert (r.content.sha256, r.content.retrieved) == (None, "2026-10-13")
    assert r.identifier("git") == "https://github.com/klarna-incubator/gram"
    assert r.raw["commit"] == "e6a6239383269f7da8c1e560ac8c7cb2ede42553"


def test_dataset_duplicate_and_part_of(fixtures):
    assert fixtures.get("cwe").type == "dataset"
    dup = fixtures.get("ecma-424")
    assert (dup.duplicate_of, dup.status) == ("cyclonedx-1-7", "stub")
    assert fixtures.get("rfc-8152").related("part_of") == ("ietf-cose-wg",)


def test_superseded_versions_are_listed_not_loaded(fixtures):
    r = fixtures.get("draft-mih-scitt-agent-action-capsule")
    assert r.versions == ("-02",)
    assert fixtures.get("draft-mih-scitt-agent-action-capsule-02") is None


def test_summary_is_found(tmp_path):
    write(tmp_path, "records/ietf/with-summary/record.yaml", record_text("with-summary"))
    write(tmp_path, "records/ietf/with-summary/summary.md", "---\ntype: summary\n---\n")
    write(tmp_path, "records/ietf/no-summary/record.yaml", record_text("no-summary"))
    lib = load_library(tmp_path)
    assert lib.get("with-summary").summary == "records/ietf/with-summary/summary.md"
    assert lib.get("no-summary").summary is None


def test_values_kept_as_written(tmp_path):
    extra = (
        "version: 1.10\n"
        "date: 2026-10-29\n"
        "identifiers:\n"
        "  arxiv: 2409.06390\n"
        "  rfc: 0042\n"
        "  nist: yes\n"
    )
    text = record_text("as-written", extra=extra).replace(
        "  local: false\n", "  local: false\n  pages: 23\n"
    )
    write(tmp_path, "records/ietf/as-written/record.yaml", text)
    r = load_library(tmp_path).get("as-written")
    assert r.version == "1.10"  # a float would say 1.1
    assert r.date == "2026-10-29"  # not a date object
    assert r.identifier("arxiv") == "2409.06390"  # a float would drop the last 0
    assert r.identifier("rfc") == "0042"
    assert r.identifier("nist") == "yes"  # not True
    assert r.content.pages == 23 and r.content.local is False


# --- deterministic and read-only -------------------------------------------------


def test_same_input_same_output(fixtures):
    again = load_library(FIXTURES)
    assert again.records == fixtures.records
    assert again.digest == fixtures.digest
    assert json.dumps(again.to_dict()) == json.dumps(fixtures.to_dict())


def test_digest_tracks_the_bytes(tmp_path):
    shutil.copytree(FIXTURES, tmp_path / "lib")
    before = load_library(tmp_path / "lib")
    path = tmp_path / "lib" / "records" / "other" / "cwe" / "record.yaml"
    path.write_text(path.read_text(encoding="utf-8") + "# a comment\n", encoding="utf-8")
    after = load_library(tmp_path / "lib")
    assert after.digest != before.digest  # different bytes
    assert after.records == before.records  # same values


def test_records_and_raw_are_read_only(fixtures):
    r = fixtures.get("rfc-8785")
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.title = "changed"
    with pytest.raises(TypeError):
        r.raw["title"] = "changed"
    assert isinstance(r.raw["tags"], tuple)


def test_loads_without_writing(tmp_path):
    lib_root = tmp_path / "lib"
    shutil.copytree(FIXTURES, lib_root)
    paths = sorted(lib_root.rglob("*"))
    before = [(p, p.stat().st_mtime_ns) for p in paths]
    for p in reversed(paths):  # files and folders read-only, deepest first
        p.chmod(0o555 if p.is_dir() else 0o444)
    lib_root.chmod(0o555)
    try:
        assert len(load_library(lib_root)) == 12
        assert sorted(lib_root.rglob("*")) == paths  # nothing new, such as a cache
        assert [(p, p.stat().st_mtime_ns) for p in paths] == before
    finally:
        for p in [lib_root, *paths]:
            p.chmod(0o755 if p.is_dir() else 0o644)


# --- a broken record fails with an error that names its file -----------------------

BROKEN = {
    "records/ietf/no-title/record.yaml": (
        record_text("no-title", drop="title"),
        "missing required field 'title'",
    ),
    "records/ietf/bad-yaml/record.yaml": ("title: ok\nid: [unclosed\n", "not valid YAML at line"),
    "records/ietf/latin-1/record.yaml": (b"title: caf\xe9\n", "not UTF-8 text"),
    "records/ietf/a-list/record.yaml": ("- just\n- a list\n", "expected a mapping at the top"),
    "records/ietf/wrong-folder/record.yaml": (
        record_text("other-id"),
        "id 'other-id' does not match its folder 'wrong-folder'",
    ),
    "records/nist/wrong-shelf/record.yaml": (
        record_text("wrong-shelf", body="ietf"),
        "body 'ietf' does not match its folder 'nist'",
    ),
    "records/ietf/Not_Kebab/record.yaml": (record_text("Not_Kebab"), "is not kebab-case"),
    "records/ietf/bad-authors/record.yaml": (
        record_text("bad-authors", extra="authors:\n  name: someone\n"),
        "'authors' should be a list, found mapping",
    ),
    "records/ietf/bad-local/record.yaml": (
        record_text("bad-local").replace("local: false", "local: maybe"),
        "'content.local' should be true or false",
    ),
    "records/ietf/bad-pages/record.yaml": (
        record_text("bad-pages").replace("local: false", "local: false\n  pages: twelve"),
        "'content.pages' should be a whole number",
    ),
    "records/ietf/unicode-pages/record.yaml": (  # "²".isdigit() is True, int("²") fails
        record_text("unicode-pages").replace("local: false", "local: false\n  pages: ²"),
        "'content.pages' should be a whole number, found '²'",
    ),
    "records/ietf/blank-title/record.yaml": (
        record_text("blank-title").replace('title: "Title of blank-title"', 'title: ""'),
        "'title' is empty",
    ),
}


@pytest.mark.parametrize("rel", sorted(BROKEN))
def test_broken_record_error_names_the_file(tmp_path, rel):
    text, reason = BROKEN[rel]
    write(tmp_path, "records/ietf/good/record.yaml", record_text("good"))
    write(tmp_path, rel, text)
    with pytest.raises(LibraryError) as caught:
        load_library(tmp_path)
    (problem,) = caught.value.problems  # one problem, for the broken file only
    assert problem.startswith(f"{rel}: ")
    assert reason in problem
    assert "\n" not in problem  # one line, even when the YAML parser's message is not
    assert rel in str(caught.value)


def test_every_broken_file_is_named_and_the_rest_load(tmp_path):
    write(tmp_path, "records/ietf/good/record.yaml", record_text("good"))
    for rel, (text, _) in BROKEN.items():
        write(tmp_path, rel, text)
    with pytest.raises(LibraryError) as caught:
        load_library(tmp_path)
    named = [line.split(": ", 1)[0] for line in caught.value.problems]
    assert named == sorted(BROKEN)  # one line per broken file, in path order
    assert f"{len(BROKEN)} records failed to load" in str(caught.value)

    partial = load_library(tmp_path, strict=False)
    assert [r.id for r in partial] == ["good"]
    assert partial.problems == caught.value.problems


@pytest.mark.parametrize("strict", [True, False])
def test_unicode_page_count_fails_only_its_record(tmp_path, strict):
    shutil.copytree(FIXTURES, tmp_path / "lib")
    rel = "records/academic/benedetti-2024-sbom-python/record.yaml"
    path = tmp_path / "lib" / rel
    path.write_text(
        path.read_text(encoding="utf-8").replace("pages: 23", "pages: ²"), encoding="utf-8"
    )
    expected = f"{rel}: 'content.pages' should be a whole number, found '²'"
    if strict:
        with pytest.raises(LibraryError) as caught:
            load_library(tmp_path / "lib")
        assert caught.value.problems == (expected,)
    else:
        lib = load_library(tmp_path / "lib", strict=False)
        assert len(lib) == 11 and lib.problems == (expected,)
        assert lib.get("benedetti-2024-sbom-python") is None


@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="root reads any folder")
@pytest.mark.parametrize("strict", [True, False])
def test_unreadable_versions_folder_fails_only_its_record(tmp_path, strict):
    shutil.copytree(FIXTURES, tmp_path / "lib")
    record = "records/ietf/draft-mih-scitt-agent-action-capsule"
    versions = tmp_path / "lib" / record / "versions"
    versions.chmod(0)
    try:
        expected = f"{record}/record.yaml: cannot read versions/ (Permission denied)"
        if strict:
            with pytest.raises(LibraryError) as caught:
                load_library(tmp_path / "lib")
            assert caught.value.problems == (expected,)
        else:
            lib = load_library(tmp_path / "lib", strict=False)
            assert len(lib) == 11 and lib.problems == (expected,)
    finally:
        versions.chmod(0o755)


def test_duplicate_id_names_both_files(tmp_path):
    write(tmp_path, "records/ietf/same-id/record.yaml", record_text("same-id"))
    write(tmp_path, "records/nist/same-id/record.yaml", record_text("same-id", body="nist"))
    with pytest.raises(LibraryError) as caught:
        load_library(tmp_path)
    assert caught.value.problems == (
        "records/nist/same-id/record.yaml: id 'same-id' is also used by "
        "records/ietf/same-id/record.yaml",
    )


def test_not_a_library(tmp_path):
    with pytest.raises(LibraryError, match="no records/ folder"):
        load_library(tmp_path)


# --- the whole pinned library ------------------------------------------------------


@pytest.mark.skipif(
    not (PINNED / "records").is_dir(),
    reason="library submodule not checked out (git submodule update --init library)",
)
def test_every_record_in_the_pinned_library_loads():
    lib = load_library(PINNED)
    assert lib.problems == ()
    assert len(lib) > 0
    for r in lib:
        assert r.path == f"records/{r.body}/{r.id}/record.yaml"
    # one record per record.yaml at the top of a record folder
    assert len(lib) == len(list(PINNED.glob("records/*/*/record.yaml")))
    assert os.fspath(PINNED.resolve()) == lib.root
