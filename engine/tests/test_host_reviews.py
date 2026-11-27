"""Desktop-owned identities, project grants and proof before bearer disclosure."""

import hashlib
import hmac
import json
import os
import urllib.error
import urllib.request
from dataclasses import replace

import pytest
from review_support import MemoryWorkspace
from test_review_api import running
from test_review_service import request, review

from engine.api.host_reviews import PROOF_DOMAIN, HostReviewAPI, local_reviewer
from engine.review_workspace import ReviewError

TOKEN = "test-only-host-key-not-a-production-credential"
MODEL = "project:" + "a" * 32
IDENTITY = f"party:local:{'1' * 32}:{os.getuid()}"


class Projects(MemoryWorkspace):
    """Storage test double: #288 supplies the real project implementation."""

    def __init__(self):
        super().__init__()
        self.opened = False

    def models(self):
        return {"models": [{"model_id": MODEL}] if self.opened else []}

    def read(self, model_id, revision):
        if model_id != MODEL:
            raise ReviewError("not_found", "Project not found.")
        return replace(super().read("local:one", revision), model_id=MODEL)

    def history(self, model_id, revision):
        return [
            self.read(model_id, key) for key in self.versions if int(key[1:]) <= int(revision[1:])
        ]

    def save_version(self, model_id, expected_revision, document, *, description, summary):
        revision = super().commit(model_id, expected_revision, document)
        self.metadata = {"revision": revision, "description": description, "summary": summary}
        return revision


def configured():
    projects = Projects()
    api = HostReviewAPI(projects, TOKEN, IDENTITY, list_models=projects.models)
    return projects, api


def test_host_identity_is_tied_to_the_real_os_user():
    assert local_reviewer(IDENTITY).party_id == IDENTITY
    assert local_reviewer(IDENTITY).allow_party_creation
    with pytest.raises(ReviewError):
        local_reviewer(f"party:local:{'1' * 32}:{os.getuid() + 1}")
    with pytest.raises(ReviewError):
        local_reviewer("party:sponsor")


def test_model_grants_follow_only_the_hosts_opened_registry():
    projects, api = configured()
    assert not api.authenticate(f"Bearer {TOKEN}").model_ids
    projects.opened = True
    principal = api.authenticate(f"Bearer {TOKEN}")
    assert principal.model_ids == frozenset({MODEL})
    with pytest.raises(ReviewError):
        api.authenticate("Bearer client-claimed-session")
    payload = {**request(projects, True), "model_id": MODEL, "reviews": [review()]}
    saved = api.dispatch("/reviews/changes", principal, json.dumps(payload).encode())
    assert saved["revision"] == "r2"
    assert projects.versions["r2"]["reviews"][0]["reviewer"] == IDENTITY
    assert projects.metadata["summary"]["incomplete"] == 0
    assert projects.metadata["revision"] == "r2"


def test_proof_is_domain_separated_and_replay_does_not_match_a_new_challenge():
    _, api = configured()
    challenge = "a" * 64
    expected = hmac.new(
        TOKEN.encode(), PROOF_DOMAIN + challenge.encode(), hashlib.sha256
    ).hexdigest()
    # The native verifier uses the same synthetic vector, never a real token.
    assert expected == "a5098e6f9bfc3cd5b4fe96e5c06c812417af83a49fa8284384be1cda95fa7acc"
    assert api.host_proof(challenge) == {"challenge": challenge, "proof": expected}
    assert api.host_proof("b" * 64)["proof"] != expected
    assert TOKEN not in json.dumps(api.host_proof(challenge))
    with pytest.raises(ReviewError):
        api.host_proof("unbounded signing input")


def test_http_proof_needs_no_bearer_and_is_not_available_to_webview_origins():
    _, api = configured()
    with running(api) as url:
        with urllib.request.urlopen(url + "/host/health?challenge=" + "a" * 64) as response:
            assert json.load(response) == api.host_proof("a" * 64)
            assert response.headers["Cache-Control"] == "no-store"
        request_ = urllib.request.Request(
            url + "/host/health?challenge=" + "a" * 64, headers={"Origin": "tauri://localhost"}
        )
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request_)
        assert error.value.code == 403
    with running() as url:
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(url + "/host/health?challenge=" + "a" * 64)
        assert error.value.code == 503
