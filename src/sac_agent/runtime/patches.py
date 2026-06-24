import re
import subprocess
from pathlib import Path

from pydantic import BaseModel


class PatchProposal(BaseModel):
    summary: str
    diff: str

    def changed_files(self) -> list[str]:
        files: list[str] = []
        for match in re.finditer(r"^diff --git a/(.+?) b/(.+)$", self.diff, flags=re.MULTILINE):
            target = match.group(2)
            if target not in files:
                files.append(target)
        return files


class PatchApplyResult(BaseModel):
    return_code: int
    stdout: str
    stderr: str


def apply_patch(repo_path: Path, proposal: PatchProposal) -> PatchApplyResult:
    # Patch application is a separate function so the approval gate can call exactly
    # one write primitive after the user accepts the diff shown in the TUI.
    result = subprocess.run(
        ["git", "apply", "--whitespace=fix", "-"],
        cwd=repo_path,
        input=proposal.diff,
        check=False,
        capture_output=True,
        text=True,
    )
    return PatchApplyResult(return_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
