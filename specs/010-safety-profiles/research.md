# Research: Safety Profiles

**Feature**: 010-safety-profiles
**Date**: 2026-01-07

## R1: Network Blocking in Python

### Question
How to block outbound network requests in Python without affecting AI provider calls?

### Research Findings

**Approach 1: Socket Monkey Patching**
- Override `socket.socket` to raise an exception for blocked destinations
- Maintain allowlist of permitted hosts (AI providers)
- Context manager pattern for clean setup/teardown

```python
# Concept
class NetworkGuard:
    ALLOWED_HOSTS = [
        "generativelanguage.googleapis.com",  # Gemini
        "api.openai.com",                      # OpenAI
        "api.anthropic.com",                   # Claude
    ]

    def __enter__(self):
        self._original_socket = socket.socket
        socket.socket = self._guarded_socket

    def _guarded_socket(self, *args, **kwargs):
        # Check destination against allowlist
        ...
```

**Approach 2: urllib3/requests Interceptor**
- Hook into HTTP client libraries
- More targeted but doesn't catch all network calls

**Decision**: Approach 1 (Socket level)
- Catches ALL network calls including subprocess
- Works with any HTTP client library
- Clean context manager pattern

### References
- Python socket module documentation
- pytest-socket for testing inspiration

---

## R2: Audit Log Format for CI/CD

### Question
What format should audit logs use for CI mode?

### Research Findings

**Format Comparison**:

| Format | Pros | Cons |
|--------|------|------|
| JSON Lines | Machine-readable, appendable, streamable | Slightly larger |
| Plain text | Human-readable | Hard to parse |
| SQLite | Queryable | Requires DB handling |
| Structured logs (logfmt) | Compact, parseable | Less common |

**Decision**: JSON Lines (JSONL)
- Each line is a valid JSON object
- Easy to stream and append
- Parseable by jq, Python, and CI tools

**Log Entry Schema**:
```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "level": "INFO",
  "event": "analysis_started",
  "profile": "ci",
  "details": {...}
}
```

### References
- JSONL specification
- GitHub Actions log format best practices

---

## R3: Command Allowlist Format

### Question
How should the command allowlist be structured?

### Research Findings

**Requirements**:
- Allow glob patterns (e.g., `git *`, `pytest *`)
- Support exact matches
- Mergeable with user config

**Format Decision**: JSON with pattern array

```json
{
  "version": "1.0",
  "patterns": [
    "git *",
    "pytest *",
    "python -m pytest *",
    "black *",
    "ruff *",
    "mypy *"
  ],
  "exact": [
    "git status",
    "git diff"
  ]
}
```

**Validation**:
- Use `fnmatch` for glob matching
- Validate patterns at load time
- Warn on malformed entries

---

## R4: CI Environment Detection

### Question
How to reliably detect CI/CD environment?

### Research Findings

**Detection Methods**:
1. `os.environ.get('CI')` - Set by most CI systems
2. `sys.stdin.isatty()` - Detects non-interactive terminal
3. Specific env vars: `GITHUB_ACTIONS`, `GITLAB_CI`, `JENKINS_URL`

**Decision**: Combined approach

```python
def is_ci_environment() -> bool:
    # Explicit CI flag
    if os.environ.get('CI', '').lower() in ('true', '1', 'yes'):
        return True
    # Specific CI systems
    ci_vars = ['GITHUB_ACTIONS', 'GITLAB_CI', 'JENKINS_URL', 'TRAVIS']
    if any(os.environ.get(v) for v in ci_vars):
        return True
    # Non-interactive terminal
    return not sys.stdin.isatty()
```

---

## R5: Yolo Mode Warning

### Question
How should the yolo warning be displayed and acknowledged?

### Research Findings

**UX Patterns**:
1. Interactive prompt with confirmation
2. `--yes` / `-y` flag to skip prompt
3. Countdown timer (annoying)

**Decision**: Interactive prompt + `--yes` flag

```text
⚠️  WARNING: YOLO MODE ENABLED
═══════════════════════════════════════════════════
This profile removes safety guardrails:
• Network access unrestricted
• No diff size limits
• Extended repair loops (10 iterations)
• Large refactors allowed

Only use this mode if you:
✓ Understand the risks
✓ Have backups/version control
✓ Are working on non-critical code

Continue? [y/N]:
```

With `--yes` flag: Skip prompt but log warning to audit.

---

## Summary

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Network blocking | Socket-level guard | Comprehensive coverage |
| Audit format | JSONL | Machine-readable, CI-friendly |
| Allowlist format | JSON with glob patterns | Flexible, familiar |
| CI detection | Multi-signal approach | Reliable across platforms |
| Yolo warning | Interactive + --yes flag | Explicit acknowledgment |
