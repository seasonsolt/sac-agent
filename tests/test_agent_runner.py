from pathlib import Path

from sac_agent.agent.runner import DeepAgentRunner
from sac_agent.runtime.events import EventKind
from sac_agent.runtime.session import AgentSession


def test_runner_records_plan_event_without_live_model(tmp_path: Path):
    session = AgentSession.start(tmp_path)
    runner = DeepAgentRunner()

    response = runner.run_turn(session, "Add a README")

    assert "I inspected the request" in response
    assert len(session.messages) == 1
    assert session.messages[0].role == "user"
    assert session.messages[0].content == "Add a README"
    assert len(session.events) == 2
    assert session.events[0].kind == EventKind.USER_MESSAGE
    assert session.events[0].message == "Add a README"
    assert session.events[1].kind == EventKind.AGENT_THOUGHT
    assert session.events[1].message == "Created an initial coding plan and will inspect repository context first."
    assert session.events[1].data["tools"] == runner.tools.names()


def test_deepagent_dependency_is_available():
    from deepagents import create_deep_agent

    assert callable(create_deep_agent)
