from pathlib import Path

import typer

from sac_agent.tui.app import SacTuiApp

app = typer.Typer(
    name="sac",
    help="Start the SAC Agent TUI for an interactive coding session.",
)
REPO_ARGUMENT = typer.Argument(Path.cwd(), help="Repository path to open.")


@app.callback(invoke_without_command=True)
def run(
    ctx: typer.Context,
    repo: Path = REPO_ARGUMENT,
) -> None:
    """Start the SAC Agent TUI."""
    if ctx.invoked_subcommand is not None:
        return
    SacTuiApp(repo_path=_resolve_repo_path(repo)).run()


def main() -> None:
    app()


def _resolve_repo_path(repo: Path) -> Path:
    resolved = repo.expanduser().resolve()
    if not resolved.exists():
        raise typer.BadParameter(f"Repository path does not exist: {resolved}")
    if not resolved.is_dir():
        raise typer.BadParameter(f"Repository path is not a directory: {resolved}")
    return resolved
