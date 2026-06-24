import asyncio
from pathlib import Path
from types import SimpleNamespace

from rich.markup import escape
from textual.widgets import Footer, Header, Input, RichLog

from sac_agent.tui.app import SacTuiApp


def test_tui_app_stores_repo_path(tmp_path: Path):
    app = SacTuiApp(repo_path=tmp_path)

    assert app.repo_path == tmp_path


def test_tui_css_does_not_dock_command_input(tmp_path: Path):
    app = SacTuiApp(repo_path=tmp_path)

    assert "#command" not in app.CSS
    assert "dock: bottom" not in app.CSS


def test_tui_app_renders_required_widgets(tmp_path: Path):
    app = SacTuiApp(repo_path=tmp_path)

    async def run_smoke_test() -> None:
        async with app.run_test():
            assert app.query_one(Header)
            assert app.query_one("#main")
            assert app.query_one("#transcript")
            assert app.query_one("#activity")
            assert app.query_one("#chat-log", RichLog)
            assert app.query_one("#activity-log", RichLog)
            assert app.query_one("#command", Input)
            assert app.query_one(Footer)

    asyncio.run(run_smoke_test())


def test_tui_submit_escapes_dynamic_log_text(tmp_path: Path, monkeypatch):
    app = SacTuiApp(repo_path=tmp_path)
    chat_log = FakeLog()
    activity_log = FakeLog()
    command_input = SimpleNamespace(value="ignored")

    class FakeRunner:
        def run_turn(self, session, command: str) -> str:
            session.record_user_message(command)
            session.events.append(SimpleNamespace(kind="agent<thought>", message="used [tool]"))
            return "response [not markup]"

    def fake_query_one(selector, widget_type):
        if selector == "#chat-log" and widget_type is RichLog:
            return chat_log
        if selector == "#activity-log" and widget_type is RichLog:
            return activity_log
        raise AssertionError(f"unexpected selector: {selector}")

    app.runner = FakeRunner()
    monkeypatch.setattr(app, "query_one", fake_query_one)

    app.on_input_submitted(SimpleNamespace(value="hello [bold]<world>", input=command_input))

    assert chat_log.messages == [
        f"[bold]You:[/bold] {escape('hello [bold]<world>')}",
        f"[bold green]SAC:[/bold green] {escape('response [not markup]')}",
    ]
    assert activity_log.messages[-2:] == [
        f"{escape('user_message')}: {escape('hello [bold]<world>')}",
        f"{escape('agent<thought>')}: {escape('used [tool]')}",
    ]
    assert command_input.value == ""


class FakeLog:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def write(self, message: str) -> None:
        self.messages.append(message)
