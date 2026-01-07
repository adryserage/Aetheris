# Implementation Plan: README Safety & Trust Documentation

**Branch**: `011-readme-safety-docs` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-readme-safety-docs/spec.md`
**Target Version**: v3.0.4

## Summary

Add two new sections to README.md to improve user trust: "Safety & Execution Model" explaining what Aetheris does and its boundaries, and "Fix Guarantees" listing explicit promises and limitations. This is a documentation-only change.

## Technical Context

**Language/Version**: Markdown
**Primary Dependencies**: None (documentation only)
**Storage**: N/A
**Testing**: Manual review, markdown linting
**Target Platform**: GitHub README rendering
**Project Type**: Documentation
**Performance Goals**: N/A
**Constraints**: Must fit README structure; maintain readability
**Scale/Scope**: ~100-150 lines of markdown
**Depends On**: v3.0.3 (Safety Profiles), v3.0 (Persistent Config)

## Configuration & Profile Integration

The Safety documentation must reference:

1. **Safety Profiles** (v3.0.3): `--profile safe|ci|yolo`
2. **Config.json Settings** (v3.0): `safety.default_profile`, `safety.custom_allowlist`
3. **Configuration Hierarchy**: CLI > config.json > defaults

Document how users can:
- Set default profile via config.json
- Customize allowlist for safe mode
- Configure audit logging path for CI mode

## Constitution Check

*GATE: Documentation feature - minimal constitution impact*

| Principle | Status | Notes |
|-----------|--------|-------|
| Library-First | N/A | Documentation only |
| CLI Interface | ✅ Pass | Documents CLI behavior |
| Observability | ✅ Pass | Improves transparency |
| Simplicity | ✅ Pass | Clear, focused sections |

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/011-readme-safety-docs/
├── plan.md              # This file
├── research.md          # N/A - no research needed
├── data-model.md        # N/A - no data model
├── quickstart.md        # N/A - no quickstart
└── tasks.md             # Phase 2 output
```

### Files to Modify

```text
README.md                # ADD: Safety & Execution Model section
                         # ADD: Fix Guarantees section
pyproject.toml           # UPDATE: version to 3.0.4
```

## Content Structure

### Placement in README

Current README structure (relevant sections):
```
1. Title & Badges
2. Why Aetheris?
3. Roadmap
4. Quick Start
5. Commands
   └── aetheris fix (line 218)
6. Features
...
```

**Insertion Point**: After "Commands" section, before "Features" section.

This placement ensures:
- Users see safety info after learning what commands do
- Safety context before diving into feature details
- Natural reading flow: What → How → Safety → Details

### Section Outlines

#### Safety & Execution Model Section

```markdown
## 🔒 Safety & Execution Model

### Local-Only by Default
- No cloud services
- No telemetry
- Your code never leaves your machine

### Safety Profiles
- `--profile safe` (default): Conservative guardrails
- `--profile ci`: Strict CI/CD mode with audit logging
- `--profile yolo`: Full autonomy (requires explicit confirmation)

### Execution Boundaries
- What commands `fix` can run
- Where they run (subprocess, same process)
- Permission model

### The `--dangerously-skip-permissions` Flag
- What it does: bypasses permission checks
- Why it's dangerous: unrestricted command execution
- When to use: never in production; only testing

### Configuring Safety via config.json
- Set default profile: `"safety": {"default_profile": "safe"}`
- Custom allowlist for commands
- Audit log path configuration

### Running Safely
- Docker example (sandboxed)
- Using safe profile
- Recommended practices
```

#### Fix Guarantees Section

```markdown
## ✅ Fix Guarantees

### What We Guarantee
- ✅ Never force-push to remote
- ✅ Always run tests (unless disabled)
- ✅ Creates a branch per bug fix
- ✅ Atomic commits with clear messages

### What We Don't Guarantee
- ⚠️ May fail (will not silently continue)
- ⚠️ Does not guarantee all bugs found
- ⚠️ Fixes may need manual review
- ⚠️ Not a replacement for human review
```

## Research Summary

No external research needed - this is internal documentation of existing behavior.

Key sources:
- Existing `fix` command code in `src/cli.py`
- Current behavior documentation in `docs/commands/fix.md`
- User feature request for trust documentation

## Next Steps

1. Generate tasks.md with implementation tasks
2. Write the markdown sections
3. Update version in pyproject.toml
4. Review and merge
