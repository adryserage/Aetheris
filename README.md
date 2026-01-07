# Aetheris by Adryan - Multi-Agent Code Analysis System

[![PyPI version](https://badge.fury.io/py/adryserage-aetheris.svg)](https://badge.fury.io/py/adryserage-aetheris)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI status](https://img.shields.io/pypi/status/adryserage-aetheris.svg)](https://pypi.org/project/adryserage-aetheris/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](http://mypy-lang.org/)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey)](https://pypi.org/project/adryserage-aetheris/)

Automated code analysis system using multiple cooperating AI agents to provide comprehensive quality, security, and architecture analysis of your codebase.

---

> **We Want Your Input!** Help shape the future of Aetheris - vote on whether it should become fully open source.
>
> **[Cast Your Vote Now](https://adryanserage.ca/poll/aetheris)**

---

### 📊 Download Stats

| Total Downloads | Monthly | Weekly | Daily |
|:---------------:|:-------:|:------:|:-----:|
| [![Downloads](https://static.pepy.tech/badge/adryserage-aetheris)](https://pepy.tech/project/adryserage-aetheris) | [![Downloads/Month](https://static.pepy.tech/badge/adryserage-aetheris/month)](https://pepy.tech/project/adryserage-aetheris) | [![Downloads/Week](https://static.pepy.tech/badge/adryserage-aetheris/week)](https://pepy.tech/project/adryserage-aetheris) | [![Downloads/Day](https://img.shields.io/pypi/dd/adryserage-aetheris?label=downloads)](https://pypistats.org/packages/adryserage-aetheris) |

### 🗳️ Community Poll

**Should Aetheris become Open Source?** [Vote here!](https://adryanserage.ca/poll/aetheris)

[![Yes, open source it!](https://adryanserage.ca/api/poll/svg?pollId=aetheris&option=Yes%2C%20open%20source%20it!&color=%2322c55e)](https://adryanserage.ca/poll/aetheris?vote=Yes%2C%20open%20source%20it!)
[![No, keep it private](https://adryanserage.ca/api/poll/svg?pollId=aetheris&option=No%2C%20keep%20it%20private&color=%23ef4444)](https://adryanserage.ca/poll/aetheris?vote=No%2C%20keep%20it%20private)
[![I don't mind either way](https://adryanserage.ca/api/poll/svg?pollId=aetheris&option=I%20don%27t%20mind%20either%20way&color=%236366f1)](https://adryanserage.ca/poll/aetheris?vote=I%20don%27t%20mind%20either%20way)

## Quick Start

```bash
# Install
pip install adryserage-aetheris

# Configure
echo "GEMINI_API_KEY=your_key_here" > .env

# Analyze
aetheris analysis
```

## Commands

### `aetheris analysis` — [Full docs](docs/commands/analysis.md)
Full codebase analysis with multi-agent AI.

```bash
aetheris analysis                                    # Full analysis
aetheris analysis --changed-files-only --files "src/a.py,src/b.py"
aetheris analysis --changed-files-only --pr-number 123
```

| Option | Description |
|--------|-------------|
| `--changed-files-only` | Analyze only modified files |
| `--files` | Files to analyze (JSON array or comma-separated) |
| `--pr-number` | PR number for context |

---

### `aetheris fix` — [Full docs](docs/commands/fix.md)
Fix bugs automatically with Claude Code.

```bash
aetheris fix --test                     # Test Claude Code connection
aetheris fix --auto --batch-size 10     # Parallel mode (recommended)
aetheris fix --analyze-first            # Analyze then fix
aetheris fix --severity high            # Only critical/high bugs
aetheris fix --retry-failed             # Retry failed fixes
```

| Option | Description |
|--------|-------------|
| `--test` | Test Claude Code connection |
| `--analyze-first` | Run analysis before fixing |
| `--auto` | Automatic mode (no confirmations) |
| `--batch-size`, `-b` | Parallel fixes count (default: 1, max: 10) |
| `--timeout` | Timeout per bug in seconds (default: 300) |
| `--severity` | Minimum severity: `critical`, `high`, `medium`, `low` |
| `--terminal` | Open Claude Code in terminal window |
| `--retry-failed` | Retry only previously failed bugs |

---

### `aetheris pr` — [Full docs](docs/commands/pr-review.md)
Review GitHub Pull Requests with AI.

```bash
aetheris pr --url https://github.com/owner/repo/pull/123
aetheris pr --repo owner/repo --pr 123
aetheris pr --url ... --providers gemini,claude      # Multi-provider
aetheris pr --url ... --dry-run --output review.md
```

| Option | Description |
|--------|-------------|
| `--url` | PR URL |
| `--repo` | Repository (owner/repo format) |
| `--pr` | PR number (required with `--repo`) |
| `--providers` | AI providers, comma-separated (default: gemini) |
| `--consensus` | Report only issues found by ALL providers (default) |
| `--no-consensus` | Report all issues from all providers |
| `--dry-run` | Analyze without posting comments |
| `--severity` | Minimum severity to report |
| `--no-inline` | Don't post inline comments |
| `--output` | Save report to file |
| `--auto-fix` | Propose to fix with Claude Code (own PRs) |

---

### `aetheris user-story` — [Full docs](docs/commands/user-story.md)
Analyze user flows and detect frontend↔backend inconsistencies.

```bash
aetheris user-story --auto                          # Auto-detect flows
aetheris user-story --text "When user clicks..."   # From description
aetheris user-story --file user-stories.md         # From file
aetheris user-story --entry src/LoginButton.tsx    # From code entry
```

| Option | Description |
|--------|-------------|
| `--text` | User story as text description |
| `--file` | Path to markdown file with stories |
| `--entry` | Code file as entry point |
| `--auto` | Auto-detect all user flows |
| `--output-format` | `markdown`, `json`, or `both` (default) |
| `--diagram` | `mermaid`, `plantuml`, `both`, or `none` |
| `--output-file` | Output file path |
| `--severity` | Minimum severity for issues |

---

### `aetheris issues` — [Full docs](docs/commands/issues.md)
Create GitHub issues from analysis reports.

```bash
aetheris issues                                     # Create all issues
aetheris issues --dry-run                           # Preview only
aetheris issues --labels security,sprint-42
aetheris issues --assignee username --repo owner/repo
```

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview issues without creating |
| `--labels` | Additional labels (comma-separated) |
| `--assignee` | GitHub username to assign |
| `--repo` | Target repository (owner/repo) |
| `--from-report` | Process specific report file only |

---

### `aetheris pr-gen` — [Full docs](docs/commands/pr-gen.md)
Generate PRs with AI-generated fixes for bugs.

```bash
aetheris pr-gen --dry-run                          # Preview PRs
aetheris pr-gen --link-issues                      # Link to GitHub issues
aetheris pr-gen --base-branch develop
aetheris pr-gen --bug-index 0                      # Single bug
```

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview PRs without creating |
| `--base-branch` | Target base branch for PRs |
| `--from-report` | Process specific report file only |
| `--bug-index` | Process only bug at this index (0-based) |
| `--link-issues` | Link PRs to matching GitHub issues |
| `--issue-number` | Link all PRs to this issue number |

## Features

### Multi-Provider AI
- **Providers**: Gemini, Claude (Anthropic), OpenAI
- **Consensus Mode**: Only report issues found by ALL providers
- **Structured Outputs**: JSON responses validated via Pydantic

### Analysis Capabilities
- Security vulnerabilities (injections, secrets, weak crypto)
- Code quality and metrics
- Architecture review
- Dependency CVE scanning via OSV API
- CWE/OWASP classifications

### Performance
- **Smart Cache**: 60-80% API cost reduction (git SHA based)
- **Parallelization**: Dependency graph-based
- **Context Caching**: 50% cost reduction (Gemini)
- **Batch API**: 50% price reduction (Gemini)

### Automation
- GitHub Actions integration
- Auto-fix with Claude Code
- GitHub issue creation
- PR generation with fixes

## Documentation

| Topic | Link |
|-------|------|
| Installation | [docs/installation.md](docs/installation.md) |
| Configuration | [docs/configuration.md](docs/configuration.md) |
| AI Providers | [docs/ai-providers.md](docs/ai-providers.md) |
| Commands Reference | [docs/commands/README.md](docs/commands/README.md) |
| Analysis Agents | [docs/agents.md](docs/agents.md) |
| Features | [docs/features.md](docs/features.md) |
| GitHub Actions | [docs/github-actions.md](docs/github-actions.md) |
| Extensibility | [docs/PLUGINS.md](docs/PLUGINS.md) |
| Troubleshooting | [docs/troubleshooting.md](docs/troubleshooting.md) |

## Analysis Agents

Aetheris uses **6 specialized agents**:

1. **Code Analysis Expert** - Individual file analysis
2. **Architect Analysis Agent** - Architecture overview
3. **Security Analysis Agent** - Vulnerability detection
4. **Code Metrics Agent** - Complexity and duplication
5. **Dependency Vulnerability Agent** - CVE scanning
6. **Quality Assurance Agent** - Final synthesis

## Basic Configuration

Create `.env` file:

```env
# AI Provider (gemini, openai, claude)
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key_here

# Optional
AI_MODEL=gemini-2.5-pro
BATCH_SIZE=10
ENABLE_CACHE=true
```

See [Configuration Guide](docs/configuration.md) for all options.

## Example Workflows

### Full Analysis
```bash
aetheris analysis
```

### Analyze and Fix Bugs
```bash
aetheris fix --analyze-first --auto --batch-size 10
```

### PR Review with Multiple Providers
```bash
aetheris pr --url https://github.com/owner/repo/pull/123 --providers gemini,claude
```

### Create Issues and Generate Fix PRs
```bash
aetheris issues
aetheris pr-gen --link-issues
```

## Project Structure

```
aetheris/
├── src/
│   ├── core/           # Main modules (analyzer, orchestrator, cache)
│   ├── models/         # Data models
│   ├── agents/         # AI agents
│   └── services/       # Utilities
├── docs/               # Documentation
├── scripts/            # Utility scripts
└── main.py            # Entry point
```

## Supported Languages

Python, TypeScript, JavaScript, Dart/Flutter, Java, Kotlin, Swift, Go, Rust, C/C++, C#, PHP, Ruby, and more.

## Output

Reports generated in `docs/analyses/`:
- Individual file reports
- Architecture overview
- Quality assurance report
- Vulnerabilities report
- Performance metrics (JSON)

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or pull request.

## Resources

- [Repository](https://github.com/adryserage/aetheris)
- [PyPI Package](https://pypi.org/project/adryserage-aetheris/)
- [Gemini API](https://ai.google.dev/docs)
- [OpenAI API](https://platform.openai.com/docs)
- [Claude API](https://docs.anthropic.com)
