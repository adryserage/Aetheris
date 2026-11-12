from aetheris.checks.secrets import find_secrets, mask_secret, redact
from aetheris.server import run_checks
from tests.conftest import FAKE_AWS_KEY, PASSWORD_LINE, write


def test_leaked_key_is_found_and_never_returned_in_clear(repo):
    write(repo, "config.py", f'AWS_KEY = "{FAKE_AWS_KEY}"\n')
    result = run_checks("security")
    finding = next(f for f in result["findings"] if "aws access key" in f["message"])
    assert finding["severity"] == "critical"
    assert finding["file"] == "config.py" and finding["line"] == 1
    assert FAKE_AWS_KEY not in str(result)
    assert "AKIA" in finding["evidence"] and "*" in finding["evidence"]


def test_mask_keeps_only_edges():
    assert mask_secret("abcdefghijklmnop") == "abcd********op"
    assert mask_secret("short") == "*****"


def test_placeholders_and_references_are_not_secrets():
    assert not find_secrets("password = os.environ['DB_PASSWORD']")
    assert not find_secrets('token = "your_token_here"')
    assert find_secrets(PASSWORD_LINE)


def test_overlapping_matches_keep_one_hit_and_redact_it():
    line = f'api_key = "{FAKE_AWS_KEY}"'
    assert len(find_secrets(line)) == 1
    assert FAKE_AWS_KEY not in redact(line)


def test_security_patterns_flag_sql_concatenation(repo):
    write(repo, "db.py", 'cursor.execute("SELECT * FROM t WHERE id=" + user_id)\n')
    messages = [f["message"] for f in run_checks("security")["findings"]]
    assert any(m.startswith("sql_injection") for m in messages)
