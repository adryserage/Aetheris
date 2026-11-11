# Implementation Tasks: Migration Gemini CLI & Intégration Skills

**Branch**: `015-gemini-cli-skills` | **Date**: 2026-01-09
**Target Version**: v3.0 | **Depends On**: v3.0, v3.1, v3.2
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

> ⚠️ **Note**: Cette spec ne peut être implémentée qu'après v3.0 (Config), v3.1 (Security), v3.2 (Headless)

## Summary

| Phase | Tasks | Priority | Status |
|-------|-------|----------|--------|
| 1. CLI Interactive Mode | 8 | P1 | ⬜ Pending |
| 2. Command Registry & Autocomplete | 6 | P1 | ⬜ Pending |
| 3. Base Skills | 7 | P1 | ⬜ Pending |
| 4. Claude Adapter | 4 | P1 | ⬜ Pending |
| 5. Gemini Adapter | 4 | P1 | ⬜ Pending |
| 6. Conductor | 7 | P2 | ⬜ Pending |
| 7. MCP Integration | 9 | P2 | ⬜ Pending |
| 8. Custom Skill Registry | 5 | P3 | ⬜ Pending |
| 9. Documentation Update | 6 | P1 | ⬜ Pending |
| 10. Testing & Polish | 6 | P1 | ⬜ Pending |
| **Total** | **62** | | |

---

## Phase 1: CLI Interactive Mode (P1)

### T001: Add --cli flag to main CLI
- [x] Modify `src/cli.py` to add `--cli` / `-c` option
- [x] Ensure backward compatibility (all existing commands unchanged)
- **FR**: FR-028, FR-029
- **Files**: `src/cli.py`

### T002: Create CLI module structure
- [x] Create `src/cli/__init__.py`
- [x] Create `src/cli/interactive.py` skeleton
- [x] Export public interfaces
- **Files**: `src/cli/__init__.py`, `src/cli/interactive.py`

### T003: Implement InteractiveSession class
- [x] Create `InteractiveSession` class with prompt_toolkit
- [x] Implement main REPL loop
- [x] Handle Ctrl+C graceful exit
- **FR**: FR-038
- **Files**: `src/cli/interactive.py`

### T004: Add provider indicator to prompt
- [x] Display current provider in prompt: `aetheris[gemini]>`
- [x] Support provider switching (placeholder for v2.9)
- **US**: US2-1
- **Files**: `src/cli/interactive.py`

### T005: Implement /exit command
- [x] Handle `/exit` command
- [x] Clean up resources on exit
- [x] Display goodbye message
- **FR**: FR-038
- **Files**: `src/cli/interactive.py`

### T006: Add prompt_toolkit dependency
- [x] Add `prompt_toolkit>=3.0.0` to requirements.txt
- [x] Test import on all platforms
- **Files**: `requirements.txt`

### T007: Implement command parsing
- [x] Parse `/command -arguments` syntax
- [x] Handle quoted arguments with shlex
- [x] Support special characters
- **Edge Case**: Caractères spéciaux/quotes
- **Files**: `src/cli/interactive.py`

### T008: Test CLI interactive mode
- [x] Create `tests/unit/test_cli_interactive.py`
- [x] Test REPL startup and exit
- [x] Test command parsing
- **Files**: `tests/unit/test_cli_interactive.py`

---

## Phase 2: Command Registry & Autocomplete (P1)

### T009: Create CommandRegistry class
- [x] Create `src/cli/command_registry.py`
- [x] Implement `Command` and `Argument` dataclasses
- [x] Implement provider-specific command lists
- **Entity**: CommandRegistry, Command
- **Files**: `src/cli/command_registry.py`

### T010: Register built-in Aetheris commands
- [x] Register `/analysis`, `/fix`, `/pr`, `/issues`, `/help`, `/exit`
- [x] Include descriptions and arguments
- **Files**: `src/cli/command_registry.py`

### T011: Register Claude-specific commands
- [x] Parse Claude Code CLI help output
- [x] Register commands like `/commit`, `/review`, etc.
- **US**: US2-5
- **Files**: `src/cli/command_registry.py`

### T012: Register Gemini-specific commands
- [x] Parse Gemini CLI help output
- [x] Register Gemini-specific commands
- **US**: US2-6
- **Files**: `src/cli/command_registry.py`

### T013: Implement CommandCompleter
- [x] Create `src/cli/autocomplete.py`
- [x] Implement `CommandCompleter` with prompt_toolkit
- [x] Filter by current provider
- [x] Autocomplete within 100ms (SC-007)
- **FR**: FR-031, FR-032, FR-033
- **Files**: `src/cli/autocomplete.py`

### T014: Implement similar command suggestions
- [x] Add Levenshtein distance calculation
- [x] Suggest commands with distance ≤2
- [x] Display suggestions on unknown command
- **FR**: FR-035
- **Edge Case**: Commande inexistante
- **Files**: `src/cli/autocomplete.py`

---

## Phase 3: Base Skills (P1)

### T015: Create skills module structure
- [x] Create `src/skills/__init__.py`
- [x] Create `src/skills/base_skill.py`
- [x] Define `Skill`, `SkillParameter`, `SkillResult` dataclasses
- **Entity**: Skill, SkillParameter, SkillResult
- **Files**: `src/skills/__init__.py`, `src/skills/base_skill.py`

### T016: Implement read_file skill
- [x] Create `src/skills/file_skills.py`
- [x] Implement `ReadFileSkill` class
- [x] Add path validation (sandboxing)
- **FR**: FR-006
- **Files**: `src/skills/file_skills.py`

### T017: Implement write_file skill
- [x] Implement `WriteFileSkill` class
- [x] Add safe mode confirmation prompt
- [x] Support overwrite/append modes
- **FR**: FR-007, FR-010
- **Files**: `src/skills/file_skills.py`

### T018: Implement search_files skill
- [x] Implement `SearchFilesSkill` class
- [x] Support glob patterns
- [x] Support content regex search
- **FR**: FR-009
- **Files**: `src/skills/file_skills.py`

### T019: Implement execute_command skill
- [x] Create `src/skills/shell_skill.py`
- [x] Implement `ExecuteCommandSkill` class
- [x] Add timeout support
- [x] Add safe mode confirmation
- **FR**: FR-008, FR-010
- **Files**: `src/skills/shell_skill.py`

### T020: Implement path sandboxing
- [x] Create sandbox validation in base skill
- [x] Restrict to project directory by default
- [x] Add `--unsafe` flag to disable
- **Edge Case**: Skill accède à fichier hors projet
- **Files**: `src/skills/base_skill.py`

### T021: Create SkillRegistry
- [x] Create `src/skills/registry.py`
- [x] Implement skill registration
- [x] Implement enabled/disabled skills list
- **Entity**: SkillRegistry
- **FR**: FR-024
- **Files**: `src/skills/registry.py`

---

## Phase 4: Claude Adapter (P1)

### T022: Create adapters module structure
- [x] Create `src/skills/adapters/__init__.py`
- [x] Create `src/skills/adapters/base_adapter.py`
- [x] Define `SkillAdapter` abstract class
- **Entity**: SkillAdapter
- **Files**: `src/skills/adapters/__init__.py`, `src/skills/adapters/base_adapter.py`

### T023: Implement ClaudeAdapter.to_api_format
- [x] Create `src/skills/adapters/claude_adapter.py`
- [x] Convert `Skill` to Claude tool definition format
- [x] Generate JSON Schema for input_schema
- **Files**: `src/skills/adapters/claude_adapter.py`

### T024: Implement ClaudeAdapter.parse_response
- [x] Parse `tool_use` blocks from response
- [x] Extract skill name and arguments
- [x] Return list of `SkillCall` objects
- **Files**: `src/skills/adapters/claude_adapter.py`

### T025: Implement ClaudeAdapter.format_result
- [x] Format `SkillResult` as `tool_result`
- [x] Handle success and error cases
- **Files**: `src/skills/adapters/claude_adapter.py`

---

## Phase 5: Gemini Adapter (P1)

### T026: Implement GeminiAdapter.to_api_format
- [x] Create `src/skills/adapters/gemini_adapter.py`
- [x] Convert `Skill` to Gemini function declaration
- [x] Use google-genai function calling format
- **FR**: FR-011
- **Files**: `src/skills/adapters/gemini_adapter.py`

### T027: Implement GeminiAdapter.parse_response
- [x] Parse `function_call` from response candidates
- [x] Handle multiple function calls
- [x] Return list of `SkillCall` objects
- **FR**: FR-013
- **Files**: `src/skills/adapters/gemini_adapter.py`

### T028: Implement GeminiAdapter.format_result
- [x] Format `SkillResult` as `function_response`
- [x] Handle structured return data
- **Files**: `src/skills/adapters/gemini_adapter.py`

### T029: Test adapter parity
- [x] Create `tests/unit/test_adapters.py`
- [x] Test identical behavior for same skills
- [x] Verify SC-002 (±5% success rate)
- **SC**: SC-002, SC-006
- **Files**: `tests/unit/test_adapters.py`

---

## Phase 6: Conductor (P2)

### T030: Create conductor module structure
- [x] Create `src/conductor/__init__.py`
- [x] Create `src/conductor/planner.py`
- [x] Create `src/conductor/executor.py`
- **Files**: `src/conductor/__init__.py`, `src/conductor/planner.py`, `src/conductor/executor.py`

### T031: Implement ExecutionPlan dataclass
- [x] Create `PlanStep` dataclass
- [x] Create `ExecutionPlan` dataclass
- [x] Add validation (max 20 steps, valid deps)
- **Entity**: ExecutionPlan, PlanStep
- **NFR**: NFR-003
- **Files**: `src/conductor/planner.py`

### T032: Implement Planner.create_plan
- [x] Create planning prompt template
- [x] Call Gemini with structured output
- [x] Parse JSON plan response
- [x] Validate plan structure
- **FR**: FR-014, FR-015
- **Files**: `src/conductor/planner.py`

### T033: Implement CycleDetector
- [x] Create `src/conductor/cycle_detector.py`
- [x] Implement state hashing
- [x] Detect cycles (same state 2x)
- **Edge Case**: Boucle infinie
- **Files**: `src/conductor/cycle_detector.py`

### T034: Implement Executor.execute_plan
- [x] Execute steps in dependency order
- [x] Track step status and results
- [x] Handle step failures
- **FR**: FR-016, FR-017
- **Files**: `src/conductor/executor.py`

### T035: Implement verbose progress display
- [x] Display plan table with Rich
- [x] Update status in real-time
- [x] Show step details on completion
- **FR**: FR-018
- **Files**: `src/conductor/executor.py`

### T036: Test Conductor
- [x] Create `tests/unit/test_conductor.py`
- [x] Test planning with mock Gemini
- [x] Test cycle detection
- [x] Test execution with mock skills
- **SC**: SC-003
- **Files**: `tests/unit/test_conductor.py`

---

## Phase 7: MCP Integration (P2)

### T037: Create MCP module structure
- [x] Create `src/mcp/__init__.py`
- [x] Create `src/mcp/client.py`
- [x] Create `src/mcp/discovery.py`
- **Files**: `src/mcp/__init__.py`, `src/mcp/client.py`, `src/mcp/discovery.py`

### T038: Add MCP dependency
- [x] Add `mcp>=0.9.0` to requirements.txt (when available)
- [x] Or implement JSON-RPC client manually
- **Files**: `requirements.txt`

### T039: Implement MCPClient.connect
- [x] Spawn server process
- [x] Send initialize request
- [x] Store capabilities
- [x] Connection timeout <2s (SC-004)
- **FR**: FR-019
- **SC**: SC-004
- **Files**: `src/mcp/client.py`

### T040: Implement tool/resource discovery
- [x] Send tools/list request
- [x] Send resources/list request
- [x] Store discovered items
- **FR**: FR-020
- **Files**: `src/mcp/discovery.py`

### T041: Implement MCPToolBridge
- [x] Create `src/mcp/skill_bridge.py`
- [x] Convert MCPTool to Skill
- [x] Execute via MCP client
- **FR**: FR-021
- **Files**: `src/mcp/skill_bridge.py`

### T042: Handle MCP conflicts
- [x] Detect name conflicts with built-in skills
- [x] Apply priority rules (built-in first by default)
- [x] Support `override_builtins` config
- **Edge Case**: Conflit nom skill MCP vs intégré
- **Files**: `src/mcp/skill_bridge.py`

### T043: Handle MCP connection loss
- [x] Implement retry with exponential backoff
- [x] Continue without MCP on failure
- [x] Auto-reconnect when available
- **FR**: FR-023
- **Edge Case**: Connexion MCP perdue
- **Files**: `src/mcp/client.py`

### T044: Test MCP integration
- [x] Create `tests/unit/test_mcp_client.py`
- [x] Test with mock MCP server
- [x] Test connection failure handling
- **Files**: `tests/unit/test_mcp_client.py`

### T044b: Implement MCP resources as analysis context
- [x] Fetch resources from connected MCP servers
- [x] Include resource content in analysis prompts
- [x] Handle resource read failures gracefully
- **FR**: FR-022
- **US**: US6-3
- **Files**: `src/mcp/discovery.py`, `src/core/analyzer.py`

---

## Phase 8: Custom Skill Registry (P3)

### T045: Implement skill definition loader
- [x] Load YAML skill definitions from custom path
- [x] Validate schema
- [x] Report errors clearly
- **FR**: FR-025, FR-026
- **Files**: `src/skills/registry.py`

### T046: Implement command-based skills
- [x] Parse `command` field in skill definition
- [x] Execute command with parameter substitution
- [x] Return command output as result
- **Files**: `src/skills/registry.py`

### T047: Add custom skills path config
- [x] Read `skills.custom_skills_path` from config.json
- [x] Default to `./aetheris-skills/`
- **Files**: `src/skills/registry.py`, `src/core/config.py`

### T048: Document skill definition format
- [x] Add skill definition schema to docs
- [x] Provide example skills
- **FR**: FR-027
- **SC**: SC-005
- **Files**: `docs/skills/custom-skills.md`

### T049: Test custom skill loading
- [x] Create test skill definitions
- [x] Test valid/invalid definitions
- [x] Test execution
- **Files**: `tests/unit/test_custom_skills.py`

---

## Phase 9: Documentation Update (P1)

### T050: Create CLI interactive mode documentation
- [x] Create `docs/cli-interactive.md` with full usage guide
- [x] Document all commands and shortcuts
- [x] Add examples and use cases
- **Files**: `docs/cli-interactive.md`

### T051: Create Skills documentation
- [x] Create `docs/skills/README.md` with skills overview
- [x] Create `docs/skills/builtin-skills.md` listing all built-in skills
- [x] Create `docs/skills/custom-skills.md` with custom skill guide
- **Files**: `docs/skills/README.md`, `docs/skills/builtin-skills.md`, `docs/skills/custom-skills.md`

### T052: Create MCP integration documentation
- [x] Create `docs/mcp-integration.md` with setup guide
- [x] Document MCP server configuration
- [x] Add troubleshooting section
- **Files**: `docs/mcp-integration.md`

### T053: Update docs/commands/README.md
- [x] Add CLI interactive mode section
- [x] Add skills command reference
- [x] Update command table with v3.0 commands
- **Files**: `docs/commands/README.md`

### T054: Update README.md for v3.0
- [x] Add multi-provider section
- [x] Add CLI interactive mode section
- [x] Add Skills documentation links
- [x] Update feature table
- [x] Update roadmap to mark v3.0 as implemented
- **Files**: `README.md`

### T055: Add CHANGELOG.md entry for v3.0
- [x] Document all new features
- [x] Document breaking changes if any
- [x] Add migration notes
- **Files**: `CHANGELOG.md`

---

## Phase 10: Testing & Polish (P1)

### T056: Integration test - CLI interactive
- [x] Create `tests/integration/test_cli_interactive.py`
- [x] Test full REPL session
- [x] Test command passthrough
- **Files**: `tests/integration/test_cli_interactive.py`

### T057: Integration test - Skill execution
- [x] Create `tests/integration/test_skill_execution.py`
- [x] Test skills with real files
- [x] Test safe mode prompts
- **Files**: `tests/integration/test_skill_execution.py`

### T058: Backward compatibility tests
- [x] Test all existing commands unchanged
- [x] Test `aetheris analysis` without --cli
- [x] Test `aetheris fix --auto`
- **FR**: FR-029
- **US**: US2-9
- **Files**: `tests/integration/test_backward_compat.py`

### T059: Update CLI help text
- [x] Add --cli description
- [x] Document new flags
- [x] Update --help output
- **Files**: `src/cli.py`

### T060: Add config.json schema for v3.0
- [x] Add `cli.*` section
- [x] Add `skills.*` section
- [x] Add `mcp.*` section
- **Files**: `src/core/config.py`

### T061: Final validation
- [x] Run full test suite
- [x] Run lint and typecheck
- [x] Verify all SC metrics
- [x] Update pyproject.toml version to 3.0.0
- [x] Tag release v3.0.0

---

## Dependencies Graph

```
Phase 1 (CLI) ──────────────────────────────────────────────┐
      │                                                     │
      ▼                                                     │
Phase 2 (Registry) ─────────────────────────────────────────┤
      │                                                     │
      ▼                                                     │
Phase 3 (Skills) ───────────────────────────────────────────┤
      │                                                     │
      ├─────────────┬─────────────┐                         │
      ▼             ▼             ▼                         │
Phase 4       Phase 5       Phase 6                         │
(Claude)      (Gemini)      (Conductor)                     │
      │             │             │                         │
      └─────────────┴─────────────┘                         │
                    │                                       │
                    ▼                                       │
              Phase 7 (MCP) ────────────────────────────────┤
                    │                                       │
                    ▼                                       │
              Phase 8 (Custom) ─────────────────────────────┤
                    │                                       │
                    ▼                                       │
              Phase 9 (Docs) ───────────────────────────────┤
                                                            │
                                                            ▼
                                                    Phase 10 (Polish)
```

## Estimation

| Phase | Complexity | Est. LOC |
|-------|------------|----------|
| 1. CLI Interactive | Medium | ~300 |
| 2. Command Registry | Low | ~200 |
| 3. Base Skills | Medium | ~400 |
| 4. Claude Adapter | Low | ~150 |
| 5. Gemini Adapter | Low | ~150 |
| 6. Conductor | High | ~400 |
| 7. MCP Integration | High | ~350 |
| 8. Custom Registry | Medium | ~200 |
| 9. Documentation | Low | ~150 |
| 10. Testing | Medium | ~500 |
| **Total** | | **~2800** |
