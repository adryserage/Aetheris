import asyncio
import json
import logging
import os
import pathlib

import pytest
from starlette.testclient import TestClient

from aetheris import server
from aetheris.hosted import (
    MAX_BODY_BYTES,
    BodyLimit,
    ConfigError,
    SessionVerifier,
    build_app,
    read_config,
)
from tests.conftest import FAKE_AWS_KEY

KEY = "k" * 40
BASE = "https://mcp.example.com/aetheris"
ENV = {
    "AETHERIS_BASE_PUBLIQUE": BASE,
    "OAUTH_EMETTEUR": "https://mcp.example.com",
    "AETHERIS_HOTES_AUTORISES": "mcp.example.com,testserver",
    "MCP_TOKEN": KEY,
}
SECRET = FAKE_AWS_KEY
MCP_HEADERS = {"Accept": "application/json, text/event-stream"}


class FakeExecutor:
    """get-session stand-in: answers from a queue and counts the calls."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.calls = 0

    async def __call__(self, url, token):
        self.calls += 1
        assert url == "https://mcp.example.com/api/auth/mcp/get-session"
        answer = self.answers.pop(0) if len(self.answers) > 1 else self.answers[0]
        if isinstance(answer, Exception):
            raise answer
        return answer


class Clock:
    def __init__(self, now=1_800_000_000.0):
        self.now = now

    def __call__(self):
        return self.now


def client_for(executor=None, clock=None):
    config = read_config(ENV)
    verify = SessionVerifier(config.issuer, executor or FakeExecutor((401, None)), clock or Clock())
    return TestClient(build_app(config, verify))


def rpc(client, method, params=None, token=KEY, path="/mcp"):
    headers = dict(MCP_HEADERS)
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    return client.post(path, json=body, headers=headers)


INITIALIZE = {
    "protocolVersion": "2025-06-18",
    "capabilities": {},
    "clientInfo": {"name": "test", "version": "0"},
}


def call_tool(client, name, arguments):
    response = rpc(client, "tools/call", {"name": name, "arguments": arguments})
    assert response.status_code == 200
    return response.json()["result"]


def test_without_token_401_points_to_the_resource_metadata():
    with client_for() as client:
        response = rpc(client, "initialize", INITIALIZE, token=None)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == (
        f'Bearer resource_metadata="{BASE}/.well-known/oauth-protected-resource"'
    )


def test_service_key_opens_mcp_initialize():
    executor = FakeExecutor((401, None))
    with client_for(executor) as client:
        response = rpc(client, "initialize", INITIALIZE)
    assert response.status_code == 200
    assert response.json()["result"]["serverInfo"]["name"] == "aetheris"
    assert executor.calls == 0


def test_valid_session_passes_and_expired_session_is_refused():
    clock = Clock()
    valid = (200, {"userId": "u1", "accessTokenExpiresAt": "2099-01-01T00:00:00.000Z"})
    expired = (200, {"userId": "u1", "accessTokenExpiresAt": "2020-01-01T00:00:00.000Z"})
    with client_for(FakeExecutor(valid), clock) as client:
        assert rpc(client, "initialize", INITIALIZE, token="session-a").status_code == 200
    with client_for(FakeExecutor(expired), clock) as client:
        response = rpc(client, "initialize", INITIALIZE, token="session-b")
    assert response.status_code == 401
    assert response.headers["www-authenticate"].endswith(', error="invalid_token"')


def test_executor_failure_refuses_without_being_cached():
    executor = FakeExecutor((503, None), ConnectionError("down"), (200, {"userId": "u1"}))
    with client_for(executor) as client:
        assert rpc(client, "initialize", INITIALIZE, token="t").status_code == 401
        assert rpc(client, "initialize", INITIALIZE, token="t").status_code == 401
        assert rpc(client, "initialize", INITIALIZE, token="t").status_code == 200
    assert executor.calls == 3


def test_verdict_is_kept_60_seconds():
    clock = Clock()
    executor = FakeExecutor((200, {"userId": "u1"}), (401, None))
    with client_for(executor, clock) as client:
        assert rpc(client, "initialize", INITIALIZE, token="t").status_code == 200
        clock.now += 59
        assert rpc(client, "initialize", INITIALIZE, token="t").status_code == 200
        assert executor.calls == 1
        clock.now += 2
        assert rpc(client, "initialize", INITIALIZE, token="t").status_code == 401
    assert executor.calls == 2


@pytest.mark.parametrize("prefix", ["", "/aetheris"])
def test_routes_answer_with_or_without_the_prefix(prefix):
    with client_for() as client:
        assert client.get(f"{prefix}/sante").json() == {"statut": "ok"}
        metadata = client.get(f"{prefix}/.well-known/oauth-protected-resource/mcp").json()
        assert rpc(client, "initialize", INITIALIZE, path=f"{prefix}/mcp").status_code == 200
    assert metadata["resource"] == f"{BASE}/mcp"
    assert metadata["authorization_servers"] == ["https://mcp.example.com"]


def test_host_and_origin_outside_the_list_are_refused():
    with client_for() as client:
        assert client.get("/sante", headers={"Host": "evil.example"}).status_code == 421
        assert client.get("/sante", headers={"Host": "mcp.example.com:443"}).status_code == 200
        assert client.get("/sante", headers={"Origin": "https://evil.example"}).status_code == 403


def test_body_over_4_mb_is_refused_with_413():
    with client_for() as client:
        response = client.post(
            "/mcp", content=b"x" * (MAX_BODY_BYTES + 1), headers={"Authorization": f"Bearer {KEY}"}
        )
    assert response.status_code == 413


def test_streamed_body_over_the_limit_is_refused_without_reaching_the_app():
    reached = []

    async def app(scope, receive, send):
        reached.append(True)

    sent = []

    async def scenario():
        chunks = [{"type": "http.request", "body": b"x" * 6, "more_body": True}] * 2

        async def receive():
            return chunks.pop(0)

        async def send(message):
            sent.append(message)

        await BodyLimit(app, limit=10)({"type": "http", "headers": []}, receive, send)

    asyncio.run(scenario())
    assert not reached and sent[0]["status"] == 413


@pytest.fixture
def no_disk(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("hosted mode touched the disk")

    monkeypatch.setattr(pathlib.Path, "read_bytes", refuse)
    monkeypatch.setattr(pathlib.Path, "read_text", refuse)
    monkeypatch.setattr(os, "scandir", refuse)
    monkeypatch.setattr(server, "project_root", refuse)
    monkeypatch.setattr(server, "select_files", refuse)


def test_run_checks_finds_a_masked_secret_in_sent_content(no_disk, caplog):
    caplog.set_level(logging.INFO, logger="aetheris")
    files = [{"path": "src/conf.py", "content": f'KEY = "{SECRET}"\n'}]
    with client_for() as client:
        result = call_tool(client, "run_checks", {"agent": "security", "files": files})
        plan = call_tool(client, "plan_review", {"files": [{"path": "src/conf.py"}]})
    text = result["content"][0]["text"]
    payload = json.loads(text)
    assert payload["finding_count"] >= 1 and payload["findings"][0]["file"] == "src/conf.py"
    assert SECRET not in text
    assert json.loads(plan["content"][0]["text"])["scope"] == "provided"
    assert "files=1" in caplog.text
    assert "src/conf.py" not in caplog.text and SECRET not in caplog.text


@pytest.mark.parametrize(
    "path", ["../etc/passwd", "a/../../b", "/etc/passwd", "C:\\x.py", "a\0.py"]
)
def test_paths_that_could_escape_are_refused(path, no_disk):
    with client_for() as client:
        checked = call_tool(
            client, "run_checks", {"agent": "security", "files": [{"path": path, "content": ""}]}
        )
        planned = call_tool(client, "plan_review", {"files": [{"path": path}]})
    assert checked["isError"] and planned["isError"]


def test_more_than_100_files_are_refused():
    files = [{"path": f"f{i}.py", "content": "x = 1\n"} for i in range(101)]
    with client_for() as client:
        result = call_tool(client, "run_checks", {"agent": "security", "files": files})
    assert result["isError"] and "limit is 100" in result["content"][0]["text"]


def test_hosted_schemas_expose_no_disk_or_git_parameter():
    async def schemas():
        return await server.build_server(hosted=True).list_tools()

    tools = asyncio.run(schemas())
    names = set()

    def walk(node):
        if isinstance(node, dict):
            names.update(node.get("properties", {}))
            names.update(v for v in node.get("enum", []) if isinstance(v, str))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    for tool in tools:
        walk(tool.inputSchema)
    assert len(tools) == 6
    assert not names & {"paths", "base", "diff", "repo", "scope"}


@pytest.mark.parametrize(
    "change, variable",
    [
        ({"MCP_TOKEN": ""}, "MCP_TOKEN"),
        ({"MCP_TOKEN": "short"}, "MCP_TOKEN"),
        ({"OAUTH_EMETTEUR": "http://mcp.example.com"}, "OAUTH_EMETTEUR"),
        ({"AETHERIS_HOTES_AUTORISES": " , "}, "AETHERIS_HOTES_AUTORISES"),
        ({"AETHERIS_BASE_PUBLIQUE": ""}, "AETHERIS_BASE_PUBLIQUE"),
    ],
)
def test_config_refuses_a_missing_or_bad_variable(change, variable):
    with pytest.raises(ConfigError, match=variable):
        read_config({**ENV, **change})
