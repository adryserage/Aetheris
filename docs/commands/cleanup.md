# Cleanup Command

The `aetheris cleanup` command removes development artifacts and prepares your codebase for packaging and distribution.

## Usage

```bash
aetheris cleanup [options]
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--dry-run` | Preview files to be deleted without deleting | `false` |
| `--deep` | Include build directories (dist/, build/, *.egg-info/) | `false` |
| `--patterns` | Additional patterns to exclude (comma-separated) | `""` |
| `--directory`, `-d` | Directory to clean | Current directory |

## What Gets Cleaned

### Standard Cleanup (Default)

| Category | Patterns |
|----------|----------|
| **Security** | `.env`, `.env.*`, `secrets.json`, `*.pem`, `*.key`, `id_rsa*` |
| **OS Artifacts** | `.DS_Store`, `Thumbs.db`, `desktop.ini`, `._*` |
| **Dev Tooling** | `.eslintrc*`, `.prettierrc*`, `mypy.ini`, `.ruff.toml` |
| **Test Files** | `*_test.py`, `test_*.py`, `conftest.py`, `tests/` |
| **IDE Files** | `.vscode/`, `.idea/`, `*.swp`, `*.swo` |

### Deep Cleanup (`--deep`)

In addition to standard cleanup:

| Category | Patterns |
|----------|----------|
| **Build Directories** | `build/`, `dist/`, `*.egg-info/` |
| **Cache Directories** | `__pycache__/`, `.pytest_cache/`, `.mypy_cache/` |
| **Compiled Files** | `*.pyc`, `*.pyo`, `*.so`, `*.pyd` |
| **Logs** | `*.log`, `logs/` |
| **Backups** | `*.bak`, `*.backup`, `*.orig` |

## Examples

### Preview Cleanup (Recommended First)

```bash
# See what would be deleted without actually deleting
aetheris cleanup --dry-run
```

### Standard Cleanup

```bash
# Remove dev artifacts, keep build directories
aetheris cleanup
```

### Deep Cleanup

```bash
# Full cleanup including build directories
aetheris cleanup --deep
```

### Custom Patterns

```bash
# Add project-specific patterns
aetheris cleanup --patterns "*.bak,*.tmp,logs/"
```

### Specific Directory

```bash
# Clean only a specific directory
aetheris cleanup -d src/
```

## Output Example

```
Cleanup: /path/to/project
Mode: Dry run (preview)
Deep clean: No

Files/directories that would be deleted:

Directories:
  /path/to/project/.git/ (5.0 MB)
  /path/to/project/tests/ (1.2 MB)

Files:
  /path/to/project/.env (363 B)
  /path/to/project/mypy.ini (1.2 KB)

Total: 6.5 MB would be freed
```

## Best Practices

1. **Always use `--dry-run` first** — Review what will be deleted before actual cleanup
2. **Use version control** — Ensure changes are committed before cleanup
3. **Consider CI integration** — Run cleanup as part of your release workflow
4. **Combine with validate-package** — Run `aetheris validate-package` after cleanup

## Use Cases

### Pre-Release Packaging

```bash
# Clean before building package
aetheris cleanup --deep
python -m build
```

### CI/CD Pipeline

```yaml
# In GitHub Actions
- name: Clean artifacts
  run: aetheris cleanup --deep

- name: Build package
  run: python -m build
```

### Development Reset

```bash
# Full reset of development environment
aetheris cleanup --deep --patterns ".tox/,.nox/"
```

## Security Considerations

The cleanup command removes security-sensitive files like:

- `.env` files (API keys, secrets)
- Private keys (`*.pem`, `*.key`)
- SSH keys (`id_rsa*`, `id_ed25519*`)
- Credential files (`credentials.json`, `secrets.yaml`)

This helps prevent accidental publication of secrets to package registries.

## Related Commands

- [`aetheris validate-package`](./validate-package.md) — Validate package before publication
- [`aetheris analysis`](./analysis.md) — Full codebase analysis
