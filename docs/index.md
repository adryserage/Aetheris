# Aetheris Documentation

**AI Code Review That Actually Works**

6 AI agents. 15+ vulnerabilities per codebase. 2 minutes instead of 2 hours.

## Quick Install

```bash
pip install adryserage-aetheris
echo "GEMINI_API_KEY=your_key" > .env
aetheris analysis
```

## What is Aetheris?

Aetheris is a multi-agent AI code analysis system that coordinates 6 specialized agents to review your codebase for:

- **Security vulnerabilities** — SQL injection, XSS, hardcoded secrets, OWASP Top 10
- **Architecture issues** — Circular dependencies, coupling problems, anti-patterns
- **Code quality** — Dead code, complexity hotspots, maintainability issues
- **Dependencies** — CVE scanning, outdated packages, license compliance
- **Metrics** — Cyclomatic complexity, duplication, LOC statistics

## Why Aetheris?

| Traditional Tools | Aetheris |
|:-----------------|:---------:|
| Thousands of noisy warnings | **Actionable insights only** |
| Pattern matching (shallow) | **Context-aware AI (deep)** |
| Security OR quality OR architecture | **All 6 agents working together** |
| Suggestions you ignore | **Auto-fix that actually works** |

## Get Started

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } **Installation**

    ---

    Install Aetheris and configure your AI provider

    [:octicons-arrow-right-24: Installation Guide](installation.md)

-   :material-cog:{ .lg .middle } **Configuration**

    ---

    Configure AI providers, timeouts, and output formats

    [:octicons-arrow-right-24: Configuration](configuration.md)

-   :material-console:{ .lg .middle } **Commands**

    ---

    Learn all available CLI commands

    [:octicons-arrow-right-24: Commands Reference](commands/README.md)

-   :material-robot:{ .lg .middle } **AI Agents**

    ---

    Understand the 6 specialized analysis agents

    [:octicons-arrow-right-24: Agents Guide](agents.md)

</div>

## Features

- **Multi-Provider Support** — Gemini, OpenAI, Claude
- **Incremental Analysis** — Analyze only changed files with `--reanalyze`
- **Timeout Control** — Set analysis duration with `--timeout 30m`
- **Auto-Fix** — Fix issues automatically with Claude Code
- **GitHub Integration** — Create issues, review PRs, generate fix PRs
- **Smart Caching** — 60-80% cost reduction on repeat analyses

## Links

- [GitHub Repository](https://github.com/adryserage/aetheris)
- [PyPI Package](https://pypi.org/project/adryserage-aetheris/)
- [Get Free Gemini API Key](https://ai.google.dev)
