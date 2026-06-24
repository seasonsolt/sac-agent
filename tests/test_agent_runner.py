from pathlib import Path

from sac_agent.agent.runner import DeepAgentRunner
from sac_agent.runtime.events import EventKind
from sac_agent.runtime.session import AgentSession


def test_runner_records_plan_event_without_live_model(tmp_path: Path):
    session = AgentSession.start(tmp_path)
    runner = DeepAgentRunner()

    response = runner.run_turn(session, "Add a README")

    assert "I inspected the request" in response
    assert session.events[-1].kind == EventKind.AGENT_THOUGHT


def test_deepagent_dependency_is_available():
    from deepagents import create_deep_agent

    assert callable(create_deep_agent)
