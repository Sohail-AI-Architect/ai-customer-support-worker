"""Agent-facing escalation endpoints (T047, US4).

Human agents list open escalations with context and mark them resolved. Agent
role is required for both endpoints (require_agent). Escalations are
worker-initiated and audited (plan Section 14).
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db, require_agent
from models.user import User
from services.escalations import list_open_escalations, resolve_escalation

router = APIRouter(prefix="/api/agent/escalations", tags=["agent-escalations"])


def _serialize(escalation) -> dict:
    return {
        "id": str(escalation.id),
        "conversation_id": str(escalation.conversation_id),
        "reason": escalation.reason,
        "context": escalation.context,
        "status": escalation.status,
        "created_at": escalation.created_at.isoformat() if escalation.created_at else None,
        "handled_by": str(escalation.handled_by) if escalation.handled_by else None,
        "resolved_at": escalation.resolved_at.isoformat() if escalation.resolved_at else None,
    }


@router.get("")
def list_escalations(
    agent: User = Depends(require_agent),
    db: Session = Depends(get_db),
) -> list[dict]:
    """List open escalations for the agent queue, newest first."""
    return [_serialize(e) for e in list_open_escalations(db)]


@router.post("/{escalation_id}/resolve")
def mark_resolved(
    escalation_id: str,
    agent: User = Depends(require_agent),
    db: Session = Depends(get_db),
) -> dict:
    """Mark an escalation resolved by the acting agent."""
    try:
        parsed = uuid.UUID(escalation_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="escalation_not_found") from None
    try:
        escalation = resolve_escalation(db, parsed, agent.id)
    except LookupError:
        raise HTTPException(status_code=404, detail="escalation_not_found") from None
    return _serialize(escalation)
