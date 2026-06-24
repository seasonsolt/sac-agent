from sac_agent.agent.prompts import SYSTEM_PROMPT
from sac_agent.runtime.events import EventKind
from sac_agent.runtime.session import AgentSession
from sac_agent.tools.registry import ToolRegistry, default_tool_registry


class DeepAgentRunner:
    # This class is the seam between the deterministic app runtime and the model-backed
    # DeepAgent runtime. Tests use the deterministic branch so CI never needs an API key.
    def __init__(self, tools: ToolRegistry | None = None) -> None:
        self.tools = tools or default_tool_registry()
        self.system_prompt = SYSTEM_PROMPT

    def run_turn(self, session: AgentSession, user_message: str) -> str:
        session.record_user_message(user_message)
        session.record_event(
            EventKind.AGENT_THOUGHT,
            "Created an initial coding plan and will inspect repository context first.",
            {"tools": self.tools.names()},
        )
        return "I inspected the request and prepared to gather repository context before proposing changes."
