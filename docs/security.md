# Security

## What the server reads and sends

- Aetheris never calls an AI provider. Your assistant does the reasoning, with its own provider and its own data policy. That provider still sees whatever your assistant reads, as it does without Aetheris.
- The server reads files only under the project directory: `AETHERIS_ROOT` if set, otherwise the directory it starts in. A path that escapes it, through `..` or a symlink, is refused.
- The only network call is the `osv_lookup` check of the dependency agent (`run_checks` with `agent="dependency"`). It sends package names, ecosystems and versions to the [OSV API](https://osv.dev). No source code leaves your machine.
- Secrets found by the `secret_scan` check are masked in every result.
- `aetheris install` edits the MCP configuration of your clients (Claude Code, Cursor, Claude Desktop). It only adds or removes the `aetheris` entry, and it never rewrites a file it cannot parse.

## Reporting a vulnerability

Do not report a vulnerability in a public issue. Use GitHub's private report instead:

1. Open the [Security tab](https://github.com/adryserage/aetheris/security) of the repository and choose "Report a vulnerability", or go straight to the [private report form](https://github.com/adryserage/aetheris/security/advisories/new).
2. Describe the type of issue and its impact, the affected files and the version, tag or commit, the configuration needed to reproduce it, and the steps to reproduce it.

Only the maintainers see the report. It becomes a public security advisory once the fix is released.

You get an acknowledgement within 48 hours and an assessment within 7 days. A fix for a verified vulnerability usually follows within 30 days. Good-faith research is covered by the safe harbor in [SECURITY.md](https://github.com/adryserage/aetheris/blob/main/SECURITY.md), which also lists the supported versions: 4.x is supported, earlier versions are not.
