# Implementation Plan: Cython Binary Distribution

**Branch**: `001-cython-binary-dist` | **Date**: 2025-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-cython-binary-dist/spec.md`

## Summary

Transform Aetheris from source distribution to compiled binary distribution on PyPI. Use Cython to compile all Python source files to platform-native extensions (`.so`/`.pyd`), and use cibuildwheel with GitHub Actions to build wheels for all supported platforms (Linux x86_64, macOS x86_64/arm64, Windows x64) across Python 3.8-3.13.

## Technical Context

**Language/Version**: Python 3.8-3.13 (6 versions)
**Primary Dependencies**: Cython ≥3.0, setuptools, cibuildwheel
**Storage**: N/A (build/distribution feature)
**Testing**: Manual verification on each platform; existing test suite for functionality
**Target Platform**: Linux x86_64, macOS x86_64, macOS arm64, Windows x64
**Project Type**: Single CLI package with compiled extensions
**Performance Goals**: Build completes in <30 minutes; no runtime performance regression
**Constraints**: Wheels must be under 50MB each; no source distribution published
**Scale/Scope**: ~20 Python files to compile; 4 platforms × 6 Python versions = 24 wheel variants

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **PASS** - Constitution template not configured for this project. No specific gates defined.

## Project Structure

### Documentation (this feature)

```text
specs/001-cython-binary-dist/
├── plan.md              # This file
├── research.md          # Phase 0: Cython/cibuildwheel research
├── checklists/          # Validation checklists
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2: Implementation tasks
```

### Source Code (repository root)

```text
# Existing structure (unchanged)
src/
├── __init__.py
├── cli.py               # Entry point - will be compiled
├── core/                # Core modules - will be compiled
│   ├── __init__.py
│   ├── analyzer.py
│   ├── orchestrator.py
│   └── ...
├── agents/              # AI agents - will be compiled
├── models/              # Data models - will be compiled
└── services/            # Services - will be compiled

# New files for Cython build
setup.py                 # NEW: Cython build configuration
pyproject.toml           # MODIFIED: Build system config
MANIFEST.in              # NEW: Exclude source from sdist

# CI/CD
.github/workflows/
├── publish.yml          # MODIFIED: Use cibuildwheel
└── build-wheels.yml     # NEW: Multi-platform wheel builder
```

**Structure Decision**: Existing `src/` structure remains unchanged. New build configuration files added at repository root. GitHub Actions workflows modified for multi-platform compiled builds.

## Complexity Tracking

No constitution violations to justify.

---

## Phase 0: Research

### Research Tasks

1. **Cython compilation for CLI packages**
   - How to compile all `.py` files to extensions
   - Handling `__init__.py` files and package imports
   - Entry point configuration with compiled modules

2. **cibuildwheel configuration**
   - Multi-platform wheel building (manylinux, macOS, Windows)
   - Python version matrix (3.8-3.13)
   - GitHub Actions integration

3. **PyPI binary-only distribution**
   - Publishing wheels without sdist
   - Trusted publisher workflow compatibility

### Research Output: [research.md](./research.md)

---

## Phase 1: Design

### Build Configuration

**setup.py** - Cython extension definitions:
```python
# Compile all .py files in src/ to extensions
# Use Cython.Build.cythonize with proper settings
# Configure package_data to exclude .py files
```

**pyproject.toml** - Build system:
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel", "Cython>=3.0"]
build-backend = "setuptools.build_meta"
```

**MANIFEST.in** - Source exclusion:
```text
exclude src/*.py
exclude src/**/*.py
recursive-exclude src *.py
```

### CI/CD Configuration

**GitHub Actions Workflow**:
- Trigger: Version tag (v*)
- Matrix: Linux (manylinux2014), macOS (x86_64, arm64), Windows (x64)
- Python: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- Tool: cibuildwheel
- Publish: PyPI trusted publisher (no token needed)

### No API Contracts

This feature does not introduce new APIs - it changes the build/distribution process only.

### No Data Model Changes

This feature does not introduce new entities or data structures beyond build configuration.

---

## Phase 1 Artifacts

| Artifact | Status | Notes |
|----------|--------|-------|
| research.md | To generate | Cython + cibuildwheel research |
| data-model.md | N/A | No data model for build feature |
| contracts/ | N/A | No API contracts |
| quickstart.md | N/A | No user-facing API changes |

---

## Next Steps

1. Generate `research.md` with detailed Cython/cibuildwheel findings
2. Run `/speckit.tasks` to generate implementation task list
3. Implement build configuration
4. Test locally on one platform
5. Set up GitHub Actions workflow
6. Test full multi-platform build
7. Release v2.6.0 with binary distribution
