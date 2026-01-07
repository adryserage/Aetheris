# Tasks: Cython Binary Distribution

**Input**: Design documents from `/specs/001-cython-binary-dist/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅

**Tests**: No automated tests requested - manual verification per user story.

**Organization**: Tasks grouped by user story for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3)
- Exact file paths included

---

## Phase 1: Setup (Build Infrastructure)

**Purpose**: Add Cython build dependencies and configuration base

- [X] T001 Update pyproject.toml build-system to include Cython in `pyproject.toml`
- [X] T002 [P] Create setup.py with Cython extension configuration in `setup.py`
- [X] T003 [P] Create MANIFEST.in to exclude source files in `MANIFEST.in`
- [X] T004 Add cibuildwheel configuration section to `pyproject.toml`

---

## Phase 2: Foundational (Local Build Verification)

**Purpose**: Ensure Cython compilation works locally before CI setup

**⚠️ CRITICAL**: Must verify local build works before setting up multi-platform CI

- [X] T005 Create minimal `__init__.py` stubs for all packages in `src/`
- [X] T006 Test local Cython build with `python setup.py build_ext --inplace`
- [X] T007 Verify CLI entry point works with compiled modules locally
- [X] T008 Verify no `.py` source files in build output (except `__init__.py`)

**Checkpoint**: Local build works - can proceed to multi-platform CI

---

## Phase 3: User Story 1 - Install Compiled Package (Priority: P1) 🎯 MVP

**Goal**: Users install via pip and receive compiled binaries, no readable source code

**Independent Test**: Run `pip install ./dist/*.whl` locally, verify `aetheris analysis` works and no `.py` files exist in installed package

### Implementation for User Story 1

- [X] T009 [US1] Configure Cython compiler directives (language_level=3) in `setup.py`
- [X] T010 [US1] Add glob pattern to find all `.py` files in src/ for compilation in `setup.py`
- [X] T011 [US1] Exclude `__init__.py` files from Cython compilation in `setup.py`
- [X] T012 [US1] Configure package_data to exclude `.py` files from wheel in `setup.py`
- [X] T013 [US1] Build test wheel locally with `python -m build --wheel`
- [X] T014 [US1] Install test wheel in fresh venv and verify `aetheris --help` works
- [X] T015 [US1] Verify installed package contains `.so`/`.pyd` files, not `.py` files

**Checkpoint**: Local wheel builds and installs correctly with compiled modules

---

## Phase 4: User Story 2 - Cross-Platform Availability (Priority: P2)

**Goal**: Pre-built wheels available for Linux, macOS (Intel + ARM), Windows

**Independent Test**: Download wheels from CI artifacts, install on each platform without compiler

### Implementation for User Story 2

- [X] T016 [P] [US2] Create `.github/workflows/build-wheels.yml` with cibuildwheel action
- [X] T017 [US2] Configure build matrix: ubuntu-latest, macos-latest, windows-latest in `build-wheels.yml`
- [X] T018 [US2] Configure CIBW_ARCHS_LINUX=x86_64 in `build-wheels.yml`
- [X] T019 [US2] Configure CIBW_ARCHS_MACOS="x86_64 arm64" in `build-wheels.yml`
- [X] T020 [US2] Configure CIBW_ARCHS_WINDOWS=AMD64 in `build-wheels.yml`
- [X] T021 [US2] Configure Python version matrix (cp38-cp313) in `pyproject.toml` [tool.cibuildwheel]
- [X] T022 [US2] Configure skip patterns (32-bit, musllinux, PyPy) in `pyproject.toml` [tool.cibuildwheel]
- [X] T023 [US2] Add test-command to verify wheel works in `pyproject.toml` [tool.cibuildwheel]
- [X] T024 [US2] Configure artifact upload for wheels in `build-wheels.yml`
- [ ] T025 [US2] Test workflow manually (push to test branch)

**Checkpoint**: CI builds wheels for all 4 platform targets across 6 Python versions

---

## Phase 5: User Story 3 - Automated Release Pipeline (Priority: P3)

**Goal**: Version tag triggers automatic build and publish to PyPI

**Independent Test**: Create tag vX.Y.Z, verify wheels appear on PyPI within 30 minutes

### Implementation for User Story 3

- [X] T026 [P] [US3] Create `.github/workflows/publish-wheels.yml` for PyPI publishing
- [X] T027 [US3] Configure trigger on version tags (v*) in `publish-wheels.yml`
- [X] T028 [US3] Add job dependency: publish after all builds succeed in `publish-wheels.yml`
- [X] T029 [US3] Download all wheel artifacts in publish job in `publish-wheels.yml`
- [X] T030 [US3] Configure PyPI trusted publisher action in `publish-wheels.yml`
- [X] T031 [US3] Remove sdist build from publish workflow (wheels only) in `publish-wheels.yml`
- [ ] T032 [US3] Update existing `.github/workflows/publish.yml` to use new wheel workflow
- [ ] T033 [US3] Add build status badge to README.md

**Checkpoint**: Tag push triggers full build and PyPI publish automatically

---

## Phase 6: Polish & Validation

**Purpose**: Final verification and documentation

- [ ] T034 [P] Update CHANGELOG.md with v2.6.0 entry for binary distribution
- [ ] T035 [P] Update README.md installation section (note: binary-only distribution)
- [ ] T036 Bump version to 2.6.0 in `pyproject.toml`
- [ ] T037 Create and push tag v2.6.0 to trigger release
- [ ] T038 Verify all wheels appear on PyPI
- [ ] T039 Test pip install on clean Linux system
- [ ] T040 Test pip install on clean macOS system
- [ ] T041 Test pip install on clean Windows system
- [ ] T042 Verify `aetheris analysis` works on all platforms

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS user stories
- **US1 (Phase 3)**: Depends on Foundational - MVP
- **US2 (Phase 4)**: Depends on US1 (needs working setup.py)
- **US3 (Phase 5)**: Depends on US2 (needs working CI build)
- **Polish (Phase 6)**: Depends on US3 completion

### User Story Dependencies

```
Setup → Foundational → US1 (local build) → US2 (multi-platform CI) → US3 (auto-publish)
```

These stories are **sequential** because each builds on the previous:
- US1: Setup.py must work locally before CI
- US2: Multi-platform CI needs working setup.py from US1
- US3: Auto-publish needs working CI from US2

### Parallel Opportunities

**Within Phase 1 (Setup)**:
```
T002 (setup.py) || T003 (MANIFEST.in)  # Can run in parallel
```

**Within Phase 4 (US2)**:
```
T018 (Linux config) || T019 (macOS config) || T020 (Windows config)  # Independent arch configs
```

**Within Phase 6 (Polish)**:
```
T034 (CHANGELOG) || T035 (README)  # Documentation updates
T039 (Linux test) || T040 (macOS test) || T041 (Windows test)  # Platform tests
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T008)
3. Complete Phase 3: US1 (T009-T015)
4. **STOP and VALIDATE**: Local wheel builds with compiled modules
5. Can release as test version if needed

### Full Release

1. Complete US1 → Local build works
2. Complete US2 → CI builds for all platforms
3. Complete US3 → Auto-publish on tag
4. Complete Polish → Release v2.6.0

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 42 |
| **Phase 1 (Setup)** | 4 tasks |
| **Phase 2 (Foundational)** | 4 tasks |
| **Phase 3 (US1)** | 7 tasks |
| **Phase 4 (US2)** | 10 tasks |
| **Phase 5 (US3)** | 8 tasks |
| **Phase 6 (Polish)** | 9 tasks |
| **Parallel Opportunities** | 8 tasks |
| **MVP Scope** | T001-T015 (Setup + Foundational + US1) |

---

## Notes

- No automated tests - manual verification at each checkpoint
- Sequential user stories (each builds on previous)
- Local verification (US1) before CI setup (US2)
- Keep existing source distribution on PyPI for old versions
- New versions (v2.6.0+) will be binary-only
