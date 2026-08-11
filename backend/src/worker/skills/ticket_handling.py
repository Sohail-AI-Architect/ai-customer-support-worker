"""Ticket Handling skill (T037, plan Section 6).

Reusable domain knowledge for ticket creation (US3). Wraps the session-scoped
`ticket.create` tool and returns a safe result — the skill never fabricates a
reference and never acts without a scope. Create + read only (FR-010): no
update/close/delete capability exists here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TicketCreateResult:
    ok: bool
    ticket: dict[str, Any] | None = None
    reason: str | None = None


class TicketHandlingSkill:
    name = "ticket_handling"

    def __init__(self, data_server) -> None:
        self._data_server = data_server  # session-scoped SupportDataServer

    def create_ticket(self, subject: str, description: str) -> TicketCreateResult:
        try:
            result = self._data_server.call_tool(
                "ticket.create",
                {"subject": subject, "description": description},
            )
        except Exception as exc:  # noqa: BLE001 - any tool failure -> safe result
            return TicketCreateResult(ok=False, reason=str(exc))
        return TicketCreateResult(ok=True, ticket=result)
