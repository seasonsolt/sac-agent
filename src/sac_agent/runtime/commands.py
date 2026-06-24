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
    "git",
    "ls",
    "pytest",
    "rg",
}


def classify_command(argv: list[str]) -> CommandClassification:
    if not argv:
        return CommandClassification(argv=argv, risk=CommandRisk.RISKY, reason="empty command")

    executable = argv[0]
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
    return CommandClassification(argv=argv, risk=CommandRisk.RISKY, reason="unknown command")
