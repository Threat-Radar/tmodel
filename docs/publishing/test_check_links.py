from pathlib import Path

from check_links import check_links


def test_pages_root_and_asset_sources_resolve(tmp_path: Path):
    docs = tmp_path / "docs"
    app = docs / "app"
    assets = app / "assets"
    assets.mkdir(parents=True)
    (assets / "app.js").write_text("", encoding="utf-8")
    (app / "index.html").write_text(
        '<script src="/tmodel/app/assets/app.js"></script><a href="?model=mvp-01">model</a>',
        encoding="utf-8",
    )
    assert check_links(docs) == []


def test_missing_and_escaping_paths_fail(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.html").write_text(
        '<script src="/tmodel/app/missing.js"></script><a href="../secret">bad</a>',
        encoding="utf-8",
    )
    assert check_links(docs) == [
        (Path("index.html"), "/tmodel/app/missing.js"),
        (Path("index.html"), "../secret"),
    ]
