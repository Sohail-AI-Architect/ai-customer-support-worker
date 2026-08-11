"""GET/POST /api/tickets and GET /api/tickets/{id} (US2, US3).

Reads are session-scoped: a customer may only read their OWN tickets; reading
another customer's ticket is refused (FR-006, SC-005). Creation (POST) inserts
a ticket for the authenticated customer (US3, FR-010). No update/close/delete
endpoint exists — tickets are create + read-only only.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.deps import get_customer
from api.schemas import TicketCreateRequest
from db import get_db
from domain.authorization import SessionScope, ensure_customer_scope
from models.customer import Customer
from models.ticket import SupportTicket

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


def _serialize(ticket: SupportTicket) -> dict:
    return {
        "id": str(ticket.id),
        "subject": ticket.subject,
        "status": ticket.status,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
    }


@router.get("")
def list_tickets(
    customer: Customer = Depends(get_customer),
    db: Session = Depends(get_db),
) -> list[dict]:
    scope = SessionScope(str(customer.id))
    tickets = db.scalars(
        select(SupportTicket).where(SupportTicket.customer_id == scope.customer_id)
    ).all()
    return [_serialize(t) for t in tickets]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreateRequest,
    customer: Customer = Depends(get_customer),
    db: Session = Depends(get_db),
) -> dict:
    """Create a ticket for the authenticated customer (US3).

    Create-only (FR-010): the returned ticket has status "open" and no
    update/close/delete capability is exposed here.
    """
    ticket = SupportTicket(
        customer_id=customer.id,
        subject=payload.subject,
        description=payload.description,
        status="open",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return _serialize(ticket)


@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: str,
    customer: Customer = Depends(get_customer),
    db: Session = Depends(get_db),
) -> dict:
    try:
        parsed = uuid.UUID(ticket_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="ticket_not_found") from None

    ticket = db.get(SupportTicket, parsed)
    if ticket is None:
        raise HTTPException(status_code=404, detail="ticket_not_found")

    # Session scoping: only the owning customer may read this ticket.
    scope = SessionScope(str(customer.id))
    ensure_customer_scope(scope, str(ticket.customer_id))
    return _serialize(ticket)
