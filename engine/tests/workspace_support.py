"""Shared helpers for the threat model project tests (#288). Test-only."""

import errno
import hashlib
import shutil
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path

from engine import core, model_workspace

EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "model-workspace"
EXAMPLE = "workspace-example.yaml"
VECTORS = core.APPROVED_VECTOR_DIRECTORY  # the real examples, read before any test moves it
TOKEN = "test-host-token-" + "x" * 32  # a test secret, not a credential


def use_examples(monkeypatch, tmp_path, *names):
    """Make the engine list only these models (default: the synthetic example), as copies."""
    folder = tmp_path / "examples"
    folder.mkdir()
    for name in names or (EXAMPLE,):
        shutil.copyfile(EXAMPLES / name if name == EXAMPLE else VECTORS / name, folder / name)
    monkeypatch.setattr(core, "APPROVED_VECTOR_DIRECTORY", folder)
    return folder


def projects(tmp_path):
    """The folder the user keeps projects in (a project folder's parent must exist)."""
    folder = tmp_path / "projects"
    folder.mkdir(exist_ok=True)
    return folder


def snapshot(folder):
    """Every file and folder below `folder`: a file by its SHA-256, a folder as "folder"."""
    return {
        path.relative_to(folder).as_posix(): (
            hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "folder"
        )
        for path in sorted(Path(folder).rglob("*"))
    }


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Clock:
    """A clock that moves one minute per reading, for repeatable times."""

    def __init__(self, start=datetime(2026, 11, 27, 12, 0, tzinfo=UTC)):
        self.now = start

    def __call__(self):
        value, self.now = self.now, self.now + timedelta(minutes=1)
        return value


class Tokens:
    """Repeatable hex tokens in place of secrets.token_hex."""

    def __init__(self, seed="test"):
        self.seed, self.count = seed, 0

    def __call__(self, size):
        self.count += 1
        return hashlib.sha256(f"{self.seed}-{self.count}".encode()).hexdigest()[: 2 * size]


def rating_change(document, rating="high"):
    """A changed copy: the first attack path's rating set. `document` is not changed."""
    changed = deepcopy(document)
    changed["attack_paths"][0]["attack_feasibility"] = rating
    return changed


def review_change(document, rating="high", verdict="accepted"):
    """The kind of change the #289 review service saves: a person's Review of one exact
    Assertion, and a rating on the path it is about. `document` is not changed."""
    changed = deepcopy(document)
    assertion = next(a for a in changed["assertions"] if a["predicate"] == "realizes_threat")
    person = next(p["id"] for p in changed["parties"] if p.get("party_kind") == "person")
    if changed.get("reviews") is None:
        changed["reviews"] = []
    changed["reviews"].append(
        {
            "id": f"review:test-{len(changed['reviews']) + 1}",
            "reviews": assertion["id"],
            "reviewer": person,
            "review_status": verdict,
            "justification": "Test-only input from the test client, not a human review.",
        }
    )
    path = next(p for p in changed["attack_paths"] if p["id"] == assertion["subject"])
    path["attack_feasibility"] = rating
    return changed


def fail_at(monkeypatch, step, call, secret):
    """Make the `call`-th use of one file step raise an OSError whose text names `secret`.

    Returns a record of the calls; `record["real"]` is the step to put back.
    """
    real = getattr(model_workspace, step)
    record = {"count": 0, "real": real}

    def failing(*args, **kwargs):
        record["count"] += 1
        if record["count"] == call:
            raise OSError(errno.EIO, f"injected failure writing {secret}", str(secret))
        return real(*args, **kwargs)

    monkeypatch.setattr(model_workspace, step, failing)
    return record
