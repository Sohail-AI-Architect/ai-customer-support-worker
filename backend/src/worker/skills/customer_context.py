"""Customer Context skill (T029, plan Section 6).

Reusable domain knowledge: safely retrieve the authenticated customer's own
profile and tickets via the session-scoped support-data tools. Cross-customer
access is refused — the skill never returns another customer's data (FR-006,
SC-005).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CustomerContextResult:
    ok: bool
    data: dict[str, Any] | None = None
    reason: str | None = None


class CustomerContextSkill:
    name = "customer_context"

    def __init__(self, data_server) -> None:
        self._data_server = data_server  # session-scoped SupportDataServer

    def get_profile(self) -> CustomerContextResult:
        return self._call("customer.info.get", {})

    def list_tickets(self) -> CustomerContextResult:
        return self._call("ticket.list", {})

    def get_ticket(self, ticket_id: str) -> CustomerContextResult:
        return self._call("ticket.get", {"ticket_id": ticket_id})

    def _call(self, tool: str, arguments: dict[str, Any]) -> CustomerContextResult:
        try:
            result = self._data_server.call_tool(tool, arguments)
        except Exception as exc:  # noqa: BLE001 - any tool failure -> safe result
            return CustomerContextResult(ok=False, reason=str(exc))
        return CustomerContextResult(ok=True, data=result)
