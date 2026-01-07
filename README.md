# Aetheris by Adryan - Multi-Agent Code Analysis System

[![PyPI version](https://badge.fury.io/py/adryserage-aetheris.svg)](https://badge.fury.io/py/adryserage-aetheris)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI status](https://img.shields.io/pypi/status/adryserage-aetheris.svg)](https://pypi.org/project/adryserage-aetheris/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](http://mypy-lang.org/)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey)](https://pypi.org/project/adryserage-aetheris/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

Automated code analysis system using multiple cooperating AI agents to provide comprehensive quality, security, and architecture analysis of your codebase.

## 🎯 Why Aetheris?

### The Problem

**Code reviews are slow, inconsistent, and expensive.** A senior developer spends 30-60 minutes reviewing a PR — time that could be spent building features. Junior developers miss subtle bugs. Security vulnerabilities slip through. And across a team, review quality varies wildly.

Meanwhile, existing static analysis tools are:
- **Noisy**: Thousands of low-value warnings you learn to ignore
- **Shallow**: Pattern matching that misses context-dependent issues
- **Siloed**: Security tools don't talk to quality tools don't talk to architecture tools

### The Solution

Aetheris uses **6 specialized AI agents** working together — like having a senior developer, security expert, and architect review every commit. Each agent focuses on what it does best:

| Agent | Focus | What It Catches |
|-------|-------|-----------------|
| Code Analysis | Logic & quality | Dead code, complexity, edge cases |
| Security | Vulnerabilities | Injections, secrets, weak crypto |
| Architecture | Structure | Coupling, patterns, dependencies |
| Metrics | Quantitative | Duplication, complexity scores |
| Dependencies | CVE scanning | Known vulnerabilities in packages |
| QA Synthesis | Final review | Cross-cutting concerns, priorities |

### Why You Should Use It

1. **Save Time**: A 1-hour manual review becomes a 2-minute automated scan
2. **Save Money**:
   - Smart caching reduces API costs by 60-80%
   - ROI: If Aetheris catches one bug that would've taken 2 hours to debug in production, it's paid for itself
3. **Consistency**: Every PR gets the same thorough review, 24/7
4. **Actionable**: Not just warnings — actual fixes with `aetheris fix`
5. **CI/CD Ready**: GitHub Actions template included, runs on every PR

> **Real Impact**: On a 50-file codebase, Aetheris typically finds 15-30 issues that would've been missed — security vulnerabilities, edge cases, architectural debt. Time to find them manually? Hours. Time with Aetheris? Minutes.

---

### 🆚 How Aetheris Compares

#### Feature Comparison

| Feature | SaaS Platforms | IDE Plugins | Aetheris |
|---------|----------------|-------------|----------|
| **Pricing** | $20-500/month | Free-$20/month | **Pay-per-use** (see cost table below) |
| **Data Privacy** | Code on their servers | Code on their servers | **Your API keys only** |
| **Vendor Lock-in** | Single provider | Single IDE | **Multi-provider** |
| **Auto-Fix** | Suggestions only | Limited | **Full auto-fix** with Claude Code |
| **CI/CD Native** | Extra setup | Not supported | **GitHub Actions included** |
| **Batch Analysis** | Per-file pricing | Not supported | **Entire codebase** at once |
| **Offline Mode** | No | Limited | **Yes** - run anywhere |
| **Custom Agents** | No | No | **Yes** - add your own |

#### Cost Estimation (1000 files, full analysis)

**Assumptions**: ~200 lines/file avg, 6 agents, ~4K tokens input + ~1K tokens output per file per agent

| Provider | Model | Input $/1M | Output $/1M | Est. Cost (1000 files) | With 70% Cache |
|----------|-------|------------|-------------|------------------------|----------------|
| **Gemini** | 2.0 Flash | $0.075 | $0.30 | **~$4** | **~$1.20** |
| Gemini | 3 Flash Preview | $0.50 | $3.00 | ~$30 | ~$9 |
| Gemini | 1.5 Pro | $1.25 | $5.00 | ~$60 | ~$18 |
| Gemini | 3 Pro Preview | $2.00 | $12.00 | ~$120 | ~$36 |
| OpenAI | GPT-4o-mini | $0.15 | $0.60 | ~$8 | ~$2.40 |
| OpenAI | GPT-4o | $2.50 | $10.00 | ~$120 | ~$36 |
| Anthropic | Claude Haiku | $0.25 | $1.25 | ~$12 | ~$3.60 |
| Anthropic | Claude Sonnet | $3.00 | $15.00 | ~$162 | ~$49 |

> **Recommended**: Gemini 2.0 Flash for best cost/performance ratio. With smart caching (unchanged files skipped), expect 60-80% cost reduction on repeat analyses.

#### vs. SaaS Platforms

| Solution | Monthly Cost | Notes |
|----------|-------------|-------|
| Enterprise SaaS | $200-500 | Per-seat licensing, fixed |
| Team SaaS | $50-100 | Limited features |
| **Aetheris + Gemini Flash** | **$1-5** | Pay-per-use, scales with usage |

#### Analysis Depth

| Aspect | Traditional Tools | AI Platforms | Aetheris |
|--------|-------------------|--------------|----------|
| Pattern matching | ✅ | ✅ | ✅ |
| Context awareness | ❌ | ✅ | ✅ |
| Cross-file analysis | ❌ | Limited | ✅ **Full** |
| Architecture review | ❌ | ❌ | ✅ **Dedicated agent** |
| CVE scanning | Separate tool | ❌ | ✅ **Built-in** |
| Auto-fix capability | ❌ | Suggestions | ✅ **Actual fixes** |

**What others do well** (and we complement, not replace):
- **IDE plugins**: Real-time feedback while typing — use ESLint/Pylint alongside Aetheris
- **SaaS dashboards**: Team metrics & trends — Aetheris focuses on analysis, not dashboards
- **GitHub native**: PR comments — Aetheris posts directly to your PRs

**Where Aetheris excels**:
- **Multi-agent deep analysis**: 6-10 specialized agents vs. single-model approach
- **True auto-fix**: Not suggestions — actual code changes via Claude Code
- **Cost efficiency**: Smart caching + batch API = 60-80% cost reduction
- **Privacy-first**: Your code stays with your chosen AI provider only
- **No lock-in**: Switch Gemini ↔ Claude ↔ OpenAI anytime
- **Compliance-ready**: GDPR/HIPAA/PCI-DSS detection (coming in v3.0.1)

---

### 🗺️ Roadmap

| Version | Status | Features |
|---------|--------|----------|
| **v2.5** | ✅ Released | 6 core agents, GitHub Actions, auto-fix with Claude Code |
| **v3.0** | 🚧 In Progress | Persistent configuration system (`config.json`), config hierarchy |
| **v3.0.1** | 📋 Planned | 4 new specialized agents (Performance, API Contract, Type Safety, Data Privacy) |
| **v3.0.2** | 📋 Planned | Agent selection (`--agents`), targeted fix (`--category`), presets |

#### Coming in v3.0 — Configuration System
- Local and global `config.json` files
- Config hierarchy: CLI > Local > Global > Env > Defaults
- Custom analysis presets
- Team-shareable configurations

#### Coming in v3.0.1 — Extended Agents (6 → 10 agents)

| New Agent | Focus | What It Catches |
|-----------|-------|-----------------|
| **Performance** | Runtime efficiency | O(n²) patterns, N+1 queries, memory leaks |
| **API Contract** | REST/GraphQL consistency | Method misuse, breaking changes, undocumented endpoints |
| **Type Safety** | Type discipline | `any` usage, unsafe casts, null safety violations |
| **Data Privacy** | Compliance | PII in logs, missing encryption, GDPR/HIPAA/PCI-DSS violations |

#### Coming in v3.0.2 — Agent Selection & Targeted Fix
- `--agents performance,security` — Run only specific agents
- `--category compliance` — Fix only compliance issues
- `--preset security-audit` — Pre-configured agent combinations
- `--interactive` — Visual agent selection menu

---

### 💡 Recommended Configuration

| Task | Provider | Why |
|------|----------|-----|
| **Analysis** | Gemini | 1M token context window - analyzes entire codebase at once |
| **Bug Fixing** | Claude Code | Best-in-class for code editing and automated fixes |

```bash
# .env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key
```

Then use `aetheris fix` to auto-fix bugs with Claude Code.

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

## Resources

- [Repository](https://github.com/adryserage/aetheris)
- [PyPI Package](https://pypi.org/project/adryserage-aetheris/)
- [Gemini API](https://ai.google.dev/docs)
- [OpenAI API](https://platform.openai.com/docs)
- [Claude API](https://docs.anthropic.com)
