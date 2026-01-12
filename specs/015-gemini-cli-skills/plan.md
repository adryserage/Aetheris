# Implementation Plan: Migration Gemini CLI & Intégration Skills

**Branch**: `015-gemini-cli-skills` | **Date**: 2026-01-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/015-gemini-cli-skills/spec.md`
**Target Version**: v3.0

## Dependencies (Prerequisites)

Cette spec dépend des versions suivantes qui doivent être implémentées en premier:

| Version | Feature | Raison de la Dépendance |
|---------|---------|-------------------------|
| **v3.0** | Configuration Persistante (JSON) | Skills requièrent `config.json` pour `enabled_skills`, `safe_mode`, `custom_skills_path` |
| **v3.1** | Sécurité Renforcée | Skills exécutent des commandes shell, nécessitent profils de sécurité (`--profile safe/ci/unrestricted`) |
| **v3.2** | Architecture Headless | Conductor requiert le runner déterministe pour exécution non-interactive |

**Ordre d'implémentation requis**: v3.0 → v3.1 → v3.2 → v3.0 (cette spec)

## Summary

Transitionner Aetheris vers une architecture CLI Wrapper unifiée avec:
- Mode interactif (`aetheris --cli`) encapsulant Gemini CLI et Claude Code CLI
- Autocomplétion des commandes natives via `/command` syntax
- Agent Skills (Tool Use pour Claude, Function Calling pour Gemini)
- Conductor pour orchestration des tâches complexes avec Gemini
- Intégration MCP pour extensibilité

## Technical Context

**Language/Version**: Python 3.9+ (compatible 3.12)
**Primary Dependencies**:
- google-genai>=1.0.0 (Gemini Function Calling)
- anthropic>=0.25.0 (Claude Tool Use)
- rich>=13.0.0 (Terminal UI, autocomplete)
- prompt_toolkit (Interactive CLI, autocomplete)
- typer (CLI framework existant)

**Storage**: Local filesystem (JSON config, skill definitions)
**Testing**: pytest + pytest-asyncio
**Target Platform**: Linux, macOS, Windows (CLI)
**Project Type**: Single project (extension de l'existant)
**Performance Goals**:
- Autocomplete <100ms (SC-007)
- MCP connection <2s (SC-004)

**Constraints**:
- Rétrocompatibilité totale avec commandes existantes
- Skills sandboxés au répertoire projet par défaut

**Scale/Scope**: ~2000 nouvelles LOC, 11 nouveaux modules

## Constitution Check

*Project utilise un template de constitution non rempli. Principes appliqués basés sur CLAUDE.md:*

| Principle | Status | Notes |
|-----------|--------|-------|
| Modular Architecture | ✅ Pass | Nouveaux modules dans src/cli/, src/skills/, src/conductor/ |
| Backward Compatibility | ✅ Pass | FR-029 garantit rétrocompatibilité |
| Error Handling | ✅ Pass | Edge cases documentés avec solutions |
| Security | ✅ Pass | Sandboxing, safe mode, audit logging |
| Testing | ⚠️ Pending | Tests requis pour chaque module |

## Project Structure

### Documentation (this feature)

```text
specs/015-gemini-cli-skills/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── skills-api.yaml  # Skill interface contract
│   └── mcp-client.yaml  # MCP client contract
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── cli.py                    # Existing CLI (add --cli flag)
├── cli/                      # NEW: Interactive CLI module
│   ├── __init__.py
│   ├── interactive.py        # Interactive mode REPL
│   ├── command_registry.py   # Command registration per provider
│   ├── autocomplete.py       # Autocomplete engine
│   └── passthrough.py        # Command passthrough to underlying CLI
├── skills/                   # NEW: Agent Skills module
│   ├── __init__.py
│   ├── base_skill.py         # Abstract skill interface
│   ├── file_skills.py        # read_file, write_file, search_files
│   ├── shell_skill.py        # execute_command
│   ├── registry.py           # SkillRegistry
│   └── adapters/
│       ├── claude_adapter.py # Tool Use format
│       └── gemini_adapter.py # Function Calling format
├── conductor/                # NEW: Gemini Conductor
│   ├── __init__.py
│   ├── planner.py            # Task decomposition
│   ├── executor.py           # Plan execution
│   └── cycle_detector.py     # Infinite loop prevention
├── mcp/                      # NEW: MCP Integration
│   ├── __init__.py
│   ├── client.py             # MCP client
│   ├── discovery.py          # Resource/tool discovery
│   └── skill_bridge.py       # MCP tools as skills
├── core/
│   └── ai_providers.py       # Existing (extend for skills)
└── models/
    └── skill_models.py       # NEW: Skill data models

tests/
├── unit/
│   ├── test_autocomplete.py
│   ├── test_skills.py
│   ├── test_conductor.py
│   └── test_mcp_client.py
└── integration/
    ├── test_cli_interactive.py
    └── test_skill_execution.py
```

**Structure Decision**: Extension du projet existant avec 4 nouveaux packages (cli/, skills/, conductor/, mcp/) suivant l'architecture modulaire existante.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 4 new packages | Clear separation of concerns (CLI, Skills, Conductor, MCP) | Single package would mix unrelated code |
| Adapter pattern for skills | Claude Tool Use ≠ Gemini Function Calling formats | Direct implementation would duplicate code |

## Dependencies

### Depends On (Required)
- **v2.6.1**: Existing provider architecture in `ai_providers.py`

### Depends On (Optional)
- **v3.0 (006-persistent-config)**: For `config.json` storage of MCP servers, skill preferences

### New Dependencies to Add

```text
# requirements.txt additions
prompt_toolkit>=3.0.0  # Interactive CLI with autocomplete
mcp>=0.9.0             # Model Context Protocol client (when available)
```

## Phase 0: Research Findings

See [research.md](./research.md) for detailed research on:
- Gemini Function Calling vs Claude Tool Use comparison
- MCP protocol specification
- Autocomplete implementation patterns
- Security sandboxing approaches

## Phase 1: Design Artifacts

- [data-model.md](./data-model.md) - Entity definitions
- [contracts/skills-api.yaml](./contracts/skills-api.yaml) - Skill interface
- [contracts/mcp-client.yaml](./contracts/mcp-client.yaml) - MCP client interface
- [quickstart.md](./quickstart.md) - Usage examples

## Implementation Order (High-Level)

| Phase | Components | Priority |
|-------|------------|----------|
| 1 | CLI interactive mode (`--cli`, `/command`) | P1 |
| 2 | Command registry & autocomplete | P1 |
| 3 | Base skills (file, shell) | P1 |
| 4 | Claude adapter (Tool Use) | P1 |
| 5 | Gemini adapter (Function Calling) | P1 |
| 6 | Conductor (planner, executor) | P2 |
| 7 | MCP client integration | P2 |
| 8 | Custom skill registry | P3 |

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing CLI | Extensive backward compat tests |
| MCP spec changes | Abstract MCP behind interface |
| Skill security issues | Sandbox by default, audit logging |
| Conductor infinite loops | 20-step limit, cycle detection |
