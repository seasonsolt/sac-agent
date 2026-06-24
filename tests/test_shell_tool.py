import subprocess
from pathlib import Path

import sac_agent.tools.shell
from sac_agent.runtime.commands import CommandRisk
from sac_agent.tools.shell import ShellCommandBlocked, run_shell_command


def test_runs_safe_command(tmp_path: Path):
    (tmp_path / "known-file.txt").write_text("content")

    result = run_shell_command(tmp_path, ["ls"], allow_risky=False)

    assert result.classification.risk == CommandRisk.SAFE
    assert result.return_code == 0
    assert "known-file.txt" in result.stdout


def test_blocks_risky_command_without_approval(tmp_path: Path):
    try:
        run_shell_command(tmp_path, ["pip", "install", "requests"], allow_risky=False)
    except ShellCommandBlocked as error:
        assert "requires approval" in str(error)
    else:
        raise AssertionError("Expected risky command to be blocked")


def test_missing_executable_returns_structured_failure(tmp_path: Path):
    result = run_shell_command(tmp_path, ["unknown-sac-agent-command"], allow_risky=True)

    assert result.classification.risk == CommandRisk.RISKY
    assert result.return_code == 1
    assert result.stdout == ""
    assert result.stderr


def test_invalid_cwd_returns_structured_failure(tmp_path: Path):
    missing_path = tmp_path / "missing"

    result = run_shell_command(missing_path, ["ls"], allow_risky=False)

    assert result.classification.risk == CommandRisk.SAFE
    assert result.return_code == 1
    assert result.stdout == ""
    assert result.stderr


def test_timeout_returns_structured_failure(tmp_path: Path, monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=["ls"],
            timeout=120,
            output=b"partial \xff output",
            stderr=b"partial \xff error",
        )

    monkeypatch.setattr(sac_agent.tools.shell.subprocess, "run", raise_timeout)

    result = run_shell_command(tmp_path, ["ls"], allow_risky=False)

    assert result.classification.risk == CommandRisk.SAFE
    assert result.return_code == 124
    assert result.stdout == "partial \ufffd output"
    assert isinstance(result.stderr, str)
    assert "timed out" in result.stderr


def test_blocked_risky_command_does_not_run(tmp_path: Path, monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("subprocess.run should not be called")

    monkeypatch.setattr(sac_agent.tools.shell.subprocess, "run", fail_if_called)

    try:
        run_shell_command(tmp_path, ["pip", "install", "requests"], allow_risky=False)
    except ShellCommandBlocked:
        pass
    else:
        raise AssertionError("Expected risky command to be blocked")
