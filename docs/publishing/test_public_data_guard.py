import json
from pathlib import Path

import pytest
import render_app
import render_requirements_catalog as catalog

MALICIOUS_PUBLIC_VALUES = (
    (str(render_app.ROOT / "spec/vectors/model.yaml"), "local path marker"),
    ("/Users/alice/project/model.yaml", "local path marker"),
    ("/home/alice/project/model.yaml", "local path marker"),
    ("/private/var/tmp/model.yaml", "local path marker"),
    ("/var/folders/aa/private/model.yaml", "local path marker"),
    (r"C:\Users\alice\project\model.yaml", "local path marker"),
    ("-----BEGIN PRIVATE KEY-----", "credential marker"),
    ("-----BEGIN RSA PRIVATE KEY-----", "credential marker"),
    ("-----BEGIN OPENSSH PRIVATE KEY-----", "credential marker"),
    ("-----BEGIN EC PRIVATE KEY-----", "credential marker"),
    ("-----BEGIN DSA PRIVATE KEY-----", "credential marker"),
    ("ghp_1234567890abcdefghij", "credential marker"),
    ("github_pat_1234567890abcdefghij", "credential marker"),
    ("AKIA1234567890ABCDEF", "credential marker"),
    ("sk-live-1234567890abcdef", "credential marker"),
    ("sk-proj-1234567890abcdef", "credential marker"),
    ("rk-live-1234567890abcdef", "credential marker"),
    ("rk-proj-1234567890abcdef", "credential marker"),
)


@pytest.mark.parametrize("value, marker", MALICIOUS_PUBLIC_VALUES)
def test_both_public_renderers_reject_the_same_prohibited_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    value: str,
    marker: str,
) -> None:
    with pytest.raises(RuntimeError, match=marker):
        render_app._write_json(tmp_path / "public.json", {"value": value})

    monkeypatch.setattr(catalog, "build_catalog", lambda: {"value": value})
    with pytest.raises(RuntimeError, match=marker):
        catalog.render()


def test_both_public_renderers_accept_ordinary_public_content(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {"value": "Public requirement evidence for Clause 4.2."}
    render_app._write_json(tmp_path / "public.json", payload)
    assert json.loads((tmp_path / "public.json").read_text()) == payload

    monkeypatch.setattr(catalog, "build_catalog", lambda: payload)
    assert json.loads(catalog.render()) == payload
