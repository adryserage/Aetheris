from aetheris.server import run_checks
from tests.conftest import write


def test_python_cycle_is_reported_as_medium(repo):
    write(repo, "pkg/__init__.py", "")
    write(repo, "pkg/a.py", "from pkg import b\n")
    write(repo, "pkg/b.py", "from pkg.a import thing\n")
    write(repo, "pkg/c.py", "from pkg import a\n")
    findings = run_checks("architecture")["findings"]
    assert len(findings) == 1
    assert findings[0]["severity"] == "medium"
    assert "pkg/a.py" in findings[0]["message"] and "pkg/b.py" in findings[0]["message"]
    assert "pkg/c.py" not in findings[0]["message"]


def test_type_checking_and_function_level_imports_are_not_cycles(repo):
    write(
        repo,
        "a.py",
        "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    import b\n\n"
        "def f():\n    import b\n",
    )
    write(repo, "b.py", "import a\n")
    assert run_checks("architecture")["findings"] == []


def test_relative_imports_form_a_cycle(repo):
    write(repo, "p/__init__.py", "")
    write(repo, "p/x.py", "from . import y\n")
    write(repo, "p/y.py", "from .x import f\n")
    assert len(run_checks("architecture")["findings"]) == 1


def test_typescript_cycle(repo):
    write(repo, "src/a.ts", "import { b } from './b';\n")
    write(repo, "src/b.ts", "export { a } from './a';\n")
    write(repo, "src/index.ts", "import { a } from './a';\n")
    findings = run_checks("architecture")["findings"]
    assert len(findings) == 1 and "src/a.ts" in findings[0]["message"]
