"""Cases that used to be reported and are not problems (AETHERIS-24)."""

import pytest

from aetheris.checks.secrets import find_secrets
from aetheris.files import is_test_file
from aetheris.server import run_checks
from tests.conftest import FAKE_AWS_KEY, FAKE_CARD, FAKE_SSN, PASSWORD_LINE, write

AWS_SAMPLE = "AKIAIOSFODNN7" + "EXAMPLE"


def findings(agent: str) -> list[dict]:
    return run_checks(agent)["findings"]


def test_documented_sample_keys_are_not_secrets():
    assert not find_secrets(f'key = "{AWS_SAMPLE}"')
    assert find_secrets(f'key = "{FAKE_AWS_KEY}"')


def test_bearer_auth_param_is_not_a_token():
    bearer = "Authorization: Bear" + "er "
    assert not find_secrets(bearer + 'resource_metadata="https://x/.well-known/a"')
    assert find_secrets(bearer + "abcdef0123456789abcdef")
    assert find_secrets(bearer + "abcdefghijklmnopqrstuvwx=")


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


def test_secrets_keep_their_severity_in_test_and_doc_files(repo):
    write(repo, "tests/test_conf.py", f'KEY = "{FAKE_AWS_KEY}"\n')
    write(repo, "tests/test_pw.py", PASSWORD_LINE + "\n")
    write(repo, "docs/setup.md", PASSWORD_LINE + "\n")
    by_file = {f["file"]: f["severity"] for f in findings("security")}
    assert by_file == {
        "tests/test_conf.py": "critical",
        "tests/test_pw.py": "medium",
        "docs/setup.md": "medium",
    }


def test_personal_data_keeps_its_severity_in_test_files(repo):
    write(repo, "tests/test_users.py", f'ssn = "{FAKE_SSN}"\ncard = "{FAKE_CARD}"\n')
    severities = {f["message"].split(":")[0]: f["severity"] for f in findings("data_privacy")}
    assert severities == {"ssn": "high", "credit_card": "high"}


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


def test_sql_built_only_from_module_constants_is_not_an_injection(repo):
    write(
        repo,
        "deploy.py",
        'SERVICE = "abc"\nFILES = {"index.html": "/app/index.html"}\n'
        'paths = ",".join(f"\'/data/{SERVICE}/{name}\'" for name in FILES)\n'
        'sql = f"DELETE FROM volumes WHERE path in ({paths});"\n'
        'target = "x"\ntarget = input()\n'
        'q = f"DELETE FROM volumes WHERE path = {target}"\n'
        'r = f"DELETE FROM volumes WHERE path = {user_path}"\n'
        'table = "t"\n'
        "def read(table):\n"
        '    return f"SELECT * FROM t WHERE name = {table}"\n',
    )
    lines = [f["line"] for f in findings("security") if f["message"].startswith("sql_injection")]
    assert lines == [7, 8, 11]


def test_walking_folders_then_their_files_is_not_a_nested_loop(repo):
    write(
        repo,
        "walk.mjs",
        "for (const person of people) {\n"
        "  const trash = join(ROOT, person, 'trash');\n"
        "  let names;\n"
        "  try { names = await readdir(trash); } catch { continue; }\n"
        "  for (const name of names) {\n"
        "    await unlink(join(trash, name));\n"
        "  }\n"
        "}\n",
    )
    write(
        repo,
        "pairs.py",
        "for folder in folders:\n    for f in folder.files:\n        pass\n"
        "for i in range(n):\n    for j in range(i, n):\n        pass\n"
        "for a in items:\n    for b in others:\n        pass\n"
        "for k in items:\n    for m in items[k:]:\n        pass\n"
        "for x in rows:\n    for y in lst[:x]:\n        pass\n",
    )
    nested = [
        (f["file"], f["line"])
        for f in findings("performance")
        if f["message"].startswith("nested_loops")
    ]
    assert nested == [("pairs.py", 4), ("pairs.py", 7), ("pairs.py", 10), ("pairs.py", 13)]
