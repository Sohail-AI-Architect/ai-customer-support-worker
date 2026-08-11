"""Approval Protocol skill (T054, plan Section 6/14).

Reusable domain knowledge for proposing a sensitive/state-changing action and
requesting human approval before executing it (FR-014/015). Wraps the
session-scoped `approval.request` tool; the skill never guesses and returns a
safe result regardless of tool outcome.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ApprovalRequestResult:
    ok: bool
    approval: dict[str, Any] | None = None
    reason: str | None = None


class ApprovalProtocolSkill:
    name = "approval_protocol"

    def __init__(self, data_server) -> None:
        self._data_server = data_server  # session-scoped EscalationApprovalServer

    def request_approval(
        self,
        conversation_id: str,
        proposed_action: str,
        payload: dict[str, Any] | None = None,
    ) -> ApprovalRequestResult:
        try:
            result = self._data_server.call_tool(
                "approval.request",
                {
                    "conversation_id": conversation_id,
                    "proposed_action": proposed_action,
                    "payload": payload or {},
                },
            )
        except Exception as exc:  # noqa: BLE001 - any tool failure -> safe result
            return ApprovalRequestResult(ok=False, reason=str(exc))
        return ApprovalRequestResult(ok=True, approval=result)
