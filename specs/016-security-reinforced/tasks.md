# Implementation Tasks: Sécurité Renforcée & Stratégie Git

**Branch**: `016-security-reinforced` | **Date**: 2026-01-09
**Target Version**: v3.1 | **Depends On**: v3.0
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Summary

| Phase | Tasks | Priority | Status |
|-------|-------|----------|--------|
| 1. Security Profiles | 6 | P1 | ⬜ Pending |
| 2. Git Branch Strategy | 6 | P1 | ⬜ Pending |
| 3. Audit Logging | 5 | P2 | ⬜ Pending |
| 4. Command Allowlist | 4 | P2 | ⬜ Pending |
| 5. CLI Integration | 4 | P1 | ⬜ Pending |
| 6. Testing & Polish | 5 | P1 | ⬜ Pending |
| **Total** | **30** | | |

---

## Phase 1: Security Profiles (P1)

### T001: Create security module structure
- [ ] Create `src/security/__init__.py`
- [ ] Create `src/security/profiles.py` skeleton
- [ ] Export public interfaces
- **Files**: `src/security/__init__.py`, `src/security/profiles.py`

### T002: Implement SecurityProfile dataclass
- [ ] Create `SecurityProfile` dataclass with fields: name, network_blocked, max_diff_lines, allowlist_enabled, interactive
- [ ] Add validation for profile values
- [ ] Define SAFE, CI, UNRESTRICTED presets
- **FR**: FR-001
- **Files**: `src/security/profiles.py`

### T003: Implement ProfileManager class
- [ ] Load profiles from config.json
- [ ] Get current profile based on CLI args or config default
- [ ] Validate profile exists
- **FR**: FR-008, FR-009
- **Files**: `src/security/profiles.py`

### T004: Implement network command detection
- [ ] Create patterns for network commands (curl, wget, pip install, npm install, etc.)
- [ ] Check commands against patterns
- [ ] Block with message in safe profile
- **FR**: FR-002
- **Files**: `src/security/profiles.py`

### T005: Implement diff size validation
- [ ] Count lines in diff before apply
- [ ] Prompt for confirmation if >50 lines in safe profile
- [ ] Auto-approve in ci profile
- **FR**: FR-003
- **Files**: `src/security/profiles.py`

### T006: Test security profiles
- [ ] Create `tests/unit/test_security_profiles.py`
- [ ] Test each profile behavior
- [ ] Test profile loading from config
- **Files**: `tests/unit/test_security_profiles.py`

---

## Phase 2: Git Branch Strategy (P1)

### T007: Create git module structure
- [ ] Create `src/git/__init__.py`
- [ ] Create `src/git/branch_manager.py` skeleton
- [ ] Create `src/git/safety.py` skeleton
- **Files**: `src/git/__init__.py`, `src/git/branch_manager.py`, `src/git/safety.py`

### T008: Implement BranchManager class
- [ ] Check for uncommitted changes
- [ ] Create fix branch with naming convention
- [ ] Switch branches safely
- [ ] Delete branches on cleanup
- **FR**: FR-010, FR-011, FR-012, FR-013
- **Files**: `src/git/branch_manager.py`

### T009: Implement fix branch lifecycle
- [ ] Create branch at fix start
- [ ] Track branch status (active, success, failed)
- [ ] Offer merge/keep on success
- [ ] Auto-delete on failure
- **FR**: FR-014
- **Files**: `src/git/branch_manager.py`

### T010: Implement GitSafetyChecker
- [ ] Detect force-push attempts
- [ ] Block operations on main/master
- [ ] Log safety violations
- **FR**: FR-015, FR-016
- **Files**: `src/git/safety.py`

### T011: Handle branch naming conflicts
- [ ] Check if branch exists
- [ ] Generate unique suffix if needed
- [ ] Track all active fix branches
- **Edge Case**: Branche fix existe déjà
- **Files**: `src/git/branch_manager.py`

### T012: Test git branch strategy
- [ ] Create `tests/unit/test_branch_manager.py`
- [ ] Test branch creation/deletion
- [ ] Test safety checks
- [ ] Test conflict handling
- **Files**: `tests/unit/test_branch_manager.py`

---

## Phase 3: Audit Logging (P2)

### T013: Create audit module
- [ ] Create `src/security/audit.py`
- [ ] Implement `AuditEntry` dataclass
- [ ] Implement `AuditLogger` class
- **FR**: FR-017, FR-018
- **Files**: `src/security/audit.py`

### T014: Implement JSONL file writing
- [ ] Open file in append mode
- [ ] Write one JSON line per entry
- [ ] Handle file errors gracefully
- **FR**: FR-019
- **Files**: `src/security/audit.py`

### T015: Implement async logging
- [ ] Queue audit entries
- [ ] Write in background thread
- [ ] Ensure entries are flushed on exit
- **NFR**: NFR-002
- **Files**: `src/security/audit.py`

### T016: Implement aetheris audit command
- [ ] Add `audit` subcommand to CLI
- [ ] Display recent entries in table format
- [ ] Support filtering by date/action
- **FR**: FR-020
- **Files**: `src/cli.py`, `src/security/audit.py`

### T017: Implement log rotation
- [ ] Check entry count on write
- [ ] Archive old file when limit reached
- [ ] Create new file
- **FR**: FR-021, NFR-003
- **Files**: `src/security/audit.py`

---

## Phase 4: Command Allowlist (P2)

### T018: Create allowlist module
- [ ] Create `src/security/allowlist.py`
- [ ] Implement `CommandAllowlist` class
- [ ] Load default allowlist
- **FR**: FR-022
- **Files**: `src/security/allowlist.py`

### T019: Implement command validation
- [ ] Parse command string
- [ ] Match against allowlist patterns
- [ ] Support glob patterns
- **FR**: FR-024
- **Files**: `src/security/allowlist.py`

### T020: Implement custom allowlist loading
- [ ] Read from config.json
- [ ] Merge with defaults
- [ ] Validate pattern syntax
- **FR**: FR-023
- **Files**: `src/security/allowlist.py`

### T021: Implement blocked command messaging
- [ ] Generate helpful error message
- [ ] Suggest how to add to allowlist
- [ ] Log the blocked attempt
- **FR**: FR-025
- **Files**: `src/security/allowlist.py`

---

## Phase 5: CLI Integration (P1)

### T022: Add --profile flag to CLI
- [ ] Add `--profile` option to relevant commands
- [ ] Validate profile name
- [ ] Pass to security module
- **FR**: FR-008
- **Files**: `src/cli.py`

### T023: Integrate branch strategy with fix command
- [ ] Create branch before fix
- [ ] Handle success/failure cleanup
- [ ] Offer merge option
- **US**: US2
- **Files**: `src/cli.py`, `src/commands/fix.py`

### T024: Add security config schema
- [ ] Add `security.*` section to ConfigSchema
- [ ] Add defaults for all security settings
- [ ] Validate on load
- **Files**: `src/core/config.py`

### T025: Add default allowlist file
- [ ] Create `config/default_allowlist.json`
- [ ] Include safe commands (python, pytest, black, etc.)
- [ ] Document each pattern
- **Files**: `config/default_allowlist.json`

---

## Phase 6: Testing & Polish (P1)

### T026: Integration test - Security flow
- [ ] Create `tests/integration/test_security_flow.py`
- [ ] Test full fix with branch isolation
- [ ] Test profile switching
- [ ] Test audit logging
- **Files**: `tests/integration/test_security_flow.py`

### T027: Integration test - Allowlist
- [ ] Test command blocking
- [ ] Test custom allowlist
- [ ] Test unrestricted mode bypass
- **Files**: `tests/integration/test_allowlist.py`

### T028: Update documentation
- [ ] Add security section to README
- [ ] Document profiles and their behaviors
- [ ] Document allowlist configuration
- **Files**: `README.md`, `docs/security.md`

### T029: Update CHANGELOG
- [ ] Document new security features
- [ ] Document breaking changes (none expected)
- [ ] Add migration notes
- **Files**: `CHANGELOG.md`

### T030: Final validation
- [ ] Run full test suite
- [ ] Verify all SC metrics
- [ ] Tag release v3.1.0
- **SC**: SC-001 to SC-006

---

## Dependencies Graph

```
Phase 1 (Profiles) ──────────────────────────────┐
      │                                          │
      ▼                                          │
Phase 2 (Git Branch) ────────────────────────────┤
      │                                          │
      ├─────────────────┬────────────────────────┤
      ▼                 ▼                        │
Phase 3 (Audit)   Phase 4 (Allowlist)            │
      │                 │                        │
      └─────────────────┴────────────────────────┤
                        │                        │
                        ▼                        │
                  Phase 5 (CLI) ─────────────────┤
                        │                        │
                        ▼                        ▼
                  Phase 6 (Testing & Polish)
```

## Estimation

| Phase | Complexity | Est. LOC |
|-------|------------|----------|
| 1. Security Profiles | Medium | ~200 |
| 2. Git Branch Strategy | Medium | ~250 |
| 3. Audit Logging | Low | ~150 |
| 4. Command Allowlist | Low | ~100 |
| 5. CLI Integration | Low | ~100 |
| 6. Testing | Medium | ~300 |
| **Total** | | **~1100** |
