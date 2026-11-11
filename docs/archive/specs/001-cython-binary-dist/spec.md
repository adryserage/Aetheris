# Feature Specification: Cython Binary Distribution

**Feature Branch**: `001-cython-binary-dist`
**Created**: 2025-01-07
**Status**: Draft
**Input**: Add Cython compilation to create closed-source binary distribution for PyPI

## Overview

Transform the Aetheris package from source distribution to compiled binary distribution. Users will continue installing via `pip install adryserage-aetheris` but receive pre-compiled binaries instead of readable Python source files. This protects the codebase while maintaining full functionality and cross-platform compatibility.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install Compiled Package (Priority: P1)

As an end user, I want to install Aetheris via pip and use it normally, without being able to read the source code.

**Why this priority**: Core value proposition - users get the tool without access to source code.

**Independent Test**: Install the package on any supported platform and run `aetheris analysis`. The command works, but inspecting the installed package shows only compiled binaries (`.so`/`.pyd` files), not `.py` source files.

**Acceptance Scenarios**:

1. **Given** a user with Python 3.8+ on Linux, **When** they run `pip install adryserage-aetheris`, **Then** the package installs successfully and contains no readable `.py` source files in the `src/` directory
2. **Given** an installed package, **When** the user runs `aetheris analysis`, **Then** all features work identically to the source distribution
3. **Given** an installed package, **When** the user navigates to the package directory, **Then** they find only `.so` (Linux/Mac) or `.pyd` (Windows) files instead of `.py` files

---

### User Story 2 - Cross-Platform Availability (Priority: P2)

As an end user on any major platform, I want pre-built binaries available so I don't need a compiler to install the package.

**Why this priority**: Without pre-built wheels for each platform, users would need C compilers installed, breaking the seamless pip experience.

**Independent Test**: Verify that `pip install adryserage-aetheris` works without requiring any compiler on fresh Linux (x86_64), macOS (Intel and Apple Silicon), and Windows (x64) systems.

**Acceptance Scenarios**:

1. **Given** a fresh Ubuntu/Debian system without build tools, **When** user runs `pip install adryserage-aetheris`, **Then** a pre-built wheel installs without compilation
2. **Given** a macOS Apple Silicon (M1/M2) machine, **When** user runs `pip install adryserage-aetheris`, **Then** the arm64 wheel installs and works
3. **Given** a Windows 10/11 x64 machine, **When** user runs `pip install adryserage-aetheris`, **Then** a pre-built wheel installs without Visual Studio requirement

---

### User Story 3 - Automated Release Pipeline (Priority: P3)

As a maintainer, I want releases to automatically build and publish compiled wheels for all platforms when I create a version tag.

**Why this priority**: Manual builds across platforms are error-prone and time-consuming. Automation ensures consistent releases.

**Independent Test**: Create a git tag `vX.Y.Z`, verify CI automatically builds wheels for all 5 platform targets and publishes to PyPI.

**Acceptance Scenarios**:

1. **Given** a new version tag pushed to GitHub, **When** CI runs, **Then** wheels are built for: manylinux (x86_64), macOS (x86_64), macOS (arm64), Windows (x64)
2. **Given** successful wheel builds, **When** CI completes, **Then** all wheels are automatically uploaded to PyPI
3. **Given** a build failure on one platform, **When** CI runs, **Then** maintainer receives notification with clear error logs

---

### Edge Cases

- What happens when a user has an unsupported Python version (e.g., 3.7)? → Clear error message indicating minimum Python 3.8 required
- What happens when a user has an unsupported platform (e.g., 32-bit)? → Pip fails to find compatible wheel with informative message
- What happens if PyPI already has source distribution uploaded? → Only publish wheels for new versions; cannot retroactively remove source
- How does development workflow change for maintainers? → Local development still uses source; only releases are compiled

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Build process MUST compile all `.py` files in `src/` directory to platform-native binaries
- **FR-002**: Distributed packages MUST NOT contain readable `.py` source files (except `__init__.py` stubs if needed for imports)
- **FR-003**: CLI entry point `aetheris` MUST remain functional after compilation
- **FR-004**: All existing functionality (analysis, fix, pr, issues, etc.) MUST work identically in compiled form
- **FR-005**: Build process MUST produce wheels for Linux x86_64 (manylinux), macOS x86_64, macOS arm64, and Windows x64
- **FR-006**: Release workflow MUST automatically build and publish all platform wheels when a version tag is created
- **FR-007**: Package MUST NOT publish source distribution (sdist) to PyPI for new versions
- **FR-008**: Python version support MUST cover 3.8, 3.9, 3.10, 3.11, 3.12, and 3.13

### Key Entities

- **Wheel**: Platform-specific distribution package containing compiled binaries
- **Binary Extension**: Compiled Python module (`.so` on Linux/macOS, `.pyd` on Windows)
- **Build Matrix**: Combination of platforms × Python versions requiring separate builds

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Package installs successfully on all 4 platform targets without requiring local compilation
- **SC-002**: Users cannot read source code from installed package (no `.py` files with business logic)
- **SC-003**: All existing CLI commands work identically to source distribution
- **SC-004**: Release cycle time remains under 30 minutes from tag to PyPI availability
- **SC-005**: Package size increase stays under 3x compared to source distribution (acceptable for compiled code)

## Assumptions

- PyPI allows publishing only wheel distributions without sdist
- Cython compilation does not alter the runtime behavior of the code
- All dependencies (google-genai, pydantic, openai, etc.) remain compatible with compiled modules
- GitHub Actions provides runners for all target platforms
- Users accept that they cannot modify or inspect the source code after installation

## Out of Scope

- Obfuscation beyond compilation (no additional encryption or packing)
- Support for 32-bit platforms
- Support for Python versions below 3.8
- Retroactive removal of existing source distributions from PyPI
- License changes (MIT remains, applies to distributed compiled code)

## Clarifications

_Session 2025-01-07_

- Q: Should we support ARM Linux (e.g., Raspberry Pi)? → A: Not initially, can be added later based on demand
