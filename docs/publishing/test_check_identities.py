import json
from pathlib import Path

import check_identities


def test_scans_html_and_generated_app_json_for_protected_identities(
    tmp_path: Path,
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.html").write_text("<p>protected-html-id</p>")
    app_data = docs / "app/data/models/example"
    app_data.mkdir(parents=True)
    (app_data / "graph.json").write_text(
        json.dumps({"reviewer": "protected-json-id"})
    )
    # JSON outside the generated application is not a Pages data source and
    # remains outside the deliberately bounded extension of the existing rule.
    (docs / "site.json").write_text('{"owner": "not-scanned"}')

    violations = check_identities.identity_violations(
        docs, ["protected-html-id", "protected-json-id", "not-scanned"]
    )

    assert [(path.relative_to(docs).as_posix(), identity) for path, identity in violations] == [
        ("app/data/models/example/graph.json", "protected-json-id"),
        ("index.html", "protected-html-id"),
    ]


def test_approved_identity_filter_keeps_existing_rules_unchanged() -> None:
    text = 'protected:\n  - "one"\n  - "two"\napproved:\n  - "TWO"\n'
    protected = check_identities.load_list("protected", text)
    approved = {value.lower() for value in check_identities.load_list("approved", text)}

    assert [value for value in protected if value.lower() not in approved] == ["one"]
