# Review flow

Your assistant runs a review with four of the six tools, in a fixed order. The server sends these instructions to the client when it connects.

```text
plan_review -> get_rules / get_playbook -> run_checks -> synthesize_report
```

(`list_agents` is optional. It lists the agents and presets without planning anything.)

1. `plan_review` picks the files and the agents to run, with a reason for each.
2. For each agent, `get_rules` returns its rules. When the plan lists playbooks, `get_playbook` returns each method to follow.
3. `run_checks` returns the findings of the agent's deterministic checks. The assistant then reads the files and adds its own findings, marked `source: "assistant"`.
4. `synthesize_report` merges all findings into one report with a score. The assistant reports the score and the top findings. The `qa_synthesis` agent goes last.

## Example

The example below uses a small git repository with one modified file, `src/app.py`, that hard-codes an AWS key example, hashes passwords with MD5 and builds an SQL query by concatenation. The results come from running the server on that repository, shortened for reading.

### 1. Plan the review

```json
{"tool": "plan_review", "arguments": {}}
```

The default scope is `diff`: the files changed against `HEAD` plus untracked files.

```json
{
  "scope": "diff",
  "base": "HEAD",
  "files": ["src/app.py"],
  "file_count": 1,
  "truncated": false,
  "max_files": 500,
  "languages": {"python": 1},
  "agents": [
    {
      "id": "security",
      "reason": "secrets and unsafe code patterns apply to any code",
      "playbooks": [
        {"id": "differential-review", "task": "analyze", "reason": "the scope is a diff"}
      ]
    },
    {"id": "architecture", "reason": "several code files may import each other", "playbooks": []},
    {"id": "type_safety", "reason": "typed languages detected: python", "playbooks": []},
    "... code_quality, metrics, performance, data_privacy ...",
    {
      "id": "qa_synthesis",
      "reason": "merges all findings into one report",
      "playbooks": [
        {"id": "fp-check", "task": "triage", "reason": "verify suspected security findings before reporting them"},
        {"id": "vulnerability-triage-brocards", "task": "triage", "reason": "triage reported vulnerabilities and CVEs"}
      ]
    }
  ],
  "next_steps": "For each agent listed: 1) call get_rules(agent) ..."
}
```

The result also holds `root` (the project directory) and the full `next_steps` text.

### 2. Read the rules and the playbook

```json
{"tool": "get_rules", "arguments": {"agent": "security", "language": "python"}}
```

The result has the agent's `name` and `summary`, 26 `rules` that apply to Python, the `playbooks` of the agent, and the `finding_schema` the assistant must follow. The first rule:

```json
{
  "id": "SEC-001",
  "title": "SQL injection",
  "severity": "critical",
  "check": "Look for SQL text built by concatenation, f-strings, ...",
  "references": ["CWE-89", "OWASP A03:2021", "OWASP A05:2025"]
}
```

The plan listed `differential-review` for this diff, so the assistant also calls:

```json
{"tool": "get_playbook", "arguments": {"id": "differential-review"}}
```

The result has `steps` (the method), `agents`, `task`, and an `attribution` block with the title, author, source, license and changes. See [Playbooks](playbooks.md).

### 3. Run the checks

```json
{"tool": "run_checks", "arguments": {"agent": "security", "paths": ["src/app.py"]}}
```

```json
{
  "agent": "security",
  "checks": ["secret_scan", "security_patterns"],
  "checked_files": 1,
  "findings": [
    {
      "agent": "security", "rule_id": "SEC-005", "severity": "critical",
      "file": "src/app.py", "line": 4,
      "message": "secret_scan: possible aws access key",
      "evidence": "AWS_KEY = \"AKIA********LE\"", "source": "check"
    },
    {
      "agent": "security", "rule_id": "SEC-001", "severity": "high",
      "file": "src/app.py", "line": 13,
      "message": "sql_injection: SQL built by concatenation or formatting; use parameterized queries",
      "evidence": "return db.execute(\"SELECT * FROM users WHERE name = '\" + name + \"'\")",
      "source": "check"
    },
    {
      "agent": "security", "rule_id": "SEC-006", "severity": "medium",
      "file": "src/app.py", "line": 9,
      "message": "weak_crypto: weak hash or cipher; use SHA-256 or AES-256",
      "evidence": "return hashlib.md5(password.encode()).hexdigest()", "source": "check"
    }
  ],
  "finding_count": 3,
  "errors": [],
  "truncated": false
}
```

The secret is masked in the evidence. The assistant now reads `src/app.py` against the rules. Suppose it also notices that `login` logs a user's email. It writes that as a finding of its own, with no `rule_id` because it is not from a check:

```json
{"agent": "security", "severity": "high", "file": "src/app.py", "line": 8,
 "message": "Login logs a user email", "source": "assistant"}
```

It repeats steps 2 and 3 for each agent in the plan.

### 4. Synthesize

```json
{"tool": "synthesize_report", "arguments": {"findings": ["...the three check findings and the assistant finding..."]}}
```

```json
{
  "total": 4,
  "duplicates_removed": 0,
  "score": 66,
  "by_severity": {"critical": 1, "high": 2, "medium": 1},
  "by_agent": {"security": 4},
  "top_findings": ["... the four findings, most severe first ..."]
}
```

The score is 100 minus 15 for the critical finding, 8 for each high and 3 for the medium: 100 - 15 - 16 - 3 = 66. The assistant reports the score and the top findings to you.
