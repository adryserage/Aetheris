# Analysis Command

The `aetheris analysis` command performs comprehensive code analysis using multiple AI agents.

## Usage

```bash
aetheris analysis [options]
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--changed-files-only` | | Analyze only modified files (for PR/commits). **Requires** `--files` or `CHANGED_FILES` env var |
| `--files FILES` | | List of files to analyze. Supports two formats (see below). When used with `--changed-files-only`, provides the list of changed files |
| `--pr-number NUM` | | PR number (optional, for information) |
| `--timeout DURATION` | | **(v2.6.1)** Set analysis timeout. Formats: `30m`, `2h`, `90s`, or `0` for unlimited |
| `--reanalyze` | `-r` | **(v2.6.1)** Only analyze files changed since the last analysis. Auto-detects via git or timestamps |
| `--agents AGENTS` | | **(v2.10)** Comma-separated list of agents to run. Use `all` for all agents (default) |
| `--skip-agents AGENTS` | | **(v2.10)** Comma-separated list of agents to skip |
| `--compliance FRAMEWORKS` | | **(v2.10)** Compliance frameworks for privacy analysis: `gdpr`, `hipaa`, `pci_dss`, `ccpa` |

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

### Incremental Reanalysis (v2.6.1)

Automatically detect and analyze only files changed since the last analysis:

```bash
# Auto-detect changed files and reanalyze
aetheris analysis --reanalyze

# Short form
aetheris analysis -r

# Combined with timeout
aetheris analysis -r --timeout 30m
```

**How it works:**
1. Reads the last analysis timestamp from `docs/metrics/metrics_*.json`
2. Detects changed files using git (preferred) or file timestamps (fallback)
3. Analyzes only the changed files
4. Updates existing reports with new findings

> **Note**: If no previous analysis exists, `--reanalyze` will run a full analysis with an informational message.

### Timeout Management (v2.6.1)

Control analysis duration for large codebases:

```bash
# 30 minute timeout
aetheris analysis --timeout 30m

# 2 hour timeout
aetheris analysis --timeout 2h

# Unlimited (no timeout)
aetheris analysis --timeout 0
```

**Supported formats:** `30s` (seconds), `30m` (minutes), `2h` (hours)

**Heartbeat Monitor:** For analyses longer than 10 minutes, a progress indicator is displayed automatically.

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

### Comparison: `--reanalyze` vs `--changed-files-only`

| Feature | `--reanalyze` | `--changed-files-only` |
|---------|---------------|------------------------|
| Auto-detect changes | ✅ Yes (git/timestamps) | ❌ No (requires `--files`) |
| Use case | Local development | CI/CD pipelines |
| Requires previous analysis | ✅ Yes | ❌ No |
| Preserves old findings | ✅ Yes | ❌ No |

## Agent Selection (v2.10)

Control which agents run during analysis:

```bash
# Run specific agents only
aetheris analysis --agents security,performance,type_safety

# Skip specific agents
aetheris analysis --skip-agents metrics,architecture

# Run all agents (default)
aetheris analysis --agents all

# Enable compliance frameworks for privacy analysis
aetheris analysis --compliance gdpr,hipaa

# Combine agent selection with compliance
aetheris analysis --agents data_privacy --compliance gdpr,pci_dss
```

### Available Agents

| Agent | Abbreviation | Description |
|-------|--------------|-------------|
| `code_analysis` | CAE | Individual file analysis |
| `architecture` | AAA | Architecture overview |
| `security` | SSA | Vulnerability detection |
| `metrics` | CMA | Code metrics and complexity |
| `vulnerability` | DVA | CVE scanning |
| `qa` | QAA | Final synthesis |
| `type_safety` | TSA | Type safety issues (v2.10) |
| `performance` | PAA | Performance anti-patterns (v2.10) |
| `api_contract` | ACA | REST API violations (v2.10) |
| `data_privacy` | DPA | PII and compliance (v2.10) |

### Extended Agents (v2.10)

Four new specialized agents for deep analysis:

- **Type Safety (TSA)**: Detects `any` usage, unsafe casts, type ignores, null safety issues
- **Performance (PAA)**: Detects O(n²) complexity, N+1 queries, memory leaks, blocking async
- **API Contract (ACA)**: HTTP method violations, REST naming issues, breaking changes
- **Data Privacy (DPA)**: PII logging, missing encryption, compliance violations

### Compliance Frameworks

Available frameworks for the Data Privacy Agent:

| Framework | Focus Areas |
|-----------|-------------|
| `gdpr` | Email, name, phone, address, IP address |
| `hipaa` | SSN, medical records, health data |
| `pci_dss` | Credit cards, CVV, cardholder data |
| `ccpa` | Email, name, financial data |

## What Gets Analyzed

The analysis includes:

1. **Code Quality** - Best practices, patterns, maintainability
2. **Security** - Vulnerabilities, injections, hardcoded secrets
3. **Architecture** - Module structure, dependencies, cohesion
4. **Metrics** - Complexity, duplication, nesting depth
5. **Dependencies** - CVE scanning via OSV API
6. **Type Safety** - (v2.10) `any` usage, unsafe casts, type ignores
7. **Performance** - (v2.10) O(n²), N+1 queries, memory leaks
8. **API Contracts** - (v2.10) REST violations, breaking changes
9. **Data Privacy** - (v2.10) PII logging, compliance violations

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
| `ANALYSIS_TIMEOUT` | **(v2.6.1)** Default timeout duration | `120m` |
| `HEARTBEAT_INTERVAL` | **(v2.6.1)** Heartbeat interval in seconds | `600` (10 min) |

See [Configuration](../configuration.md) for all options.

## Change Detection (v2.6.1)

When using `--reanalyze`, the system detects changes using one of two methods:

### Git-Based Detection (Preferred)

If the project is a git repository:
1. Reads the git commit SHA from the last analysis metrics file
2. Runs `git diff --name-only <last-sha> HEAD` to find changed files
3. Also includes staged, unstaged, and untracked files

### Timestamp-Based Detection (Fallback)

If git is unavailable:
1. Reads the timestamp from the last analysis metrics file
2. Compares against file modification times
3. Returns all files modified after the last analysis

### Excluded Directories

The following directories are always excluded from change detection:
- `.git`
- `__pycache__`
- `node_modules`
- `.venv`, `venv`
- `.tox`
