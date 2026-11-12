import asyncio
import json

import pytest

from aetheris.server import (
    build_server,
    get_playbook,
    get_rules,
    list_agents,
    plan_review,
    run_checks,
)
from tests.conftest import FAKE_AWS_KEY, write

TOOLS = {
    "list_agents",
    "plan_review",
    "get_rules",
    "get_playbook",
    "run_checks",
    "synthesize_report",
}


def test_in_process_client_lists_exactly_the_six_tools_and_calls_one(repo):
    from mcp.shared.memory import create_connected_server_and_client_session

    write(repo, "a.py", f'KEY = "{FAKE_AWS_KEY}"\n')

    async def scenario():
        server = build_server()
        async with create_connected_server_and_client_session(server._mcp_server) as client:
            tools = await client.list_tools()
            called = await client.call_tool("run_checks", {"agent": "security"})
            return tools, called

    tools, called = asyncio.run(scenario())
    assert {t.name for t in tools.tools} == TOOLS
    payload = json.loads(called.content[0].text)
    assert payload["agent"] == "security" and payload["finding_count"] >= 1
    assert FAKE_AWS_KEY not in called.content[0].text


def test_list_agents_reports_rule_counts_checks_and_presets(fixture_agents, fixture_playbooks):
    result = list_agents()
    assert result["agents"] == [
        {
            "id": "security",
            "name": "Security",
            "summary": "Fixture agent.",
            "rule_count": 2,
            "checks": ["secret_scan"],
            "playbook_count": 2,
        }
    ]
    assert "quick-scan" in result["presets"]


def test_get_rules_filters_by_language_and_returns_schema(fixture_agents):
    everything = get_rules("security")
    assert [r["id"] for r in everything["rules"]] == ["T-001", "T-002"]
    assert [r["id"] for r in get_rules("security", "TypeScript")["rules"]] == ["T-001"]
    assert "severity" in everything["finding_schema"]["properties"]
    with pytest.raises(ValueError):
        get_rules("metrics")


def test_get_rules_lists_playbooks_without_bodies(fixture_agents, fixture_playbooks):
    listed = get_rules("security")["playbooks"]
    assert [p["id"] for p in listed] == ["pb-all", "pb-go"]
    assert set(listed[0]) == {"id", "title", "task", "when"}
    assert [p["id"] for p in get_rules("security", "python")["playbooks"]] == ["pb-all"]


def test_get_playbook_returns_steps_and_attribution(fixture_playbooks):
    result = get_playbook("pb-all")
    assert result["steps"] == "1. Do the thing."
    assert result["attribution"] == {
        "title": "Title pb-all",
        "author": "Someone",
        "source": "https://example.com/pb-all",
        "license": "CC-BY-SA-4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "changes": "Condensed.",
    }
    with pytest.raises(ValueError):
        get_playbook("nope")


def test_in_process_client_serves_a_shipped_playbook(repo):
    from mcp.shared.memory import create_connected_server_and_client_session

    async def scenario():
        async with create_connected_server_and_client_session(build_server()._mcp_server) as c:
            return await c.call_tool("get_playbook", {"id": "fp-check"})

    payload = json.loads(asyncio.run(scenario()).content[0].text)
    assert payload["attribution"]["license"] == "CC-BY-SA-4.0"
    assert "Gate review" in payload["steps"]


def _playbooks_of(plan, agent):
    return {p["id"] for a in plan["agents"] if a["id"] == agent for p in a["playbooks"]}


def test_plan_review_proposes_differential_review_for_a_diff_only(git_repo):
    write(git_repo, "tracked.py", "x = 2\n")
    diff = plan_review()
    assert "differential-review" in _playbooks_of(diff, "security")
    assert {"fp-check", "vulnerability-triage-brocards"} <= _playbooks_of(diff, "qa_synthesis")
    assert "differential-review" not in _playbooks_of(plan_review(scope="repo"), "security")


def test_plan_review_proposes_the_actions_audit_for_workflow_files(repo):
    write(repo, ".github/workflows/ci.yml", "on: push\n")
    plan = plan_review(scope="repo")
    assert "agentic-actions-auditor" in _playbooks_of(plan, "security")


def test_plan_review_diff_scope_lists_changed_files_and_agents(git_repo):
    write(git_repo, "tracked.py", "x = 2\n")
    write(git_repo, "api/routes.py", "y = 1\n")
    write(git_repo, "requirements.txt", "requests==2.0.0\n")
    plan = plan_review()
    assert plan["files"] == ["api/routes.py", "tracked.py", "requirements.txt"]
    assert plan["languages"] == {"python": 2}
    ids = [a["id"] for a in plan["agents"]]
    assert {"security", "dependency", "type_safety", "api_contract"} <= set(ids)
    assert ids[-1] == "qa_synthesis"
    assert "synthesize_report" in plan["next_steps"]


def test_plan_review_repo_and_paths_scopes(repo):
    write(repo, "a.py", "x = 1\n")
    write(repo, "sub/b.py", "x = 1\n")
    assert plan_review(scope="repo")["files"] == ["a.py", "sub/b.py"]
    assert plan_review(scope="paths", paths=["sub"])["files"] == ["sub/b.py"]
    with pytest.raises(ValueError):
        plan_review(scope="paths")


def test_plan_review_preset_and_explicit_agents(repo):
    write(repo, "a.py", "x = 1\n")
    preset = plan_review(scope="repo", preset="quick-scan")
    assert [a["id"] for a in preset["agents"]] == ["security", "code_quality", "qa_synthesis"]
    explicit = plan_review(scope="repo", agents=["metrics"])
    assert [a["id"] for a in explicit["agents"]] == ["metrics"]
    with pytest.raises(ValueError):
        plan_review(scope="repo", preset="nope")


def test_path_with_parent_traversal_is_rejected_by_the_tools(repo):
    with pytest.raises(ValueError):
        run_checks("security", ["../etc/passwd"])
    with pytest.raises(ValueError):
        plan_review(scope="paths", paths=["../"])


def test_run_checks_qa_synthesis_has_no_checks(repo):
    result = run_checks("qa_synthesis")
    assert result["findings"] == [] and "synthesize_report" in result["note"]


def test_findings_are_capped_and_flagged_truncated(repo):
    write(repo, "many.py", "".join(f'k{i} = "{FAKE_AWS_KEY}"\n' for i in range(250)))
    result = run_checks("security")
    assert len(result["findings"]) == 200 and result["truncated"] is True
    assert result["finding_count"] == 250


def test_a_crashing_check_is_reported_and_others_still_run(repo, monkeypatch):
    from aetheris import server

    def broken(ctx):
        raise RuntimeError("boom")

    write(repo, "a.py", f'KEY = "{FAKE_AWS_KEY}"\n')
    monkeypatch.setitem(server.CHECKS["security"], "security_patterns", broken)
    result = run_checks("security")
    assert "security_patterns: RuntimeError: boom" in result["errors"]
    assert result["finding_count"] == 1
