"""Agent-facing approval endpoints (T055, US5).

Human agents list pending approval requests and approve or deny them. Agent role
is required (require_agent). Approvals are worker-initiated and audited; a
decision on a non-pending approval returns 409 (plan Section 14, FR-014/015).
"""

import uuid

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db, require_agent
from models.user import User
from services.approvals import VALID_DECISIONS, decide_approval, list_pending_approvals

router = APIRouter(prefix="/api/agent/approvals", tags=["agent-approvals"])


def _serialize(approval) -> dict:
    return {
        "id": str(approval.id),
        "conversation_id": str(approval.conversation_id),
        "proposed_action": approval.proposed_action,
        "payload": approval.payload or {},
        "status": approval.status,
        "created_at": approval.created_at.isoformat() if approval.created_at else None,
        "decided_by": str(approval.decided_by) if approval.decided_by else None,
        "decided_at": approval.decided_at.isoformat() if approval.decided_at else None,
    }


@router.get("")
def list_approvals(
    agent: User = Depends(require_agent),
    db: Session = Depends(get_db),
) -> list[dict]:
    """List pending approval requests for the agent queue, newest first."""
    return [_serialize(a) for a in list_pending_approvals(db)]


@router.post("/{approval_id}/decision")
def decide(
    approval_id: str,
    decision: str = Body(..., embed=True),
    agent: User = Depends(require_agent),
    db: Session = Depends(get_db),
) -> dict:
    """Approve or deny a pending approval (409 if it is no longer pending)."""
    try:
        parsed = uuid.UUID(approval_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="approval_not_found") from None
    if decision not in VALID_DECISIONS:
        raise HTTPException(status_code=422, detail="decision must be approved or denied")
    try:
        approval = decide_approval(db, parsed, decision, agent.id)
    except LookupError:
        raise HTTPException(status_code=404, detail="approval_not_found") from None
    except ValueError as exc:
        if str(exc) == "approval_not_pending":
            raise HTTPException(status_code=409, detail="approval_not_pending") from None
        raise HTTPException(status_code=422, detail=str(exc)) from None
    return _serialize(approval)
