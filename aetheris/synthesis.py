"""QA synthesis: dedupe, sort, count and score a list of findings."""

from collections import Counter

from aetheris.domain import SEVERITY_PENALTY, Finding, severity_rank

TOP_FINDINGS = 20


def _key(finding: Finding) -> tuple[str | None, int | None, str]:
    identity = finding.rule_id or f"{finding.agent}:{finding.message}"
    if finding.line is None and finding.rule_id:
        identity = f"{identity}:{finding.message}"
    return (finding.file, finding.line, identity)


def synthesize(findings: list[Finding]) -> dict[str, object]:
    best: dict[tuple[str | None, int | None, str], Finding] = {}
    for finding in findings:
        key = _key(finding)
        kept = best.get(key)
        if kept is None or severity_rank(finding.severity) < severity_rank(kept.severity):
            best[key] = finding
    unique = sorted(
        best.values(),
        key=lambda f: (severity_rank(f.severity), f.file or "", f.line or 0, f.message),
    )
    by_severity = Counter(f.severity for f in unique)
    by_agent = Counter(f.agent for f in unique)
    score = max(0, 100 - sum(SEVERITY_PENALTY[f.severity] for f in unique))
    return {
        "total": len(unique),
        "duplicates_removed": len(findings) - len(unique),
        "score": score,
        "by_severity": {s: by_severity[s] for s in SEVERITY_PENALTY if by_severity[s]},
        "by_agent": dict(sorted(by_agent.items())),
        "top_findings": [f.model_dump(exclude_none=True) for f in unique[:TOP_FINDINGS]],
    }
