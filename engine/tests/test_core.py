from engine import __version__, core


def test_version_reports_engine_and_package_version():
    v = core.version()
    assert v["engine"] == "tmodel-engine"
    assert v["version"] == __version__


def test_health_is_ok_and_includes_version():
    h = core.health()
    assert h["status"] == "ok"
    assert h["version"] == __version__
