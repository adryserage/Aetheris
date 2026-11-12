import json
from pathlib import Path

import pytest

from aetheris import cli


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    monkeypatch.setattr(cli.shutil, "which", lambda name: None)
    return tmp_path


def cursor_config(home: Path) -> Path:
    return home / ".cursor" / "mcp.json"


def test_install_adds_server_and_keeps_other_servers(home: Path, capsys) -> None:
    path = cursor_config(home)
    path.parent.mkdir()
    path.write_text(json.dumps({"mcpServers": {"other": {"command": "x"}}, "theme": "dark"}))

    assert cli.main(["install", "--client", "cursor"]) == 0

    data = json.loads(path.read_text())
    assert data["mcpServers"]["aetheris"] == {"command": "uvx", "args": ["adryserage-aetheris"]}
    assert data["mcpServers"]["other"] == {"command": "x"}
    assert data["theme"] == "dark"
    assert "Cursor: installed" in capsys.readouterr().out


def test_install_twice_changes_nothing(home: Path, capsys) -> None:
    cli.main(["install", "--client", "cursor"])
    first = cursor_config(home).read_text()

    cli.main(["install", "--client", "cursor"])

    assert cursor_config(home).read_text() == first
    assert "already installed" in capsys.readouterr().out


def test_invalid_json_is_never_overwritten(home: Path, capsys) -> None:
    path = cursor_config(home)
    path.parent.mkdir()
    path.write_text("{ not json")

    cli.main(["install", "--client", "cursor"])

    assert path.read_text() == "{ not json"
    assert "cannot read" in capsys.readouterr().out


def test_uninstall_removes_only_aetheris(home: Path) -> None:
    path = cursor_config(home)
    path.parent.mkdir()
    path.write_text(json.dumps({"mcpServers": {"aetheris": {}, "other": {"command": "x"}}}))

    assert cli.main(["uninstall", "--client", "cursor"]) == 0

    assert json.loads(path.read_text()) == {"mcpServers": {"other": {"command": "x"}}}


def test_project_scope_writes_in_current_project(home: Path, tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    monkeypatch.chdir(project)

    cli.main(["install", "--client", "cursor", "--project"])

    assert "aetheris" in json.loads((project / ".cursor" / "mcp.json").read_text())["mcpServers"]
    assert not cursor_config(home).exists()


def test_claude_desktop_has_no_project_scope(home: Path, capsys) -> None:
    cli.main(["install", "--client", "claude-desktop", "--project"])

    assert "skipped" in capsys.readouterr().out


def test_claude_code_missing_prints_the_manual_command(home: Path, capsys) -> None:
    cli.main(["install", "--client", "claude-code"])

    out = capsys.readouterr().out
    assert "claude mcp add --scope user aetheris -- uvx adryserage-aetheris" in out


def test_all_with_no_client_detected_explains_manual_setup(home: Path, capsys) -> None:
    assert cli.main(["install"]) == 1
    assert "uvx adryserage-aetheris" in capsys.readouterr().out


def test_all_installs_only_detected_clients(home: Path) -> None:
    (home / ".cursor").mkdir()

    cli.main(["install"])

    assert cursor_config(home).exists()
    assert not cli._claude_desktop_config().exists()


@pytest.mark.parametrize("command", ["analysis", "fix", "pr", "issues", "stats", "run", "--cli"])
def test_legacy_commands_explain_the_change_and_fail(command: str, capsys) -> None:
    assert cli.main([command, "--anything"]) == 2

    err = capsys.readouterr().err
    assert f"`aetheris {command}` was removed in Aetheris 4" in err
    assert 'pip install "adryserage-aetheris==3.0.0"' in err


def test_no_arguments_prints_the_overview(capsys) -> None:
    assert cli.main([]) == 0
    assert "aetheris install" in capsys.readouterr().out


def test_non_utf8_config_is_reported_not_crashing(home: Path, capsys) -> None:
    path = cursor_config(home)
    path.parent.mkdir()
    path.write_bytes(b"\xff\xfe\x00garbage")

    assert cli.main(["install", "--client", "cursor"]) == 0

    assert path.read_bytes() == b"\xff\xfe\x00garbage"
    assert "cannot read" in capsys.readouterr().out


def test_hanging_claude_falls_back_to_manual_command(home: Path, monkeypatch, capsys) -> None:
    import subprocess

    monkeypatch.setattr(cli.shutil, "which", lambda name: "/usr/bin/claude")

    def hang(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="claude", timeout=60)

    monkeypatch.setattr(cli.subprocess, "run", hang)

    cli.main(["install", "--client", "claude-code"])

    assert "run this yourself: claude mcp add" in capsys.readouterr().out
