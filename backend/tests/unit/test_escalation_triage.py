"""Unit tests for the escalation_triage skill (T045, US4)."""

from worker.skills.escalation_triage import EscalationTriageSkill


class _FakeServer:
    def __init__(self, ok: bool = True) -> None:
        self._ok = ok

    def call_tool(self, name, arguments):
        if not self._ok:
            raise RuntimeError("tool failure")
        return {
            "id": "esc-1",
            "status": "open",
            "reason": arguments["reason"],
        }


def test_escalate_records_open_escalation() -> None:
    skill = EscalationTriageSkill(_FakeServer(ok=True))
    result = skill.escalate(
        conversation_id="conv-1", reason="sensitive", context="Needs human help."
    )
    assert result.ok is True
    assert result.escalation is not None
    assert result.escalation["status"] == "open"
    assert result.escalation["reason"] == "sensitive"


def test_escalate_failure_returns_safe_result() -> None:
    skill = EscalationTriageSkill(_FakeServer(ok=False))
    result = skill.escalate(
        conversation_id="conv-1", reason="unsupported", context="Cannot answer."
    )
    assert result.ok is False
    assert result.reason is not None
    assert result.escalation is None
