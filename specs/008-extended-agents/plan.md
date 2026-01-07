# Implementation Plan: Extended Analysis Agents

**Branch**: `008-extended-agents` | **Date**: 2025-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-extended-agents/spec.md`
**Target Version**: v3.0.1
**Depends On**: v3.0 (Configuration Persistante & Fichier Local)

## Summary

Extend Aetheris from 6 to 12 specialized AI agents. Add 6 new agents covering: Performance Analysis, API Contract, Technical Debt, Documentation, Type Safety, and Data Privacy (Compliance). All configuration integrates with the v3.0 config.json system.

## Technical Context

**Language/Version**: Python 3.9+
**Primary Dependencies**: google-genai, openai, anthropic, pydantic, rich, click
**Storage**: JSON config files (config.json - v3.0 system)
**Testing**: pytest (existing test infrastructure)
**Target Platform**: CLI (Linux, macOS, Windows)
**Project Type**: Single project (Python package)
**Performance Goals**: 12 agents run in parallel without >50% performance degradation
**Constraints**: API rate limits, memory footprint for large codebases
**Scale/Scope**: Support 1M+ LOC codebases

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Agents follow existing BaseAgent pattern
- ✅ Configuration uses v3.0 config.json hierarchy (CLI > Local > Global > Defaults)
- ✅ Compliance agents configurable separately for legal isolation
- ✅ Each agent produces structured Pydantic output

## Project Structure

### Documentation (this feature)

```text
specs/008-extended-agents/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output
├── quickstart.md        # Phase 1 output
├── checklists/          # Quality checklists
│   └── requirements.md
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── agents/
│   ├── base_agent.py              # Existing - base class
│   ├── code_analysis_expert.py    # Existing
│   ├── security_analysis_agent.py # Existing
│   ├── architect_analysis_agent.py# Existing
│   ├── code_metrics_agent.py      # Existing
│   ├── dependency_vulnerability_agent.py # Existing
│   ├── quality_assurance_agent.py # Existing
│   ├── performance_analysis_agent.py  # NEW
│   ├── api_contract_agent.py          # NEW
│   ├── technical_debt_agent.py        # NEW
│   ├── documentation_agent.py         # NEW
│   ├── type_safety_agent.py           # NEW
│   └── data_privacy_agent.py          # NEW
├── core/
│   ├── config.py        # Modify: add enabled_agents, compliance_agents
│   ├── analyzer.py      # Modify: agent filtering, new agent init
│   └── orchestrator.py  # Modify: new workflow stages
├── models/
│   └── data_models.py   # Modify: add 6 new dataclasses
└── cli.py               # Modify: --agents, --skip-agents, --compliance

tests/
├── unit/
│   └── agents/          # Unit tests for new agents
└── integration/
    └── test_extended_agents.py
```

**Structure Decision**: Single project extending existing agent architecture

## Configuration Design (v3.0 Integration)

### config.json Schema Extension

```json
{
  "enabled_agents": ["all"],
  "compliance_agents": ["none"],
  "agent_settings": {
    "performance": {
      "detect_complexity": true,
      "detect_n_plus_1": true,
      "detect_memory_leaks": true
    },
    "documentation": {
      "min_coverage": 0.8
    }
  }
}
```

### Configuration Hierarchy

1. CLI flags (`--agents`, `--skip-agents`, `--compliance`)
2. Local `config.json` (project-level)
3. Global `~/.aetheris/config.json` (user-level)
4. Environment variables (backward compatibility)
5. Defaults

### Agent Names (for configuration)

| Agent | Config Name | Default |
|-------|-------------|---------|
| Performance Analysis | `performance` | enabled |
| API Contract | `api_contract` | enabled |
| Technical Debt | `technical_debt` | enabled |
| Documentation | `documentation` | enabled |
| Type Safety | `type_safety` | enabled |
| Data Privacy | `data_privacy` | disabled (opt-in) |

### Compliance Profiles

| Profile | Config Value | Focus |
|---------|--------------|-------|
| GDPR | `gdpr` | EU data protection |
| HIPAA | `hipaa` | Healthcare data (PHI) |
| PCI DSS | `pci_dss` | Payment card data |
| CCPA | `ccpa` | California privacy |

## Data Models

### New Dataclasses

```python
@dataclass
class PerformanceIssue:
    file: str
    line: int
    issue_type: str  # "complexity", "memory", "database", "async"
    severity: str    # "critical", "high", "medium", "low"
    description: str
    suggestion: str
    estimated_impact: str  # "10x slower", "O(n²)"

@dataclass
class APIContractViolation:
    endpoint: str
    method: str
    violation_type: str  # "naming", "method", "status_code", "breaking_change"
    severity: str
    description: str
    suggestion: str

@dataclass
class TechnicalDebtItem:
    file: str
    line: int
    debt_type: str       # "smell", "deprecated", "todo", "circular"
    effort_estimate: str # "small", "medium", "large"
    description: str
    refactoring_suggestion: str

@dataclass
class DocumentationGap:
    file: str
    line: int
    gap_type: str   # "missing_docstring", "stale_comment", "undocumented_param"
    target: str     # function/class name
    severity: str
    suggestion: str

@dataclass
class TypeSafetyIssue:
    file: str
    line: int
    issue_type: str  # "any_usage", "unsafe_cast", "null_safety"
    severity: str
    code_snippet: str
    suggestion: str

@dataclass
class PrivacyViolation:
    file: str
    line: int
    violation_type: str       # "pii_logged", "no_encryption", "retention"
    compliance_framework: str # "GDPR", "HIPAA", "PCI_DSS", "CCPA"
    severity: str
    data_category: str        # "PII", "PHI", "PCI"
    remediation: str
```

## Workflow Stages

### New WorkflowStage Enum Values

```python
class WorkflowStage(Enum):
    # ... existing stages ...
    PERFORMANCE_ANALYSIS = "performance_analysis"
    API_CONTRACT_ANALYSIS = "api_contract_analysis"
    TECHNICAL_DEBT_ANALYSIS = "technical_debt_analysis"
    DOCUMENTATION_ANALYSIS = "documentation_analysis"
    TYPE_SAFETY_ANALYSIS = "type_safety_analysis"
    PRIVACY_ANALYSIS = "privacy_analysis"
```

### Report Files Generated

| Agent | Report Path |
|-------|-------------|
| Performance | `docs/analyses/performance_report.md` |
| API Contract | `docs/analyses/api_contract_report.md` |
| Technical Debt | `docs/analyses/technical_debt_report.md` |
| Documentation | `docs/analyses/documentation_report.md` |
| Type Safety | `docs/analyses/type_safety_report.md` |
| Data Privacy | `docs/analyses/privacy_report.md` |

## CLI Extensions

```bash
# Selective agent activation
aetheris analysis --agents performance,api_contract,documentation

# Skip specific agents
aetheris analysis --skip-agents technical_debt

# Compliance mode
aetheris analysis --compliance gdpr,hipaa

# Combined
aetheris analysis --agents all --compliance pci_dss --skip-agents documentation
```

## Implementation Order

Priority based on complexity and dependencies:

1. **Documentation Agent** - Easiest (pattern matching for docstrings)
2. **Type Safety Agent** - Well-defined patterns (any, type: ignore)
3. **Technical Debt Agent** - Extends existing metrics agent
4. **Performance Agent** - Complex but high value
5. **API Contract Agent** - Requires endpoint parsing
6. **Data Privacy Agent** - Compliance-sensitive, last for review

## Files to Create

| File | Purpose |
|------|---------|
| `src/agents/performance_analysis_agent.py` | O(n²), N+1, memory leak detection |
| `src/agents/api_contract_agent.py` | REST violations, breaking changes |
| `src/agents/technical_debt_agent.py` | Code smells, TODO tracking |
| `src/agents/documentation_agent.py` | Docstring coverage analysis |
| `src/agents/type_safety_agent.py` | any usage, unsafe casts |
| `src/agents/data_privacy_agent.py` | PII detection, compliance |

## Files to Modify

| File | Changes |
|------|---------|
| `src/models/data_models.py` | Add 6 new dataclasses |
| `src/core/config.py` | Add `enabled_agents`, `compliance_agents` to AnalysisConfig |
| `src/core/orchestrator.py` | Add 6 new WorkflowStage values |
| `src/core/analyzer.py` | Initialize new agents, filter by config |
| `src/cli.py` | Add `--agents`, `--skip-agents`, `--compliance` options |

## Complexity Tracking

No constitution violations requiring justification.

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Performance degradation with 12 agents | Parallel execution, agent filtering |
| API rate limits | Existing rate limiter, caching |
| False positives in compliance | Configurable sensitivity, manual review |
| Agent failures | Graceful degradation, per-agent error handling |
