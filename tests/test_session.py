from pathlib import Path

from sac_agent.runtime.events import EventKind
from sac_agent.runtime.session import AgentSession


def test_session_records_user_message_and_event(tmp_path: Path):
    session = AgentSession.start(repo_path=tmp_path)

    session.record_user_message("Fix the failing test")
    session.record_event(EventKind.AGENT_THOUGHT, "Planning repository inspection")

    assert session.repo_path == tmp_path
    assert session.messages[-1].role == "user"
    assert session.messages[-1].content == "Fix the failing test"
    assert session.events[-1].kind == EventKind.AGENT_THOUGHT
    assert session.events[-1].message == "Planning repository inspection"


def test_session_rejects_missing_repo_path(tmp_path: Path):
    missing = tmp_path / "missing"

    try:
        AgentSession.start(repo_path=missing)
    except ValueError as error:
        assert "Repository path does not exist" in str(error)
    else:
        raise AssertionError("Expected missing repository path to fail")
