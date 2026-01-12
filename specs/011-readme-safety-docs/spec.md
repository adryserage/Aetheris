# Feature Specification: README Safety & Trust Documentation

**Feature Branch**: `011-readme-safety-docs`
**Created**: 2026-01-07
**Status**: Draft
**Target Version**: v2.12
**Input**: User description: "Add Safety & Execution Model section and Fix Guarantees section to README to improve user trust"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Understand Safety Model Before Using Fix Command (Priority: P1)

As a potential user evaluating Aetheris, I want to understand exactly what the `fix` command does and its safety boundaries so that I can decide if it's safe to run on my codebase.

**Why this priority**: Trust is the primary barrier to adoption. Users need confidence before running any automated code modification tool.

**Independent Test**: Can be fully tested by reading the README and answering: "What does fix do? What are the boundaries? Is it safe?"

**Acceptance Scenarios**:

1. **Given** a user reads the README, **When** they look for safety information, **Then** they find a clearly labeled "Safety & Execution Model" section
2. **Given** a user reads the Safety section, **When** they want to understand execution boundaries, **Then** they see that Aetheris is local-only by default
3. **Given** a user reads the Safety section, **When** they want to understand `fix` behavior, **Then** they see exactly what boundary commands run within
4. **Given** a user reads the Safety section, **When** they see `--dangerously-skip-permissions`, **Then** they understand what it does and why it's dangerous

---

### User Story 2 - Learn How to Run Fix Safely (Priority: P1)

As a security-conscious developer, I want to see recommended safe usage patterns so that I can use the fix command with minimal risk.

**Why this priority**: Actionable guidance converts cautious evaluators into users.

**Independent Test**: Can be fully tested by following the documented safe usage examples (Docker, restricted mode).

**Acceptance Scenarios**:

1. **Given** a user wants to run fix safely, **When** they read the Safety section, **Then** they find a Docker example for sandboxed execution
2. **Given** a user wants to limit fix scope, **When** they read the Safety section, **Then** they find restricted mode instructions
3. **Given** a user follows the safe usage guidance, **When** they execute fix, **Then** the documented boundaries are enforced

---

### User Story 3 - Understand Fix Command Guarantees (Priority: P2)

As a developer integrating Aetheris into my workflow, I want to know what the fix command guarantees and what it doesn't so that I can set appropriate expectations.

**Why this priority**: Clear guarantees prevent misuse and reduce support burden.

**Independent Test**: Can be fully tested by reading the Fix Guarantees section and verifying claims against behavior.

**Acceptance Scenarios**:

1. **Given** a user reads the Fix Guarantees section, **When** they look for positive guarantees, **Then** they see: never force-push, always run tests (unless disabled), creates branch per bug
2. **Given** a user reads the Fix Guarantees section, **When** they look for limitations, **Then** they see: may fail, will not silently ship changes
3. **Given** a user reads the Fix Guarantees section, **When** they want to verify guarantees, **Then** they can observe the documented behavior in practice

---

### Edge Cases

- What happens when users skim the README? → Section headers are descriptive enough to convey safety posture
- What happens when users copy-paste examples blindly? → Examples are safe by default; dangerous flags require explicit action
- What happens when the fix behavior changes? → Version the guarantees section; update when behavior changes

## Requirements *(mandatory)*

### Functional Requirements

#### Safety & Execution Model Section

- **FR-001**: README MUST include a "Safety & Execution Model" section with clear heading
- **FR-002**: Section MUST state that Aetheris is local-only by default (no cloud, no telemetry)
- **FR-003**: Section MUST describe the execution boundary for the `fix` command
- **FR-004**: Section MUST explain what `--dangerously-skip-permissions` does
- **FR-005**: Section MUST explain why `--dangerously-skip-permissions` is dangerous
- **FR-006**: Section MUST provide a Docker example for sandboxed execution
- **FR-007**: Section MUST describe restricted mode usage (if available)

#### Fix Guarantees Section

- **FR-010**: README MUST include a "Fix Guarantees" section with clear heading
- **FR-011**: Section MUST list positive guarantees (what fix WILL do)
- **FR-012**: Section MUST include guarantee: "Never force-push to remote"
- **FR-013**: Section MUST include guarantee: "Always run tests before applying changes (unless explicitly disabled)"
- **FR-014**: Section MUST include guarantee: "Creates a separate branch per bug fix"
- **FR-015**: Section MUST list limitations (what fix does NOT guarantee)
- **FR-016**: Section MUST include limitation: "May fail; will not silently ship changes"
- **FR-017**: Section MUST include limitation: "Does not guarantee all bugs are found or fixed"

#### Documentation Quality

- **FR-020**: All documentation MUST be clear enough for first-time users
- **FR-021**: Examples MUST be copy-paste ready and safe by default
- **FR-022**: Dangerous options MUST be visually distinguished (warning icons, bold text)

### Key Entities

- **Safety Section**: A README section explaining execution model and boundaries
- **Guarantees Section**: A README section listing what fix does and doesn't guarantee
- **Dangerous Flag**: A CLI flag that bypasses safety checks with explicit naming

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can find safety information within 30 seconds of opening README
- **SC-002**: Safety section answers the 3 key questions: What runs? Where? With what permissions?
- **SC-003**: Guarantees section lists at least 3 positive guarantees and 2 limitations
- **SC-004**: Docker example is complete and runnable without modification
- **SC-005**: No user needs to ask "is this safe?" after reading the documentation

## Scope & Boundaries

### In Scope

- README.md modifications only
- Safety & Execution Model section
- Fix Guarantees section
- Safe usage examples (Docker, restricted mode)
- Version bump to 3.0.4

### Out of Scope

- Code changes to fix command behavior
- New CLI flags or features
- Website or external documentation updates
- Translations

## Assumptions

- Current fix command behavior matches the documented guarantees
- Docker is a reasonable sandboxing recommendation for most users
- Users read READMEs before running potentially dangerous commands
- The existing README structure allows for new sections without major reorganization

## Clarifications

### Session 2026-01-07

- No critical ambiguities detected - specification is complete for documentation feature
