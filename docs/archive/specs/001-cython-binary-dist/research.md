# Research: Cython Binary Distribution

**Feature**: 001-cython-binary-dist
**Date**: 2025-01-07
**Status**: Complete

## Research Questions

1. How to compile entire Python package with Cython?
2. How to use cibuildwheel for multi-platform builds?
3. How to publish binary-only distribution to PyPI?

---

## 1. Cython Package Compilation

### Decision: Use Cython 3.x with setuptools

**Rationale**: Cython is the most mature and widely-used Python-to-C compiler with 70M+ monthly downloads. It supports compiling `.py` files directly (not just `.pyx`).

**Alternatives Considered**:
| Tool | Pros | Cons | Decision |
|------|------|------|----------|
| Cython | Mature, widely used, pure Python support | Requires C compiler at build time | ✅ Selected |
| Nuitka | Full optimization, standalone executables | Complex, slower builds | ❌ Overkill |
| PyInstaller | Single executable | Not a pip package anymore | ❌ Wrong use case |
| setuptools-cythonize | Simplified setup | Less control | ❌ Less flexible |

### Implementation Approach

From [Cython documentation](https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html):

```python
# setup.py
from setuptools import setup, find_packages
from Cython.Build import cythonize
import glob

# Find all .py files in src/
py_files = glob.glob("src/**/*.py", recursive=True)

# Exclude __init__.py (needed as stubs for imports)
ext_modules = [f for f in py_files if "__init__" not in f]

setup(
    ext_modules=cythonize(
        ext_modules,
        compiler_directives={
            'language_level': "3",
            'always_allow_keywords': True,
        },
        build_dir="build",
    ),
    packages=find_packages(),
)
```

### Key Considerations

1. **`__init__.py` handling**: Keep as minimal stubs for package imports
2. **Entry points**: CLI entry point (`aetheris = "src.cli:main"`) works with compiled modules
3. **Build dependencies**: Add Cython to `build-system.requires` in pyproject.toml

---

## 2. cibuildwheel Configuration

### Decision: Use cibuildwheel 2.x with GitHub Actions

**Rationale**: [cibuildwheel](https://github.com/pypa/cibuildwheel) is the PyPA-recommended tool for building cross-platform wheels. It handles manylinux, macOS, and Windows builds with minimal configuration.

**Key Features**:
- GitHub Actions native support
- Automatic manylinux container usage
- macOS universal2/arm64 support
- Windows x64 support
- Python 3.8-3.13 matrix

### Configuration

**pyproject.toml**:
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel", "Cython>=3.0"]
build-backend = "setuptools.build_meta"

[tool.cibuildwheel]
# Build for specific Python versions
build = "cp38-* cp39-* cp310-* cp311-* cp312-* cp313-*"

# Skip 32-bit builds, musllinux, PyPy
skip = "*-win32 *-manylinux_i686 *musllinux* pp*"

# Test command (verify compiled package works)
test-command = "aetheris --help"
```

**GitHub Actions Workflow**:
```yaml
name: Build Wheels
on:
  push:
    tags:
      - 'v*'

jobs:
  build_wheels:
    name: Build wheels on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]

    steps:
      - uses: actions/checkout@v4

      - name: Build wheels
        uses: pypa/cibuildwheel@v2.22
        env:
          CIBW_ARCHS_MACOS: "x86_64 arm64"
          CIBW_ARCHS_LINUX: "x86_64"
          CIBW_ARCHS_WINDOWS: "AMD64"

      - uses: actions/upload-artifact@v4
        with:
          name: wheels-${{ matrix.os }}
          path: ./wheelhouse/*.whl
```

### Platform-Specific Notes

| Platform | Image/Runner | Architecture | Notes |
|----------|--------------|--------------|-------|
| Linux | manylinux2014 | x86_64 | Default until May 2025, then manylinux_2_28 |
| macOS | macos-latest | x86_64, arm64 | Build both architectures |
| Windows | windows-latest | AMD64 | x64 only |

---

## 3. PyPI Binary-Only Distribution

### Decision: Publish wheels only, no sdist

**Rationale**: To protect source code, only publish compiled wheels. Users without matching wheels cannot install.

**Implementation**:

1. **Don't build sdist**: In GitHub Actions, only run `cibuildwheel` (not `python -m build --sdist`)

2. **MANIFEST.in** (if sdist is accidentally built):
```text
global-exclude *.py
global-exclude *.pyx
include src/__init__.py
include src/*/__init__.py
```

3. **Trusted Publisher**: Continue using GitHub Actions trusted publisher - compatible with wheel-only uploads

### Considerations

- **Existing source versions**: Cannot be removed from PyPI. Only new versions will be binary-only.
- **User experience**: Users on unsupported platforms will get "No matching distribution found" error
- **Debugging**: Stack traces will show compiled module names, not line numbers

---

## Summary

| Component | Decision | Tool/Approach |
|-----------|----------|---------------|
| Compilation | Cython 3.x | cythonize() all .py files except __init__.py |
| Build tool | cibuildwheel 2.22+ | GitHub Actions matrix for 3 OS |
| Platforms | 4 targets | Linux x86_64, macOS x86_64/arm64, Windows x64 |
| Python versions | 6 versions | 3.8, 3.9, 3.10, 3.11, 3.12, 3.13 |
| Distribution | Wheels only | No sdist published |
| CI/CD | GitHub Actions | Trusted publisher to PyPI |

---

## Sources

- [cibuildwheel GitHub](https://github.com/pypa/cibuildwheel)
- [cibuildwheel Documentation](https://cibuildwheel.pypa.io/en/stable/)
- [cibuildwheel FAQ](https://cibuildwheel.pypa.io/en/stable/faq/)
- [Cython Documentation](https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html)
- [setuptools-cythonize](https://github.com/anxuae/setuptools-cythonize)
- [CythonPackage](https://github.com/pprados/cythonpackage)
- [Cython Package Example](https://pypi.org/project/cython-package-example/)
