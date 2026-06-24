import subprocess
from pathlib import Path

from pydantic import BaseModel


class FileList(BaseModel):
    files: list[str]


class FileRead(BaseModel):
    path: str
    content: str


class CommandOutput(BaseModel):
    argv: list[str]
    output: str
    return_code: int


def _inside_repo(repo_path: Path, relative_path: str) -> Path:
    repo = repo_path.resolve()
    selected = (repo / relative_path).resolve()
    if repo not in selected.parents and selected != repo:
        raise ValueError(f"Path escapes repository: {relative_path}")
    return selected


def list_files(repo_path: Path) -> FileList:
    files = [
        str(path.relative_to(repo_path))
        for path in repo_path.rglob("*")
        if path.is_file() and ".git" not in path.parts
    ]
    return FileList(files=sorted(files))


def read_file(
    repo_path: Path,
    relative_path: str,
    start_line: int = 1,
    end_line: int | None = None,
) -> FileRead:
    selected = _inside_repo(repo_path, relative_path)
    lines = selected.read_text(encoding="utf-8").splitlines()
    start_index = max(start_line - 1, 0)
    stop_index = end_line if end_line is not None else len(lines)
    return FileRead(path=relative_path, content="\n".join(lines[start_index:stop_index]))


def git_status(repo_path: Path) -> CommandOutput:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    return CommandOutput(
        argv=["git", "status", "--short"],
        output=result.stdout,
        return_code=result.returncode,
    )
