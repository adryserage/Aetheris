# Implementation Plan: Safety Profiles

**Branch**: `010-safety-profiles` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-safety-profiles/spec.md`
**Target Version**: v3.0.3

## Summary

Add configurable safety profiles (`--profile safe|ci|yolo`) to control Aetheris analysis execution boundaries. Each profile defines constraints for network access, diff size limits, repair loop iterations, interactive prompts, and audit logging. Default profile is `safe` with conservative guardrails.

## Technical Context

**Language/Version**: Python 3.9+ (matches existing project)
**Primary Dependencies**: dataclasses, typer (CLI), rich (progress/output), pydantic (validation)
**Storage**: Local filesystem (audit logs, allowlist config)
**Testing**: pytest (existing test framework)
**Target Platform**: Linux, macOS, Windows (cross-platform CLI)
**Project Type**: Single Python package with CLI
**Performance Goals**: No significant overhead from profile checks (<10ms per operation)
**Constraints**: Must not break existing CLI commands; backward compatible
**Scale/Scope**: ~500-700 LOC addition across 5-7 files
**Depends On**: v3.0 (Persistent Config) for config.json integration

## Configuration Integration (v3.0)

Safety profile settings integrate with the config.json system from v3.0:

```json
{
  "safety": {
    "default_profile": "safe",
    "custom_allowlist": [],
    "audit_log_path": "aetheris-audit.jsonl",
    "yolo_requires_flag": true
  }
}
```

### Configuration Hierarchy
1. CLI flags (`--profile`)
2. Local `config.json`
3. Global `~/.aetheris/config.json`
4. Built-in defaults (`safe` profile)

### Settings UI Integration
Add "Safety" tab to `aetheris settings` command with:
- Default profile selection
- Custom allowlist management
- Audit log path configuration
- Yolo confirmation toggle

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Library-First | ✅ Pass | Profile logic in `src/core/profiles.py` as reusable module |
| CLI Interface | ✅ Pass | Exposes `--profile` flag with clear help text |
| Test-First | ✅ Pass | Unit tests for each profile constraint |
| Integration Testing | ✅ Pass | Integration tests for profile + analysis flow |
| Observability | ✅ Pass | Audit logging in CI mode; profile displayed at start |
| Simplicity | ✅ Pass | 3 predefined profiles, no custom profile complexity |

No violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/010-safety-profiles/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A - internal CLI, no external API)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── config.py        # MODIFY: Add profile field to AnalysisConfig
│   ├── profiles.py      # NEW: Profile definitions and constraint logic
│   ├── allowlist.py     # NEW: Command allowlist management
│   ├── audit_log.py     # NEW: Structured audit logging for CI mode
│   └── orchestrator.py  # MODIFY: Apply profile constraints
├── cli.py               # MODIFY: Add --profile flag
└── services/
    └── network_guard.py # NEW: Network access control for safe mode

tests/
├── unit/
│   ├── test_profiles.py     # NEW: Profile constraint tests
│   ├── test_allowlist.py    # NEW: Allowlist validation tests
│   └── test_audit_log.py    # NEW: Audit log format tests
└── integration/
    └── test_profile_flow.py # NEW: End-to-end profile tests

config/
└── default_allowlist.json   # NEW: Built-in command allowlist
```

**Structure Decision**: Single project structure maintained. New files added to `src/core/` for profile-related modules.

## Phase 0: Research Summary

### R1: Network Blocking Implementation

**Decision**: Use a context manager pattern to intercept/block network calls
**Rationale**: Python's `socket` module can be monkey-patched at runtime; context manager ensures clean restore
**Alternatives Rejected**:
- OS-level firewall rules (too invasive, requires privileges)
- Subprocess isolation (adds complexity, platform-specific)

### R2: Audit Log Format

**Decision**: JSON Lines (JSONL) format with ISO timestamps
**Rationale**: Machine-readable, appendable, easy to parse in CI/CD
**Alternatives Rejected**:
- Plain text (not structured)
- SQLite (overkill for append-only logs)

### R3: Allowlist Configuration Format

**Decision**: JSON file with glob patterns for commands
**Rationale**: Consistent with existing config patterns; glob patterns flexible for command matching
**Alternatives Rejected**:
- YAML (adds dependency)
- INI (limited expressiveness)

### R4: Interactive Prompt Detection

**Decision**: Check `sys.stdin.isatty()` and `os.environ.get('CI')`
**Rationale**: Standard approach for CI/CD detection
**Alternatives Rejected**:
- `--no-interactive` flag only (doesn't auto-detect)

### R5: Yolo Warning Acknowledgment

**Decision**: Interactive confirmation prompt with `--yes` flag for non-interactive override
**Rationale**: Explicit user action required; flag allows scripting
**Alternatives Rejected**:
- Environment variable (too hidden)
- Config file only (not explicit enough)

## Phase 1: Design

### Data Model

See [data-model.md](./data-model.md) for full entity definitions.

**Key Entities**:
1. `ProfileType` (Enum): `SAFE`, `CI`, `YOLO`
2. `ProfileConfig` (Dataclass): Constraint values per profile
3. `AuditLogEntry` (Dataclass): Structured log record
4. `AllowlistConfig` (Dataclass): Command patterns and validation

### API Contracts

This feature is CLI-internal; no external API contracts needed.
See [quickstart.md](./quickstart.md) for CLI usage examples.

### Integration Points

| Component | Change Type | Description |
|-----------|-------------|-------------|
| `AnalysisConfig` | Add field | `profile: ProfileType = ProfileType.SAFE` |
| `cli.py` | Add flag | `--profile` with choices `safe`, `ci`, `yolo` |
| `orchestrator.py` | Add checks | Profile constraint validation at execution points |
| `ai_providers.py` | No change | AI calls always allowed (per clarification) |

## Complexity Tracking

No constitution violations to justify.

## Next Steps

1. Generate `research.md` with detailed findings
2. Generate `data-model.md` with entity definitions
3. Generate `quickstart.md` with CLI examples
4. Run `/speckit.tasks` to generate implementation tasks
