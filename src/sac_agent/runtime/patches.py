import shlex
import subprocess
from pathlib import Path

from pydantic import BaseModel


class PatchProposal(BaseModel):
    summary: str
    diff: str

    def changed_files(self) -> list[str]:
        files: list[str] = []
        for line in self.diff.splitlines():
            target = _parse_diff_git_target(line)
            if target is None:
                continue
            if target not in files:
                files.append(target)
        return files


def _parse_diff_git_target(line: str) -> str | None:
    prefix = "diff --git "
    if not line.startswith(prefix):
        return None

    operands = line.removeprefix(prefix)
    try:
        parts = shlex.split(operands)
    except ValueError:
        parts = []

    if len(parts) == 2:
        target = parts[1]
    else:
        target = _parse_unquoted_diff_git_target(operands)
        if target is None:
            return None

    if not target.startswith("b/"):
        return None
    return target.removeprefix("b/")


def _parse_unquoted_diff_git_target(operands: str) -> str | None:
    candidates: list[tuple[str, str]] = []
    start = 0
    while True:
        index = operands.find(" b/", start)
        if index == -1:
            break
        source = operands[:index]
        target = operands[index + 1 :]
        if source.startswith("a/") and target.startswith("b/"):
            candidates.append((source, target))
        start = index + 1

    for source, target in candidates:
        if source.removeprefix("a/") == target.removeprefix("b/"):
            return target
    if candidates:
        return candidates[-1][1]
    return None


class PatchApplyResult(BaseModel):
    return_code: int
    stdout: str
    stderr: str


def apply_patch(repo_path: Path, proposal: PatchProposal) -> PatchApplyResult:
    # Patch application is a separate function so the approval gate can call exactly
    # one write primitive after the user accepts the diff shown in the TUI.
    try:
        result = subprocess.run(
            ["git", "apply", "--whitespace=fix", "-"],
            cwd=repo_path,
            input=proposal.diff,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        return PatchApplyResult(return_code=1, stdout="", stderr=str(error))
    return PatchApplyResult(return_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
