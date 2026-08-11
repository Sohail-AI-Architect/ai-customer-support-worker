"""Hybrid authorization (constitution Principle 9, plan Section 12).

Two independent checks MUST both pass before any data/tool access:
1. Session scoping: customer-scoped reads are restricted to the authenticated
   customer (never another customer's data).
2. Role-based Worker permissions: the Worker's role bounds the actions it may
   take (e.g., create + read tickets, never update/close/delete).

These checks are enforced in the service/tool layer, not only in prompts.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkerPermissions:
    """The fixed permission set granted to the AI Worker role."""

    can_read_knowledge: bool = True
    can_read_own_customer_data: bool = True
    can_read_own_tickets: bool = True
    can_create_tickets: bool = True
    can_update_close_delete_tickets: bool = False  # NEVER enabled
    can_initiate_escalations: bool = True
    can_request_approvals: bool = True


class AuthorizationError(Exception):
    """Raised when a data/tool access is not authorized."""


class SessionScope:
    """Wraps the authenticated customer for a request."""

    def __init__(self, customer_id: str | None) -> None:
        self.customer_id = customer_id


def ensure_customer_scope(session: SessionScope, requested_customer_id: str) -> None:
    """Enforce session scoping: only the authenticated customer is addressable."""
    if session.customer_id is None or session.customer_id != requested_customer_id:
        raise AuthorizationError("unauthorized: data is not scoped to the session customer")


def ensure_ticket_action_allowed(action: str) -> None:
    """Enforce role-based Worker limits on ticket operations."""
    if action in {"update", "close", "delete"}:
        raise AuthorizationError("unauthorized: ticket update/close/delete is not permitted")
