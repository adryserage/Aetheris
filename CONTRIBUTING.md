# Contributing to Aetheris

Thanks for helping. Aetheris is mostly review rules and checks, so a better rule is as useful as better code.

## Ways to contribute

- Report a bug or a crash: open a [bug report](https://github.com/adryserage/aetheris/issues/new?template=bug_report.yml).
- Report a false positive: a check flagged code that is fine. Use the [false positive form](https://github.com/adryserage/aetheris/issues/new?template=false_positive.yml).
- Propose a rule: something a reviewer should catch and Aetheris misses. Use the [new rule form](https://github.com/adryserage/aetheris/issues/new?template=new_rule.yml), or open a pull request directly.
- Security issues go through GitHub's [private vulnerability report](https://github.com/adryserage/aetheris/security/advisories/new), never a public issue. See [SECURITY.md](SECURITY.md).

## Development setup

You need Python 3.10 or later and git.

```bash
git clone https://github.com/adryserage/aetheris
cd aetheris
python -m venv .venv && source .venv/bin/activate
pip install -e . pytest pytest-cov black isort flake8 mypy types-requests types-PyYAML
pytest tests -q
```

Run the server from your checkout in any MCP client with `uvx --from /path/to/aetheris adryserage-aetheris`.

## Pull requests

1. Fork the repository and create a branch from `main`.
2. Make one change per pull request: one rule, one fix, one check.
3. Run the same checks as CI:

   ```bash
   black --check --line-length 100 aetheris tests
   isort --check-only --profile black aetheris tests
   flake8 aetheris tests --max-line-length=100 --extend-ignore=E203,W503,E501,E402,F401
   mypy aetheris --ignore-missing-imports
   pytest tests -q
   ```

4. Add a line under `[Unreleased]` in [CHANGELOG.md](CHANGELOG.md) when users will notice the change.
5. Open the pull request against `main`. The maintainer cuts a release only when a change matters to many users, so a merged change can wait a while under `[Unreleased]`.

## Writing a rule

Rules live in [`aetheris/rules/`](aetheris/rules), one YAML file per agent. The registry validates every file when the server starts, and the tests fail on a malformed rule.

```yaml
  - id: SEC-0NN
    title: Signature or token verification skipped
    severity: critical
    check: >-
      Look for ... Report ... A ... is not a violation.
    languages: []
    references: [CWE-347, "OWASP A02:2021"]
```

- `id`: the agent prefix (`SEC`, `ARC`, `CQ`, `MET`, `DEP`, `QA`, `TYP`, `PERF`, `API`, `PRIV`) and the next free three-digit number. Never reuse or renumber an existing id.
- `severity`: `critical` for something exploitable or data loss, `high` for a likely bug or security weakness, `medium` for a maintainability or performance risk, `low` for style-level debt, `info` for metrics and guidance.
- `check`: one to four sentences in imperative English. Say exactly what code to look for, and what is *not* a violation, so the assistant does not flag safe code.
- `languages`: empty for every language, otherwise lowercase names such as `python` or `typescript`.
- `references`: only real, checkable identifiers (CWE, OWASP, RFC, GDPR article). Leave the list empty rather than guess.

## Writing a check

Checks are deterministic code in [`aetheris/checks/`](aetheris/checks). They must:

- build every finding with `make_finding`, and map the check name to its rule in `RULE_IDS` (`aetheris/checks/base.py`);
- read files only through `resolve_in_root` and `read_text` in `aetheris/files.py`, never outside the project directory;
- make no network call, except OSV in the dependency check;
- never print to stdout, which carries the MCP protocol;
- come with tests that run offline.

## License

By contributing, you agree that your contribution is licensed under the [Apache License 2.0](LICENSE), as section 5 of the license states.
