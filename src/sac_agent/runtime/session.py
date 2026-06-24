from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, Field

from sac_agent.runtime.events import EventKind, RuntimeEvent


class ChatMessage(BaseModel):
    role: str
    content: str


class AgentSession(BaseModel):
    session_id: str
    repo_path: Path
    messages: list[ChatMessage] = Field(default_factory=list)
    events: list[RuntimeEvent] = Field(default_factory=list)
    pending_patch: str | None = None
    verification_results: list[str] = Field(default_factory=list)

    @classmethod
    def start(cls, repo_path: Path) -> "AgentSession":
        resolved = repo_path.expanduser().resolve()
        if not resolved.exists():
            raise ValueError(f"Repository path does not exist: {resolved}")
        if not resolved.is_dir():
            raise ValueError(f"Repository path is not a directory: {resolved}")
        return cls(session_id=f"session-{uuid4()}", repo_path=resolved)

    def record_user_message(self, content: str) -> None:
        self.messages.append(ChatMessage(role="user", content=content))
        self.record_event(EventKind.USER_MESSAGE, content)

    def record_event(
        self,
        kind: EventKind,
        message: str,
        data: dict[str, object] | None = None,
    ) -> None:
        self.events.append(RuntimeEvent(kind=kind, message=message, data=data or {}))
