"""Unit tests for the support-data-server session-scoped tools (T028/T030).

Proves the read-only contract and session scoping: a session customer can read
their own customer/tickets, and cross-customer access is refused.
"""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend" / "src"))

import pytest

from support_data_server import SupportDataServer, ToolFailure


class _FakeCustomer:
    def __init__(self, id_: str, name: str, status: str = "active") -> None:
        self.id = uuid.UUID(id_)
        self.name = name
        self.status = status


class _FakeTicket:
    def __init__(self, id_: str, customer_id: str, subject: str) -> None:
        self.id = uuid.UUID(id_)
        self.customer_id = uuid.UUID(customer_id)
        self.subject = subject
        self.status = "open"
        self.created_at = None


class _FakeDB:
    """Minimal stand-in for a SQLAlchemy Session.

    Emulates the session-scoped WHERE the production query applies: `all()`
    returns only tickets whose customer_id matches the session scope. All other
    reads (by id) are unfiltered so cross-customer refusal is exercised in the
    tool layer via `ensure_customer_scope`.
    """

    def __init__(self, objects: list, session_customer_id: str | None = None) -> None:
        self._objects = list(objects)
        self._tickets = [o for o in objects if self._is_ticket(o)]
        self._session_customer_id = session_customer_id

    @staticmethod
    def _is_ticket(o) -> bool:
        return hasattr(o, "customer_id") and hasattr(o, "subject")

    def get(self, model, ident):
        for obj in self._objects:
            if obj.id == ident:
                return obj
        return None

    def scalars(self, stmt):
        return self

    def all(self):
        if self._session_customer_id is None:
            return []
        return [t for t in self._tickets if str(t.customer_id) == self._session_customer_id]

    def add(self, obj):
        self._objects.append(obj)
        if self._is_ticket(obj):
            self._tickets.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        return obj


OWNER = _FakeCustomer("11111111-1111-1111-1111-111111111111", "Owner")
OTHER = _FakeCustomer("22222222-2222-2222-2222-222222222222", "Other")
OWN_TICKET = _FakeTicket(
    "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", str(OWNER.id), "Own ticket"
)
OTHER_TICKET = _FakeTicket(
    "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", str(OTHER.id), "Other's ticket"
)
ALL_OBJECTS = [OWNER, OTHER, OWN_TICKET, OTHER_TICKET]


def _server_for(customer_id: str | None) -> SupportDataServer:
    db = _FakeDB(ALL_OBJECTS, session_customer_id=customer_id)
    return SupportDataServer(db, customer_id)


def test_customer_info_get_scoped():
    server = _server_for(str(OWNER.id))
    result = server.call_tool("customer.info.get", {})
    assert result["id"] == str(OWNER.id)
    assert result["name"] == "Owner"


def test_ticket_get_own_ticket():
    server = _server_for(str(OWNER.id))
    result = server.call_tool("ticket.get", {"ticket_id": str(OWN_TICKET.id)})
    assert result["subject"] == "Own ticket"


def test_ticket_get_other_customers_ticket_refused():
    # Owner requests OTHER's ticket -> refused (no data returned).
    server = _server_for(str(OWNER.id))
    with pytest.raises(ToolFailure) as exc:
        server.call_tool("ticket.get", {"ticket_id": str(OTHER_TICKET.id)})
    assert exc.value.code == "unauthorized"


def test_ticket_list_only_own():
    server = _server_for(str(OWNER.id))
    result = server.call_tool("ticket.list", {})
    subjects = [t["subject"] for t in result["tickets"]]
    assert "Own ticket" in subjects
    assert "Other's ticket" not in subjects


def test_no_session_refused():
    server = _server_for(None)
    with pytest.raises(ToolFailure) as exc:
        server.call_tool("customer.info.get", {})
    assert exc.value.code == "unauthorized"


def test_ticket_create_inserts_for_session_customer():
    server = _server_for(str(OWNER.id))
    result = server.call_tool(
        "ticket.create", {"subject": "New problem", "description": "Details."}
    )
    assert result["subject"] == "New problem"
    assert result["status"] == "open"
    assert "id" in result

    # New ticket is visible to the owner via ticket.list.
    listed = server.call_tool("ticket.list", {})
    subjects = [t["subject"] for t in listed["tickets"]]
    assert "New problem" in subjects


def test_ticket_create_requires_subject():
    server = _server_for(str(OWNER.id))
    with pytest.raises(ToolFailure) as exc:
        server.call_tool("ticket.create", {"description": "No subject."})
    assert exc.value.code == "validation_error"


def test_ticket_create_requires_session():
    server = _server_for(None)
    with pytest.raises(ToolFailure) as exc:
        server.call_tool(
            "ticket.create", {"subject": "S", "description": "D"}
        )
    assert exc.value.code == "unauthorized"
