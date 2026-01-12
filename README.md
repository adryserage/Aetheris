# Aetheris — AI Code Review That Actually Works

<p align="center">
  <strong>6 AI agents. Automated vulnerability detection. Minutes instead of hours.</strong>
</p>

<p align="center">
  <a href="https://badge.fury.io/py/adryserage-aetheris"><img src="https://badge.fury.io/py/adryserage-aetheris.svg" alt="PyPI version"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+"></a>
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
  <a href="https://pypi.org/project/adryserage-aetheris/"><img src="https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey" alt="Platform"></a>
  
</p>

<p align="center">
  <a href="https://pepy.tech/project/adryserage-aetheris"><img src="https://static.pepy.tech/badge/adryserage-aetheris" alt="Total Downloads"></a>
  <a href="https://pepy.tech/project/adryserage-aetheris"><img src="https://static.pepy.tech/badge/adryserage-aetheris/month" alt="Monthly Downloads"></a>
  <a href="https://pepy.tech/project/adryserage-aetheris"><img src="https://static.pepy.tech/badge/adryserage-aetheris/week" alt="Weekly Downloads"></a>
</p>

<p align="center">
  <a href="https://pepy.tech/project/adryserage-aetheris">View Full Download History</a> |
  <a href="https://pypistats.org/packages/adryserage-aetheris">Detailed Statistics</a>
</p>

<p align="center">
  <a href="https://adryserage.github.io/aetheris/"><img src="https://img.shields.io/badge/docs-GitHub%20Pages-blue" alt="Documentation"></a>
</p>

<p align="center">
  <a href="https://adryserage.github.io/aetheris/quickstart/">Quick Start</a> |
  <a href="https://adryserage.github.io/aetheris/">Demo</a> |
  <a href="https://adryserage.github.io/aetheris/agents/">Architecture</a> |
  <a href="https://adryserage.github.io/aetheris/">Documentation</a>
</p>

---

<!-- ============================================================
     MARKETING SECTION — Why Aetheris?
     ============================================================ -->

## Help Shape Aetheris

**Should Aetheris become Open Source?** [Cast your vote](https://adryanserage.ca/poll/aetheris)

<p align="center">
  <a href="https://adryanserage.ca/poll/aetheris?vote=Yes%2C%20open%20source%20it!"><img src="https://adryanserage.ca/api/poll/svg?pollId=aetheris&option=Yes%2C%20open%20source%20it!&color=%2322c55e" alt="Yes, open source it!"></a>
  <a href="https://adryanserage.ca/poll/aetheris?vote=No%2C%20keep%20it%20private"><img src="https://adryanserage.ca/api/poll/svg?pollId=aetheris&option=No%2C%20keep%20it%20private&color=%23ef4444" alt="No, keep it private"></a>
  <a href="https://adryanserage.ca/poll/aetheris?vote=I%20don%27t%20mind%20either%20way"><img src="https://adryanserage.ca/api/poll/svg?pollId=aetheris&option=I%20don%27t%20mind%20either%20way&color=%236366f1" alt="I don't mind"></a>
</p>

---

## Stop Shipping Bugs. Start Shipping Confidence.

**Your code reviews are broken.** Senior devs spend hours reviewing PRs. Junior devs miss critical bugs. Security vulnerabilities slip into production. Sound familiar?

**Aetheris fixes this.** It's like having a senior developer, security expert, and architect review every commit — in minutes, not hours.

| Your Pain Point | Aetheris Solution |
|:----------------|:------------------|
| "Code review takes forever" | **Fast automated scans** |
| "We keep shipping the same bugs" | **Consistent, thorough reviews 24/7** |
| "Security audits are expensive" | **Built-in CVE + OWASP scanning** |
| "Junior devs miss edge cases" | **AI catches what humans miss** |
| "We're locked into [expensive tool]" | **Pay-per-use, switch providers anytime** |

```bash
pip install adryserage-aetheris && aetheris analysis
```

**That's it.** No account creation. No credit card. No 30-minute setup call.

---

## Features

- **Headless Mode (v2.8)** — Non-interactive execution for CI/CD with `aetheris run <task-file>`
- **Deterministic Execution** — Reproducible results with `--seed` and `--no-timestamps` options
- **Security Profiles** — Control operations with `--profile safe|ci|dev|unrestricted`
- **Configurable Timeout** — Set analysis duration with `--timeout 30m`, `--timeout 2h`, or `--timeout 0` (unlimited)
- **Heartbeat Monitor** — Progress indicator every 10 minutes for long-running analyses
- **Incremental Reanalysis** — Use `--reanalyze` / `-r` to analyze only files changed since last run
- **Smart Change Detection** — Auto-detects modifications via git diff or file timestamps
- **Cost-Efficient Updates** — Skip unchanged files, preserve previous results, reduce API calls
- **Graceful Interruption** — Partial results saved when timeout is reached
- **Multi-Provider Support** — Switch between Gemini, OpenAI, and Claude with `--provider`
- **Auto-Fix Integration** — Fix issues automatically with Claude Code via `aetheris fix --auto`
- **GitHub Integration** — Create issues, review PRs, generate fix PRs directly
- **Smart Caching** — 60-80% cost reduction on repeat analyses
- **Artifact Cleanup** — Remove development artifacts before packaging with `aetheris cleanup`
- **Secret Scanner** — Detect exposed credentials with confidence levels (high/medium/low)
- **Package Validation** — Pre-publication security checks with `aetheris validate-package`
- **Multi-Language Support** — CLI available in English and French with `--lang` flag or `AETHERIS_LANG` env var

| Traditional Tools | Aetheris |
|:-----------------|:---------|
| Thousands of noisy warnings | **Actionable insights only** |
| Pattern matching (shallow) | **Context-aware AI (deep)** |
| Security OR quality OR architecture | **All 6 agents working together** |
| Suggestions you ignore | **Auto-fix that actually works** |

## Pricing That Makes Sense

**No subscriptions. No per-seat licensing. Just pay for what you use.**

| What You Get | Enterprise SaaS | Aetheris |
|:-------------|:---------------:|:--------:|
| Monthly cost (10 devs) | $200-500/mo | **$5-20/mo** |
| Your code stays... | On their servers | **With your AI provider** |
| Vendor lock-in | Yes | **Switch providers anytime** |
| Auto-fix capability | Suggestions only | **Actual code changes** |

### Real Cost Example (1,000 files)

| Provider | Economy Model | With 70% Cache |
|:---------|:-------------:|:--------------:|
| **Gemini Flash** | ~$3-10 | **~$1-3** |
| GPT-4o-mini | ~$5-15 | ~$2-5 |
| Claude Haiku | ~$10-20 | ~$3-6 |

> Smart caching skips unchanged files. Expect **60-80% cost reduction** on repeat analyses.
>
> **Pricing Note**: AI API pricing changes frequently. Check current rates: [Gemini](https://ai.google.dev/pricing) | [OpenAI](https://openai.com/api/pricing/) | [Anthropic](https://www.anthropic.com/pricing)

---

<!-- ============================================================
     TECHNICAL SECTION — How Aetheris Works
     ============================================================ -->

## How It Works

<p align="center">
  <img src="https://adryserage.github.io/aetheris/assets/diagrams/how-it-works.svg" alt="How Aetheris Works" width="800">
</p>

## Architecture

Aetheris coordinates 6 specialized AI agents through a central orchestrator. Each agent analyzes a specific domain, and the QA Synthesis agent consolidates findings into prioritized, actionable reports.

<p align="center">
  <img src="https://adryserage.github.io/aetheris/assets/diagrams/architecture.svg" alt="Aetheris Architecture" width="900">
</p>

### 6 Specialized AI Agents

| Agent | Responsibility |
|:------|:---------------|
| **Security** | SQL injection, XSS, secrets in code, OWASP Top 10, weak crypto |
| **Architecture** | Coupling issues, circular dependencies, anti-patterns, layering violations |
| **Code Quality** | Dead code, complexity hotspots, edge cases, maintainability issues |
| **Metrics** | Cyclomatic complexity, duplication, maintainability index, LOC stats |
| **Dependency** | CVE scanning via OSV database, outdated packages, license compliance |
| **QA Synthesis** | Prioritizes findings, eliminates false positives, generates final report |

### Integration Points

| Integration | How It Works |
|:------------|:-------------|
| **AI Providers** | Gemini (default), OpenAI, Claude — switch with `--provider` flag |
| **GitHub** | Create issues from findings, review PRs, generate fix PRs |
| **CI/CD** | GitHub Actions template included, GitLab CI, Jenkins compatible |
| **Output Formats** | Markdown reports, JSON metrics, console summaries |

---

## Features

- **Headless Mode (v2.8)** — Non-interactive execution for CI/CD with `aetheris run <task-file>`
- **Deterministic Execution** — Reproducible results with `--seed` and `--no-timestamps` options
- **Security Profiles** — Control operations with `--profile safe|ci|dev|unrestricted`
- **Configurable Timeout** — Set analysis duration with `--timeout 30m`, `--timeout 2h`, or `--timeout 0` (unlimited)
- **Heartbeat Monitor** — Progress indicator every 10 minutes for long-running analyses
- **Incremental Reanalysis** — Use `--reanalyze` / `-r` to analyze only files changed since last run
- **Smart Change Detection** — Auto-detects modifications via git diff or file timestamps
- **Cost-Efficient Updates** — Skip unchanged files, preserve previous results, reduce API calls
- **Graceful Interruption** — Partial results saved when timeout is reached
- **Multi-Provider Support** — Switch between Gemini, OpenAI, and Claude with `--provider`
- **Auto-Fix Integration** — Fix issues automatically with Claude Code via `aetheris fix --auto`
- **GitHub Integration** — Create issues, review PRs, generate fix PRs directly
- **Smart Caching** — 60-80% cost reduction on repeat analyses
- **Artifact Cleanup** — Remove development artifacts before packaging with `aetheris cleanup`
- **Secret Scanner** — Detect exposed credentials with confidence levels (high/medium/low)
- **Package Validation** — Pre-publication security checks with `aetheris validate-package`
- **Multi-Language Support** — CLI available in English and French with `--lang` flag or `AETHERIS_LANG` env var

```bash
# Full analysis
aetheris analysis

# Incremental reanalysis (changed files only)
aetheris analysis --reanalyze

# With timeout for large codebases
aetheris analysis -r --timeout 30m

# Headless mode for CI/CD (v2.8)
aetheris run task.json --profile ci

# Auto-fix issues
aetheris fix --analyze-first --auto
```

---

## See It In Action

```bash
# Analyze your entire codebase
$ aetheris analysis

  Scanning 127 files...
  Running 6 AI agents...

  CRITICAL: SQL injection in user_service.py:45
  HIGH: Hardcoded API key in config.py:12
  HIGH: N+1 query pattern in orders.py:78-92
  MEDIUM: Circular dependency: auth -> users -> auth

  23 issues found | 4 critical | 8 high | 11 medium
  Report: docs/analyses/quality_assurance_report.md

# Auto-fix with Claude Code
$ aetheris fix --analyze-first --auto
  Fixed 19/23 issues automatically
```

---

## Get Started in 30 Seconds

```bash
# 1. Install
pip install adryserage-aetheris

# 2. Configure (free Gemini API key: https://ai.google.dev)
echo "GEMINI_API_KEY=your_key" > .env
echo ".env" >> .gitignore  # IMPORTANT: Never commit API keys

# 3. Analyze
aetheris analysis
```

---

<!-- ============================================================
     REFERENCE SECTION — Commands, Config, Docs
     ============================================================ -->

## Complete Command Suite

| Command | Purpose | Example |
|:--------|:--------|:--------|
| `aetheris analysis` | Deep codebase scan | `aetheris analysis --reanalyze --timeout 30m` |
| `aetheris run` | Headless execution for CI/CD | `aetheris run task.json --profile ci` |
| `aetheris stats` | View statistics & ROI dashboard | `aetheris stats --period week --export json` |
| `aetheris fix` | Auto-fix with Claude Code | `aetheris fix --analyze-first --auto` |
| `aetheris pr` | GitHub PR reviews | `aetheris pr --url <pr-url>` |
| `aetheris issues` | Create GitHub issues | `aetheris issues --labels security` |
| `aetheris user-story` | Flow analysis | `aetheris user-story --auto` |
| `aetheris pr-gen` | Generate fix PRs | `aetheris pr-gen --link-issues` |
| `aetheris cleanup` | Remove artifacts before packaging | `aetheris cleanup --dry-run` |
| `aetheris validate-package` | Pre-publication security check | `aetheris validate-package --fix` |

[Full command documentation](docs/commands/README.md)

---

## Works With Your Stack

<p align="center">
  <strong>Python</strong> | <strong>TypeScript</strong> | <strong>JavaScript</strong> | <strong>Go</strong> | <strong>Rust</strong> | <strong>Java</strong> | <strong>Kotlin</strong> | <strong>Swift</strong> | <strong>Dart/Flutter</strong> | <strong>C/C++</strong> | <strong>C#</strong> | <strong>PHP</strong> | <strong>Ruby</strong>
</p>

**AI Providers:** Gemini | OpenAI | Claude (Anthropic)

**CI/CD:** GitHub Actions template included | GitLab CI | Jenkins

---

## Roadmap

| Version | Status | Highlights |
|:--------|:------:|:-----------|
| **v2.8** | ✅ Done | Headless mode for CI/CD automation |
| **v3.0** | Planned | Persistent config (JSON), security profiles |
| **v3.1** | Planned | Enhanced security & Git strategy |
| **v3.2** | Planned | CI/CD templates (GitHub Actions, GitLab CI) |
| **v4.0** | Planned | Multi-model support (Gemini, Claude, OpenRouter) |

---

## Documentation

**[Full Documentation](https://adryserage.github.io/aetheris/)** — Complete guides, tutorials, and API reference

| Getting Started | Reference | Advanced |
|:----------------|:----------|:---------|
| [Quick Start Guide](https://adryserage.github.io/aetheris/quickstart/) | [CLI Commands](https://adryserage.github.io/aetheris/commands/) | [GitHub Actions](https://adryserage.github.io/aetheris/advanced/github-actions/) |
| [Installation](https://adryserage.github.io/aetheris/getting-started/installation/) | [AI Providers](https://adryserage.github.io/aetheris/reference/ai-providers/) | [Extending Agents](https://adryserage.github.io/aetheris/advanced/plugins/) |
| [Configuration](https://adryserage.github.io/aetheris/getting-started/configuration/) | [Analysis Agents](https://adryserage.github.io/aetheris/reference/agents/) | [Troubleshooting](https://adryserage.github.io/aetheris/advanced/troubleshooting/) |

**Local docs:** [docs/](docs/) — Markdown source files

---

## Important Safety Information

<details>
<summary><strong>Data Privacy Notice</strong></summary>

Aetheris sends your source code to third-party AI providers (Google Gemini, OpenAI, or Anthropic) for analysis. Before using on proprietary codebases:

1. **Review your organization's data policies** — Some companies prohibit sending source code to external services
2. **Use Enterprise/Zero Data Retention plans**:
   - [Google Vertex AI](https://cloud.google.com/vertex-ai) — Data not used for training
   - [OpenAI Enterprise](https://openai.com/enterprise) — Zero data retention
   - [Anthropic API](https://www.anthropic.com/api) — Data not used for training by default
3. **Check data residency requirements** — For regulated industries (healthcare, finance)

**Your API keys are never shared** — Aetheris connects directly to your chosen provider.

</details>

<details>
<summary><strong>Auto-Fix Safety Guidelines</strong></summary>

The `--auto` flag applies AI-generated code changes **without human review**. Risks include:

| Risk | Description |
|:-----|:------------|
| **Hallucinations** | LLMs may generate plausible but incorrect code |
| **Security vulnerabilities** | Fixes may introduce new attack vectors |
| **Business logic removal** | AI may delete critical code paths |

**Safe workflow:**
```bash
aetheris fix --analyze-first --auto  # Run fixes
git diff                              # Review ALL changes (mandatory)
pytest                                # Run tests
git add -p                            # Stage interactively
```

</details>

---

## Ready to Ship Better Code?

```bash
pip install adryserage-aetheris && aetheris analysis
```

<p align="center">
  <a href="https://pypi.org/project/adryserage-aetheris/"><strong>Install from PyPI</strong></a> |
  <a href="https://github.com/adryserage/aetheris"><strong>View on GitHub</strong></a> |
  <a href="https://ai.google.dev"><strong>Get Free Gemini API Key</strong></a>
</p>

---

<p align="center">
  <sub>Built with care by <a href="https://adryanserage.ca">Adryan Serage</a></sub>
</p>
