from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class ApprovalKind(StrEnum):
    PATCH = "patch"
    RISKY_COMMAND = "risky_command"


class ApprovalDecision(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalRequest(BaseModel):
    approval_id: str
    kind: ApprovalKind
    title: str
    data: dict[str, object] = Field(default_factory=dict)


class ApprovalGate(BaseModel):
    # The approval gate is the main human-control boundary. Tools may create a
    # request, but approval should come from a TUI action or another human-facing
    # controller, not from the same tool or model that wants to run the action.
    pending: dict[str, ApprovalRequest] = Field(default_factory=dict)
    decisions: dict[str, ApprovalDecision] = Field(default_factory=dict)

    def request(
        self,
        kind: ApprovalKind,
        title: str,
        data: dict[str, object],
    ) -> ApprovalRequest:
        # Store the exact data shown for review. For patches this should include
        # the diff or a stable reference to it; for commands it should include argv.
        approval = ApprovalRequest(
            approval_id=f"approval-{uuid4()}",
            kind=kind,
            title=title,
            data=data,
        )
        self.pending[approval.approval_id] = approval
        return approval

    def decide(self, approval_id: str, approved: bool) -> ApprovalDecision:
        # Unknown IDs are errors because silently accepting them would let callers
        # skip the pending-request state machine.
        if approval_id not in self.pending:
            raise KeyError(f"Unknown approval request: {approval_id}")
        self.pending.pop(approval_id)
        decision = ApprovalDecision.APPROVED if approved else ApprovalDecision.REJECTED
        self.decisions[approval_id] = decision
        return decision
