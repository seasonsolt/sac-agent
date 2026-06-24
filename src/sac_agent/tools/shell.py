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


def _text_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return value.decode("utf-8", errors="replace")


def run_shell_command(repo_path: Path, argv: list[str], allow_risky: bool = False) -> ShellCommandResult:
    classification = classify_command(argv)
    if classification.risk == CommandRisk.RISKY and not allow_risky:
        raise ShellCommandBlocked(f"Command requires approval: {' '.join(argv)}")

    try:
        result = subprocess.run(
            argv,
            cwd=repo_path,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as error:
        stderr = _text_output(error.stderr)
        timeout_message = f"Command timed out after {error.timeout} seconds: {' '.join(argv)}"
        return ShellCommandResult(
            argv=argv,
            classification=classification,
            return_code=124,
            stdout=_text_output(error.output),
            stderr=f"{stderr}\n{timeout_message}" if stderr else timeout_message,
        )
    except OSError as error:
        return ShellCommandResult(
            argv=argv,
            classification=classification,
            return_code=1,
            stdout="",
            stderr=str(error),
        )

    return ShellCommandResult(
        argv=argv,
        classification=classification,
        return_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )
