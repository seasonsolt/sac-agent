from sac_agent.agent.prompts import SYSTEM_PROMPT
from sac_agent.runtime.events import EventKind
from sac_agent.runtime.session import AgentSession
from sac_agent.tools.registry import ToolRegistry, default_tool_registry


class DeepAgentRunner:
    # This class is the boundary between UI/session code and the future model loop.
    # It is named for the intended DeepAgent integration, but it stays deterministic
    # today so tests do not depend on API keys, network calls, or model output.
    def __init__(self, tools: ToolRegistry | None = None) -> None:
        self.tools = tools or default_tool_registry()
        self.system_prompt = SYSTEM_PROMPT

    def run_turn(self, session: AgentSession, user_message: str) -> str:
        # Keep all session mutation here instead of letting the TUI edit message
        # history directly. When a model-backed runner is added, it should still
        # record the same events so learners can inspect each turn.
        session.record_user_message(user_message)
        session.record_event(
            EventKind.AGENT_THOUGHT,
            "Created an initial coding plan and will inspect repository context first.",
            {"tools": self.tools.names()},
        )
        # A future DeepAgent call should happen after the user message is recorded
        # and before the final response is returned. Tool use must go through
        # self.tools so approval and shell guards remain visible.
        return "I inspected the request and prepared to gather repository context before proposing changes."
