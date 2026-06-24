import subprocess
from pathlib import Path

from pydantic import BaseModel

from sac_agent.runtime.commands import CommandClassification, CommandRisk, classify_command


class ShellCommandBlocked(RuntimeError):
    pass


class ShellCommandResult(BaseModel):
    argv: list[str]
    classification: CommandClassification
    return_code: int
    stdout: str
    stderr: str


def run_shell_command(repo_path: Path, argv: list[str], allow_risky: bool = False) -> ShellCommandResult:
    classification = classify_command(argv)
    if classification.risk == CommandRisk.RISKY and not allow_risky:
        raise ShellCommandBlocked(f"Command requires approval: {' '.join(argv)}")

    result = subprocess.run(
        argv,
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return ShellCommandResult(
        argv=argv,
        classification=classification,
        return_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )
