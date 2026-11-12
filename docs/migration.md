# Migrating from 3.x

Aetheris 3.x was a command-line tool. It sent your code to Gemini, OpenAI or Claude with your own API key and wrote analysis reports. Aetheris 4 is an MCP server: your AI coding assistant runs the review, using the rules and checks Aetheris serves. There is no API key and no AI call.

Version 4 is in development. PyPI still has 3.0.0 as the latest release.

## Removed commands

These commands no longer exist: `analysis`, `fix`, `pr`, `pr-gen`, `issues`, `user-story`, `stats`, `run`, `cleanup` and `validate-package`. The `--cli` and `-c` flags are gone too. With 4.0, `aetheris` only has `install`, `uninstall` and `serve`.

Also removed: the interactive mode, the Gemini, OpenAI and Claude providers, the orchestrator, the headless mode (`aetheris run`) and its security profiles, the Claude Code integration, the GitHub commands (issues, pull requests, fixes), statistics, the translation of the CLI, the MCP client, skills, the Railway worker and user story analysis.

A removed command prints a notice to standard error and exits with code 2, so a CI job that still calls it fails with a clear message:

```text
$ aetheris analysis
`aetheris analysis` was removed in Aetheris 4.
...
$ echo $?
2
```

## Keep using 3.x

Pin the last 3.x release:

```bash
pip install "adryserage-aetheris==3.0.0"
```

The 3.0.0 documentation is in the [v3.0.0 tag](https://github.com/adryserage/aetheris/tree/v3.0.0). Version 3.x no longer gets fixes, including security fixes.

## Move to 4

1. Install the server in your client: `uvx --from adryserage-aetheris aetheris install`. See [Installation](installation.md).
2. Ask your assistant for the review you used to run from the command line, such as "review my changes with Aetheris".
3. Remove the API keys that only Aetheris used.

Each 3.x workflow maps to the [review flow](review-flow.md). The assistant plans the review, reads the rules, runs the checks and writes the report. Aetheris no longer writes report files, so keep what you need from the assistant's answer.

Every change is listed in the [changelog](https://github.com/adryserage/aetheris/blob/main/CHANGELOG.md).
