import json
import threading

import pytest

from engine import __version__
from engine.api.server import make_server
from engine.cli import main


@pytest.fixture
def engine_url():
    httpd = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def test_health_through_api(engine_url, capsys):
    assert main(["health", "--url", engine_url]) == 0
    assert capsys.readouterr().out.strip() == f"ok · tmodel-engine v{__version__}"


def test_version_json_through_api(engine_url, capsys):
    assert main(["version", "--json", "--url", engine_url]) == 0
    assert json.loads(capsys.readouterr().out)["version"] == __version__


def test_api_and_in_process_give_same_answer(engine_url, capsys):
    main(["health", "--json", "--url", engine_url])
    via_api = json.loads(capsys.readouterr().out)
    main(["health", "--json", "--in-process"])
    assert json.loads(capsys.readouterr().out) == via_api


def test_unreachable_engine_exits_1(capsys):
    assert main(["health", "--url", "http://127.0.0.1:9"]) == 1
    assert "no tmodel engine" in capsys.readouterr().err


def test_serve_refuses_port_in_use(engine_url, capsys):
    port = int(engine_url.rsplit(":", 1)[1])
    assert main(["serve", "--port", str(port)]) == 1
    assert "error" in capsys.readouterr().err


def test_missing_command_is_usage_error():
    with pytest.raises(SystemExit) as err:
        main([])
    assert err.value.code == 2
