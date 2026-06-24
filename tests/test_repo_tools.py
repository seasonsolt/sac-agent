import subprocess
from pathlib import Path

import pytest

from sac_agent.tools.repo import git_status, list_files, read_file


def make_repo(path: Path) -> Path:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    (path / "app.py").write_text("print('hello')\n", encoding="utf-8")
    return path


def test_list_files_returns_relative_paths(tmp_path: Path):
    repo = make_repo(tmp_path)

    result = list_files(repo)

    assert "app.py" in result.files


def test_read_file_returns_line_range(tmp_path: Path):
    repo = make_repo(tmp_path)

    result = read_file(repo, "app.py", start_line=1, end_line=1)

    assert result.path == "app.py"
    assert result.content == "print('hello')"


def test_read_file_rejects_parent_directory_escape(tmp_path: Path):
    repo = make_repo(tmp_path)

    with pytest.raises(ValueError):
        read_file(repo, "../outside.txt")


def test_read_file_rejects_absolute_path_escape(tmp_path: Path):
    repo = make_repo(tmp_path)
    outside_path = tmp_path.parent / "outside.txt"
    outside_path.write_text("secret\n", encoding="utf-8")

    with pytest.raises(ValueError):
        read_file(repo, str(outside_path))


def test_list_files_excludes_git_internals(tmp_path: Path):
    repo = make_repo(tmp_path)

    result = list_files(repo)

    assert all(".git" not in Path(path).parts for path in result.files)


def test_read_file_rejects_symlink_to_outside_file(tmp_path: Path):
    repo = make_repo(tmp_path)
    outside_path = tmp_path.parent / "outside.txt"
    outside_path.write_text("secret\n", encoding="utf-8")
    link_path = repo / "outside-link.txt"
    try:
        link_path.symlink_to(outside_path)
    except OSError as exc:
        pytest.skip(f"Symlink creation unavailable: {exc}")

    with pytest.raises(ValueError):
        read_file(repo, "outside-link.txt")


def test_git_status_reports_porcelain(tmp_path: Path):
    repo = make_repo(tmp_path)

    result = git_status(repo)

    assert "app.py" in result.output
