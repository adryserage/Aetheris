from aetheris.checks.metrics import compute_metrics, find_duplicate_blocks
from aetheris.server import run_checks
from tests.conftest import write

BRANCHY = "def f(x):\n" + "".join(f"    if x == {i}:\n        return {i}\n" for i in range(16))
DEEP = (
    "def g(x):\n"
    "    if x:\n        for i in x:\n            while i:\n"
    "                if i:\n                    with i:\n                        pass\n"
)


def test_python_function_metrics():
    m = compute_metrics(BRANCHY, "python")
    assert m.functions[0].name == "f" and m.functions[0].complexity == 17
    assert compute_metrics(DEEP, "python").functions[0].nesting == 5


def test_elif_chain_does_not_count_as_nesting():
    code = "def h(x):\n    if x == 1:\n        pass\n" + "    elif x == 2:\n        pass\n" * 6
    assert compute_metrics(code, "python").functions[0].nesting == 1


def test_javascript_functions_are_measured_by_braces():
    code = (
        "function big(a) {\n  if (a) {\n    for (;;) {\n      if (a && b) { x(); }\n    }\n  }\n}\n"
    )
    fn = compute_metrics(code, "javascript").functions[0]
    assert fn.name == "big" and fn.complexity == 5 and fn.nesting == 3


def test_code_quality_thresholds(repo):
    write(repo, "branchy.py", BRANCHY)
    write(repo, "deep.py", DEEP)
    write(repo, "long.py", "def long():\n" + "    value = compute(1, 2, 3)\n" * 90)
    messages = [f["message"] for f in run_checks("code_quality")["findings"]]
    assert any(m.startswith("complexity: f ") for m in messages)
    assert any(m.startswith("nesting: g ") for m in messages)
    assert any(m.startswith("function_length: long ") for m in messages)


def test_duplicate_blocks_are_detected():
    block = "".join(f"    result_{i} = compute_something({i}) + other\n" for i in range(5))
    content = "def a():\n" + block + "def b():\n" + block
    assert find_duplicate_blocks(content) == [(8, 12, 2)]


def test_metrics_agent_reports_info_per_file(repo):
    write(repo, "m.py", "def f():\n    return 1\n")
    finding = run_checks("metrics")["findings"][0]
    assert finding["severity"] == "info" and "functions=1" in finding["message"]
