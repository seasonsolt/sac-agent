from typer.testing import CliRunner

from sac_agent.cli import app


def test_cli_help_shows_sac_name():
    runner = CliRunner()

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "sac" in result.output
    assert "Start the SAC Agent TUI" in result.output
