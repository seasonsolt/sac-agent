from pathlib import Path

from typer.testing import CliRunner

import sac_agent.cli as cli
from sac_agent.cli import app


def test_cli_help_shows_sac_name():
    runner = CliRunner()

    result = runner.invoke(app, ["--help"], prog_name="sac")

    assert result.exit_code == 0
    assert "sac" in result.output
    assert "Start the SAC Agent TUI" in result.output
    assert "COMMAND [ARGS]" not in result.output


def test_cli_launches_tui_with_resolved_repo_path(tmp_path: Path, monkeypatch):
    launched_paths: list[Path] = []

    class FakeTuiApp:
        def __init__(self, repo_path: Path) -> None:
            self.repo_path = repo_path

        def run(self) -> None:
            launched_paths.append(self.repo_path)

    monkeypatch.setattr(cli, "SacTuiApp", FakeTuiApp)

    result = CliRunner().invoke(app, [str(tmp_path)])

    assert result.exit_code == 0
    assert launched_paths == [tmp_path.resolve()]


def test_cli_default_repo_is_current_working_directory(monkeypatch):
    launched_paths: list[Path] = []

    class FakeTuiApp:
        def __init__(self, repo_path: Path) -> None:
            self.repo_path = repo_path

        def run(self) -> None:
            launched_paths.append(self.repo_path)

    monkeypatch.setattr(cli, "SacTuiApp", FakeTuiApp)

    result = CliRunner().invoke(app)

    assert result.exit_code == 0
    assert launched_paths == [Path.cwd().resolve()]


def test_cli_rejects_invalid_repo_path():
    result = CliRunner().invoke(app, ["/definitely/not/a/repo"])

    assert result.exit_code != 0
    assert "Repository path does not exist" in result.output
