from pathlib import Path

import pytest

from aetheris.checks import CHECK_NAMES, RULE_IDS
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


def test_every_mapped_rule_id_exists_in_the_shipped_rules():
    shipped = {rule.id for agent in AGENTS.values() for rule in agent.rules}
    mapped = {rid for rid in RULE_IDS.values() if rid is not None}
    assert mapped <= shipped


def test_shipped_playbooks_load_with_attribution_and_license():
    from aetheris.registry import PLAYBOOKS, playbooks_dir

    assert len(PLAYBOOKS) == 7
    assert (playbooks_dir() / "trailofbits" / "LICENSE").is_file()
    for pb in PLAYBOOKS.values():
        assert set(pb.agents) <= set(AGENT_IDS), pb.id
        assert pb.license == "CC-BY-SA-4.0" and pb.author and pb.changes, pb.id
        assert pb.source.endswith(".md") and pb.source_commit in pb.source, pb.id
        assert pb.steps and len(pb.steps.encode()) <= 8 * 1024, pb.id


def write_playbook(directory: Path, source: str, pid: str, agents: str = "[security]") -> None:
    folder = directory / source
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "LICENSE").write_text("license text", encoding="utf-8")
    (folder / f"{pid}.md").write_text(
        f"---\nid: {pid}\ntitle: T\nagents: {agents}\ntask: analyze\nwhen: W.\n"
        "source: https://example.com/x.md\nsource_commit: abc\nauthor: A\n"
        "license: CC-BY-SA-4.0\nlicense_url: https://example.com/l\nchanges: C.\n"
        "---\n\n1. Step.\n",
        encoding="utf-8",
    )


def test_a_valid_playbook_folder_loads(tmp_path):
    from aetheris.registry import load_playbooks

    write_playbook(tmp_path, "src", "pb")
    assert load_playbooks(tmp_path)["pb"].steps == "1. Step."


def test_duplicate_playbook_id_is_rejected(tmp_path):
    from aetheris.registry import load_playbooks

    write_playbook(tmp_path, "one", "pb")
    write_playbook(tmp_path, "two", "pb")
    with pytest.raises(ValueError, match="pb"):
        load_playbooks(tmp_path)


def test_playbook_with_unknown_agent_is_rejected(tmp_path):
    from aetheris.registry import load_playbooks

    write_playbook(tmp_path, "src", "pb", agents="[security, wizard]")
    with pytest.raises(ValueError, match="wizard"):
        load_playbooks(tmp_path)


def test_playbook_folder_without_license_is_rejected(tmp_path):
    from aetheris.registry import load_playbooks

    write_playbook(tmp_path, "src", "pb")
    (tmp_path / "src" / "LICENSE").unlink()
    with pytest.raises(ValueError, match="LICENSE"):
        load_playbooks(tmp_path)


def test_playbook_with_empty_license_field_is_rejected(tmp_path):
    from aetheris.registry import load_playbooks

    write_playbook(tmp_path, "src", "pb")
    md = tmp_path / "src" / "pb.md"
    md.write_text(md.read_text().replace("license: CC-BY-SA-4.0", "license: ''"))
    with pytest.raises(ValueError, match="license"):
        load_playbooks(tmp_path)
