from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class EventKind(StrEnum):
    USER_MESSAGE = "user_message"
    AGENT_THOUGHT = "agent_thought"
    TOOL_STARTED = "tool_started"
    TOOL_FINISHED = "tool_finished"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_DECIDED = "approval_decided"
    ERROR = "error"


class RuntimeEvent(BaseModel):
    # Events are the teaching surface of the runtime. The TUI shows them so a learner
    # can connect an agent response with the exact tool call or approval decision.
    kind: EventKind
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data: dict[str, object] = Field(default_factory=dict)
