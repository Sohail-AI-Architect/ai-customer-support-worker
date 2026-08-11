"""Session-scoped customer data access (US2).

Backend-local adapter mirroring the support-data MCP server interface so the
customer_context skill can retrieve a customer's OWN profile and tickets while
enforcing session scoping (FR-006, SC-005). Cross-customer reads are refused;
no update/close/delete capability exists here (FR-010).
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.authorization import SessionScope, ensure_customer_scope
from models.customer import Customer
from models.ticket import SupportTicket


class CustomerDataServer:
    """Exposes the same tool contract as the support-data MCP server, scoped."""

    def __init__(self, db: Session, customer_id: str | None) -> None:
        self.db = db
        self.scope = SessionScope(customer_id)

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "customer.info.get":
            return self._customer_info_get()
        if name == "ticket.list":
            return self._ticket_list()
        if name == "ticket.get":
            return self._ticket_get(arguments["ticket_id"])
        if name == "ticket.create":
            return self._ticket_create(arguments)
        raise ValueError(f"unknown tool {name!r}")

    def _require_scope(self) -> None:
        if self.scope.customer_id is None:
            raise PermissionError("no session customer")

    def _customer_info_get(self) -> dict[str, Any]:
        self._require_scope()
        customer = self.db.get(Customer, uuid.UUID(self.scope.customer_id))
        if customer is None:
            raise LookupError("customer_not_found")
        return {"id": str(customer.id), "name": customer.name, "status": customer.status}

    def _ticket_list(self) -> dict[str, Any]:
        self._require_scope()
        customer_uuid = uuid.UUID(self.scope.customer_id)
        tickets = self.db.scalars(
            select(SupportTicket).where(SupportTicket.customer_id == customer_uuid)
        ).all()
        return {"tickets": [self._serialize(t) for t in tickets]}

    def _ticket_get(self, ticket_id: str) -> dict[str, Any]:
        self._require_scope()
        ticket = self.db.get(SupportTicket, uuid.UUID(ticket_id))
        if ticket is None:
            raise LookupError("ticket_not_found")
        ensure_customer_scope(self.scope, str(ticket.customer_id))
        return self._serialize(ticket)

    def _ticket_create(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._require_scope()
        subject = arguments.get("subject")
        description = arguments.get("description")
        if not subject or not description:
            raise ValueError("subject and description are required")
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
