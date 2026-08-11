"""Escalation service (T046, plan Section 14).

Persistence and lifecycle for cases handed to a human agent. Escalations are
worker-initiated, audited records created when the Worker cannot safely answer
or act (sensitive, high-risk, unsupported, ambiguous). Human agents list open
escalations and mark them resolved.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.escalation import Escalation


def create_escalation(
    db: Session,
    conversation_id: uuid.UUID,
    reason: str,
    context: str,
) -> Escalation:
    """Create a new open escalation for a conversation."""
    escalation = Escalation(
        conversation_id=conversation_id,
        reason=reason,
        context=context,
        status="open",
    )
    db.add(escalation)
    db.commit()
    db.refresh(escalation)
    return escalation


def list_open_escalations(db: Session) -> list[Escalation]:
    """Return open escalations, newest first."""
    return list(
        db.scalars(
            select(Escalation)
            .where(Escalation.status == "open")
            .order_by(Escalation.created_at.desc())
        ).all()
    )


def resolve_escalation(
    db: Session,
    escalation_id: uuid.UUID,
    handled_by: uuid.UUID,
) -> Escalation:
    """Mark an escalation resolved by an agent."""
    escalation = db.get(Escalation, escalation_id)
    if escalation is None:
        raise LookupError("escalation_not_found")
    escalation.status = "resolved"
    escalation.handled_by = handled_by
    escalation.resolved_at = datetime.now(UTC)
    db.commit()
    db.refresh(escalation)
    return escalation
