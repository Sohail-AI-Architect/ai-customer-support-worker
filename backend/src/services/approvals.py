"""Approval service (T053, plan Section 14).

Persistence and lifecycle for sensitive/state-changing actions the Worker
proposes but must not execute until a human approves (FR-014/015). Records are
worker-initiated and audited; a human agent approves or denies a pending
approval and the outcome is recorded for audit.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.approval import ApprovalRequest

VALID_DECISIONS = {"approved", "denied"}


def create_approval_request(
    db: Session,
    conversation_id: uuid.UUID,
    proposed_action: str,
    payload: dict | None = None,
) -> ApprovalRequest:
    """Create a pending approval request for a conversation (worker-initiated)."""
    approval = ApprovalRequest(
        conversation_id=conversation_id,
        proposed_action=proposed_action,
        payload=payload or {},
        status="pending",
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


def list_pending_approvals(db: Session) -> list[ApprovalRequest]:
    """Return pending approvals, newest first."""
    return list(
        db.scalars(
            select(ApprovalRequest)
            .where(ApprovalRequest.status == "pending")
            .order_by(ApprovalRequest.created_at.desc())
        ).all()
    )


def decide_approval(
    db: Session,
    approval_id: uuid.UUID,
    decision: str,
    decided_by: uuid.UUID,
) -> ApprovalRequest:
    """Approve or deny a pending approval.

    Raises LookupError if the approval does not exist, or ValueError if it is
    no longer pending (already decided).
    """
    if decision not in VALID_DECISIONS:
        raise ValueError("invalid_decision")
    approval = db.get(ApprovalRequest, approval_id)
    if approval is None:
        raise LookupError("approval_not_found")
    if approval.status != "pending":
        raise ValueError("approval_not_pending")
    approval.status = decision
    approval.decided_by = decided_by
    approval.decided_at = datetime.now(UTC)
    db.commit()
    db.refresh(approval)
    return approval
