# Aetheris

Aetheris is an MCP server that gives your AI coding assistant review rules and checks that need no AI. Claude Code, Cursor or any MCP client calls it to review a change, a pull request or a whole repository. Your assistant does the reasoning, so Aetheris needs no API key and costs nothing to run.

!!! note "Coming from 3.x"
    Version 4.0 replaces the 3.x command-line tool, which called Gemini, OpenAI or Claude with your own API key. If you used it, see [Migrating from 3.x](migration.md).

## What it provides

- Review rules: 152 rules across 10 agents (security, architecture, code quality, metrics, dependencies, QA synthesis, type safety, performance, API contracts, data privacy). Each rule says what to look for and how severe a violation is. See the [rules reference](rules/index.md).
- Deterministic checks: secret scanning, known vulnerabilities in your dependencies from the [OSV](https://osv.dev) database, code metrics, circular imports and code patterns. They return the same result for the same input. See [Agents](agents.md).
- Playbooks: review methods adapted from [Trail of Bits Skills](https://github.com/trailofbits/skills), such as a differential review of a diff. See [Playbooks](playbooks.md).

Aetheris never calls a language model. Your assistant chooses which tools to call, reads your code and writes the review.

## Where to start

1. [Install](installation.md) the server in your client.
2. Ask your assistant: "review my changes with Aetheris".
3. Read [the review flow](review-flow.md) to see which tools it calls and in what order.

## Pages

| Page | What it covers |
| --- | --- |
| [Installation](installation.md) | `aetheris install`, manual setup, running from a checkout |
| [Review flow](review-flow.md) | The six tools in order, with a real example |
| [Tools](tools.md) | Arguments, defaults, results and limits of each tool |
| [Agents](agents.md) | The 10 agents, their checks and their playbooks |
| [Rules](rules/index.md) | Every rule, generated from the YAML files |
| [Playbooks](playbooks.md) | The 7 playbooks and their attribution |
| [Security](security.md) | What the server reads and sends, and how to report a vulnerability |
| [Migrating from 3.x](migration.md) | Removed commands and how to keep 3.0.0 |
| [Contributing](contributing.md) | Bug reports, new rules, pull requests |
| [Releasing](releasing.md) | Who can release, and the release steps |

Aetheris is open source under the [Apache License 2.0](https://github.com/adryserage/aetheris/blob/main/LICENSE). The source is on [GitHub](https://github.com/adryserage/aetheris).
