"""escalation-approval-server MCP server (T044, plan Section 8).

Exposes worker-initiated, audited write tools:
- escalation.create  (write, worker-initiated) — records a case handed to a human
- approval.request   (write, worker-initiated, US5) — pending human approval

Every escalation is bound to a conversation that belongs to the session
customer; cross-customer escalation is refused (session scoping, FR-006/SC-005).
Escalations are audited records the Worker may create but not resolve itself.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from domain.authorization import AuthorizationError, SessionScope, ensure_customer_scope
from models.conversation import Conversation
from services.approvals import create_approval_request
from services.escalations import create_escalation


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
        name="escalation.create",
        description="Record an escalation for the session customer's conversation. Write, worker-initiated, audited.",
        input_schema={
            "type": "object",
            "properties": {
                "conversation_id": {"type": "string"},
                "reason": {"type": "string"},
                "context": {"type": "string"},
            },
            "required": ["conversation_id", "reason", "context"],
        },
    ),
    ToolSpec(
        name="approval.request",
        description="Request human approval for a sensitive/state-changing action. Write, worker-initiated, audited.",
        input_schema={
            "type": "object",
            "properties": {
                "conversation_id": {"type": "string"},
                "proposed_action": {"type": "string"},
                "payload": {"type": "object"},
            },
            "required": ["conversation_id", "proposed_action"],
        },
    ),
]


class EscalationApprovalServer:
    """Implements worker-initiated, session-scoped escalation/approval tools."""

    def __init__(self, db, session_customer_id: str | None) -> None:
        self.db = db
        self.scope = SessionScope(session_customer_id)

    def list_tools(self) -> list[ToolSpec]:
        return TOOL_SPECS

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            if name == "escalation.create":
                return self._escalation_create(**arguments)
            if name == "approval.request":
                return self._approval_request(**arguments)
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

    def _escalation_create(
        self,
        conversation_id: str | None = None,
        reason: str | None = None,
        context: str | None = None,
    ) -> dict[str, Any]:
        self._require_scope()
        if not conversation_id or not reason or not context:
            raise ToolFailure("validation_error", "conversation_id, reason, context are required")
        conversation = self.db.get(Conversation, uuid.UUID(conversation_id))
        if conversation is None:
            raise ToolFailure("conversation_not_found", "conversation not found")
        # The conversation must belong to the session customer.
        ensure_customer_scope(self.scope, str(conversation.customer_id))
        escalation = create_escalation(self.db, conversation.id, reason, context)
        return {
            "id": str(escalation.id),
            "status": escalation.status,
            "reason": escalation.reason,
        }

    def _approval_request(
        self,
        conversation_id: str | None = None,
        proposed_action: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._require_scope()
        if not conversation_id or not proposed_action:
            raise ToolFailure(
                "validation_error", "conversation_id, proposed_action are required"
            )
        conversation = self.db.get(Conversation, uuid.UUID(conversation_id))
        if conversation is None:
            raise ToolFailure("conversation_not_found", "conversation not found")
        # The conversation must belong to the session customer.
        ensure_customer_scope(self.scope, str(conversation.customer_id))
        approval = create_approval_request(
            self.db, conversation.id, proposed_action, payload or {}
        )
        return {
            "id": str(approval.id),
            "status": approval.status,
            "proposed_action": approval.proposed_action,
        }
