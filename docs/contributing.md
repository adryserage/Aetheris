# Contributing

Aetheris is mostly review rules and checks, so a better rule helps as much as better code.

The full guide is [CONTRIBUTING.md](https://github.com/adryserage/aetheris/blob/main/CONTRIBUTING.md) on GitHub. It covers:

- reporting a bug, a crash or a false positive;
- proposing a new rule, with an issue form or a pull request;
- setting up a development environment and running the tests;
- opening a pull request against the `develop` branch.

Report security issues privately, as described in [Security](security.md).

Only the repository administrator cuts releases, as described in [Releasing](releasing.md).

The rule pages in this site are generated from `aetheris/rules/*.yaml`. After you change a rule, run `python scripts/gen_rules_docs.py` and commit the updated `docs/rules/` pages. The test suite fails when they are stale.
