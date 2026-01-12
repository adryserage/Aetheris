# aetheris run

Headless (non-interactive) execution for CI/CD pipelines and automation scripts.

## Synopsis

```bash
aetheris run <task-file> [options]
```

## Description

The `run` command executes tasks from JSON/YAML configuration files in a non-interactive mode. It's designed for:

- CI/CD pipeline integration
- Automated analysis workflows
- Reproducible, deterministic execution
- Structured JSON output for parsing

## Arguments

| Argument | Description |
|----------|-------------|
| `task_file` | Path to task file (JSON or YAML format) |

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--profile` | `-p` | Security profile: `safe`, `ci`, `dev`, `unrestricted` (default: `safe`) |
| `--dry-run` | | Validate task file without executing |
| `--timeout` | `-t` | Execution timeout (e.g., `30m`, `2h`, `0` for unlimited) |
| `--seed` | | Random seed for reproducible execution |
| `--no-timestamps` | | Disable timestamps for deterministic output |
| `--verbose` | `-v` | Enable verbose logging |
| `--output-file` | `-o` | Write output to file instead of stdout |
| `--format` | | Output format: `json` (default) or `yaml` |

## Security Profiles

| Profile | Auto-Fix | File Delete | Shell Commands | Use Case |
|---------|:--------:|:-----------:|:--------------:|----------|
| `safe` | No | No | No | Default, most restrictive |
| `ci` | Yes | No | No | CI/CD environments |
| `dev` | Yes | Yes | Yes | Development use |
| `unrestricted` | Yes | Yes | Yes | Full access |

## Task File Format

### Minimal Example

```json
{
  "version": "1.0",
  "task": {
    "type": "analysis",
    "target": { "files": ["src/**/*.py"] }
  }
}
```

### Complete Example

```json
{
  "version": "1.0",
  "task": {
    "type": "analysis",
    "target": {
      "files": ["src/**/*.py"],
      "changed_only": false,
      "exclude": ["**/test_*.py"]
    },
    "options": {
      "timeout": 1800,
      "profile": "ci",
      "agents": ["security", "quality"],
      "provider": "gemini",
      "verbose": false
    }
  },
  "output": {
    "format": "json",
    "include_diff": true,
    "include_logs": true,
    "file": "result.json"
  },
  "metadata": {
    "run_id": "build-123",
    "triggered_by": "github-actions"
  }
}
```

### YAML Format

```yaml
version: "1.0"
task:
  type: analysis
  target:
    changed_only: true
  options:
    timeout: "15m"
    profile: ci
    agents:
      - security
      - quality
output:
  format: json
  include_logs: true
metadata:
  pipeline: pr-check
```

### Task Types

| Type | Description |
|------|-------------|
| `analysis` | Run code analysis with AI agents |
| `fix` | Apply fixes (requires CI or higher profile) |
| `stats` | Generate statistics |
| `cleanup` | Clean development artifacts |
| `validate-package` | Pre-publication security check |

## Output Format

### Success Response

```json
{
  "status": "success",
  "exit_code": 0,
  "duration_ms": 45230,
  "timestamp": "2026-01-11T12:30:45Z",
  "version": "2.8.0",
  "task": {
    "type": "analysis",
    "files_processed": 42,
    "source_file": "task.json"
  },
  "results": {
    "issues_found": 5,
    "critical": 0,
    "high": 2,
    "medium": 3,
    "low": 0,
    "reports": ["docs/analyses/quality_assurance_report.md"]
  },
  "logs": [
    "INFO: Starting task: analysis",
    "INFO: Security profile: ci",
    "INFO: Analysis completed successfully"
  ]
}
```

### Error Response

```json
{
  "status": "error",
  "exit_code": 1,
  "duration_ms": 150,
  "error": {
    "type": "file_not_found",
    "message": "Task file not found: task.json",
    "details": { "path": "task.json" }
  }
}
```

### Status Values

| Status | Exit Code | Description |
|--------|-----------|-------------|
| `success` | 0 | Task completed successfully |
| `error` | 1 | Task failed with error |
| `timeout` | 1 | Task exceeded timeout |
| `interrupted` | 1 | Task was interrupted (SIGINT/SIGTERM) |
| `blocked` | 1 | Operations blocked by security profile |

## Examples

### Basic Analysis

```bash
# Run analysis from task file
aetheris run task.json

# With CI profile
aetheris run task.json --profile ci
```

### Dry Run (Validation Only)

```bash
# Validate task file without executing
aetheris run task.json --dry-run
```

### Deterministic Execution

```bash
# Use seed and disable timestamps for reproducible results
aetheris run task.json --seed 42 --no-timestamps
```

### CI/CD Integration

```bash
# With timeout and output to file
aetheris run task.json --profile ci --timeout 30m --output-file result.json
```

### GitHub Actions

```yaml
- name: Run Aetheris Analysis
  run: |
    echo '${{ env.TASK_CONFIG }}' > task.json
    aetheris run task.json --profile ci --output-file result.json
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
    TASK_CONFIG: |
      {
        "version": "1.0",
        "task": {
          "type": "analysis",
          "target": { "changed_only": true },
          "options": { "timeout": "30m" }
        }
      }

- name: Check Results
  run: |
    if jq -e '.exit_code != 0' result.json > /dev/null; then
      echo "Analysis found issues"
      jq '.results' result.json
      exit 1
    fi
```

### GitLab CI

```yaml
aetheris-scan:
  script:
    - aetheris run task.yaml --profile ci
  artifacts:
    paths:
      - result.json
    when: always
```

## Signal Handling

The run command handles signals gracefully:

- **SIGINT** (Ctrl+C): Graceful shutdown, returns partial results
- **SIGTERM**: Graceful shutdown, returns partial results

## Related Commands

- [`analysis`](analysis.md) — Interactive codebase analysis
- [`stats`](stats.md) — View statistics and ROI dashboard
- [`cleanup`](cleanup.md) — Remove development artifacts
- [`validate-package`](validate-package.md) — Pre-publication security check

## See Also

- [Headless Mode Documentation](../headless.md) — Complete guide
- [Task File Examples](../../examples/tasks/) — Sample configurations
