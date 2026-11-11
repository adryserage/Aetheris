import pytest

from aetheris.changes import GitError, changed_files
from tests.conftest import write


def test_modified_and_untracked_files_are_listed(git_repo):
    write(git_repo, "tracked.py", "x = 2\n")
    write(git_repo, "new.py", "y = 1\n")
    write(git_repo, "pkg/deep.py", "z = 1\n")
    assert changed_files(git_repo) == ["new.py", "pkg/deep.py", "tracked.py"]


def test_clean_repo_has_no_changes(git_repo):
    assert changed_files(git_repo) == []


def test_option_like_revision_is_refused(git_repo):
    with pytest.raises(GitError):
        changed_files(git_repo, "--output=/tmp/x")


def test_not_a_git_repo_raises(repo):
    with pytest.raises(GitError):
        changed_files(repo)
