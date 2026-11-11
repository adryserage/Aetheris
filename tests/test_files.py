import os

import pytest

from aetheris.files import (
    PathOutsideRootError,
    project_root,
    read_text,
    resolve_in_root,
    select_files,
)
from tests.conftest import write


def test_root_comes_from_environment(repo):
    assert project_root() == repo


def test_parent_traversal_is_rejected(repo):
    with pytest.raises(PathOutsideRootError):
        resolve_in_root(repo, "../outside.txt")
    with pytest.raises(PathOutsideRootError):
        select_files(repo, ["../outside.txt"])


def test_absolute_path_outside_root_is_rejected(repo, tmp_path):
    outside = write(tmp_path, "elsewhere.txt", "secret")
    with pytest.raises(PathOutsideRootError):
        select_files(repo, [str(outside)])


def test_symlink_escaping_root_is_not_listed_and_refused_on_read(repo, tmp_path):
    outside = write(tmp_path, "elsewhere.txt", "secret")
    os.symlink(outside, repo / "link.txt")
    write(repo, "inside.txt", "ok")
    assert select_files(repo).files == ["inside.txt"]
    with pytest.raises(PathOutsideRootError):
        read_text(repo, "link.txt")


def test_gitignore_default_exclusions_binary_and_size_filters(repo):
    write(repo, ".gitignore", "ignored.py\nbuild_out/\n")
    write(repo, "kept.py", "x = 1\n")
    write(repo, "ignored.py", "x = 1\n")
    write(repo, "build_out/a.py", "x = 1\n")
    write(repo, "node_modules/pkg/index.js", "x\n")
    write(repo, "huge.py", "x" * (1024 * 1024 + 1))
    (repo / "blob.dat").write_bytes(b"\x00\x01\x02")
    write(repo, "sub/.gitignore", "local.py\n")
    write(repo, "sub/local.py", "x = 1\n")
    write(repo, "sub/other.py", "x = 1\n")
    files = select_files(repo).files
    assert "kept.py" in files and "sub/other.py" in files
    assert not {"ignored.py", "build_out/a.py", "huge.py", "sub/local.py"} & set(files)
    assert not any(f.startswith("node_modules") for f in files)
    assert read_text(repo, "blob.dat") is None


def test_file_cap_sets_truncated(repo):
    for index in range(5):
        write(repo, f"f{index}.py", "x = 1\n")
    selection = select_files(repo, limit=3)
    assert len(selection.files) == 3 and selection.truncated
