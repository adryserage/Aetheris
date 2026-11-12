"""Cases that used to be reported and are not problems (AETHERIS-24)."""

import pytest

from aetheris.checks.secrets import find_secrets
from aetheris.files import is_test_file
from aetheris.server import run_checks
from tests.conftest import FAKE_AWS_KEY, write

AWS_SAMPLE = "AKIAIOSFODNN7" + "EXAMPLE"


def findings(agent: str) -> list[dict]:
    return run_checks(agent)["findings"]


def test_documented_sample_keys_are_not_secrets():
    assert not find_secrets(f'key = "{AWS_SAMPLE}"')
    assert find_secrets(f'key = "{FAKE_AWS_KEY}"')


def test_bearer_auth_param_is_not_a_token():
    assert not find_secrets("h = f'Bearer resource_metadata=\"{base}/x\"'")
    assert find_secrets("Authorization: Bearer abcdef0123456789abcdef")
    assert find_secrets("Authorization: Bearer abcdefghijklmnopqrstuvwx=")


@pytest.mark.parametrize(
    "path",
    [
        "tests/a.py",
        "src/__tests__/a.ts",
        "test_a.py",
        "a_test.go",
        "a.spec.ts",
        "a.test.js",
        "Tests/A.cs",
        "src/UserTest.java",
    ],
)
def test_test_files_are_recognized(path):
    assert is_test_file(path)


@pytest.mark.parametrize(
    "path", ["src/a.py", "latest.py", "contest/a.py", "docs/specs/a.md", "src/spec/openapi.py"]
)
def test_other_files_are_not_test_files(path):
    assert not is_test_file(path)


def test_pattern_findings_in_test_files_drop_to_info(repo):
    write(repo, "tests/test_db.py", 'q = "SELECT * FROM u WHERE id=" + uid\n')
    write(repo, "src/db.py", 'q = "SELECT * FROM u WHERE id=" + uid\n')
    by_file = {f["file"]: f for f in findings("security")}
    assert by_file["tests/test_db.py"]["severity"] == "info"
    assert by_file["tests/test_db.py"]["message"].endswith("(test file)")
    assert by_file["src/db.py"]["severity"] == "high"


def test_non_pattern_checks_keep_their_severity_in_test_files(repo):
    write(repo, "tests/a.py", "import tests.b\n")
    write(repo, "tests/b.py", "import tests.a\n")
    assert {f["severity"] for f in findings("architecture")} == {"medium"}


def test_a_real_key_in_a_test_file_stays_critical(repo):
    write(repo, "tests/test_conf.py", f'KEY = "{FAKE_AWS_KEY}"\n')
    write(repo, "tests/test_pw.py", 'password = "hunter2hunter2"\n')
    by_file = {f["file"]: f["severity"] for f in findings("security")}
    assert by_file == {"tests/test_conf.py": "critical", "tests/test_pw.py": "info"}


def test_generic_secrets_in_docs_drop_to_info(repo):
    write(repo, "docs/setup.md", f'password = "hunter2hunter2"\nKEY={FAKE_AWS_KEY}\n')
    severities = {f["line"]: f["severity"] for f in findings("security")}
    assert severities == {1: "info", 2: "critical"}


def test_inner_loops_of_fixed_size_are_not_nested_loops(repo):
    write(
        repo,
        "p.py",
        "for a in items:\n    for s in ('x', 'y'):\n        pass\n"
        "for b in items:\n    for p in PATTERNS:\n        pass\n"
        "for c in items:\n    for d in others:\n        pass\n"
        "for e in items:\n    for g in [h for h in rows]:\n        pass\n"
        "for i in items:\n    for j in T.rows:\n        pass\n",
    )
    lines = [f["line"] for f in findings("performance") if f["message"].startswith("nested")]
    assert lines == [7, 10, 13]


def test_the_word_any_in_a_docstring_is_not_an_any_hint(repo):
    write(repo, "a.py", '"""Escape hatches: any, casts."""\n\ndef f(x: Any) -> int:\n    pass\n')
    lines = [f["line"] for f in findings("type_safety") if f["message"].startswith("any_usage")]
    assert lines == [3]


def test_html_sinks_are_only_checked_in_javascript_and_typescript(repo):
    write(repo, "rules.py", 'XSS = r"innerHTML\\s*=|document\\.write\\s*\\("\n')
    write(repo, "page.ts", "el.innerHTML = html;\n")
    files = [f["file"] for f in findings("security") if f["message"].startswith("xss")]
    assert files == ["page.ts"]
