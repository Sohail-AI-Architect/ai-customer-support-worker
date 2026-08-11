"""Escalation Triage skill (T045, plan Section 6).

Reusable domain knowledge for recognizing when a request cannot be safely
answered or acted upon and handing it to a human. Wraps the session-scoped
`escalation.create` tool; the skill never guesses and returns a safe result
regardless of tool outcome. Escalation is worker-initiated and audited
(plan Section 14).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EscalationResult:
    ok: bool
    escalation: dict[str, Any] | None = None
    reason: str | None = None


class EscalationTriageSkill:
    name = "escalation_triage"

    def __init__(self, data_server) -> None:
        self._data_server = data_server  # session-scoped EscalationApprovalServer

    def escalate(
        self, conversation_id: str, reason: str, context: str
    ) -> EscalationResult:
        try:
            result = self._data_server.call_tool(
                "escalation.create",
                {
                    "conversation_id": conversation_id,
                    "reason": reason,
                    "context": context,
                },
            )
        except Exception as exc:  # noqa: BLE001 - any tool failure -> safe result
            return EscalationResult(ok=False, reason=str(exc))
        return EscalationResult(ok=True, escalation=result)
