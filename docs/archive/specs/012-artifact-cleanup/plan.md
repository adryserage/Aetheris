# Implementation Plan: Nettoyage des Artefacts & Sécurisation des Paquets

**Branch**: `012-artifact-cleanup` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-artifact-cleanup/spec.md`
**Target Version**: v2.6.2

## Summary

Implement an artifact cleanup and package security system with three main components:
1. **Automatic exclusion**: Default patterns for files/folders to exclude from packages
2. **Cleanup command**: `aetheris cleanup` for removing build artifacts and temporary files
3. **Secret scanner**: Pre-publish validation to detect leaked credentials

## Technical Context

**Language/Version**: Python 3.9+ (matches existing project)
**Primary Dependencies**: pathlib (file operations), re (regex patterns), typer (CLI), rich (output)
**Storage**: Local filesystem, `.secretsignore` file
**Testing**: pytest (existing test framework)
**Target Platform**: Linux, macOS, Windows (cross-platform CLI)
**Project Type**: Single Python package with CLI
**Performance Goals**: Secret scan < 5s for 10k files
**Constraints**: Must integrate with existing build tools (setup.py, pyproject.toml)
**Scale/Scope**: ~400-500 LOC addition across 4-6 files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Library-First | ✅ Pass | Cleanup/scanner logic in `src/services/` as reusable modules |
| CLI Interface | ✅ Pass | Exposes `aetheris cleanup` and `aetheris validate-package` commands |
| Test-First | ✅ Pass | Unit tests for exclusion patterns, secret detection |
| Integration Testing | ✅ Pass | Integration tests for full cleanup + validation flow |
| Observability | ✅ Pass | Detailed output of deleted files, detected secrets (masked) |
| Simplicity | ✅ Pass | Uses regex patterns, no external dependencies for scanning |

No violations. Proceed to Phase 0.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Commands                              │
├─────────────────────────────────────────────────────────────────┤
│  aetheris cleanup [--dry-run] [--deep] [--patterns ...]         │
│  aetheris validate-package [--fix]                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Services Layer                                │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  CleanupService │  SecretScanner  │  PackageValidator           │
│  - cleanup()    │  - scan()       │  - validate()               │
│  - dry_run()    │  - detect()     │  - check_exclusions()       │
│  - get_size()   │  - load_ignore()│  - check_size()             │
└─────────────────┴─────────────────┴─────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Models / Config                               │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ ExclusionConfig │ SecretPattern   │ ValidationReport            │
│ - patterns[]    │ - name          │ - size_mb                   │
│ - deep_patterns │ - regex         │ - excluded_files[]          │
│ - custom[]      │ - description   │ - secrets_found[]           │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

## Project Structure

### Documentation (this feature)

```text
specs/012-artifact-cleanup/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output (patterns research)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── cli.py                    # MODIFY: Add cleanup and validate-package commands
├── services/
│   ├── cleanup_service.py    # NEW: Artifact cleanup logic
│   ├── secret_scanner.py     # NEW: Secret detection engine
│   └── package_validator.py  # NEW: Pre-publish validation
├── models/
│   └── cleanup_models.py     # NEW: ExclusionConfig, SecretPattern, ValidationReport
└── config/
    ├── exclusion_patterns.py # NEW: Default exclusion patterns
    └── secret_patterns.py    # NEW: Secret detection regex patterns

tests/
├── unit/
│   ├── test_cleanup_service.py    # NEW: Cleanup logic tests
│   ├── test_secret_scanner.py     # NEW: Secret detection tests
│   └── test_package_validator.py  # NEW: Validation tests
└── fixtures/
    ├── sample_project/            # NEW: Test fixtures with various files
    └── secrets_samples/           # NEW: Sample secrets for testing (fake)
```

## Default Exclusion Patterns

### Always Excluded (security)

| Pattern | Category | Reason |
|---------|----------|--------|
| `.env` | Secrets | Environment variables with credentials |
| `.env.*` (except `.env.example`) | Secrets | Environment variants |
| `.git/` | VCS | Version control metadata |
| `.gitignore` | VCS | Not needed in package |
| `.github/` | CI | GitHub-specific configs |

### Always Excluded (OS artifacts)

| Pattern | Category | Reason |
|---------|----------|--------|
| `.DS_Store` | macOS | Finder metadata |
| `Thumbs.db` | Windows | Explorer thumbnails |
| `desktop.ini` | Windows | Folder settings |
| `*.swp`, `*.swo` | Editor | Vim swap files |
| `*~` | Editor | Backup files |

### Always Excluded (dev tooling)

| Pattern | Category | Reason |
|---------|----------|--------|
| `tsconfig.tsbuildinfo` | TypeScript | Build cache |
| `*.tsbuildinfo` | TypeScript | Build info |
| `.eslintrc*`, `eslint.config.*` | Linting | Not needed in prod |
| `.prettierrc*` | Formatting | Not needed in prod |
| `.editorconfig` | Editor | Dev convenience |
| `*.pyc`, `__pycache__/` | Python | Compiled bytecode |
| `*.pyo` | Python | Optimized bytecode |

### Always Excluded (tests)

| Pattern | Category | Reason |
|---------|----------|--------|
| `tests/`, `test/` | Testing | Test suites |
| `__tests__/` | Testing | Jest convention |
| `*_test.py`, `test_*.py` | Testing | Python test files |
| `conftest.py` | Testing | Pytest fixtures |
| `mocks/`, `__mocks__/` | Testing | Mock data |
| `fixtures/` | Testing | Test fixtures |

### Deep Clean (optional, `--deep`)

| Pattern | Category | Reason |
|---------|----------|--------|
| `dist/` | Build | Distribution folder |
| `build/` | Build | Build artifacts |
| `*.egg-info/` | Build | Package metadata |
| `.eggs/` | Build | Egg cache |
| `.tox/` | Testing | Tox environments |
| `.pytest_cache/` | Testing | Pytest cache |
| `.coverage` | Testing | Coverage data |
| `htmlcov/` | Testing | Coverage reports |

## Secret Detection Patterns

### High Confidence Patterns

| Pattern Name | Regex | Example Match |
|--------------|-------|---------------|
| AWS Access Key | `AKIA[0-9A-Z]{16}` | `AKIAIOSFODNN7EXAMPLE` |
| AWS Secret Key | `(?i)aws_secret_access_key\s*=\s*['"]?([A-Za-z0-9/+=]{40})` | `aws_secret_access_key = wJalrXUtnFEMI...` |
| Generic API Key | `(?i)(api[_-]?key|apikey)\s*[=:]\s*['"]?([a-zA-Z0-9_-]{20,})` | `API_KEY=sk-1234...` |
| Generic Secret | `(?i)(secret|password|passwd|pwd)\s*[=:]\s*['"]?([^\s'"]{8,})` | `PASSWORD=<value>` |
| Generic Token | `(?i)(token|auth[_-]?token|bearer)\s*[=:]\s*['"]?([a-zA-Z0-9_.-]{20,})` | `TOKEN=<token>` |

### Medium Confidence Patterns

| Pattern Name | Regex | Example Match |
|--------------|-------|---------------|
| Private Key Header | `-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----` | PEM private key |
| JWT Token | `eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*` | JWT format |
| GitHub Token | `gh[pousr]_[A-Za-z0-9_]{36,}` | `ghp_xxxx...` |
| Slack Token | `xox[baprs]-[0-9]{10,}-[a-zA-Z0-9-]+` | `xoxb-123...` |

### Provider-Specific Patterns

| Provider | Pattern | Notes |
|----------|---------|-------|
| Google Cloud | `AIza[0-9A-Za-z_-]{35}` | GCP API key |
| Stripe | `sk_live_[0-9a-zA-Z]{24,}` | Stripe secret key |
| Stripe | `rk_live_[0-9a-zA-Z]{24,}` | Stripe restricted key |
| SendGrid | `SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}` | SendGrid API key |
| Twilio | `SK[0-9a-fA-F]{32}` | Twilio API key |

## .secretsignore Format

Similar to `.gitignore`, one pattern per line:

```gitignore
# Ignore test fixtures
tests/fixtures/fake_credentials.py

# Ignore specific file
src/config/example_config.py

# Ignore hash values (false positives)
*.md:SHA256

# Ignore specific line patterns
*:EXAMPLE_API_KEY=
```

## CLI Commands Design

### aetheris cleanup

```bash
# Basic cleanup (removes .pyc, __pycache__, etc.)
aetheris cleanup

# Preview what would be deleted
aetheris cleanup --dry-run

# Deep clean (includes dist/, build/, etc.)
aetheris cleanup --deep

# Custom patterns
aetheris cleanup --patterns "*.log" "*.tmp"

# Combine options
aetheris cleanup --deep --dry-run --patterns "*.bak"
```

**Output Example:**
```
🧹 Cleaning up artifacts...

Files to remove:
  - __pycache__/             (12 files, 45.2 KB)
  - src/__pycache__/         (8 files, 32.1 KB)
  - .pytest_cache/           (5 files, 12.0 KB)
  - *.pyc                    (3 files, 8.5 KB)

Total: 28 files, 97.8 KB

✅ Cleanup complete. Freed 97.8 KB.
```

### aetheris validate-package

```bash
# Validate package before publish
aetheris validate-package

# Auto-fix detected issues
aetheris validate-package --fix

# Check specific directory
aetheris validate-package --path ./dist/
```

**Output Example (failure):**
```
🔍 Validating package...

❌ SECRETS DETECTED:
  - src/config/api.py:23 - AWS Access Key (AKIA...)
  - src/services/auth.py:45 - Generic API Key (sk-...)

❌ EXCLUDED FILES FOUND IN PACKAGE:
  - .env (should be excluded)
  - tests/ (should be excluded)

📦 Package size: 2.3 MB (OK, < 50 MB limit)

❌ Validation FAILED. Fix issues before publishing.
   Use --fix to automatically correct some issues.
```

## Config Integration (v3.0+)

Will integrate with `config.json` system from 006-persistent-config:

```json
{
  "cleanup": {
    "auto_run_on_build": false,
    "deep_clean": false,
    "extra_exclude_patterns": [],
    "minify": false,
    "strip_docstrings": false
  },
  "security": {
    "scan_for_secrets": true,
    "block_on_secrets": true,
    "max_package_size_mb": 50,
    "secrets_ignore_file": ".secretsignore"
  }
}
```

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| False positives in secret scan | Medium | `.secretsignore` support, clear error messages |
| Accidental deletion of needed files | High | `--dry-run` by default suggestion, confirmation for `--deep` |
| Slow scan on large projects | Medium | Parallel file scanning, early exit on exclusions |
| Pattern misses real secrets | High | Comprehensive regex library, regular updates |
| Minification breaks code | Medium | Optional flag, keep backups, test first |

## Dependencies

- **Internal**: Uses existing CLI framework (typer), output formatting (rich)
- **External**: None required for core functionality
- **Optional**: `python-minifier` for optional minification feature

## Testing Strategy

| Test Type | Coverage | Tools |
|-----------|----------|-------|
| Unit tests | Pattern matching, file detection | pytest |
| Integration tests | Full cleanup + validate flow | pytest |
| Fixtures | Sample projects with various files | Custom |
| Security tests | Known secret patterns | pytest |
| Performance tests | Large file count scenarios | pytest-benchmark |
