"""Backend-local adapter for the escalation-approval MCP server (US4/US5).

Mirrors the escalation-approval MCP server interface so the escalation_triage
skill can record an escalation for the session customer's conversation while
enforcing session scoping (FR-006, SC-005). Cross-customer escalation is
refused; escalations are worker-initiated and audited (plan Section 14).
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from domain.authorization import SessionScope, ensure_customer_scope
from models.conversation import Conversation
from services.approvals import create_approval_request
from services.escalations import create_escalation


class EscalationApprovalServer:
    """Exposes the escalation-approval tool contract, session-scoped."""

    def __init__(self, db: Session, customer_id: str | None) -> None:
        self.db = db
        self.scope = SessionScope(customer_id)

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "escalation.create":
            return self._escalation_create(arguments)
        if name == "approval.request":
            return self._approval_request(arguments)
        raise ValueError(f"unknown tool {name!r}")

    def _escalation_create(self, arguments: dict[str, Any]) -> dict[str, Any]:
        if self.scope.customer_id is None:
            raise PermissionError("no session customer")
        conversation_id = arguments.get("conversation_id")
        reason = arguments.get("reason")
        context = arguments.get("context")
        if not conversation_id or not reason or not context:
            raise ValueError("conversation_id, reason, context are required")
        conversation = self.db.get(Conversation, uuid.UUID(conversation_id))
        if conversation is None:
            raise LookupError("conversation_not_found")
        ensure_customer_scope(self.scope, str(conversation.customer_id))
        escalation = create_escalation(self.db, conversation.id, reason, context)
        return {
            "id": str(escalation.id),
            "status": escalation.status,
            "reason": escalation.reason,
        }

    def _approval_request(self, arguments: dict[str, Any]) -> dict[str, Any]:
        if self.scope.customer_id is None:
            raise PermissionError("no session customer")
        conversation_id = arguments.get("conversation_id")
        proposed_action = arguments.get("proposed_action")
        payload = arguments.get("payload") or {}
        if not conversation_id or not proposed_action:
            raise ValueError("conversation_id, proposed_action are required")
        conversation = self.db.get(Conversation, uuid.UUID(conversation_id))
        if conversation is None:
            raise LookupError("conversation_not_found")
        ensure_customer_scope(self.scope, str(conversation.customer_id))
        approval = create_approval_request(
            self.db, conversation.id, proposed_action, payload
        )
        return {
            "id": str(approval.id),
            "status": approval.status,
            "proposed_action": approval.proposed_action,
        }
