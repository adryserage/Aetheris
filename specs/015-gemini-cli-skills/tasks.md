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
- [ ] Modify `src/cli.py` to add `--cli` / `-c` option
- [ ] Ensure backward compatibility (all existing commands unchanged)
- **FR**: FR-028, FR-029
- **Files**: `src/cli.py`

### T002: Create CLI module structure
- [ ] Create `src/cli/__init__.py`
- [ ] Create `src/cli/interactive.py` skeleton
- [ ] Export public interfaces
- **Files**: `src/cli/__init__.py`, `src/cli/interactive.py`

### T003: Implement InteractiveSession class
- [ ] Create `InteractiveSession` class with prompt_toolkit
- [ ] Implement main REPL loop
- [ ] Handle Ctrl+C graceful exit
- **FR**: FR-038
- **Files**: `src/cli/interactive.py`

### T004: Add provider indicator to prompt
- [ ] Display current provider in prompt: `aetheris[gemini]>`
- [ ] Support provider switching (placeholder for v2.9)
- **US**: US2-1
- **Files**: `src/cli/interactive.py`

### T005: Implement /exit command
- [ ] Handle `/exit` command
- [ ] Clean up resources on exit
- [ ] Display goodbye message
- **FR**: FR-038
- **Files**: `src/cli/interactive.py`

### T006: Add prompt_toolkit dependency
- [ ] Add `prompt_toolkit>=3.0.0` to requirements.txt
- [ ] Test import on all platforms
- **Files**: `requirements.txt`

### T007: Implement command parsing
- [ ] Parse `/command -arguments` syntax
- [ ] Handle quoted arguments with shlex
- [ ] Support special characters
- **Edge Case**: Caractères spéciaux/quotes
- **Files**: `src/cli/interactive.py`

### T008: Test CLI interactive mode
- [ ] Create `tests/unit/test_cli_interactive.py`
- [ ] Test REPL startup and exit
- [ ] Test command parsing
- **Files**: `tests/unit/test_cli_interactive.py`

---

## Phase 2: Command Registry & Autocomplete (P1)

### T009: Create CommandRegistry class
- [ ] Create `src/cli/command_registry.py`
- [ ] Implement `Command` and `Argument` dataclasses
- [ ] Implement provider-specific command lists
- **Entity**: CommandRegistry, Command
- **Files**: `src/cli/command_registry.py`

### T010: Register built-in Aetheris commands
- [ ] Register `/analysis`, `/fix`, `/pr`, `/issues`, `/help`, `/exit`
- [ ] Include descriptions and arguments
- **Files**: `src/cli/command_registry.py`

### T011: Register Claude-specific commands
- [ ] Parse Claude Code CLI help output
- [ ] Register commands like `/commit`, `/review`, etc.
- **US**: US2-5
- **Files**: `src/cli/command_registry.py`

### T012: Register Gemini-specific commands
- [ ] Parse Gemini CLI help output
- [ ] Register Gemini-specific commands
- **US**: US2-6
- **Files**: `src/cli/command_registry.py`

### T013: Implement CommandCompleter
- [ ] Create `src/cli/autocomplete.py`
- [ ] Implement `CommandCompleter` with prompt_toolkit
- [ ] Filter by current provider
- [ ] Autocomplete within 100ms (SC-007)
- **FR**: FR-031, FR-032, FR-033
- **Files**: `src/cli/autocomplete.py`

### T014: Implement similar command suggestions
- [ ] Add Levenshtein distance calculation
- [ ] Suggest commands with distance ≤2
- [ ] Display suggestions on unknown command
- **FR**: FR-035
- **Edge Case**: Commande inexistante
- **Files**: `src/cli/autocomplete.py`

---

## Phase 3: Base Skills (P1)

### T015: Create skills module structure
- [ ] Create `src/skills/__init__.py`
- [ ] Create `src/skills/base_skill.py`
- [ ] Define `Skill`, `SkillParameter`, `SkillResult` dataclasses
- **Entity**: Skill, SkillParameter, SkillResult
- **Files**: `src/skills/__init__.py`, `src/skills/base_skill.py`

### T016: Implement read_file skill
- [ ] Create `src/skills/file_skills.py`
- [ ] Implement `ReadFileSkill` class
- [ ] Add path validation (sandboxing)
- **FR**: FR-006
- **Files**: `src/skills/file_skills.py`

### T017: Implement write_file skill
- [ ] Implement `WriteFileSkill` class
- [ ] Add safe mode confirmation prompt
- [ ] Support overwrite/append modes
- **FR**: FR-007, FR-010
- **Files**: `src/skills/file_skills.py`

### T018: Implement search_files skill
- [ ] Implement `SearchFilesSkill` class
- [ ] Support glob patterns
- [ ] Support content regex search
- **FR**: FR-009
- **Files**: `src/skills/file_skills.py`

### T019: Implement execute_command skill
- [ ] Create `src/skills/shell_skill.py`
- [ ] Implement `ExecuteCommandSkill` class
- [ ] Add timeout support
- [ ] Add safe mode confirmation
- **FR**: FR-008, FR-010
- **Files**: `src/skills/shell_skill.py`

### T020: Implement path sandboxing
- [ ] Create sandbox validation in base skill
- [ ] Restrict to project directory by default
- [ ] Add `--unsafe` flag to disable
- **Edge Case**: Skill accède à fichier hors projet
- **Files**: `src/skills/base_skill.py`

### T021: Create SkillRegistry
- [ ] Create `src/skills/registry.py`
- [ ] Implement skill registration
- [ ] Implement enabled/disabled skills list
- **Entity**: SkillRegistry
- **FR**: FR-024
- **Files**: `src/skills/registry.py`

---

## Phase 4: Claude Adapter (P1)

### T022: Create adapters module structure
- [ ] Create `src/skills/adapters/__init__.py`
- [ ] Create `src/skills/adapters/base_adapter.py`
- [ ] Define `SkillAdapter` abstract class
- **Entity**: SkillAdapter
- **Files**: `src/skills/adapters/__init__.py`, `src/skills/adapters/base_adapter.py`

### T023: Implement ClaudeAdapter.to_api_format
- [ ] Create `src/skills/adapters/claude_adapter.py`
- [ ] Convert `Skill` to Claude tool definition format
- [ ] Generate JSON Schema for input_schema
- **Files**: `src/skills/adapters/claude_adapter.py`

### T024: Implement ClaudeAdapter.parse_response
- [ ] Parse `tool_use` blocks from response
- [ ] Extract skill name and arguments
- [ ] Return list of `SkillCall` objects
- **Files**: `src/skills/adapters/claude_adapter.py`

### T025: Implement ClaudeAdapter.format_result
- [ ] Format `SkillResult` as `tool_result`
- [ ] Handle success and error cases
- **Files**: `src/skills/adapters/claude_adapter.py`

---

## Phase 5: Gemini Adapter (P1)

### T026: Implement GeminiAdapter.to_api_format
- [ ] Create `src/skills/adapters/gemini_adapter.py`
- [ ] Convert `Skill` to Gemini function declaration
- [ ] Use google-genai function calling format
- **FR**: FR-011
- **Files**: `src/skills/adapters/gemini_adapter.py`

### T027: Implement GeminiAdapter.parse_response
- [ ] Parse `function_call` from response candidates
- [ ] Handle multiple function calls
- [ ] Return list of `SkillCall` objects
- **FR**: FR-013
- **Files**: `src/skills/adapters/gemini_adapter.py`

### T028: Implement GeminiAdapter.format_result
- [ ] Format `SkillResult` as `function_response`
- [ ] Handle structured return data
- **Files**: `src/skills/adapters/gemini_adapter.py`

### T029: Test adapter parity
- [ ] Create `tests/unit/test_adapters.py`
- [ ] Test identical behavior for same skills
- [ ] Verify SC-002 (±5% success rate)
- **SC**: SC-002, SC-006
- **Files**: `tests/unit/test_adapters.py`

---

## Phase 6: Conductor (P2)

### T030: Create conductor module structure
- [ ] Create `src/conductor/__init__.py`
- [ ] Create `src/conductor/planner.py`
- [ ] Create `src/conductor/executor.py`
- **Files**: `src/conductor/__init__.py`, `src/conductor/planner.py`, `src/conductor/executor.py`

### T031: Implement ExecutionPlan dataclass
- [ ] Create `PlanStep` dataclass
- [ ] Create `ExecutionPlan` dataclass
- [ ] Add validation (max 20 steps, valid deps)
- **Entity**: ExecutionPlan, PlanStep
- **NFR**: NFR-003
- **Files**: `src/conductor/planner.py`

### T032: Implement Planner.create_plan
- [ ] Create planning prompt template
- [ ] Call Gemini with structured output
- [ ] Parse JSON plan response
- [ ] Validate plan structure
- **FR**: FR-014, FR-015
- **Files**: `src/conductor/planner.py`

### T033: Implement CycleDetector
- [ ] Create `src/conductor/cycle_detector.py`
- [ ] Implement state hashing
- [ ] Detect cycles (same state 2x)
- **Edge Case**: Boucle infinie
- **Files**: `src/conductor/cycle_detector.py`

### T034: Implement Executor.execute_plan
- [ ] Execute steps in dependency order
- [ ] Track step status and results
- [ ] Handle step failures
- **FR**: FR-016, FR-017
- **Files**: `src/conductor/executor.py`

### T035: Implement verbose progress display
- [ ] Display plan table with Rich
- [ ] Update status in real-time
- [ ] Show step details on completion
- **FR**: FR-018
- **Files**: `src/conductor/executor.py`

### T036: Test Conductor
- [ ] Create `tests/unit/test_conductor.py`
- [ ] Test planning with mock Gemini
- [ ] Test cycle detection
- [ ] Test execution with mock skills
- **SC**: SC-003
- **Files**: `tests/unit/test_conductor.py`

---

## Phase 7: MCP Integration (P2)

### T037: Create MCP module structure
- [ ] Create `src/mcp/__init__.py`
- [ ] Create `src/mcp/client.py`
- [ ] Create `src/mcp/discovery.py`
- **Files**: `src/mcp/__init__.py`, `src/mcp/client.py`, `src/mcp/discovery.py`

### T038: Add MCP dependency
- [ ] Add `mcp>=0.9.0` to requirements.txt (when available)
- [ ] Or implement JSON-RPC client manually
- **Files**: `requirements.txt`

### T039: Implement MCPClient.connect
- [ ] Spawn server process
- [ ] Send initialize request
- [ ] Store capabilities
- [ ] Connection timeout <2s (SC-004)
- **FR**: FR-019
- **SC**: SC-004
- **Files**: `src/mcp/client.py`

### T040: Implement tool/resource discovery
- [ ] Send tools/list request
- [ ] Send resources/list request
- [ ] Store discovered items
- **FR**: FR-020
- **Files**: `src/mcp/discovery.py`

### T041: Implement MCPToolBridge
- [ ] Create `src/mcp/skill_bridge.py`
- [ ] Convert MCPTool to Skill
- [ ] Execute via MCP client
- **FR**: FR-021
- **Files**: `src/mcp/skill_bridge.py`

### T042: Handle MCP conflicts
- [ ] Detect name conflicts with built-in skills
- [ ] Apply priority rules (built-in first by default)
- [ ] Support `override_builtins` config
- **Edge Case**: Conflit nom skill MCP vs intégré
- **Files**: `src/mcp/skill_bridge.py`

### T043: Handle MCP connection loss
- [ ] Implement retry with exponential backoff
- [ ] Continue without MCP on failure
- [ ] Auto-reconnect when available
- **FR**: FR-023
- **Edge Case**: Connexion MCP perdue
- **Files**: `src/mcp/client.py`

### T044: Test MCP integration
- [ ] Create `tests/unit/test_mcp_client.py`
- [ ] Test with mock MCP server
- [ ] Test connection failure handling
- **Files**: `tests/unit/test_mcp_client.py`

### T044b: Implement MCP resources as analysis context
- [ ] Fetch resources from connected MCP servers
- [ ] Include resource content in analysis prompts
- [ ] Handle resource read failures gracefully
- **FR**: FR-022
- **US**: US6-3
- **Files**: `src/mcp/discovery.py`, `src/core/analyzer.py`

---

## Phase 8: Custom Skill Registry (P3)

### T045: Implement skill definition loader
- [ ] Load YAML skill definitions from custom path
- [ ] Validate schema
- [ ] Report errors clearly
- **FR**: FR-025, FR-026
- **Files**: `src/skills/registry.py`

### T046: Implement command-based skills
- [ ] Parse `command` field in skill definition
- [ ] Execute command with parameter substitution
- [ ] Return command output as result
- **Files**: `src/skills/registry.py`

### T047: Add custom skills path config
- [ ] Read `skills.custom_skills_path` from config.json
- [ ] Default to `./aetheris-skills/`
- **Files**: `src/skills/registry.py`, `src/core/config.py`

### T048: Document skill definition format
- [ ] Add skill definition schema to docs
- [ ] Provide example skills
- **FR**: FR-027
- **SC**: SC-005
- **Files**: `docs/skills/custom-skills.md`

### T049: Test custom skill loading
- [ ] Create test skill definitions
- [ ] Test valid/invalid definitions
- [ ] Test execution
- **Files**: `tests/unit/test_custom_skills.py`

---

## Phase 9: Documentation Update (P1)

### T050: Create CLI interactive mode documentation
- [ ] Create `docs/cli-interactive.md` with full usage guide
- [ ] Document all commands and shortcuts
- [ ] Add examples and use cases
- **Files**: `docs/cli-interactive.md`

### T051: Create Skills documentation
- [ ] Create `docs/skills/README.md` with skills overview
- [ ] Create `docs/skills/builtin-skills.md` listing all built-in skills
- [ ] Create `docs/skills/custom-skills.md` with custom skill guide
- **Files**: `docs/skills/README.md`, `docs/skills/builtin-skills.md`, `docs/skills/custom-skills.md`

### T052: Create MCP integration documentation
- [ ] Create `docs/mcp-integration.md` with setup guide
- [ ] Document MCP server configuration
- [ ] Add troubleshooting section
- **Files**: `docs/mcp-integration.md`

### T053: Update docs/commands/README.md
- [ ] Add CLI interactive mode section
- [ ] Add skills command reference
- [ ] Update command table with v3.0 commands
- **Files**: `docs/commands/README.md`

### T054: Update README.md for v3.0
- [ ] Add multi-provider section
- [ ] Add CLI interactive mode section
- [ ] Add Skills documentation links
- [ ] Update feature table
- [ ] Update roadmap to mark v3.0 as implemented
- **Files**: `README.md`

### T055: Add CHANGELOG.md entry for v3.0
- [ ] Document all new features
- [ ] Document breaking changes if any
- [ ] Add migration notes
- **Files**: `CHANGELOG.md`

---

## Phase 10: Testing & Polish (P1)

### T056: Integration test - CLI interactive
- [ ] Create `tests/integration/test_cli_interactive.py`
- [ ] Test full REPL session
- [ ] Test command passthrough
- **Files**: `tests/integration/test_cli_interactive.py`

### T057: Integration test - Skill execution
- [ ] Create `tests/integration/test_skill_execution.py`
- [ ] Test skills with real files
- [ ] Test safe mode prompts
- **Files**: `tests/integration/test_skill_execution.py`

### T058: Backward compatibility tests
- [ ] Test all existing commands unchanged
- [ ] Test `aetheris analysis` without --cli
- [ ] Test `aetheris fix --auto`
- **FR**: FR-029
- **US**: US2-9
- **Files**: `tests/integration/test_backward_compat.py`

### T059: Update CLI help text
- [ ] Add --cli description
- [ ] Document new flags
- [ ] Update --help output
- **Files**: `src/cli.py`

### T060: Add config.json schema for v3.0
- [ ] Add `cli.*` section
- [ ] Add `skills.*` section
- [ ] Add `mcp.*` section
- **Files**: `src/core/config.py`

### T061: Final validation
- [ ] Run full test suite
- [ ] Run lint and typecheck
- [ ] Verify all SC metrics
- [ ] Update pyproject.toml version to 3.0.0
- [ ] Tag release v3.0.0

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
