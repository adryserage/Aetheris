# Implementation Plan: Agent Selection & Targeted Fix

**Branch**: `009-agent-selection` | **Date**: 2025-01-07 | **Spec**: [spec.md](./spec.md)
**Target Version**: v3.0.2
**Depends On**: v3.0.1 (Extended Analysis Agents)

## Summary

Enable selective agent execution and targeted fixes by category. Add presets for common agent combinations and interactive selection mode.

## Technical Context

**Language/Version**: Python 3.9+
**Primary Dependencies**: Rich/Textual (interactive UI)
**Testing**: Unit tests for selection logic, integration tests for CLI
**Constraints**: Must be backward compatible (default = all agents)
**Depends On**: v3.0 (Persistent Config) for config.json integration

## Configuration Integration (v3.0)

Presets and agent selection settings integrate with the config.json system:

```json
{
  "analysis": {
    "default_preset": "quick-scan",
    "enabled_agents": ["all"],
    "skip_agents": []
  },
  "presets": {
    "custom-preset": {
      "description": "My custom preset",
      "agents": ["security", "performance"]
    }
  }
}
```

### Configuration Hierarchy
1. CLI flags (`--agents`, `--preset`)
2. Local `config.json`
3. Global `~/.aetheris/config.json`
4. Built-in presets (`config/presets.json`)

### Settings UI Integration
Add "Presets" tab to `aetheris settings` command with:
- Default preset selection
- Custom preset creation
- Agent enable/disable toggles

## Project Structure

```text
src/core/agent_selector.py    # NEW: Agent selection logic
src/core/presets.py           # NEW: Preset definitions
src/core/fix_categories.py    # NEW: Category definitions
src/core/interactive_select.py # NEW: Interactive UI
src/cli.py                    # MODIFY: Add --agents, --category, --preset, --interactive
src/core/orchestrator.py      # MODIFY: Apply agent/category filters
config/presets.json           # NEW: Preset configurations
```

## Data Model

### AgentPreset
```python
@dataclass
class AgentPreset:
    name: str
    description: str
    agents: list[str]
    compliance_profile: Optional[str] = None
```

### FixCategory
```python
@dataclass
class FixCategory:
    name: str
    agent_source: str
    issue_types: list[str]
```

### Default Presets
```python
PRESETS = {
    "security-audit": AgentPreset(
        name="security-audit",
        description="Security-focused analysis",
        agents=["security", "data_privacy", "dependency"]
    ),
    "performance-review": AgentPreset(
        name="performance-review",
        description="Performance optimization analysis",
        agents=["performance", "metrics", "architecture"]
    ),
    "quick-scan": AgentPreset(
        name="quick-scan",
        description="Fast minimal analysis",
        agents=["code_analysis", "security"]
    ),
    "compliance-gdpr": AgentPreset(
        name="compliance-gdpr",
        description="GDPR compliance check",
        agents=["data_privacy"],
        compliance_profile="gdpr"
    )
}
```

## Category Mapping

| Category | Agent | Issue Types |
|----------|-------|-------------|
| security | SecurityAgent | SecurityIssue, Vulnerability |
| performance | PerformanceAgent | PerformanceIssue |
| compliance | DataPrivacyAgent | PrivacyViolation |
| code_quality | CodeAnalysisAgent | QualityIssue |
| architecture | ArchitectAgent | ArchitectureIssue |

## Next Steps

1. Generate tasks.md
2. Implement agent selector
3. Implement presets
4. Implement category filter
5. Add interactive mode
6. Integrate with orchestrator
