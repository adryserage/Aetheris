"""
Preset definitions for agent analysis combinations (v2.11)
"""

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class AgentPreset:
    """Defines a preset configuration for agent analysis"""

    name: str
    description: str
    agents: List[str]
    compliance_profile: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = {
            "name": self.name,
            "description": self.description,
            "agents": self.agents,
        }
        if self.compliance_profile:
            result["compliance_profile"] = self.compliance_profile
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> "AgentPreset":
        """Create from dictionary"""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            agents=data.get("agents", []),
            compliance_profile=data.get("compliance_profile"),
        )


# Built-in presets
DEFAULT_PRESETS: Dict[str, AgentPreset] = {
    "full": AgentPreset(
        name="full",
        description="Complete analysis with all 10 agents",
        agents=["all"],
    ),
    "core": AgentPreset(
        name="core",
        description="Core 6 agents only (no extended agents)",
        agents=["code_analysis", "architecture", "security", "metrics", "vulnerability", "qa"],
    ),
    "security-audit": AgentPreset(
        name="security-audit",
        description="Security-focused analysis",
        agents=["security", "data_privacy", "vulnerability"],
    ),
    "performance-review": AgentPreset(
        name="performance-review",
        description="Performance optimization analysis",
        agents=["performance", "metrics", "architecture"],
    ),
    "quick-scan": AgentPreset(
        name="quick-scan",
        description="Fast minimal analysis",
        agents=["code_analysis", "security"],
    ),
    "compliance-gdpr": AgentPreset(
        name="compliance-gdpr",
        description="GDPR compliance check",
        agents=["data_privacy"],
        compliance_profile="gdpr",
    ),
    "compliance-hipaa": AgentPreset(
        name="compliance-hipaa",
        description="HIPAA compliance check",
        agents=["data_privacy"],
        compliance_profile="hipaa",
    ),
    "compliance-pci": AgentPreset(
        name="compliance-pci",
        description="PCI-DSS compliance check",
        agents=["data_privacy"],
        compliance_profile="pci_dss",
    ),
    "type-safety": AgentPreset(
        name="type-safety",
        description="Type safety analysis for TypeScript/Python",
        agents=["type_safety", "code_analysis"],
    ),
    "api-review": AgentPreset(
        name="api-review",
        description="API contract and REST compliance",
        agents=["api_contract", "security"],
    ),
}


def load_presets_from_file(file_path: str) -> Dict[str, AgentPreset]:
    """Load presets from a JSON file"""
    presets = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for name, preset_data in data.get("presets", {}).items():
                    preset_data["name"] = name
                    presets[name] = AgentPreset.from_dict(preset_data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load presets from {file_path}: {e}")
    return presets


def load_presets(
    config_json_path: Optional[str] = None,
    global_config_path: Optional[str] = None,
) -> Dict[str, AgentPreset]:
    """
    Load presets from all sources in priority order:
    1. Local config.json (highest priority)
    2. Global ~/.aetheris/config.json
    3. Built-in presets (lowest priority)

    Returns merged dict where higher priority overwrites lower.
    """
    # Start with built-in presets
    presets = dict(DEFAULT_PRESETS)

    # Load global config presets
    if global_config_path is None:
        global_config_path = os.path.expanduser("~/.aetheris/config.json")
    global_presets = load_presets_from_file(global_config_path)
    presets.update(global_presets)

    # Load local config presets (highest priority)
    if config_json_path is None:
        config_json_path = "config.json"
    local_presets = load_presets_from_file(config_json_path)
    presets.update(local_presets)

    return presets


def get_preset(
    name: str, presets: Optional[Dict[str, AgentPreset]] = None
) -> Optional[AgentPreset]:
    """Get a preset by name"""
    if presets is None:
        presets = load_presets()
    return presets.get(name)


def list_presets(presets: Optional[Dict[str, AgentPreset]] = None) -> List[AgentPreset]:
    """List all available presets"""
    if presets is None:
        presets = load_presets()
    return list(presets.values())


def get_preset_descriptions() -> str:
    """Get formatted preset descriptions for CLI help"""
    presets = load_presets()
    lines = ["Available presets:"]
    for preset in presets.values():
        agents_str = ", ".join(preset.agents[:3])
        if len(preset.agents) > 3:
            agents_str += f" (+{len(preset.agents) - 3} more)"
        lines.append(f"  {preset.name}: {preset.description}")
        lines.append(f"    Agents: {agents_str}")
    return "\n".join(lines)
