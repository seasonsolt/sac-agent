from pathlib import Path

from sac_agent.tui.app import SacTuiApp


def test_tui_app_stores_repo_path(tmp_path: Path):
    app = SacTuiApp(repo_path=tmp_path)

    assert app.repo_path == tmp_path
