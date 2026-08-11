"""Unit tests for the Customer Context skill (T029)."""

from worker.skills.customer_context import CustomerContextSkill


class _FakeDataServer:
    def __init__(self, failures: dict[str, Exception] | None = None) -> None:
        self._failures = failures or {}

    def call_tool(self, name: str, arguments: dict) -> dict:
        if name in self._failures:
            raise self._failures[name]
        return {"ok": True}


def test_get_profile_ok():
    skill = CustomerContextSkill(_FakeDataServer())
    result = skill.get_profile()
    assert result.ok is True
    assert result.data == {"ok": True}


def test_list_tickets_ok():
    skill = CustomerContextSkill(_FakeDataServer())
    result = skill.list_tickets()
    assert result.ok is True


def test_get_ticket_ok():
    skill = CustomerContextSkill(_FakeDataServer())
    result = skill.get_ticket("ticket-1")
    assert result.ok is True


def test_tool_failure_is_safe():
    # A refused/errored tool must not raise; it returns a safe non-ok result.
    skill = CustomerContextSkill(_FakeDataServer(failures={"ticket.get": PermissionError("no")}))
    result = skill.get_ticket("ticket-1")
    assert result.ok is False
    assert result.reason
