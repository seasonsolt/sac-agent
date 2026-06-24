from sac_agent.runtime.approvals import ApprovalDecision, ApprovalGate, ApprovalKind


def test_approval_gate_records_pending_patch():
    gate = ApprovalGate()

    request = gate.request(ApprovalKind.PATCH, "Apply generated patch", {"files": ["a.py"]})

    assert request.approval_id.startswith("approval-")
    assert request.kind == ApprovalKind.PATCH
    assert gate.pending[request.approval_id] == request


def test_approval_gate_records_decision_and_clears_pending():
    gate = ApprovalGate()
    request = gate.request(ApprovalKind.RISKY_COMMAND, "Run install command", {})

    decision = gate.decide(request.approval_id, approved=False)

    assert decision == ApprovalDecision.REJECTED
    assert request.approval_id not in gate.pending
