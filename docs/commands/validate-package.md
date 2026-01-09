# Validate Package Command

The `aetheris validate-package` command performs pre-publication security checks to ensure your package is safe to publish.

## Usage

```bash
aetheris validate-package [options]
```

**Alias**: `aetheris validate`

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--directory`, `-d` | Directory to validate | Current directory |
| `--fix` | Automatically fix issues (remove excluded files) | `false` |
| `--max-size` | Maximum package size in MB | `50` |
| `--secrets-ignore` | Path to secrets ignore file | `.secretsignore` |

## What Gets Validated

### 1. Excluded Files Check

Detects files that should not be included in a published package:

| Category | Examples |
|----------|----------|
| **Security Files** | `.env`, `*.pem`, `*.key`, `credentials.json` |
| **Source Control** | `.git/`, `.svn/` |
| **Test Directories** | `tests/`, `test_*.py` |
| **Dev Config** | `mypy.ini`, `.eslintrc`, `.prettierrc` |

### 2. Secret Scanner

Scans all files for exposed credentials with confidence levels:

| Level | Detection |
|-------|-----------|
| **HIGH** | AWS keys, GitHub tokens, private keys, Stripe keys |
| **MEDIUM** | Generic API keys, JWT tokens, connection strings |
| **LOW** | Base64 encoded strings, potential passwords |

#### Detected Secret Patterns

- **AWS**: Access keys (`AKIA...`), secret keys
- **GitHub**: Personal access tokens, OAuth tokens
- **Anthropic/OpenAI**: API keys
- **Stripe**: Live/test API keys
- **GCP/Azure**: Service account keys, connection strings
- **Generic**: `api_key=`, `password=`, `secret=` patterns

### 3. Package Size Check

Validates that the package doesn't exceed the size limit (default: 50 MB).

## Output Example

```
Validating: /path/to/project

Package Validation Report
==================================================

Size: 12.5 MB (limit: 50.0 MB)
Status: FAIL

Warnings:
  - Found 5 files that should be excluded
  - Found 2 high-confidence secrets!

Excluded files found (5):
  - /path/to/project/.env
  - /path/to/project/.git
  - /path/to/project/tests
  - /path/to/project/mypy.ini
  - /path/to/project/credentials.json

Secrets detected:
  HIGH: .env:3 - AWS Access Key ID (AKIA...)
  HIGH: config.py:15 - GitHub Personal Access Token (ghp_...)
```

## Examples

### Basic Validation

```bash
# Validate current directory
aetheris validate-package
```

### Validate with Auto-Fix

```bash
# Automatically remove excluded files
aetheris validate-package --fix
```

### Custom Size Limit

```bash
# Set 100 MB limit for large packages
aetheris validate-package --max-size 100
```

### Specific Directory

```bash
# Validate dist directory
aetheris validate-package -d dist/
```

## Ignoring False Positives

Create a `.secretsignore` file to ignore false positives:

```
# .secretsignore - Patterns to ignore during secret scanning

# File patterns
tests/fixtures/*
**/test_*.py
*.example

# Content patterns (exact match)
CHANGEME
YOUR_API_KEY_HERE
test_key
fake_key

# Base64 encoded test strings
dGVzdA==
ZXhhbXBsZQ==
```

### Ignore File Syntax

| Type | Example | Description |
|------|---------|-------------|
| File glob | `tests/*` | Ignore all files in tests/ |
| Extension | `*.example` | Ignore all .example files |
| Content | `CHANGEME` | Ignore lines containing this text |

## CI/CD Integration

### GitHub Actions

```yaml
name: Validate Package

on:
  push:
    branches: [main]
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Aetheris
        run: pip install adryserage-aetheris

      - name: Validate Package
        run: aetheris validate-package

      - name: Build if valid
        run: python -m build
```

### Pre-Commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-package
        name: Validate Package
        entry: aetheris validate-package
        language: system
        pass_filenames: false
        stages: [pre-push]
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Validation passed |
| `1` | Validation failed (issues found) |
| `2` | Configuration error |

## Best Practices

1. **Run before every release** — Add to your release checklist
2. **Use `.secretsignore`** — Document known false positives
3. **Set appropriate size limits** — Adjust `--max-size` for your project
4. **Integrate with CI** — Block releases if validation fails
5. **Combine with cleanup** — Run `aetheris cleanup` before validation

## Recommended Workflow

```bash
# 1. Clean artifacts
aetheris cleanup --deep

# 2. Validate package
aetheris validate-package

# 3. If issues found, fix them
aetheris validate-package --fix

# 4. Build package
python -m build

# 5. Publish
twine upload dist/*
```

## Security Considerations

This command is designed to catch common security mistakes before publication:

- **Exposed API Keys** — AWS, GitHub, Stripe, OpenAI, etc.
- **Private Keys** — SSH, TLS, GPG keys
- **Environment Files** — `.env` with secrets
- **Debug Credentials** — Hardcoded test passwords

Always review the validation report carefully and never publish packages with detected secrets.

## Related Commands

- [`aetheris cleanup`](./cleanup.md) — Remove artifacts before packaging
- [`aetheris analysis`](./analysis.md) — Full security analysis
