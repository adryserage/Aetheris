import asyncio
import json

import pytest

from aetheris.server import (
    build_server,
    get_rules,
    list_agents,
    plan_review,
    run_checks,
)
from tests.conftest import write

TOOLS = {"list_agents", "plan_review", "get_rules", "run_checks", "synthesize_report"}


def test_in_process_client_lists_exactly_the_five_tools_and_calls_one(repo):
    from mcp.shared.memory import create_connected_server_and_client_session

    write(repo, "a.py", 'KEY = "AKIAIOSFODNN7EXAMPLE"\n')

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
    assert "AKIAIOSFODNN7EXAMPLE" not in called.content[0].text


def test_list_agents_reports_rule_counts_checks_and_presets(fixture_agents):
    result = list_agents()
    assert result["agents"] == [
        {
            "id": "security",
            "name": "Security",
            "summary": "Fixture agent.",
            "rule_count": 2,
            "checks": ["secret_scan"],
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
    write(repo, "many.py", "".join(f'k{i} = "AKIAIOSFODNN7EXAMPLE"\n' for i in range(250)))
    result = run_checks("security")
    assert len(result["findings"]) == 200 and result["truncated"] is True
    assert result["finding_count"] == 250


def test_a_crashing_check_is_reported_and_others_still_run(repo, monkeypatch):
    from aetheris import server

    def broken(ctx):
        raise RuntimeError("boom")

    write(repo, "a.py", 'KEY = "AKIAIOSFODNN7EXAMPLE"\n')
    monkeypatch.setitem(server.CHECKS["security"], "security_patterns", broken)
    result = run_checks("security")
    assert "security_patterns: RuntimeError: boom" in result["errors"]
    assert result["finding_count"] == 1
