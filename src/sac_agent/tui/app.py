from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, RichLog, Static

from sac_agent.agent.runner import DeepAgentRunner
from sac_agent.runtime.session import AgentSession


class SacTuiApp(App[None]):
    CSS = """
    #main {
        height: 1fr;
    }
    #transcript {
        width: 2fr;
        border: solid $accent;
    }
    #activity {
        width: 1fr;
        border: solid $panel;
    }
    #command {
        dock: bottom;
    }
    """

    def __init__(self, repo_path: Path) -> None:
        super().__init__()
        self.repo_path = repo_path
        self.session = AgentSession.start(repo_path)
        self.runner = DeepAgentRunner()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main"):
            with Vertical(id="transcript"):
                yield Static("SAC Agent", id="title")
                yield RichLog(id="chat-log", markup=True)
            with Vertical(id="activity"):
                yield Static("Activity", id="activity-title")
                yield RichLog(id="activity-log", markup=True)
        yield Input(id="command")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        command = event.value.strip()
        if not command:
            return
        chat_log = self.query_one("#chat-log", RichLog)
        activity_log = self.query_one("#activity-log", RichLog)
        chat_log.write(f"[bold]You:[/bold] {command}")
        response = self.runner.run_turn(self.session, command)
        chat_log.write(f"[bold green]SAC:[/bold green] {response}")
        for runtime_event in self.session.events[-3:]:
            activity_log.write(f"{runtime_event.kind}: {runtime_event.message}")
        event.input.value = ""
