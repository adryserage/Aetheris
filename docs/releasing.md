# Releasing

This page is for the repository administrator, the only person who can release. Releases are rare: one is cut only when a change matters to many users. Until then, merged changes wait under `[Unreleased]` in `CHANGELOG.md`.

`main` changes only through a pull request. A GitHub ruleset enforces this: the CI must pass, the pull request is merged with a merge commit or squashed, and `main` cannot be force-pushed or deleted. Work happens on short-lived branches such as `fix/...` or `release/X.Y.Z`, deleted once merged. Pushing a `vX.Y.Z` tag on `main` starts the release workflow.

## Who does what

- Contributors open pull requests to `main`, from a fork or a branch.
- Only repository administrators can release. The "version tags" ruleset lets only them create, move or delete a `v*` tag, so a contributor cannot start the release workflow. The administrator is also the only required reviewer of the `pypi` environment.
- The repository is on a personal GitHub account, where the owner is the only administrator. The owner is therefore the one person who cuts releases.

The `main` ruleset requires no approval yet, because the project has no reviewer other than the author. Once it has one, raise "Required approvals" to 1 in the ruleset.

## Steps

The example releases 4.0.1. Pick the number from the last tag:

- a small change, such as a fix or a minor improvement, raises the last number (4.0.0 to 4.0.1);
- a security fix raises the middle number and resets the last one (4.0.1 to 4.1.0);
- a major change, such as a new major version of a dependency or a change that breaks existing setups, raises the first number and resets the others (4.1.0 to 5.0.0).

1. On a `release/4.0.1` branch from `main`, prepare the version:

    - set `version = "4.0.1"` in `pyproject.toml` and `__version__ = "4.0.1"` in `aetheris/__init__.py`;
    - in `CHANGELOG.md`, rename `## [Unreleased]` to `## [4.0.1] - YYYY-MM-DD` and add an empty `## [Unreleased]` above it;
    - at the bottom of `CHANGELOG.md`, update the comparison links:

    ```text
    [Unreleased]: https://github.com/adryserage/aetheris/compare/v4.0.1...HEAD
    [4.0.1]: https://github.com/adryserage/aetheris/compare/v4.0.0...v4.0.1
    ```

    Then commit and push:

    ```bash
    git checkout main && git pull && git checkout -b release/4.0.1
    git commit -am "release: 4.0.1" && git push -u origin release/4.0.1
    ```

2. Open an issue, then a pull request from `release/4.0.1` to `main` that closes it. Merge it once the CI passes:

    ```bash
    gh issue create --title "Release 4.0.1" --body "Release 4.0.1"
    gh pr create --base main --head release/4.0.1 --title "release: 4.0.1" --body "Closes #<issue>"
    gh pr checks <pr> --watch
    gh pr merge <pr> --merge
    ```

3. Check the version number, then tag `main` and push the tag. The tag push cannot be undone: the GitHub release and the documentation go public a few minutes later, without waiting for any approval.

    ```bash
    git checkout main && git pull && git tag v4.0.1 && git push origin v4.0.1
    ```

4. Approve the publication. In the Actions tab, open the "Release" run, click "Review deployments", select `pypi` and click "Approve".

## What the release workflow does

`release.yml` first checks that the tag matches the version in `pyproject.toml`. If they differ, it stops and nothing is published.

It then builds the package and the documentation. These steps follow in parallel:

- the GitHub release is created, with the notes taken from the version's section in `CHANGELOG.md`;
- this documentation is deployed to GitHub Pages;
- the package waits for the `pypi` approval, then goes to PyPI with Trusted Publishing, without a token.

Only PyPI waits for the approval. If the approval is refused or the PyPI upload fails, the GitHub release still exists, for a version nobody can install. Fix the cause and run the release again (below), or delete that GitHub release.

The GitHub release fails when `CHANGELOG.md` has no section for the version. A section with a "Changements incompatibles" (breaking changes) heading gets a warning at the top of the notes.

## Running a release again

To rerun the workflow for a tag that already exists:

```bash
gh workflow run release.yml --ref v4.0.1 -f tag=v4.0.1
```

PyPI refuses a version it already has. When the package is already published, add `-f skip_pypi=true`. Add `-f skip_docs=true` to leave the documentation as it is.
