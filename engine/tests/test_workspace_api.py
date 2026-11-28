"""HTTP routes for threat model projects (#288): off unless the host turns them on, the
host's token on every call, paths only from the host itself, structured errors that
name no path, and the shared mock contract for #290.

To rewrite examples/model-workspace/contract.json after a deliberate change, run this
file with TMODEL_WRITE_CONTRACT=1 and review the diff.
"""

import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlencode

import pytest
from workspace_support import (
    EXAMPLE,
    EXAMPLES,
    TOKEN,
    Clock,
    Tokens,
    fail_at,
    projects,
    review_change,
    snapshot,
    use_examples,
)

from engine import model_workspace
from engine.api import server
from engine.api import workspace as workspace_api
from engine.api.server import make_server
from engine.api.workspace import WorkspaceRoutes, check_host_token, install_workspace_routes
from engine.cli import main
from engine.model_workspace import ProjectWorkspace
from engine.review_workspace import ReviewError
from engine.risk import MATRIX_ID, assess_document

CONTRACT = EXAMPLES / "contract.json"
APP_ROUTES = [
    ("GET", "/workspace/models"),
    ("GET", "/workspace/model"),
    ("GET", "/workspace/versions"),
]
HOST_ROUTES = [
    ("POST", "/workspace/host/create-project"),
    ("POST", "/workspace/host/open-project"),
    ("POST", "/workspace/host/open-file"),
]


@contextmanager
def running(workspace=None, token=TOKEN):
    httpd = make_server("127.0.0.1", 0)
    install_workspace_routes(httpd, workspace, token if workspace is not None else None)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)


def call(url, path, method="GET", body=None, token=TOKEN, headers=None, raw=None):
    sent = {"Authorization": f"Bearer {token}"} if token else {}
    data = raw
    if method == "POST":
        sent["Content-Type"] = "application/json"
        if data is None:
            data = json.dumps({} if body is None else body).encode()
    sent.update(headers or {})
    request = urllib.request.Request(url + path, data=data, headers=sent, method=method)
    try:
        response = urllib.request.urlopen(request, timeout=10)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        payload = response.read()
        parsed = json.loads(payload) if payload[:1] == b"{" else payload
        return response.status, dict(response.headers), parsed


@pytest.fixture
def engine(monkeypatch, tmp_path):
    """A server with project folders on, the synthetic example listed, and a project."""
    use_examples(monkeypatch, tmp_path)
    workspace = ProjectWorkspace(schema_check=False, clock=Clock(), token=Tokens())
    folder = projects(tmp_path) / "Example Threat Model"
    model_id = workspace.create_project(folder, source_file=EXAMPLE)["model_id"]
    with running(workspace) as url:
        yield url, workspace, model_id, folder


def test_project_routes_are_off_unless_the_host_turns_them_on(tmp_path):
    plain = make_server("127.0.0.1", 0)  # make_server alone adds no workspace routes
    assert not issubclass(plain.RequestHandlerClass, WorkspaceRoutes)
    thread = threading.Thread(target=plain.serve_forever, daemon=True)
    thread.start()
    try:
        with running() as url:
            for method, path in APP_ROUTES + HOST_ROUTES:
                status, _, body = call(url, path, method, {"path": str(tmp_path / "New")})
                assert status == 503, path
                assert body["error"]["code"] == "workspace_failure"
            # Every other request gets the engine's own answer, as without these routes.
            unchanged = f"http://127.0.0.1:{plain.server_address[1]}"
            for method, path in (("GET", "/health"), ("POST", "/reviews/changes")):
                assert call(url, path, method)[0] == call(unchanged, path, method)[0]
    finally:
        plain.shutdown()
        plain.server_close()
        thread.join(timeout=5)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "authorization", [None, "Bearer wrong-" + "x" * 40, f"Basic {TOKEN}", f"Bearer {TOKEN} "]
)
def test_every_route_needs_the_host_token(engine, tmp_path, authorization):
    url, workspace, model_id, folder = engine
    before = snapshot(tmp_path)
    for method, path in APP_ROUTES + HOST_ROUTES:
        headers = {"Authorization": authorization} if authorization else {}
        status, _, body = call(
            url, f"{path}?model_id={model_id}", method, {"path": str(folder)}, None, headers
        )
        assert (status, body["error"]["code"]) == (403, "permission_denied"), path
    assert snapshot(tmp_path) == before


def test_only_the_host_passes_paths(engine, tmp_path):
    url, workspace, model_id, folder = engine
    for method, path in HOST_ROUTES:
        status, _, body = call(
            url, path, method, {"path": str(folder)}, headers={"Origin": "tauri://localhost"}
        )
        assert (status, body["error"]["code"]) == (403, "permission_denied")
        preflight = call(url, path, "OPTIONS", token=None, headers={"Origin": "tauri://localhost"})
        assert preflight[0] == 403
    status, headers, _ = call(
        url, "/workspace/versions", "OPTIONS", token=None, headers={"Origin": "tauri://localhost"}
    )
    assert status == 204
    assert headers["Access-Control-Allow-Origin"] == "tauri://localhost"
    assert headers["Access-Control-Allow-Methods"] == "GET"
    assert headers["Access-Control-Allow-Headers"] == "Authorization"
    status, headers, body = call(
        url, f"/workspace/model?model_id={model_id}", headers={"Origin": "tauri://localhost"}
    )
    assert (status, body["revision"]) == (200, "v001")  # the webview reads with the token
    assert headers["Access-Control-Allow-Origin"] == "tauri://localhost"
    assert headers["Cache-Control"] == "no-store"


@pytest.mark.parametrize("headers", [{"Origin": "https://evil.example"}, {"Host": "evil.example"}])
def test_a_foreign_host_or_origin_is_refused(engine, tmp_path, headers):
    url, workspace, model_id, folder = engine
    before = snapshot(tmp_path)
    for method, path in APP_ROUTES + HOST_ROUTES:
        status, _, body = call(url, path, method, {"path": str(tmp_path / "New")}, headers=headers)
        assert (status, body["error"]["code"]) == (403, "permission_denied")
    assert call(url, "/workspace/models", "OPTIONS", token=None, headers=headers)[0] == 403
    assert snapshot(tmp_path) == before


def test_the_project_flow_over_http(engine, tmp_path):
    url, workspace, model_id, folder = engine
    document = workspace.read(model_id, "v001").document
    workspace.save_version(model_id, "v001", review_change(document), description="Reviewed")
    status, _, listed = call(url, "/workspace/models")
    assert (status, listed["count"], listed["models"][0]["current_revision"]) == (200, 1, "v002")
    status, _, current = call(url, f"/workspace/model?model_id={model_id}")
    assert (status, current["revision"], current["version"]["description"]) == (
        200,
        "v002",
        "Reviewed",
    )
    status, _, older = call(url, f"/workspace/model?model_id={model_id}&revision=v001")
    assert (status, older["revision"], older["document"]) == (200, "v001", document)
    status, _, versions = call(url, f"/workspace/versions?model_id={model_id}")
    assert [v["version"] for v in versions["versions"]] == ["v001", "v002"]
    assert all("file" not in v for v in versions["versions"])
    loose = tmp_path / "imported.yaml"
    shutil.copyfile(EXAMPLES / EXAMPLE, loose)
    status, _, opened = call(url, "/workspace/host/open-file", "POST", {"path": str(loose)})
    assert (status, opened["kind"], opened["editable"]) == (200, "file", False)
    status, _, started = call(
        url,
        "/workspace/host/create-project",
        "POST",
        {"path": str(projects(tmp_path) / "Imported"), "model_id": opened["model_id"]},
    )
    assert (status, started["revision"], started["source"]["origin"]) == (201, "v001", "file")
    restarted = ProjectWorkspace(schema_check=False)
    with running(restarted) as again:
        status, _, reopened = call(
            again, "/workspace/host/open-project", "POST", {"path": str(folder)}
        )
        assert (status, reopened["model_id"], reopened["revision"]) == (200, model_id, "v002")
    text = json.dumps([listed, current, older, versions, opened, started, reopened])
    assert str(tmp_path) not in text and os.path.realpath(tmp_path) not in text


OPEN_FILE = "/workspace/host/open-file"
OPEN_PROJECT = "/workspace/host/open-project"
NO_PROJECT = "project:" + "0" * 32
TEXT = {"Content-Type": "text/plain"}


@pytest.mark.parametrize(
    ("method", "path", "body", "headers", "status", "field"),
    [
        ("GET", "/workspace/models?extra=1", None, {}, 422, "extra"),
        ("GET", "/workspace/model", None, {}, 422, "model_id"),
        ("GET", "/workspace/model?model_id=a&model_id=b", None, {}, 422, "model_id"),
        ("GET", f"/workspace/versions?model_id={NO_PROJECT}", None, {}, 404, None),
        ("GET", "/workspace/model?model_id={model}&revision=v404", None, {}, 404, None),
        ("GET", "/workspace/unknown", None, {}, 404, None),
        ("POST", "/workspace/models", {}, {}, 404, None),
        ("POST", OPEN_PROJECT, {}, {}, 422, "path"),
        ("POST", OPEN_PROJECT, {"path": "/x", "extra": 1}, {}, 422, "extra"),
        ("POST", OPEN_PROJECT, {"path": "relative"}, {}, 422, "path"),
        ("POST", OPEN_FILE, b"[]", {}, 422, "request"),
        ("POST", OPEN_FILE, b'{"path":"/a.yaml","path":"/b.yaml"}', {}, 422, "request"),
        ("POST", OPEN_FILE, b'{"path":NaN}', {}, 422, "request"),
        ("POST", OPEN_FILE, b"\xff", {}, 422, "request"),
        ("POST", OPEN_FILE, {"path": "/x.yaml"}, TEXT, 422, "request"),
        ("POST", OPEN_FILE, b'{"path":"/' + b"x" * 17000 + b'"}', {}, 422, "request"),
        (
            "POST",
            "/workspace/host/create-project",
            {"path": "/no-such-parent-folder/x", "source_file": "sdl-01-tmodel-desktop.yaml"},
            {},
            404,
            None,
        ),
    ],
)
def test_bad_requests_get_structured_errors(
    engine, tmp_path, method, path, body, headers, status, field
):
    url, workspace, model_id, folder = engine
    before = snapshot(tmp_path)
    raw = body if isinstance(body, bytes) else None
    answer, _, payload = call(
        url, path.format(model=model_id), method, None if raw else body, raw=raw, headers=headers
    )
    code = {404: "not_found", 422: "validation_error"}[status]
    assert (answer, payload["error"]["code"]) == (status, code)
    assert payload["error"].get("fields", [{}])[0].get("field") == field
    assert snapshot(tmp_path) == before


def test_a_body_that_stops_arriving_is_refused(engine, monkeypatch):
    url, workspace, model_id, folder = engine
    monkeypatch.setattr(workspace_api, "BODY_TIMEOUT_S", 0.2)
    host, port = url.removeprefix("http://").split(":")
    head = (
        "POST /workspace/host/open-file HTTP/1.1\r\nHost: 127.0.0.1\r\n"
        f"Authorization: Bearer {TOKEN}\r\nContent-Type: application/json\r\n"
        "Content-Length: 100\r\n\r\n"
    )
    with socket.create_connection((host, int(port)), timeout=10) as connection:
        connection.sendall(head.encode() + b'{"path":')  # and then nothing more
        answer = b""
        while chunk := connection.recv(65536):
            answer += chunk
    assert answer.split(b" ", 2)[1] == b"422"  # its reason phrase differs between Pythons
    assert json.loads(answer.split(b"\r\n\r\n", 1)[1])["error"]["fields"][0] == {
        "field": "request",
        "message": "Incomplete request body.",
    }


def test_a_body_that_trickles_in_gets_one_deadline_for_all_of_it(engine, monkeypatch):
    url, workspace, model_id, folder = engine
    monkeypatch.setattr(workspace_api, "BODY_TIMEOUT_S", 0.5)
    host, port = url.removeprefix("http://").split(":")
    head = (
        "POST /workspace/host/open-file HTTP/1.1\r\nHost: 127.0.0.1\r\n"
        f"Authorization: Bearer {TOKEN}\r\nContent-Type: application/json\r\n"
        "Content-Length: 40\r\n\r\n"
    )
    with socket.create_connection((host, int(port)), timeout=10) as connection:
        connection.sendall(head.encode())
        start = time.monotonic()

        def trickle():  # one byte every 0.15 s: each read gets data, the whole takes 6 s
            for _ in range(40):
                try:
                    connection.sendall(b" ")
                except OSError:
                    return
                time.sleep(0.15)

        threading.Thread(target=trickle, daemon=True).start()
        answer = b""
        while chunk := connection.recv(65536):
            answer += chunk
        elapsed = time.monotonic() - start
    assert answer.split(b" ", 2)[1] == b"422"
    assert b"Incomplete request body." in answer
    assert elapsed < 4.0  # the 0.5 s deadline, well before the 6 s the body would take


def test_failures_answer_without_paths(engine, monkeypatch, tmp_path):
    url, workspace, model_id, folder = engine
    fail_at(monkeypatch, "_link", 1, tmp_path / "secret folder")
    status, _, body = call(
        url,
        "/workspace/host/create-project",
        "POST",
        {"path": str(projects(tmp_path) / "New"), "source_file": EXAMPLE},
    )
    assert (status, body["error"]["code"]) == (503, "save_failure")
    assert not (projects(tmp_path) / "New").exists()

    def broken():
        raise RuntimeError(f"unexpected trouble in {tmp_path}")

    monkeypatch.setattr(workspace, "list_models", broken)
    status, _, internal = call(url, "/workspace/models")
    assert (status, internal) == (
        500,
        {"error": {"code": "internal_error", "message": "Workspace operation failed."}},
    )
    (folder / "project.json").write_text("{", encoding="utf-8")
    status, _, damaged = call(url, f"/workspace/model?model_id={model_id}")
    assert (status, damaged["error"]["code"]) == (503, "workspace_failure")
    text = json.dumps([body, internal, damaged])
    assert str(tmp_path) not in text and os.path.realpath(tmp_path) not in text


def _serve(tmp_path, *args, token=None):
    environment = {**os.environ, "HOME": str(tmp_path), "XDG_DATA_HOME": str(tmp_path / "xdg")}
    environment.pop("TMODEL_HOST_TOKEN", None)
    if token is not None:
        environment["TMODEL_HOST_TOKEN"] = token
    return subprocess.Popen(
        [sys.executable, "-m", "engine", "serve", "--port", "0", "--exit-with-parent", *args],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
    )


def test_serve_turns_projects_on_only_with_the_host_token(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    for args, token, expected in (([], None, 503), (["--projects"], TOKEN, 200)):
        proc = _serve(home, *args, token=token)
        try:
            url = proc.stdout.readline().split("listening on ", 1)[1].strip()
            if expected == 200:
                assert "project folders: on" in proc.stdout.readline()
            assert call(url, "/workspace/models")[0] == expected
            if expected == 200:
                assert call(url, "/workspace/models", token=None)[0] == 403
        finally:
            proc.stdin.close()
            assert proc.wait(timeout=10) == 0
    assert list(home.iterdir()) == []  # neither run wrote anything of its own


@pytest.mark.parametrize("token", [None, "short"])
def test_serve_with_projects_refuses_a_missing_or_weak_token(tmp_path, token):
    proc = _serve(tmp_path, "--projects", token=token)
    out, err = proc.communicate(timeout=20)
    assert proc.returncode == 1
    assert "TMODEL_HOST_TOKEN" in err or "host token" in err
    assert "listening" not in out
    if token:
        assert token not in err


def test_check_host_token():
    assert check_host_token(TOKEN) == TOKEN
    for bad in (None, "x" * 31, "x" * 513, "spaces " + "x" * 40, "é" * 40, "x" * 39 + "\n"):
        with pytest.raises(ValueError) as err:
            check_host_token(bad)
        assert str(bad) not in str(err.value) or bad is None


def test_the_cli_reads_the_token_from_the_environment(monkeypatch):
    seen = {}
    monkeypatch.setattr(server, "serve", lambda **kwargs: seen.update(kwargs))
    monkeypatch.setenv("TMODEL_HOST_TOKEN", TOKEN)
    assert main(["serve", "--port", "0"]) == 0
    assert seen["host_token"] is None  # without --projects the token is ignored
    assert main(["serve", "--port", "0", "--projects"]) == 0
    assert seen["host_token"] == TOKEN


# The shared mock contract (#290)

FOLDER = "/Users/example/Threat Models/Example Threat Model"
LOOSE = "/Users/example/Downloads/imported-model.yaml"
FORK = "/Users/example/Threat Models/Imported Model"
OTHER = "/Users/example/Threat Models/Another"
NOTE = (
    "Synthetic examples of the #288 project routes, for #290's mocks. tests/"
    "test_workspace_api.py makes them from examples/model-workspace/workspace-example.yaml "
    "with a fixed clock and fixed ids, and checks that the engine still answers exactly "
    "this. Paths are placeholders; no value is a credential or a human review."
)
ENABLE = {
    "command": "TMODEL_HOST_TOKEN=<secret> tmodel serve --projects",
    "header": "Authorization: Bearer <the host token>, on every request",
    "host_only": "The /workspace/host/* routes take paths and refuse any request with an "
    "Origin header, so only the desktop host can call them.",
    "saving": "There is no save route: #289's saveModelChanges calls "
    "ProjectWorkspace.commit, which is save_version with no description or summary.",
}


def build_contract(tmp_path, monkeypatch):
    use_examples(monkeypatch, tmp_path)
    workspace = ProjectWorkspace(schema_check=False, clock=Clock(), token=Tokens("contract"))
    folder = projects(tmp_path) / "Example Threat Model"
    loose = tmp_path / "downloads" / "imported-model.yaml"
    loose.parent.mkdir()
    shutil.copyfile(EXAMPLES / EXAMPLE, loose)
    places = {
        str(folder): FOLDER,
        str(loose): LOOSE,
        str(projects(tmp_path) / "Imported Model"): FORK,
        str(projects(tmp_path) / "Another"): OTHER,
    }
    contract = {"note": NOTE, "enable": ENABLE}
    errors = []

    def exchange(url, method, path, body=None, query=None, token=TOKEN, headers=None):
        target = path + ("?" + urlencode(query) if query else "")
        status, _, payload = call(url, target, method, body, token=token, headers=headers)
        request = {"method": method, "path": path}
        if query:
            request["query"] = query
        if body is not None:
            request["body"] = {key: places.get(value, value) for key, value in body.items()}
        return {"request": request, "status": status, "response": payload}

    with running(workspace) as url:
        contract["createProject"] = exchange(
            url,
            "POST",
            "/workspace/host/create-project",
            {"path": str(folder), "source_file": EXAMPLE},
        )
        model_id = contract["createProject"]["response"]["model_id"]
        changed = review_change(workspace.read(model_id, "v001").document)
        risk = assess_document(changed, matrix=MATRIX_ID)["assessments"][0]["derived_risk"]
        arguments = {
            "model_id": model_id,
            "expected_revision": "v001",
            "description": "Reviewed the example path and rated it high",
            "summary": {"matrix": MATRIX_ID, "derived_risk": risk},
        }
        saved = workspace.save_version(document=changed, **arguments)
        contract["saveVersion"] = {
            "request": {"call": "ProjectWorkspace.save_version", **arguments, "document": changed},
            "response": {"revision": saved},
        }
        contract["openProject"] = exchange(
            url, "POST", "/workspace/host/open-project", {"path": str(folder)}
        )
        contract["openFile"] = exchange(
            url, "POST", "/workspace/host/open-file", {"path": str(loose)}
        )
        contract["startProjectFromFile"] = exchange(
            url,
            "POST",
            "/workspace/host/create-project",
            {
                "path": str(projects(tmp_path) / "Imported Model"),
                "model_id": contract["openFile"]["response"]["model_id"],
                "name": "Imported model",
            },
        )
        contract["listOpenModels"] = exchange(url, "GET", "/workspace/models")
        contract["openModel"] = exchange(
            url, "GET", "/workspace/model", query={"model_id": model_id}
        )
        contract["readVersion"] = exchange(
            url, "GET", "/workspace/model", query={"model_id": model_id, "revision": "v001"}
        )
        contract["listVersions"] = exchange(
            url, "GET", "/workspace/versions", query={"model_id": model_id}
        )
        errors.append(
            {
                "operation": "createProject",
                **exchange(
                    url,
                    "POST",
                    "/workspace/host/create-project",
                    {"path": str(folder), "source_file": EXAMPLE},
                ),
            }
        )
        errors.append(
            {
                "operation": "openModel",
                **exchange(
                    url, "GET", "/workspace/model", query={"model_id": "project:" + "0" * 32}
                ),
            }
        )
        with pytest.raises(ReviewError) as stale:
            workspace.save_version(document=changed, **arguments)
        errors.append(
            {
                "operation": "saveVersion",
                "request": {"call": "ProjectWorkspace.save_version", **arguments},
                "status": 409,  # as the #289 review routes answer it
                "response": stale.value.to_dict(),
            }
        )
        errors.append(
            {"operation": "listOpenModels", **exchange(url, "GET", "/workspace/models", token=None)}
        )
        errors.append(
            {
                "operation": "openProject",
                **exchange(
                    url,
                    "POST",
                    "/workspace/host/open-project",
                    {"path": str(folder)},
                    headers={"Origin": "tauri://localhost"},
                ),
            }
        )
        record = fail_at(monkeypatch, "_link", 1, tmp_path)
        errors.append(
            {
                "operation": "createProject",
                **exchange(
                    url,
                    "POST",
                    "/workspace/host/create-project",
                    {"path": str(projects(tmp_path) / "Another"), "source_file": EXAMPLE},
                ),
            }
        )
        monkeypatch.setattr(model_workspace, "_link", record["real"])

        def broken():
            raise RuntimeError("unexpected")

        monkeypatch.setattr(workspace, "list_models", broken)
        errors.append({"operation": "listOpenModels", **exchange(url, "GET", "/workspace/models")})
    with running() as url:
        errors.append({"operation": "listOpenModels", **exchange(url, "GET", "/workspace/models")})
    contract["errors"] = errors
    return contract


def test_the_contract_examples_are_what_the_engine_answers(monkeypatch, tmp_path):
    contract = build_contract(tmp_path, monkeypatch)
    text = json.dumps(contract, indent=2, ensure_ascii=False) + "\n"
    assert str(tmp_path) not in text and os.path.realpath(tmp_path) not in text
    assert {e["response"]["error"]["code"] for e in contract["errors"]} == {
        "validation_error",
        "not_found",
        "revision_conflict",
        "permission_denied",
        "save_failure",
        "workspace_failure",
        "internal_error",
    }
    if os.environ.get("TMODEL_WRITE_CONTRACT") == "1":
        CONTRACT.write_text(text, encoding="utf-8")
    assert json.loads(CONTRACT.read_text(encoding="utf-8")) == contract
    assert Path(CONTRACT).read_text(encoding="utf-8") == text
