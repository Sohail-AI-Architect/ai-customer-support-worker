"""Unit tests for escalation-approval-server (T044, US4).

Proves the escalation.create contract: an escalation is recorded for the
session customer's own conversation, cross-customer escalation is refused, and
missing fields/session are rejected.
"""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend" / "src"))

import pytest

from escalation_approval_server import EscalationApprovalServer, ToolFailure


class _FakeConversation:
    def __init__(self, id_: str, customer_id: str) -> None:
        self.id = uuid.UUID(id_)
        self.customer_id = uuid.UUID(customer_id)


class _FakeEscalation:
    def __init__(self, conversation_id, reason, context):
        self.id = uuid.uuid4()
        self.conversation_id = conversation_id
        self.reason = reason
        self.context = context
        self.status = "open"


class _FakeApproval:
    def __init__(self, conversation_id, proposed_action, payload=None):
        self.id = uuid.uuid4()
        self.conversation_id = conversation_id
        self.proposed_action = proposed_action
        self.payload = payload or {}
        self.status = "pending"


class _FakeDB:
    """Minimal Session stand-in: get by id, add, commit, refresh."""

    def __init__(self, objects: list) -> None:
        self._objects = list(objects)

    def get(self, model, ident):
        for obj in self._objects:
            if obj.id == ident:
                return obj
        return None

    def add(self, obj):
        self._objects.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        return obj


OWNER = "11111111-1111-1111-1111-111111111111"
OTHER = "22222222-2222-2222-2222-222222222222"
OWN_CONV = _FakeConversation("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", OWNER)
OTHER_CONV = _FakeConversation("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", OTHER)


def _server_for(customer_id, conversations=None):
    db = _FakeDB(conversations or [OWN_CONV, OTHER_CONV])
    return EscalationApprovalServer(db, customer_id)


def test_escalation_create_for_own_conversation():
    server = _server_for(OWNER)
    result = server.call_tool(
        "escalation.create",
        {"conversation_id": str(OWN_CONV.id), "reason": "sensitive", "context": "Needs human."},
    )
    assert result["status"] == "open"
    assert result["reason"] == "sensitive"
    assert "id" in result


def test_escalation_create_other_conversation_refused():
    # Owner tries to escalate OTHER's conversation -> refused (no cross-customer).
    server = _server_for(OWNER)
    with pytest.raises(ToolFailure) as exc:
        server.call_tool(
            "escalation.create",
            {"conversation_id": str(OTHER_CONV.id), "reason": "sensitive", "context": "x"},
        )
    assert exc.value.code == "unauthorized"


def test_escalation_create_requires_fields():
    server = _server_for(OWNER)
    with pytest.raises(ToolFailure) as exc:
        server.call_tool("escalation.create", {"reason": "sensitive"})
    assert exc.value.code == "validation_error"


def test_escalation_create_requires_session():
    server = _server_for(None)
    with pytest.raises(ToolFailure) as exc:
        server.call_tool(
            "escalation.create",
            {"conversation_id": str(OWN_CONV.id), "reason": "sensitive", "context": "x"},
        )
    assert exc.value.code == "unauthorized"


def test_approval_request_for_own_conversation():
    server = _server_for(OWNER)
    result = server.call_tool(
        "approval.request",
        {
            "conversation_id": str(OWN_CONV.id),
            "proposed_action": "cancel_subscription",
            "payload": {"message": "Cancel my subscription"},
        },
    )
    assert result["status"] == "pending"
    assert result["proposed_action"] == "cancel_subscription"
    assert "id" in result


def test_approval_request_other_conversation_refused():
    server = _server_for(OWNER)
    with pytest.raises(ToolFailure) as exc:
        server.call_tool(
            "approval.request",
            {"conversation_id": str(OTHER_CONV.id), "proposed_action": "delete_account"},
        )
    assert exc.value.code == "unauthorized"


def test_approval_request_requires_fields():
    server = _server_for(OWNER)
    with pytest.raises(ToolFailure) as exc:
        server.call_tool("approval.request", {"conversation_id": str(OWN_CONV.id)})
    assert exc.value.code == "validation_error"


def test_approval_request_requires_session():
    server = _server_for(None)
    with pytest.raises(ToolFailure) as exc:
        server.call_tool(
            "approval.request",
            {"conversation_id": str(OWN_CONV.id), "proposed_action": "cancel_order"},
        )
    assert exc.value.code == "unauthorized"
