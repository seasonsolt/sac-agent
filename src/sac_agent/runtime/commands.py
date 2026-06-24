from enum import StrEnum

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


def classify_command(argv: list[str]) -> CommandClassification:
    # The classifier is intentionally conservative. A command should become safe
    # only after someone has checked the executable and the supported arguments.
    if not argv:
        return CommandClassification(argv=argv, risk=CommandRisk.RISKY, reason="empty command")

    executable = argv[0]
    # Only read-only git subcommands are safe. Mutating git commands such as
    # commit, checkout, reset, and apply still require approval.
    if executable == "git" and len(argv) >= 2 and argv[1] in {"status", "diff", "log", "show"}:
        return CommandClassification(argv=argv, risk=CommandRisk.SAFE, reason="read-only git command")
    if executable in {"pytest", "rg", "ls"}:
        return CommandClassification(argv=argv, risk=CommandRisk.SAFE, reason="read-only or test command")
    if executable in RISKY_EXECUTABLES:
        return CommandClassification(
            argv=argv,
            risk=CommandRisk.RISKY,
            reason="command can mutate state or use network",
        )
    if executable in SAFE_EXECUTABLES:
        return CommandClassification(argv=argv, risk=CommandRisk.SAFE, reason="known safe command")
    # Unknown commands default to risky so installing a new tool cannot expand the
    # agent's permissions by accident.
    return CommandClassification(argv=argv, risk=CommandRisk.RISKY, reason="unknown command")
