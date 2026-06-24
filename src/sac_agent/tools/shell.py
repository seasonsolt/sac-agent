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
    # TimeoutExpired may carry bytes even when subprocess.run(text=True) was used.
    # Normalize that output so callers can render one predictable result model.
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return value.decode("utf-8", errors="replace")


def _candidate_path_arguments(argv: list[str]) -> list[str]:
    if not argv:
        return []
    start_index = 2 if argv[0] == "git" and len(argv) > 1 else 1
    candidates: list[str] = []
    for argument in argv[start_index:]:
        if argument == "--":
            continue
        _, separator, option_value = argument.partition("=")
        value = option_value if separator else argument
        if not value or value.startswith("-"):
            continue
        candidates.append(value)
    return candidates


def _looks_like_path_argument(repo_path: Path, value: str) -> bool:
    path = Path(value).expanduser()
    return path.is_absolute() or "/" in value or value in {".", ".."} or (repo_path / path).exists()


def _first_repo_escape_argument(repo_path: Path, argv: list[str]) -> str | None:
    repo = repo_path.resolve()
    for value in _candidate_path_arguments(argv):
        if not _looks_like_path_argument(repo, value):
            continue
        path = Path(value).expanduser()
        selected = path if path.is_absolute() else repo / path
        resolved = selected.resolve()
        if resolved != repo and repo not in resolved.parents:
            return value
    return None


def run_shell_command(repo_path: Path, argv: list[str], allow_risky: bool = False) -> ShellCommandResult:
    # Classify before spawning a subprocess. This prevents a risky command from
    # running while the UI is still waiting for human approval.
    classification = classify_command(argv)
    if not allow_risky:
        if classification.risk == CommandRisk.RISKY:
            raise ShellCommandBlocked(f"Command requires approval: {' '.join(argv)}")
        if escaping_argument := _first_repo_escape_argument(repo_path, argv):
            raise ShellCommandBlocked(f"Command argument escapes repository: {escaping_argument}")

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
        # Return timeouts as data rather than exceptions so the agent can explain
        # the failure and the TUI can show partial output.
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
        # Missing executables and invalid working directories are expected user
        # environment problems, so they get the same structured result shape.
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
