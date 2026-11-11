# Feature Specification: Safety Profiles

**Feature Branch**: `010-safety-profiles`
**Created**: 2026-01-07
**Status**: Draft
**Target Version**: v2.12
**Input**: User description: "Safety Profiles - Configurable execution boundaries with 3 profiles (safe, ci, yolo) for controlling analysis behavior and risk levels"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run Analysis in Safe Mode (Priority: P1)

As a developer working on a production codebase, I want to run Aetheris analysis with strict safety boundaries so that automated operations cannot cause unintended damage to my code or environment.

**Why this priority**: This is the primary use case - protecting users from unintended consequences. Safe mode should be the recommended default for users who want guardrails.

**Independent Test**: Can be fully tested by running `aetheris analysis --profile safe` on any codebase and verifying all safety constraints are enforced.

**Acceptance Scenarios**:

1. **Given** a user runs analysis with `--profile safe`, **When** the analysis attempts to make network calls, **Then** the network request is blocked and logged
2. **Given** a user runs analysis with `--profile safe`, **When** proposed changes exceed the bounded diff size, **Then** the changes are rejected with a clear explanation
3. **Given** a user runs analysis with `--profile safe`, **When** a repair loop is initiated, **Then** the system stops after maximum 3 iterations regardless of completion status
4. **Given** a user runs analysis with `--profile safe`, **When** analysis proposes a command not in the allowlist, **Then** the command is blocked and the user is notified
5. **Given** a user runs analysis with `--profile safe`, **When** any code changes are proposed, **Then** the mandatory test step is executed before changes are finalized

---

### User Story 2 - Run Analysis in CI/CD Pipeline (Priority: P1)

As a DevOps engineer, I want to run Aetheris analysis in my CI/CD pipeline with strict, non-interactive behavior so that builds fail fast on issues and provide audit trails.

**Why this priority**: CI/CD integration is essential for automated workflows. CI mode must be deterministic and auditable.

**Independent Test**: Can be fully tested by running `aetheris analysis --profile ci` in a headless environment and verifying no prompts appear and logs are generated.

**Acceptance Scenarios**:

1. **Given** a user runs analysis with `--profile ci`, **When** an error occurs, **Then** the analysis fails immediately with a non-zero exit code
2. **Given** a user runs analysis with `--profile ci`, **When** a decision point is reached that would normally prompt the user, **Then** the system uses a safe default or fails rather than waiting for input
3. **Given** a user runs analysis with `--profile ci`, **When** analysis completes, **Then** a detailed audit log is written with all actions taken, decisions made, and outcomes
4. **Given** a user runs analysis with `--profile ci`, **When** the terminal is not interactive (no TTY), **Then** the analysis runs without requiring any user interaction

---

### User Story 3 - Run Analysis with Full Autonomy (Priority: P2)

As an experienced developer who understands the risks, I want to run Aetheris with extended capabilities for large-scale refactoring tasks when I explicitly opt in.

**Why this priority**: This is an advanced feature for power users. It must require explicit opt-in and clear warning acknowledgment.

**Independent Test**: Can be fully tested by running `aetheris analysis --profile yolo` and verifying extended capabilities are enabled with appropriate warnings.

**Acceptance Scenarios**:

1. **Given** a user runs analysis with `--profile yolo`, **When** the profile is activated, **Then** a clear warning about increased risk is displayed and acknowledged
2. **Given** a user runs analysis with `--profile yolo`, **When** the analysis needs external resources, **Then** network access is permitted
3. **Given** a user runs analysis with `--profile yolo`, **When** large-scale refactoring is proposed, **Then** the changes are allowed without bounded diff size restrictions
4. **Given** a user runs analysis with `--profile yolo`, **When** repair loops are needed, **Then** extended iteration limits are applied (beyond the safe mode limit)

---

### User Story 4 - Configure Default Profile (Priority: P3)

As a team lead, I want to set a default safety profile for my project so that all team members use consistent safety settings without having to specify them each time.

**Why this priority**: Improves team consistency and reduces configuration burden, but is not essential for core functionality.

**Independent Test**: Can be fully tested by setting a default profile in configuration and running analysis without the `--profile` flag.

**Acceptance Scenarios**:

1. **Given** a project has a default profile configured, **When** a user runs analysis without specifying `--profile`, **Then** the configured default profile is applied
2. **Given** a project has a default profile configured, **When** a user explicitly specifies `--profile`, **Then** the explicit flag overrides the default
3. **Given** no default profile is configured, **When** a user runs analysis without specifying `--profile`, **Then** safe mode is applied as the system default

---

### Edge Cases

- What happens when a user specifies an invalid profile name? → Clear error message listing valid profiles
- What happens when CI mode detects an interactive-only situation? → Fail with descriptive error rather than hang
- What happens when safe mode's test step fails? → Changes are not applied, user is notified of test failures
- What happens when the allowlist file is missing or malformed? → Use built-in default allowlist, warn user
- What happens when yolo mode is used in CI environment? → Allow but emit strong warning in audit log

## Requirements *(mandatory)*

### Functional Requirements

#### Profile Selection & Configuration

- **FR-001**: System MUST accept a `--profile` flag with values: `safe`, `ci`, or `yolo`
- **FR-002**: System MUST apply `safe` profile as the default when no profile is specified
- **FR-003**: System MUST allow default profile configuration at project level (configuration file)
- **FR-004**: System MUST display the active profile at the start of each analysis run

#### Safe Profile Constraints

- **FR-010**: Safe profile MUST block all outbound network requests during analysis
- **FR-011**: Safe profile MUST validate all proposed commands against a configurable allowlist
- **FR-012**: Safe profile MUST enforce a maximum diff size limit (default: 500 lines changed)
- **FR-013**: Safe profile MUST limit repair/retry loops to maximum 3 iterations
- **FR-014**: Safe profile MUST execute a test validation step before applying any code changes
- **FR-015**: Safe profile MUST reject changes if the mandatory test step fails

#### CI Profile Behavior

- **FR-020**: CI profile MUST exit with non-zero code on any error (fail-fast behavior)
- **FR-021**: CI profile MUST never wait for user input (no interactive prompts)
- **FR-022**: CI profile MUST write a structured audit log of all actions and decisions
- **FR-023**: CI profile MUST detect non-interactive terminals and adjust behavior accordingly
- **FR-024**: CI profile MUST include machine-readable output format option (JSON/structured)

#### Yolo Profile Capabilities

- **FR-030**: Yolo profile MUST display and require acknowledgment of a risk warning before proceeding
- **FR-031**: Yolo profile MUST allow outbound network requests
- **FR-032**: Yolo profile MUST allow changes exceeding the standard diff size limit
- **FR-033**: Yolo profile MUST allow extended repair loop iterations (configurable, default: 10)
- **FR-034**: Yolo profile MUST log all extended operations for traceability

#### Allowlist Management

- **FR-040**: System MUST provide a built-in default command allowlist for safe mode
- **FR-041**: System MUST allow users to customize the command allowlist via configuration
- **FR-042**: System MUST merge user allowlist with built-in allowlist (not replace)
- **FR-043**: System MUST validate allowlist format and warn on malformed entries

### Key Entities

- **Profile**: Represents a named set of execution boundaries (safe, ci, yolo) with specific constraint configurations
- **Allowlist**: A configurable list of permitted commands/operations for safe mode
- **AuditLog**: A record of all actions, decisions, and outcomes during CI mode analysis
- **DiffBoundary**: Configuration defining maximum allowed changes (line count, file count)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can select any of the three profiles with a single command-line flag
- **SC-002**: Safe mode blocks 100% of network requests during analysis execution
- **SC-003**: Safe mode enforces the 3-iteration repair loop limit in all scenarios
- **SC-004**: CI mode completes without any user prompts in headless environments
- **SC-005**: CI mode produces audit logs for 100% of analysis runs
- **SC-006**: Yolo mode displays risk warning before any extended operation begins
- **SC-007**: Profile configuration reduces per-run command complexity (no repeated flags)
- **SC-008**: Error messages for invalid profiles guide users to valid options within 1 message

## Scope & Boundaries

### In Scope

- Three predefined profiles with fixed constraint sets
- Command-line profile selection
- Project-level default profile configuration
- Audit logging for CI mode
- Command allowlist for safe mode
- Risk warnings for yolo mode

### Out of Scope

- Custom user-defined profiles (future enhancement)
- Per-agent profile overrides
- Remote profile management
- Profile-based pricing/licensing
- GUI-based profile configuration

## Assumptions

- Users understand the implications of choosing the yolo profile
- The existing CLI infrastructure supports additional flags
- Audit logs will be written to local filesystem (not remote logging services)
- The test step in safe mode uses the project's existing test command
- Network blocking in safe mode applies to auxiliary services (web search, documentation lookup) but ALLOWS AI provider calls (required for core analysis functionality)

## Clarifications

### Session 2026-01-07

- Q: Should safe mode block AI provider network calls? → A: No - AI calls are essential for analysis. Safe mode blocks auxiliary network (web search, doc lookup) but allows AI provider communication.
