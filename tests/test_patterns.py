from aetheris.server import run_checks
from tests.conftest import write


def messages(agent: str) -> list[str]:
    return [f["message"] for f in run_checks(agent)["findings"]]


def test_typescript_escape_hatches(repo):
    write(repo, "a.ts", "const x: any = 1;\n// @ts-ignore\nconst y = z as unknown as T;\n")
    found = messages("type_safety")
    assert any(m.startswith("any_usage") for m in found)
    assert any(m.startswith("unsafe_cast") for m in found)
    assert not any(m.startswith("type_ignore") for m in found)


def test_python_type_ignore(repo):
    write(repo, "a.py", "x: int = foo()  # type: ignore\n")
    assert any(m.startswith("type_ignore") for m in messages("type_safety"))


def test_nested_loops_and_n_plus_one(repo):
    write(
        repo,
        "p.py",
        "for a in items:\n    for b in others:\n        pass\n"
        "for u in users:\n    db.execute('SELECT 1')\n",
    )
    found = messages("performance")
    assert any(m.startswith("nested_loops") for m in found)
    assert any(m.startswith("n_plus_one") for m in found)


def test_orphan_call_and_orphan_endpoint(repo):
    write(repo, "server.js", "app.get('/api/users/:id', h);\napp.post('/api/orphan', h);\n")
    write(repo, "client.js", "fetch(`/api/users/${id}`);\nfetch('/api/missing');\n")
    found = messages("api_contract")
    assert any(m.startswith("orphan_endpoint") and "/api/orphan" in m for m in found)
    assert any(m.startswith("orphan_call") and "/api/missing" in m for m in found)
    assert not any("/api/users" in m for m in found)


def test_verb_in_url(repo):
    write(repo, "api.py", "@app.get('/getUsers')\ndef users(): ...\n")
    assert any(m.startswith("verb_in_url") for m in messages("api_contract"))


def test_privacy_ssn_card_and_logging(repo):
    write(
        repo,
        "p.py",
        'ssn = "123-45-6789"\ncard = "4111 1111 1111 1111"\nprint("user email", email)\n',
    )
    found = messages("data_privacy")
    assert any(m.startswith("ssn") for m in found)
    assert any(m.startswith("credit_card") for m in found)
    assert any(m.startswith("pii_logging") for m in found)
    assert "4111 1111 1111 1111" not in str(run_checks("data_privacy"))
