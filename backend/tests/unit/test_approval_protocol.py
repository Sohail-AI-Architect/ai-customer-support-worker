"""Unit tests for the approval_protocol skill (T054, US5)."""

from worker.skills.approval_protocol import ApprovalProtocolSkill


class _FakeServer:
    def __init__(self, ok: bool = True) -> None:
        self._ok = ok

    def call_tool(self, name, arguments):
        if not self._ok:
            raise RuntimeError("tool failure")
        return {
            "id": "appr-1",
            "status": "pending",
            "proposed_action": arguments["proposed_action"],
        }


def test_request_approval_records_pending() -> None:
    skill = ApprovalProtocolSkill(_FakeServer(ok=True))
    result = skill.request_approval(
        conversation_id="conv-1",
        proposed_action="cancel_subscription",
        payload={"message": "Cancel my subscription"},
    )
    assert result.ok is True
    assert result.approval is not None
    assert result.approval["status"] == "pending"
    assert result.approval["proposed_action"] == "cancel_subscription"


def test_request_approval_failure_returns_safe_result() -> None:
    skill = ApprovalProtocolSkill(_FakeServer(ok=False))
    result = skill.request_approval(
        conversation_id="conv-1", proposed_action="delete_account"
    )
    assert result.ok is False
    assert result.reason is not None
    assert result.approval is None
