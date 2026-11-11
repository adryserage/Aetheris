from pathlib import Path

import pytest

from aetheris.checks import CHECK_NAMES
from aetheris.domain import AGENT_IDS
from aetheris.registry import AGENTS, PRESETS, load_agents, rules_dir


def test_all_ten_rule_files_load_with_unique_rule_ids():
    assert sorted(p.stem for p in rules_dir().glob("*.yaml")) == sorted(AGENT_IDS)
    assert set(AGENTS) == set(AGENT_IDS)
    ids = [r.id for a in AGENTS.values() for r in a.rules]
    assert len(ids) == len(set(ids)) and ids
    for agent in AGENTS.values():
        assert agent.rules, agent.id
        assert agent.checks == CHECK_NAMES[agent.id]


def test_presets_only_reference_known_agents():
    assert set(PRESETS["full"].agents) == set(AGENT_IDS)
    assert PRESETS["compliance-gdpr"].compliance_profile == "gdpr"


def write_rules(directory: Path, name: str, agent: str, rule_id: str) -> None:
    (directory / f"{name}.yaml").write_text(
        f"agent: {agent}\nname: N\nsummary: S\nrules:\n"
        f"  - id: {rule_id}\n    title: T\n    severity: high\n    check: Look.\n",
        encoding="utf-8",
    )


def test_duplicate_rule_id_across_files_is_rejected(tmp_path):
    write_rules(tmp_path, "security", "security", "X-1")
    write_rules(tmp_path, "metrics", "metrics", "X-1")
    with pytest.raises(ValueError, match="X-1"):
        load_agents(tmp_path)


def test_agent_must_match_file_name(tmp_path):
    write_rules(tmp_path, "security", "metrics", "X-1")
    with pytest.raises(ValueError):
        load_agents(tmp_path)


def test_invalid_rule_is_rejected(tmp_path):
    (tmp_path / "security.yaml").write_text(
        "agent: security\nname: N\nsummary: S\nrules:\n  - id: X\n    title: T\n"
        "    severity: bogus\n    check: c\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        load_agents(tmp_path)
