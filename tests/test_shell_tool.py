from pathlib import Path

from sac_agent.runtime.commands import CommandRisk
from sac_agent.tools.shell import ShellCommandBlocked, run_shell_command


def test_runs_safe_command(tmp_path: Path):
    result = run_shell_command(tmp_path, ["git", "status"], allow_risky=False)

    assert result.classification.risk == CommandRisk.SAFE
    assert result.return_code in {0, 128}


def test_blocks_risky_command_without_approval(tmp_path: Path):
    try:
        run_shell_command(tmp_path, ["pip", "install", "requests"], allow_risky=False)
    except ShellCommandBlocked as error:
        assert "requires approval" in str(error)
    else:
        raise AssertionError("Expected risky command to be blocked")
