import subprocess
from pathlib import Path

import pytest

from aetheris import registry
from aetheris.domain import Agent, Playbook, Rule

# A key shaped like an AWS access key. Split so this file holds no matching literal, and not
# AWS's documented sample (AKIA...EXAMPLE), which the scan ignores.
FAKE_AWS_KEY = "AKIA" + "Q7RZ3MX2B4K6N8P1"
# Same idea for the other fixtures: the scanners must find nothing in this repository.
PASSWORD_LINE = "password" + ' = "hunter2hunter2"'
FAKE_SSN = "123-45-" + "6789"
FAKE_CARD = "4111 1111 " + "1111 1111"
TEST_EMAIL = "test" + "@example.com"


def write(root: Path, rel: str, content: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    monkeypatch.setenv("AETHERIS_ROOT", str(root))
    return root.resolve()


@pytest.fixture
def git_repo(repo: Path) -> Path:
    def git(*args: str) -> None:
        subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.email", TEST_EMAIL)
    git("config", "user.name", "Test")
    write(repo, "tracked.py", "x = 1\n")
    git("add", ".")
    git("commit", "-q", "-m", "init")
    return repo


@pytest.fixture
def fixture_agents(monkeypatch: pytest.MonkeyPatch) -> None:
    """One minimal agent so the tools do not depend on the shipped rule files."""
    agent = Agent(
        id="security",
        name="Security",
        summary="Fixture agent.",
        rules=(
            Rule(id="T-001", title="All languages", severity="high", check="Look everywhere."),
            Rule(
                id="T-002",
                title="Python only",
                severity="low",
                check="Look in Python.",
                languages=("python",),
            ),
        ),
        checks=("secret_scan",),
    )
    monkeypatch.setattr(registry, "AGENTS", {"security": agent})


def make_playbook(id: str, agents: tuple, languages: tuple = ()) -> Playbook:
    return Playbook(
        id=id,
        title=f"Title {id}",
        agents=agents,
        task="analyze",
        languages=languages,
        when="When testing.",
        source=f"https://example.com/{id}",
        source_commit="abc123",
        author="Someone",
        license="CC-BY-SA-4.0",
        license_url="https://creativecommons.org/licenses/by-sa/4.0/",
        changes="Condensed.",
        steps="1. Do the thing.",
    )


@pytest.fixture
def fixture_playbooks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Two playbooks so the tools do not depend on the shipped playbook files."""
    playbooks = (
        make_playbook("pb-all", ("security",)),
        make_playbook("pb-go", ("security", "metrics"), languages=("go",)),
    )
    monkeypatch.setattr(registry, "PLAYBOOKS", {p.id: p for p in playbooks})
