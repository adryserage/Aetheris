from aetheris.domain import Finding
from aetheris.server import synthesize_report


def finding(severity="high", file="a.py", line=1, rule_id="SEC-001", **extra):
    return Finding(
        agent="security",
        severity=severity,
        file=file,
        line=line,
        rule_id=rule_id,
        message="m",
        **extra,
    )


def test_duplicates_collapse_keeping_the_worst_severity():
    report = synthesize_report([finding("medium"), finding("critical"), finding(line=2)])
    assert report["total"] == 2 and report["duplicates_removed"] == 1
    assert report["by_severity"] == {"critical": 1, "high": 1}
    assert report["top_findings"][0]["severity"] == "critical"


def test_score_penalties_and_floor():
    mixed = [
        finding("critical", line=1),
        finding("high", line=2),
        finding("medium", line=3),
        finding("low", line=4),
        finding("info", line=5),
    ]
    assert synthesize_report(mixed)["score"] == 100 - 15 - 8 - 3 - 1
    many = [finding("critical", line=i) for i in range(10)]
    assert synthesize_report(many)["score"] == 0


def test_findings_without_rule_id_are_told_apart_by_message():
    a = finding(rule_id=None, source="assistant")
    b = a.model_copy(update={"message": "other"})
    assert synthesize_report([a, b])["total"] == 2


def test_sorted_by_severity_then_file_and_top_is_capped():
    items = [finding("low", file=f"f{i:02d}.py") for i in range(30)] + [
        finding("high", file="z.py")
    ]
    top = synthesize_report(items)["top_findings"]
    assert len(top) == 20 and top[0]["file"] == "z.py" and top[1]["file"] == "f00.py"
