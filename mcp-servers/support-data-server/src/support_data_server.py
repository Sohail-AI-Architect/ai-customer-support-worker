"""support-data-server MCP server (T028, plan Section 8).

Exposes read-only customer and ticket tools scoped to the session customer:
- customer.info.get  (read-only, scoped to session customer)
- ticket.get         (read-only, scoped to session customer)
- ticket.list        (read-only, scoped to session customer)

Every data read enforces session scoping (T030): a tool only returns rows for
the session customer and refuses cross-customer access (FR-006, SC-005). No
update/close/delete capability exists here (FR-010).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select

from domain.authorization import AuthorizationError, SessionScope, ensure_customer_scope
from models.customer import Customer
from models.ticket import SupportTicket


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)


class ToolFailure(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


TOOL_SPECS: list[ToolSpec] = [
    ToolSpec(
        name="customer.info.get",
        description="Get the authenticated customer's own profile. Read-only.",
        input_schema={"type": "object", "properties": {}, "required": []},
    ),
    ToolSpec(
        name="ticket.get",
        description="Get one of the session customer's own tickets by id. Read-only.",
        input_schema={
            "type": "object",
            "properties": {"ticket_id": {"type": "string"}},
            "required": ["ticket_id"],
        },
    ),
    ToolSpec(
        name="ticket.list",
        description="List the session customer's own tickets. Read-only.",
        input_schema={"type": "object", "properties": {}, "required": []},
    ),
    ToolSpec(
        name="ticket.create",
        description="Create a new ticket on the session customer's account. Create-only.",
        input_schema={
            "type": "object",
            "properties": {
                "subject": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["subject", "description"],
        },
    ),
]


class SupportDataServer:
    """Implements read-only, session-scoped customer/ticket tools."""

    def __init__(self, db, session_customer_id: str | None) -> None:
        self.db = db
        self.scope = SessionScope(session_customer_id)

    def list_tools(self) -> list[ToolSpec]:
        return TOOL_SPECS

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            if name == "customer.info.get":
                return self._customer_info_get()
            if name == "ticket.get":
                return self._ticket_get(**arguments)
            if name == "ticket.list":
                return self._ticket_list()
            if name == "ticket.create":
                return self._ticket_create(**arguments)
            raise ToolFailure("unknown_tool", f"unknown tool {name!r}")
        except AuthorizationError as exc:
            raise ToolFailure("unauthorized", str(exc)) from exc
        except ToolFailure:
            raise
        except Exception as exc:  # noqa: BLE001 - tools return structured errors
            raise ToolFailure("data_unavailable", str(exc)) from exc

    def _require_scope(self) -> None:
        if self.scope.customer_id is None:
            raise AuthorizationError("no session customer")

    def _customer_info_get(self) -> dict[str, Any]:
        self._require_scope()
        customer = self.db.get(Customer, uuid.UUID(self.scope.customer_id))
        if customer is None:
            raise ToolFailure("customer_not_found", "customer not found")
        return {"id": str(customer.id), "name": customer.name, "status": customer.status}

    def _ticket_get(self, ticket_id: str) -> dict[str, Any]:
        self._require_scope()
        try:
            parsed = uuid.UUID(ticket_id)
        except ValueError:
            raise ToolFailure("ticket_not_found", "ticket not found")
        ticket = self.db.get(SupportTicket, parsed)
        if ticket is None:
            raise ToolFailure("ticket_not_found", "ticket not found")
        # Session scoping: only the owning customer may read this ticket.
        ensure_customer_scope(self.scope, str(ticket.customer_id))
        return self._serialize(ticket)

    def _ticket_list(self) -> dict[str, Any]:
        self._require_scope()
        tickets = self.db.scalars(
            select(SupportTicket).where(SupportTicket.customer_id == uuid.UUID(self.scope.customer_id))
        ).all()
        return {"tickets": [self._serialize(t) for t in tickets]}

    def _ticket_create(self, subject: str | None = None, description: str | None = None) -> dict[str, Any]:
        self._require_scope()
        if not subject or not description:
            raise ToolFailure("validation_error", "subject and description are required")
        ticket = SupportTicket(
            customer_id=uuid.UUID(self.scope.customer_id),
            subject=subject,
            description=description,
            status="open",
        )
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return self._serialize(ticket)

    @staticmethod
    def _serialize(ticket: SupportTicket) -> dict[str, Any]:
        return {
            "id": str(ticket.id),
            "subject": ticket.subject,
            "status": ticket.status,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
        }
