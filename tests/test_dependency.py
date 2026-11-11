import requests

from aetheris.checks import dependency
from aetheris.checks.dependency import (
    parse_package_json,
    parse_pubspec,
    parse_pyproject,
    parse_requirements,
)
from aetheris.server import run_checks
from tests.conftest import write


def test_manifests_parse_to_pinned_packages():
    assert parse_requirements(
        "# c\nrequests==2.31.0\nflask>=2\nfoo[extra]==1.0 # x\n-r b.txt\n"
    ) == [
        ("PyPI", "requests", "2.31.0"),
        ("PyPI", "foo", "1.0"),
    ]
    assert parse_package_json(
        '{"dependencies": {"left-pad": "^1.3.0", "x": "*"}, "devDependencies": {"y": "~2.0.1"}}'
    ) == [("npm", "left-pad", "1.3.0"), ("npm", "y", "2.0.1")]
    assert parse_pubspec("dependencies:\n  http: ^1.2.0\n  flutter:\n    sdk: flutter\n") == [
        ("Pub", "http", "1.2.0")
    ]
    assert parse_pyproject('dependencies = ["pyyaml==6.0.1", "mcp>=1"]') == [
        ("PyPI", "pyyaml", "6.0.1")
    ]


def test_known_vulnerability_becomes_a_finding(repo, monkeypatch):
    write(repo, "requirements.txt", "requests==2.0.0\nsafe==1.0\n")
    sent = {}

    def fake_osv(payload):
        sent.update(payload)
        return {"results": [{"vulns": [{"id": "GHSA-xxxx"}]}, {}]}

    monkeypatch.setattr(dependency, "query_osv", fake_osv)
    result = run_checks("dependency")
    assert sent["queries"][0] == {
        "package": {"name": "requests", "ecosystem": "PyPI"},
        "version": "2.0.0",
    }
    assert [f["file"] for f in result["findings"]] == ["requirements.txt"]
    assert "requests@2.0.0" in result["findings"][0]["message"]
    assert result["errors"] == []


def test_network_failure_is_an_error_entry_not_an_exception(repo, monkeypatch):
    write(repo, "requirements.txt", "requests==2.0.0\n")

    def boom(payload):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(dependency, "query_osv", boom)
    result = run_checks("dependency")
    assert result["findings"] == []
    assert "OSV unreachable" in result["errors"][0]


def test_broken_manifest_is_reported(repo, monkeypatch):
    write(repo, "package.json", "{not json")
    monkeypatch.setattr(dependency, "query_osv", lambda p: {"results": []})
    messages = [f["message"] for f in run_checks("dependency")["findings"]]
    assert any("cannot parse package.json" in m for m in messages)
