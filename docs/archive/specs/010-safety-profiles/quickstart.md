# Quickstart: Safety Profiles

**Feature**: 010-safety-profiles
**Date**: 2026-01-07

## Basic Usage

### Safe Mode (Default)

Conservative analysis with maximum guardrails.

```bash
# Explicit safe mode
aetheris analysis --profile safe

# Implicit (safe is default)
aetheris analysis
```

**What happens**:
- Network requests blocked (except AI provider)
- Max 500 lines changed per analysis
- Max 3 repair loops
- Commands validated against allowlist
- Tests must pass before changes applied

---

### CI Mode

Strict mode for automated pipelines.

```bash
# CI pipeline usage
aetheris analysis --profile ci

# With JSON output for parsing
aetheris analysis --profile ci --output json
```

**What happens**:
- Fails immediately on any error (exit code 1)
- No interactive prompts ever
- Audit log written to `./aetheris-audit.jsonl`
- Machine-readable output available

**GitHub Actions Example**:
```yaml
- name: Run Aetheris Analysis
  run: aetheris analysis --profile ci
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

---

### Yolo Mode

Full autonomy for experienced users.

```bash
# Interactive confirmation required
aetheris analysis --profile yolo

# Skip confirmation (for scripting)
aetheris analysis --profile yolo --yes
```

**What happens**:
- Warning displayed, confirmation required
- Network access unrestricted
- No diff size limits
- Up to 10 repair loops
- Large refactors allowed
- All operations logged for traceability

---

## Configuration

### Project-Level Default

Set default profile in `.aetheris.json`:

```json
{
  "default_profile": "safe",
  "safe": {
    "max_diff_lines": 300,
    "max_repair_loops": 2
  }
}
```

### Custom Allowlist

Extend the command allowlist in `.aetheris.json`:

```json
{
  "allowlist": {
    "patterns": [
      "npm *",
      "yarn *",
      "cargo *"
    ]
  }
}
```

---

## Common Scenarios

### Local Development

```bash
# Quick analysis with safe defaults
aetheris analysis

# Analyze specific files with safe mode
aetheris analysis --files src/core/analyzer.py --profile safe
```

### Pull Request Review

```bash
# CI-friendly PR analysis
aetheris pr review 123 --profile ci
```

### Large Refactoring Session

```bash
# When you need extended capabilities
aetheris analysis --profile yolo --yes

# Check the audit log after
cat aetheris-audit.jsonl | jq '.event'
```

---

## Profile Comparison

| Feature | Safe | CI | Yolo |
|---------|------|----|----- |
| Network (aux) | ❌ | ✅ | ✅ |
| Network (AI) | ✅ | ✅ | ✅ |
| Interactive | ✅ | ❌ | ✅ |
| Fail-fast | ❌ | ✅ | ❌ |
| Audit log | ❌ | ✅ | ✅ |
| Max diff | 500 lines | 500 lines | Unlimited |
| Repair loops | 3 | 3 | 10 |
| Allowlist | ✅ | ❌ | ❌ |
| Tests required | ✅ | ✅ | ❌ |

---

## Error Messages

### Invalid Profile

```
Error: Invalid profile 'foo'. Valid profiles: safe, ci, yolo
```

### Safe Mode Constraint

```
⚠️ Diff size limit exceeded (732 lines > 500 max)
   Profile: safe
   Action: Changes rejected. Use --profile yolo to override.
```

### CI Mode Failure

```
Error: Analysis failed with exit code 1
Audit log: ./aetheris-audit.jsonl
```
