# Features

## Performance & Optimization

### Intelligent Cache
- Git SHA-based cache invalidation
- Persistent storage in `.cache/aetheris/`
- Configurable TTL (default: 7 days)
- 60-80% API cost reduction

```bash
# Disable cache if needed
ENABLE_CACHE=false aetheris analysis
```

### Smart Parallelization
- Dependency graph-based analysis
- Independent files analyzed simultaneously
- Respects dependency order
- Significant time reduction

### Priority System (PR Reviews)
| Priority | Files |
|----------|-------|
| HIGH | Modified in PR |
| MEDIUM | Direct dependencies |
| LOW | Other files |

### Context Caching (Gemini)
```env
ENABLE_CONTEXT_CACHING=true
CONTEXT_CACHE_TTL_SECONDS=3600
```
- 50% API cost reduction
- Reuses context between requests

### Batch API (Gemini)
```env
ENABLE_BATCH_MODE=true
```
- 50% price reduction
- Best for large projects

## Analysis Capabilities

### Security Analysis
- SQL/XSS/Command injection
- Hardcoded secrets detection
- Weak cryptography
- Authentication issues
- CWE identifiers
- OWASP categories

### Code Metrics
- Cyclomatic complexity
- Code duplication detection
- Nesting depth
- Maintainability index

### Dependency Vulnerabilities
- OSV API integration
- npm, PyPI, Pub support
- CVE identification
- Fixed version recommendations

### Incremental Analysis
- Transitive dependencies analysis
- Configurable depth (default: 2)
- PR-optimized (only impacted files)

## AI Features

### Multi-Provider Support
```env
AI_PROVIDER=gemini  # or openai, claude
```

### Consensus Mode (PR Review)
```bash
aetheris pr --providers gemini,claude --consensus
```
Only reports issues found by ALL providers.

### Structured Outputs (Gemini)
```env
ENABLE_STRUCTURED_OUTPUTS=true
```
JSON responses validated via Pydantic.

### Thinking Mode (Gemini 2.5+)
```env
ENABLE_THINKING=true
THINKING_BUDGET=2048
```
See the model's reasoning process.

### Code Execution (Gemini)
```env
ENABLE_CODE_EXECUTION=true
```
Python sandbox for dynamic analysis.

## Error Handling

### Circuit Breaker
Prevents repeated API calls on errors.

### Exponential Backoff
Intelligent retry with increasing delays.

### Error Classification
- Temporary: Retry with backoff
- Permanent: Skip with logging
- Critical: Halt and report

## Package Security (v2.6.2)

### Artifact Cleanup

Remove development artifacts before packaging:

```bash
# Preview cleanup
aetheris cleanup --dry-run

# Standard cleanup
aetheris cleanup

# Deep cleanup (includes build/, dist/, __pycache__/)
aetheris cleanup --deep
```

**Cleaned files include:**
- Security files: `.env`, `*.pem`, `*.key`, `credentials.json`
- OS artifacts: `.DS_Store`, `Thumbs.db`
- Dev tooling: `mypy.ini`, `.eslintrc`, `.prettierrc`
- Test files: `tests/`, `*_test.py`, `test_*.py`

### Secret Scanner

Detect exposed credentials with confidence levels:

| Level | Detection |
|-------|-----------|
| HIGH | AWS keys, GitHub tokens, private keys |
| MEDIUM | Generic API keys, JWT, connection strings |
| LOW | Base64 strings, potential passwords |

**Supported providers:**
- AWS (Access Keys, Secret Keys)
- GitHub (PAT, OAuth tokens)
- Anthropic, OpenAI API keys
- Stripe (Live/Test keys)
- GCP, Azure credentials
- Generic patterns (`api_key=`, `password=`)

### Package Validation

Pre-publication security checks:

```bash
# Validate package
aetheris validate-package

# Auto-fix issues
aetheris validate-package --fix

# Custom size limit
aetheris validate-package --max-size 100
```

**Checks performed:**
- Excluded files detection
- Secret scanning with confidence levels
- Package size validation

### False Positive Management

Create `.secretsignore` to ignore known false positives:

```
# File patterns
tests/fixtures/*
*.example

# Content patterns
CHANGEME
test_key
```

## Extensibility

### Hook System
Register custom hooks on workflow stages:

```python
orchestrator.register_hook(WorkflowStage.FILE_ANALYSIS, my_hook)
```

See [PLUGINS.md](./PLUGINS.md) for details.

### Metrics Export
Performance metrics saved to:
```
docs/metrics/metrics_YYYYMMDD_HHMMSS.json
```

Contains:
- Execution duration
- Per-stage metrics
- Agent statistics
- Cache hit rate
- Token estimates

## Supported Languages

| Language | Extensions |
|----------|------------|
| Python | `.py` |
| TypeScript | `.ts`, `.tsx` |
| JavaScript | `.js`, `.jsx` |
| Dart/Flutter | `.dart` |
| Java | `.java` |
| Kotlin | `.kt` |
| Swift | `.swift` |
| Go | `.go` |
| Rust | `.rs` |
| C/C++ | `.c`, `.cpp`, `.h` |
| C# | `.cs` |
| PHP | `.php` |
| Ruby | `.rb` |

## Excluded Files

Automatically excluded:
- Build directories (`build/`, `dist/`, `node_modules/`)
- Generated files (`.g.dart`, `.d.ts`, `.pyc`)
- Lock files (`package-lock.json`, `yarn.lock`)
- Binary files (> 1MB)
- Hidden directories (`.git/`, `.venv/`)
- `.gitignore` patterns respected

## Output Examples

### Console Output

```
$ aetheris analysis

  Aetheris v2.6.1 - AI Code Analysis
  ══════════════════════════════════════════

  ✓ Discovered 127 files to analyze
  ✓ Building dependency graph...

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
  Analyzing files... [127/127]

  FINDINGS SUMMARY
  ────────────────────────────────────────────

  🔴 CRITICAL: 2 issues
     • SQL injection in user_service.py:45
     • Hardcoded API key in config.py:12

  🟠 HIGH: 5 issues
     • N+1 query pattern in orders.py:78-92
     • Missing input validation in api/routes.py:34
     • Weak password hashing in auth.py:23
     • Circular dependency: auth → users → auth
     • Exposed debug endpoint in server.py:156

  🟡 MEDIUM: 8 issues
  🔵 LOW: 8 issues

  TOTAL: 23 issues found
  ────────────────────────────────────────────

  📊 Quality Score: 72/100 (Fair)
  📁 Report: docs/analyses/quality_assurance_report.md
  ⏱  Completed in 2m 34s
```

### Quality Assurance Report Structure

```markdown
# Quality Assurance Report

## Executive Summary
- **Overall Score**: 72/100
- **Risk Level**: Medium
- **Files Analyzed**: 127
- **Issues Found**: 23

## Critical Issues (Immediate Action Required)

### 1. SQL Injection Vulnerability
- **File**: `src/services/user_service.py:45`
- **CWE**: CWE-89
- **OWASP**: A03:2021 - Injection
- **Description**: User input directly concatenated into SQL query
- **Impact**: Complete database compromise
- **Recommendation**: Use parameterized queries

```python
# Before (vulnerable)
query = f"SELECT * FROM users WHERE id = {user_id}"

# After (secure)
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

## Architecture Analysis
- Layered architecture detected
- 3 circular dependencies found
- Coupling score: 0.68 (moderate)

## Metrics Summary
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Cyclomatic Complexity | 12.3 avg | < 10 | ⚠️ |
| Code Duplication | 8.2% | < 5% | ⚠️ |
| Test Coverage | 67% | > 80% | ❌ |
| Maintainability Index | 72 | > 65 | ✅ |

## Action Plan
1. **Week 1**: Fix critical security issues
2. **Week 2**: Address high-priority findings
3. **Week 3**: Reduce code duplication
4. **Week 4**: Improve test coverage
```

### Vulnerability Report Structure

```markdown
# Dependency Vulnerabilities Report

## Summary
- **Total Dependencies**: 45
- **Vulnerable**: 3
- **Up-to-date**: 38
- **Outdated**: 4

## Critical Vulnerabilities

### CVE-2023-12345 - requests
- **Severity**: CRITICAL (9.8)
- **Installed**: 2.28.0
- **Fixed In**: 2.31.0
- **Description**: Server-side request forgery vulnerability
- **Action**: `pip install requests>=2.31.0`

### CVE-2023-67890 - pyyaml
- **Severity**: HIGH (7.5)
- **Installed**: 5.4.0
- **Fixed In**: 6.0.1
- **Description**: Arbitrary code execution via YAML deserialization
- **Action**: `pip install pyyaml>=6.0.1`
```

### JSON Metrics Output

```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "version": "2.6.1",
  "git_sha": "abc123def456",
  "duration_seconds": 154,
  "files_analyzed": 127,
  "cache_hit_rate": 0.73,
  "stages": {
    "file_discovery": {"duration_ms": 234, "files": 127},
    "dependency_analysis": {"duration_ms": 1523, "dependencies": 45},
    "file_analysis": {"duration_ms": 89234, "completed": 127},
    "security_analysis": {"duration_ms": 12456, "issues": 7},
    "architecture_analysis": {"duration_ms": 8234, "patterns": 3},
    "metrics_analysis": {"duration_ms": 5678, "files": 127},
    "vulnerability_scan": {"duration_ms": 3456, "cves": 3},
    "qa_synthesis": {"duration_ms": 4567}
  },
  "token_usage": {
    "input_tokens": 145000,
    "output_tokens": 23000,
    "estimated_cost_usd": 0.42
  },
  "quality_score": 72,
  "issues_by_severity": {
    "critical": 2,
    "high": 5,
    "medium": 8,
    "low": 8
  }
}
