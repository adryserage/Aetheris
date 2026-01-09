# Implementation Plan: Sécurité Renforcée & Stratégie Git

**Branch**: `016-security-reinforced` | **Date**: 2026-01-09 | **Spec**: [spec.md](./spec.md)
**Target Version**: v3.1

## Dependencies (Prerequisites)

| Version | Feature | Raison de la Dépendance |
|---------|---------|-------------------------|
| **v3.0** | Configuration Persistante (JSON) | Profils de sécurité stockés dans `config.json` |

## Summary

Implémenter un système de sécurité complet pour Aetheris avec:
- Profils de sécurité configurables (safe, ci, unrestricted)
- Stratégie Git "One Branch Per Fix" pour isolation
- Audit logging de toutes les opérations sensibles
- Allowlist de commandes configurable

## Technical Context

**Language/Version**: Python 3.9+ (compatible 3.12)
**Primary Dependencies**:
- gitpython>=3.1.0 (Git operations)
- rich>=13.0.0 (Console output)
- existing config module (v3.0)

**Storage**:
- `config.json` pour les profils et allowlist
- `aetheris-audit.jsonl` pour les logs d'audit

**Testing**: pytest + pytest-asyncio
**Target Platform**: Linux, macOS, Windows

**Constraints**:
- Pas d'impact sur les performances (<10ms pour vérification de profil)
- Audit logging asynchrone
- Compatibilité avec tous les workflows Git existants

**Scale/Scope**: ~800 nouvelles LOC, 4 nouveaux modules

## Project Structure

### Source Code

```text
src/
├── security/                     # NEW: Security module
│   ├── __init__.py
│   ├── profiles.py               # SecurityProfile, ProfileManager
│   ├── allowlist.py              # CommandAllowlist, CommandValidator
│   └── audit.py                  # AuditLogger, AuditEntry
├── git/                          # NEW: Git operations module
│   ├── __init__.py
│   ├── branch_manager.py         # BranchManager, FixBranch
│   └── safety.py                 # GitSafetyChecker
└── core/
    └── config.py                 # Update: Add security config schema
```

### Configuration Schema Addition

```json
{
  "security": {
    "default_profile": "safe",
    "custom_allowlist": [],
    "audit_log_path": "aetheris-audit.jsonl",
    "audit_max_entries": 100000
  }
}
```

## Research Decisions

### R1: Git Branch Management Library

**Decision**: GitPython
**Rationale**:
- Pure Python, cross-platform
- Full Git operations support
- Active maintenance
**Alternatives**:
- subprocess + git CLI (more verbose, but no dependency)
- pygit2 (C bindings, harder to install)

### R2: Audit Log Format

**Decision**: JSONL (JSON Lines)
**Rationale**:
- One JSON object per line
- Easy to append (no file structure to maintain)
- Parseable with standard tools (jq, grep)
- Supports streaming reads

### R3: Network Blocking Strategy

**Decision**: Command pattern matching (no actual network blocking)
**Rationale**:
- Pattern matching on commands like `curl`, `wget`, `pip install`
- No system-level blocking required
- Sufficient for agent-controlled commands

## Data Model Summary

| Entity | Attributes |
|--------|------------|
| SecurityProfile | name, network_blocked, max_diff_lines, allowlist_enabled, interactive |
| AuditEntry | timestamp, action, params, result, duration_ms, profile |
| CommandAllowlist | patterns[], descriptions{} |
| FixBranch | name, parent_branch, status, created_at |
| OperationResult | success, error, rollback_performed |

## Integration Points

- **v3.0 Config**: Load/save security settings from `config.json`
- **CLI Module**: Add `--profile` flag to relevant commands
- **Fix Command**: Integrate branch isolation strategy
- **All Commands**: Integrate audit logging
