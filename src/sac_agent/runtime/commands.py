from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath

from pydantic import BaseModel


class CommandRisk(StrEnum):
    SAFE = "safe"
    RISKY = "risky"


class CommandClassification(BaseModel):
    argv: list[str]
    risk: CommandRisk
    reason: str


RISKY_EXECUTABLES = {
    "curl",
    "docker",
    "gh",
    "npm",
    "pip",
    "python",
    "rm",
    "scp",
    "ssh",
    "uv",
    "wrangler",
}

SAFE_EXECUTABLES = {
    "ls",
    "pytest",
    "rg",
}
SAFE_GIT_SUBCOMMANDS = {"status", "diff", "log", "show"}
PATH_ESCAPE_OPTIONS = {
    "--git-dir",
    "--pathspec-from-file",
    "--work-tree",
}


def _argument_has_escape_syntax(argument: str) -> bool:
    if not argument or argument == "--":
        return False
    if argument == "--no-index":
        return True

    option_name, separator, option_value = argument.partition("=")
    if option_name in PATH_ESCAPE_OPTIONS:
        return True
    values = [argument]
    if separator:
        values.append(option_value)

    for value in values:
        if value.startswith("~"):
            return True
        if PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute():
            return True
        if ".." in PurePosixPath(value).parts or ".." in PureWindowsPath(value).parts:
            return True
    return False


def _has_path_escape_syntax(arguments: list[str]) -> bool:
    return any(_argument_has_escape_syntax(argument) for argument in arguments)


def _has_symlink_follow_option(argv: list[str]) -> bool:
    executable = argv[0] if argv else ""
    arguments = argv[1:]
    if executable == "rg":
        return any(argument in {"--follow", "-L"} for argument in arguments)
    if executable == "ls":
        for argument in arguments:
            if argument == "--dereference":
                return True
            if argument.startswith("-") and not argument.startswith("--") and "L" in argument[1:]:
                return True
    return False


def classify_command(argv: list[str]) -> CommandClassification:
    # The classifier is intentionally conservative. A command should become safe
    # only after someone has checked the executable and the supported arguments.
    if not argv:
        return CommandClassification(argv=argv, risk=CommandRisk.RISKY, reason="empty command")

    executable = argv[0]
    # Only read-only git subcommands are safe. Mutating git commands such as
    # commit, checkout, reset, and apply still require approval.
    if executable == "git" and len(argv) >= 2 and argv[1] in SAFE_GIT_SUBCOMMANDS:
        if _has_path_escape_syntax(argv[2:]):
            return CommandClassification(
                argv=argv,
                risk=CommandRisk.RISKY,
                reason="command argument can access outside the repository",
            )
        return CommandClassification(argv=argv, risk=CommandRisk.SAFE, reason="read-only git command")
    if executable in SAFE_EXECUTABLES:
        if _has_symlink_follow_option(argv):
            return CommandClassification(
                argv=argv,
                risk=CommandRisk.RISKY,
                reason="command can follow symlinks outside the repository",
            )
        if _has_path_escape_syntax(argv[1:]):
            return CommandClassification(
                argv=argv,
                risk=CommandRisk.RISKY,
                reason="command argument can access outside the repository",
            )
        return CommandClassification(argv=argv, risk=CommandRisk.SAFE, reason="allowed low-risk command")
    if executable in RISKY_EXECUTABLES:
        return CommandClassification(
            argv=argv,
            risk=CommandRisk.RISKY,
            reason="command can mutate state or use network",
        )
    # Unknown commands default to risky so installing a new tool cannot expand the
    # agent's permissions by accident.
    return CommandClassification(argv=argv, risk=CommandRisk.RISKY, reason="unknown command")
