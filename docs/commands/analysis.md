# Analysis Command

The `aetheris analysis` command performs comprehensive code analysis using multiple AI agents.

## Usage

```bash
aetheris analysis [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--changed-files-only` | Analyze only modified files (for PR/commits) |
| `--files FILES` | List of files to analyze (JSON array or comma-separated) |
| `--pr-number NUM` | PR number (optional, for information) |

## Examples

### Full Analysis
```bash
aetheris analysis
```

### Analyze Specific Files
```bash
aetheris analysis --files src/file1.py,src/file2.py
```

### Analyze Changed Files (GitHub Actions)
```bash
aetheris analysis --changed-files-only --files '["src/file1.py", "src/file2.py"]'
```

### With PR Number
```bash
aetheris analysis --changed-files-only --files src/file1.py --pr-number 123
```

## What Gets Analyzed

The analysis includes:

1. **Code Quality** - Best practices, patterns, maintainability
2. **Security** - Vulnerabilities, injections, hardcoded secrets
3. **Architecture** - Module structure, dependencies, cohesion
4. **Metrics** - Complexity, duplication, nesting depth
5. **Dependencies** - CVE scanning via OSV API

## Output

Reports are generated in `docs/analyses/`:

| File | Description |
|------|-------------|
| `docs/analyses/<file>.md` | Individual file reports |
| `docs/architecture_overview.md` | Architecture overview |
| `docs/analyses/quality_assurance_report.md` | QA synthesis |
| `docs/analyses/vulnerabilities_report.md` | Dependency vulnerabilities |
| `docs/metrics/metrics_*.json` | Performance metrics |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ROOT_DIR` | Directory to analyze | `.` |
| `OUTPUT_DIR` | Output directory | `docs/analyses` |
| `BATCH_SIZE` | Files analyzed in parallel | `10` |
| `ENABLE_SECURITY_ANALYSIS` | Enable security checks | `true` |
| `ENABLE_METRICS_ANALYSIS` | Enable code metrics | `true` |
| `ENABLE_DEPENDENCY_VULNERABILITY` | Enable CVE scanning | `true` |

See [Configuration](../configuration.md) for all options.
