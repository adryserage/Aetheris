# Implementation Plan: Architecture Headless Déterministe

**Branch**: `017-headless-deterministic` | **Date**: 2026-01-09 | **Spec**: [spec.md](./spec.md)
**Target Version**: v3.2

## Dependencies (Prerequisites)

| Version | Feature | Raison de la Dépendance |
|---------|---------|-------------------------|
| **v3.0** | Configuration Persistante (JSON) | Task files utilisent le même format de config |
| **v3.1** | Sécurité Renforcée | Mode headless utilise les profils de sécurité |

## Summary

Implémenter une architecture headless pour Aetheris permettant:
- Exécution via fichiers de tâche JSON/YAML
- Sortie JSON structurée et documentée
- Mode non-interactif complet
- Reproductibilité des exécutions

## Technical Context

**Language/Version**: Python 3.9+ (compatible 3.12)
**Primary Dependencies**:
- pyyaml>=6.0 (YAML parsing)
- jsonschema>=4.0 (Schema validation)
- existing config module (v3.0)
- existing security module (v3.1)

**Storage**:
- Task files: JSON/YAML
- Output: JSON to stdout or file

**Testing**: pytest + pytest-asyncio
**Target Platform**: Linux, macOS, Windows (headless)

**Constraints**:
- Pas de TTY requis
- Output toujours JSON valide
- Graceful degradation on crash

**Scale/Scope**: ~600 nouvelles LOC, 3 nouveaux modules

## Project Structure

### Source Code

```text
src/
├── runner/                       # NEW: Headless runner module
│   ├── __init__.py
│   ├── task_parser.py            # TaskFile parser and validator
│   ├── executor.py               # TaskRunner, non-interactive execution
│   └── output_formatter.py       # JSON/YAML output formatting
├── schemas/                      # NEW: JSON schemas
│   ├── task_file_schema.json     # Task file schema
│   └── output_schema.json        # Output schema
└── cli.py                        # Update: Add 'run' command
```

### Task File Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "task"],
  "properties": {
    "version": { "type": "string", "enum": ["1.0"] },
    "task": {
      "type": "object",
      "required": ["type"],
      "properties": {
        "type": { "enum": ["analysis", "fix", "pr"] },
        "target": { "type": "object" },
        "options": { "type": "object" }
      }
    }
  }
}
```

## Research Decisions

### R1: Task File Format

**Decision**: Support both JSON and YAML
**Rationale**:
- JSON for programmatic generation
- YAML for human readability
- Both widely supported

### R2: Output Format

**Decision**: JSON only for output
**Rationale**:
- Machine-parseable
- Consistent structure
- Easy to pipe to tools (jq)

### R3: Signal Handling

**Decision**: Catch SIGINT/SIGTERM for graceful shutdown
**Rationale**:
- Return valid JSON even on interrupt
- Log partial results
- Clean exit codes

## Data Model Summary

| Entity | Attributes |
|--------|------------|
| TaskFile | version, task_type, target, options, output_config |
| ExecutionResult | status, exit_code, duration_ms, logs, diff, error |
| TaskRunner | task_file, security_profile, execution_context |
| OutputFormatter | format, include_diff, include_logs |

## Integration Points

- **v3.0 Config**: Read default options from config.json
- **v3.1 Security**: Apply security profile to execution
- **CLI Module**: Add `aetheris run` command
- **Existing Commands**: Wrap existing analysis/fix in runner
