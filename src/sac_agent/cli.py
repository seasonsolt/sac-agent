from pathlib import Path

import typer

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
    typer.echo(f"SAC Agent will open: {repo.resolve()}")


def main() -> None:
    app()
