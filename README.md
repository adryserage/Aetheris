# Aetheris

Code review rules and reproducible checks for your AI coding assistant, served over MCP. Your assistant does the reasoning, so Aetheris needs no API key and costs nothing to run.

[Lire en français](https://github.com/adryserage/aetheris/blob/main/README.fr.md)

> **Status:** Aetheris 4.0 is in development on the `develop` branch. The latest release on PyPI is 3.0.0, the older command-line tool that calls Gemini, OpenAI or Claude with your own API key. Its documentation is in the [3.0.0 tag](https://github.com/adryserage/aetheris/tree/v3.0.0).

## What it does

Ask Claude Code, Cursor or any MCP client to review a change, and it can call Aetheris for two kinds of help:

- Review rules: for each category, Aetheris returns what to check, how to rate severity and the report format to fill in. Categories: security, performance, type safety, data privacy, API contracts, code review, architecture, QA, pull request review and user flows.
- Checks that need no AI: secret scanning, known vulnerabilities in your dependencies (from the [OSV](https://osv.dev) database), code metrics, dependency graphs and API call tracing. They return the same result every time.

Your assistant chooses which tools to call, reads your code and writes the review. Aetheris never calls a language model.

## Install

Aetheris runs locally through [`uvx`](https://docs.astral.sh/uv/). There is no account to create.

### Claude Code

```bash
claude mcp add aetheris -- uvx adryserage-aetheris
```

### Cursor

Add this to `.cursor/mcp.json` in your project, or to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "aetheris": {
      "command": "uvx",
      "args": ["adryserage-aetheris"]
    }
  }
}
```

### Other MCP clients

Run `uvx adryserage-aetheris` as a stdio server.

Then ask your assistant something like "review my staged changes with Aetheris" or "run an Aetheris security audit on this repository".

## Tools

The tool list below is the 4.0 plan and may change before the release.

| Tool | What it returns |
|------|-----------------|
| `list_rule_categories` | Rule categories and preset rule sets, such as a security audit |
| `get_rules` | The rules for one category, optionally for one language, with the expected report format |
| `scan_secrets` | Credentials found in files or content, masked |
| `parse_dependencies` | Packages and versions from `requirements.txt`, `pyproject.toml`, `package.json` or `pubspec.yaml` |
| `check_vulnerabilities` | Known vulnerabilities for those packages, from OSV |
| `scan_patterns` | Pattern matches for security, performance, typing, personal data or API issues |
| `code_metrics` | Line counts, cyclomatic complexity, nesting depth and duplication |
| `dependency_graph` | Imports between files, cycles and dependents |
| `impact_of` | Files affected by a change to a given file |
| `detect_changes` | Files changed or deleted since a git reference |
| `list_source_files` | Files worth reviewing, after `.gitignore` and common exclusions |
| `prioritize_files` | A review order for changed files |
| `list_exports` | The public API of a file |
| `trace_api_flows` | API calls with no matching endpoint, and endpoints nothing calls |
| `parse_user_stories` | Structured user stories from text, Markdown or Gherkin, with a Mermaid flow diagram |

## What leaves your machine

In local mode, Aetheris reads files under your project directory and sends nothing to any AI provider. The only network call is `check_vulnerabilities`, which sends package names and versions to the OSV API. Your assistant's own provider still sees whatever your assistant reads, as it does without Aetheris.

## Contributing

Bug reports and ideas go to [GitHub Issues](https://github.com/adryserage/aetheris/issues). Pull requests target the `develop` branch. Improvements to the review rules are as welcome as code.

## Versions

Aetheris follows [semantic versioning](https://semver.org). Every change is listed in [CHANGELOG.md](https://github.com/adryserage/aetheris/blob/main/CHANGELOG.md), and every version has a tag and a [GitHub release](https://github.com/adryserage/aetheris/releases).

## Coming from 3.x

Version 4.0 removes the command-line tool, the AI provider integrations and the Railway worker. To keep using the CLI, pin the last 3.x release:

```bash
pip install "adryserage-aetheris==3.0.0"
```

## License

Apache License 2.0. See [LICENSE](https://github.com/adryserage/aetheris/blob/main/LICENSE) and [NOTICE](https://github.com/adryserage/aetheris/blob/main/NOTICE).
