import json
import threading
import urllib.error
import urllib.request

import pytest

from engine import __version__
from engine.api.server import is_loopback, make_server


@pytest.fixture
def server():
    httpd = make_server("127.0.0.1", 0)  # any free port
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, dict(resp.headers), json.loads(resp.read())


def test_health_endpoint(server):
    status, _, body = get(f"{server}/health")
    assert status == 200
    assert body["status"] == "ok"
    assert body["version"] == __version__


def test_version_endpoint(server):
    status, _, body = get(f"{server}/version")
    assert status == 200
    assert body["engine"] == "tmodel-engine"


def test_unknown_path_is_404(server):
    with pytest.raises(urllib.error.HTTPError) as err:
        get(f"{server}/nope")
    assert err.value.code == 404


def test_cors_only_for_tauri_origins(server):
    _, headers, _ = get(f"{server}/health", {"Origin": "tauri://localhost"})
    assert headers.get("Access-Control-Allow-Origin") == "tauri://localhost"
    _, headers, _ = get(f"{server}/health", {"Origin": "https://evil.example"})
    assert "Access-Control-Allow-Origin" not in headers


@pytest.mark.parametrize("host", ["0.0.0.0", "192.168.1.10", "example.com"])
def test_refuses_non_loopback_bind(host):
    with pytest.raises(ValueError):
        make_server(host, 0)


def test_is_loopback():
    assert is_loopback("127.0.0.1")
    assert is_loopback("::1")
    assert is_loopback("localhost")
    assert not is_loopback("0.0.0.0")
