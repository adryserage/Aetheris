# Analysis Command

The `aetheris analysis` command performs comprehensive code analysis using multiple AI agents.

## Usage

```bash
aetheris analysis [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--changed-files-only` | Analyze only modified files (for PR/commits). **Requires** `--files` or `CHANGED_FILES` env var |
| `--files FILES` | List of files to analyze. Supports two formats (see below). When used with `--changed-files-only`, provides the list of changed files |
| `--pr-number NUM` | PR number (optional, for information) |

### `--files` Format

The `--files` option accepts **comma-separated paths** (recommended for manual use):

```bash
# Recommended: Simple comma-separated list (no spaces after commas)
--files src/file1.py,src/file2.py,src/file3.py
```

> **Note**: JSON array format (`'["file1.py"]'`) is also supported for CI/CD pipelines that generate JSON output, but comma-separated is preferred for manual usage to avoid shell escaping issues.

### Option Interaction

The `--changed-files-only` and `--files` options work together as follows:

| Mode | Behavior |
|------|----------|
| `--files` alone | Analyzes the specified files directly |
| `--changed-files-only` alone | **Error**: requires `--files` or `CHANGED_FILES` env var to specify which files changed |
| `--changed-files-only --files ...` | Analyzes the files provided via `--files` as the changed file list |

**Priority order** (when `--changed-files-only` is set):
1. `--files` CLI argument (highest priority)
2. `CHANGED_FILES` environment variable (fallback)

## Examples

### Full Analysis
```bash
aetheris analysis
```

### Analyze Specific Files (Manual)
```bash
# Recommended: comma-separated (no spaces)
aetheris analysis --files src/file1.py,src/file2.py
```

### Analyze Changed Files (CI/CD)

For GitHub Actions or other CI pipelines:

```bash
# Using environment variable (recommended for CI)
export CHANGED_FILES="src/file1.py,src/file2.py"
aetheris analysis --changed-files-only

# Or pass files directly (comma-separated)
aetheris analysis --changed-files-only --files src/file1.py,src/file2.py
```

> **Important**: `--changed-files-only` does **not** auto-detect changes via Git. It signals that the analysis scope is limited to the provided file list. Your CI pipeline must detect and pass the changed files (e.g., using `git diff --name-only`).

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

Reports are generated in the directory specified by `OUTPUT_DIR` (default: `docs/analyses`):

| File | Description |
|------|-------------|
| `${OUTPUT_DIR}/<file>.md` | Individual file reports |
| `${OUTPUT_DIR}/quality_assurance_report.md` | QA synthesis |
| `${OUTPUT_DIR}/vulnerabilities_report.md` | Dependency vulnerabilities |
| `${OUTPUT_DIR}/../architecture_overview.md` | Architecture overview |
| `${OUTPUT_DIR}/../metrics/metrics_*.json` | Performance metrics |

> **Note**: Paths shown use `${OUTPUT_DIR}` placeholder. With the default value `docs/analyses`, reports appear in `docs/analyses/`, `docs/architecture_overview.md`, and `docs/metrics/`.

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
