import copy
import shutil
import subprocess

import pytest
import yaml
from input_digest import ROOT, TEMPLATE, blob_id, digest, inputs, load, tree_id

RECORD = ROOT / "models" / "tcu" / "governance.yaml"
V1 = "threat-model:tcu-tara-v1"


@pytest.fixture
def record():
    return load(RECORD)


@pytest.fixture
def site(tmp_path, record):
    """A copy of the inputs in a scratch root, so a test can change one of them."""
    for rel in (record["governs"], *TEMPLATE, "models/tcu/governance.yaml"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, tmp_path / rel)
    return tmp_path


def v1(doc):
    return next(v for v in doc["threat_models"] if v["id"] == V1)


# --- it is git's tree hash (DL-0027 decision 4) --------------------------------------------------


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
def test_the_digest_is_the_tree_git_writes_for_the_same_files(tmp_path, record):
    files = inputs(RECORD, record, V1)
    # names that sort differently as files and as directories, as git sorts them
    files |= {"a-b/x.txt": b"1", "a/y.txt": b"2", "a.txt": b"3"}
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    for path, data in files.items():
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / path).write_bytes(data)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    git = subprocess.run(
        ["git", "-C", str(repo), "write-tree"], check=True, capture_output=True, text=True
    )
    assert tree_id(files) == git.stdout.strip()


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
def test_the_vector_is_hashed_as_committed(record):
    git = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", record["governs"]],
        check=True,
        capture_output=True,
        text=True,
    )
    assert blob_id((ROOT / record["governs"]).read_bytes()) == git.stdout.strip()


def test_the_inputs_are_the_vector_the_version_and_the_template(record):
    assert sorted(inputs(RECORD, record, V1)) == sorted(
        [record["governs"], *TEMPLATE, "models/tcu/governance/threat-model-tcu-tara-v1.json"]
    )


def test_the_digest_is_written_git_tree_and_a_sha1(record):
    value = digest(RECORD, record, V1)
    assert value.startswith("git-tree:") and len(value) == len("git-tree:") + 40


# --- changing an input changes the digest (#183) -------------------------------------------------


@pytest.mark.parametrize("rel", ["spec/vectors/mvp-02-automotive-ecu.yaml", *TEMPLATE])
def test_editing_an_input_file_changes_the_digest(site, record, rel):
    path = site / "models/tcu/governance.yaml"
    before = digest(path, record, V1, site)
    with (site / rel).open("ab") as f:
        f.write(b"\n# edited\n")
    assert digest(path, record, V1, site) != before


def test_changing_what_the_version_holds_changes_the_digest(record):
    edited = copy.deepcopy(record)
    v1(edited)["members"].remove("attack-path:infotainment-pivot")
    assert digest(RECORD, edited, V1) != digest(RECORD, record, V1)


# --- approving does not change it ----------------------------------------------------------------


def test_approving_reviewing_and_commenting_leave_the_digest_alone(record):
    edited = copy.deepcopy(record)
    v1(edited).update(
        governance_status="approved",
        approval_status="approved",
        approved_by=["review:x"],
        approval_digest="git-tree:" + "0" * 40,
        updated="2026-12-01T00:00:00Z",
    )
    edited["reviews"].append({"id": "review:x", "reviews": V1, "review_outcome": "approved"})
    edited["review_comments"][1]["comment_status"] = "resolved"
    assert digest(RECORD, edited, V1) == digest(RECORD, record, V1)


def test_a_new_version_leaves_version_1s_digest_alone(record):
    edited = copy.deepcopy(record)
    v2 = copy.deepcopy(v1(record)) | {"id": "threat-model:tcu-tara-v2", "revision": "2"}
    edited["threat_models"].append(v2)
    assert digest(RECORD, edited, V1) == digest(RECORD, record, V1)
    assert digest(RECORD, edited, v2["id"]) != digest(RECORD, edited, V1)


def test_the_records_layout_does_not_matter(record):
    reordered = yaml.safe_load(yaml.safe_dump(record, sort_keys=True, width=40))
    assert digest(RECORD, reordered, V1) == digest(RECORD, record, V1)


def test_an_unknown_version_is_refused(record):
    with pytest.raises(KeyError, match="threat-model:nope"):
        digest(RECORD, record, "threat-model:nope")


@pytest.mark.parametrize("bad", ["", "/abs", "a//b", "a/../b", "./a"])
def test_a_path_that_is_not_plain_is_refused(bad):
    with pytest.raises(ValueError):
        tree_id({bad: b"x"})
