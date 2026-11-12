# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 4.x     | Yes       |
| < 4.0   | No        |

Version 3.x and earlier are no longer maintained. They called AI providers with your own API key; 4.x does not.

## Reporting a vulnerability

Do not report security vulnerabilities through public GitHub issues.

Send them by email to security@allowebs.com, or use GitHub's private vulnerability reporting from the [Security tab](https://github.com/adryserage/aetheris/security) ("Report a vulnerability").

Please include:

- the type of issue and its impact
- the affected file paths and the version, tag or commit
- the configuration needed to reproduce it
- step-by-step reproduction, and a proof of concept if you have one

### Response timeline

- Acknowledgement within 48 hours.
- An assessment within 7 days.
- A fix for verified vulnerabilities, usually within 30 days.

You will get credit in the release notes if you want it.

### Safe harbor

We consider security research conducted in good faith to be authorized. We will not pursue legal action against researchers who avoid privacy violations, data destruction and service interruption, only use accounts they own or are allowed to use, and do not exploit a vulnerability beyond what is needed to demonstrate it.

## What Aetheris does with your code

- Aetheris never calls an AI provider. Your assistant does the reasoning, with its own provider and its own data policy.
- In local mode, the server reads files only under the project directory (`AETHERIS_ROOT`, or the directory it starts in). Paths that escape it are refused.
- The only network call is the dependency agent's `osv_lookup` check (`run_checks` with `agent="dependency"`), which sends package names, ecosystems and versions to the [OSV API](https://osv.dev). No source code leaves your machine.
- Secrets found by the security agent's `secret_scan` check are masked in every result.
- `aetheris install` edits the MCP configuration of your clients (Claude Code, Cursor, Claude Desktop). It only adds or removes the `aetheris` entry, and it never rewrites a file it cannot parse.
